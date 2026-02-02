# 🚗 Vehicle Safety System – Motion & Driver Drowsiness Detection

## Key Features
- Real-time **driver eye monitoring** using a camera
- **Driver drowsiness detection** using computer vision
- **Vehicle motion & shake detection** using accelerometer + ML
- AI-based motion classification (Idle, Snake, Updown, Wave)
- **Instant Telegram alerts** with optional image capture
- Non-intrusive, embedded, and easy to deploy
- Designed for **Arduino UNO Q (Linux + MCU architecture)**



## 🚘 Project Overview

The **Vehicle Safety System** is a real-time, embedded safety solution designed to enhance road safety by monitoring both **vehicle behavior** and **driver alertness**.

The system combines:
- **Accelerometer-based motion classification** using a pre-trained ML model
- **Camera-based drowsiness detection** by analyzing eye closure

When abnormal vehicle motion or driver fatigue is detected, the system sends **instant Telegram alerts**, helping prevent accidents caused by driver drowsiness or unsafe vehicle conditions.

This project is ideal for:
- Smart vehicle safety systems
- Embedded AI applications
- Research and academic projects
- Long-distance driving safety monitoring



## Technologies Used

- **Python**
- **OpenCV**
- **Arduino App Lab**
- **Telegram Bot API**
- **Modulino® Movement Sensor**
- **Arduino UNO Q**


## Hardware Requirements

- Arduino® UNO Q
- Modulino® Movement sensor
- Qwiic cable
- USB-C cable
- USB camera


## Software Requirements

- Arduino App Lab (UNO Q Linux environment)
- Python 3.9+


## Python Environment Setup

### Upgrade pip

```bash
python3 -m pip install --upgrade pip --break-system-packages
```
Install Required Libraries
```bash
python3 -m pip install \
opencv-python \
requests \
--break-system-packages

```

>⚠️ Arduino-specific modules, arduino.app_utils and arduino.app_bricks.motion_detection are preinstalled in Arduino App Lab.

## Telegram Bot Setup
- Create a Telegram bot using @BotFather
- Copy the Bot Token
- Get your Chat ID (using @userinfobot)
### Recommended: Environment Variables
```bash
export TG_BOT_TOKEN="YOUR_BOT_TOKEN"
export TG_CHAT_ID="YOUR_CHAT_ID"
```

### Or Configure in main.py