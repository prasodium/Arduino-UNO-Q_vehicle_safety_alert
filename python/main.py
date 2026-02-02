# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL
# SPDX-License-Identifier: MPL-2.0

# ================= IMPORTS =================
import cv2
import time
import os
import requests
from datetime import datetime
from arduino.app_utils import *
from arduino.app_bricks.motion_detection import MotionDetection

# ================= TELEGRAM CONFIG =================
BOT_TOKEN = os.getenv("8335146846:AAG3REJxz2oOOTpPVk-A2ZTsWCPO1HzpPvE") or "8335146846:AAG3REJxz2oOOTpPVk-A2ZTsWCPO1HzpPvE"
CHAT_ID   = os.getenv("6849528320") or "6849528320"

ALERT_COOLDOWN = 10  # seconds

# ================= CAMERA CONFIG =================
CAMERA_INDEX = 0
FRAME_WIDTH = 400
CLOSED_FRAMES_THRESHOLD = 3
CAPTURE_DIR = "captures"
MAX_STORED_IMAGES = 20

# ================= MOTION CONFIG =================
CONFIDENCE = 0.4
SHAKE_CLASSES = ["snake", "updown", "wave"]
SHAKE_CONFIDENCE_THRESHOLD = 0.6
SHAKE_TIME_THRESHOLD = 2.5  # seconds

# ================= INIT =================
os.makedirs(CAPTURE_DIR, exist_ok=True)

logger = Logger("vehicle-safety-system")
logger.info("Starting Vehicle Safety System")

# Separate cooldown timers
last_shake_alert_time = 0
last_drowsy_alert_time = 0

shake_start_time = None
shake_active = False

# ================= TELEGRAM =================
def send_telegram(text, image_path=None, alert_type="generic"):
    global last_shake_alert_time, last_drowsy_alert_time
    now = time.time()

    if alert_type == "shake":
        if now - last_shake_alert_time < ALERT_COOLDOWN:
            return
        last_shake_alert_time = now

    elif alert_type == "drowsy":
        if now - last_drowsy_alert_time < ALERT_COOLDOWN:
            return
        last_drowsy_alert_time = now

    try:
        if image_path:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(image_path, "rb") as img:
                requests.post(
                    url,
                    files={"photo": img},
                    data={"chat_id": CHAT_ID, "caption": text},
                    timeout=10
                )
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(
                url,
                data={"chat_id": CHAT_ID, "text": text},
                timeout=10
            )

        logger.info("Telegram alert sent")

    except Exception as e:
        logger.exception(f"Telegram error: {e}")

# ================= MOTION DETECTION =================
motion_detection = MotionDetection(confidence=CONFIDENCE)

def on_movement_detected(classification: dict):
    global shake_start_time, shake_active

    if not classification:
        return

    now = time.time()
    max_shake_conf = max(classification.get(c, 0.0) for c in SHAKE_CLASSES)

    if max_shake_conf >= SHAKE_CONFIDENCE_THRESHOLD:
        if shake_start_time is None:
            shake_start_time = now

        elif (now - shake_start_time) >= SHAKE_TIME_THRESHOLD and not shake_active:
            shake_active = True

            message = (
                "🚗 Vehicle Shake Detected\n"
                f"Confidence: {max_shake_conf:.2f}\n"
                f"Duration: {SHAKE_TIME_THRESHOLD} sec\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            logger.warning("Vehicle shake confirmed")
            send_telegram(message, alert_type="shake")

    else:
        shake_start_time = None
        shake_active = False

for cls in ["idle", "snake", "updown", "wave"]:
    motion_detection.on_movement_detection(cls, on_movement_detected)

# ================= BRIDGE =================
def record_sensor_movement(x: float, y: float, z: float):
    try:
        # Convert g → m/s²
        motion_detection.accumulate_samples(
            (x * 9.81, y * 9.81, z * 9.81)
        )
    except Exception as e:
        logger.exception(f"record_sensor_movement error: {e}")

Bridge.provide("record_sensor_movement", record_sensor_movement)

# ================= DROWSINESS DETECTION =================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
)

cap = cv2.VideoCapture(CAMERA_INDEX)
closed_eye_frames = 0

def cleanup_images():
    files = sorted(
        [os.path.join(CAPTURE_DIR, f) for f in os.listdir(CAPTURE_DIR) if f.endswith(".jpg")],
        key=os.path.getmtime
    )
    while len(files) > MAX_STORED_IMAGES:
        os.remove(files.pop(0))

# ================= MAIN LOOP =================
def loop():
    global closed_eye_frames

    ret, frame = cap.read()
    if not ret:
        time.sleep(0.05)
        return

    h, w = frame.shape[:2]
    frame = cv2.resize(frame, (FRAME_WIDTH, int(h * FRAME_WIDTH / w)))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        closed_eye_frames = 0
        return

    eyes_detected = False
    for (x, y, w, h) in faces:
        roi = gray[y:y + h // 2, x:x + w]
        eyes = eye_cascade.detectMultiScale(
            roi,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(30, 30)
        )
        if len(eyes) >= 2:
            eyes_detected = True
            break

    closed_eye_frames = closed_eye_frames + 1 if not eyes_detected else 0

    if closed_eye_frames >= CLOSED_FRAMES_THRESHOLD:
        image_path = os.path.join(
            CAPTURE_DIR, f"drowsy_{int(time.time())}.jpg"
        )
        cv2.imwrite(image_path, frame)
        cleanup_images()

        message = (
            "🚨 Driver Drowsiness Detected\n"
            "Eyes CLOSED\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        send_telegram(
            message,
            image_path=image_path,
            alert_type="drowsy"
        )

        closed_eye_frames = 0

    time.sleep(0.02)

# ================= START APP =================
logger.info("System running (NO Web UI)")
App.run(user_loop=loop)
