


# AI Surveillance System with ESP32-CAM

> Real-time multi-camera surveillance system with AI-based detection of weapons and people. Built with ESP32-CAM, YOLOv8, Flask, and Qt.

![image](https://github.com/user-attachments/assets/1bc702db-762e-4786-a803-9f0ad2fd03e2)

## Overview

This project implements a scalable AI-powered surveillance system consisting of:

- **ESP32-CAM Nodes**: Capture JPEG images and send to the server.
- **Python Flask Server**: Runs object detection using YOLOv8 and manages multiple camera streams.
- **Qt GUI Client**: Displays live annotated feeds with status indicators and IP labels.

All AI computations are performed **on the server**, enabling lightweight camera nodes.

---

## Components

### ESP32-CAM Firmware

- Written in C++ (PlatformIO)
- Captures frames and sends them to a configurable list of server IPs.
- Lightweight and optimized for battery-powered operation.

> Folder: `esp32cam-firmware/`

### Python Flask Server

- Accepts frames from ESP32 nodes.
- Performs:
  - **Weapon detection** (pistol, rifle, knife) using a custom-trained `YOLOv8m` model.
  - **Person detection** using pre-trained `YOLOv8l`.
- Annotates images and broadcasts live feeds.

> Folder: `server/`

### 🖥️ Qt GUI Client (C++)

- Developed using **Qt Creator**.
- Fetches active camera IPs.
- Displays annotated feeds with:
  - Smooth scaling and alignment.
  - IP tag and live/offline status indicator.
- Automatically refreshes feed every 100 ms.

> Folder: `client/`

---

## AI Models

- YOLOv8 used for object detection via [Ultralytics](https://github.com/ultralytics/ultralytics).
- Trained on [Roboflow Weapon Detection Dataset](https://universe.roboflow.com/weapon-detect-qbsiw/yolo-weapon-detection).
- Training:
  - 100 epochs
  - Model: `YOLOv8m`
  - Optimized for pistols, rifles, and knives

---

## System Architecture

