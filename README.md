# AI Surveillance System with ESP32-CAM

> Real-time multi-camera surveillance system with AI-powered detection of people and weapons. Built with ESP32-CAM, YOLOv8, Flask, and Qt.

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

### Qt GUI Client (C++)

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

![image](https://github.com/user-attachments/assets/a4b3d319-e660-4e9d-b266-6353d61c8a3d)

---

## System Architecture

![image](https://github.com/user-attachments/assets/1bc702db-762e-4786-a803-9f0ad2fd03e2)


> All detection is centralized — ESP32 nodes are lightweight, cost-efficient, and easy to deploy.

---
## How to Run

### Prerequisites

- Python 3.11+
- ESP32-CAM module (AI Thinker or similar)
- PlatformIO (VSCode)
- Qt Creator (for GUI client)
- Ultralytics library: `pip install ultralytics`

### 1. Flash ESP32-CAM

```sh
cd esp32cam-firmware/
pio run --target upload
```

Update SSID, password, and server IP in the firmware before flashing.

### 2. Start the Server

Update the Telegram bot token in `notification.py`

```bash
cd server/
python app.py
```

Ensure the correct YOLO model weights exist under `server/weights`.

### 3. Run the Client GUI

Update the server IP in `clienteye.cpp`

Open `clienteye.pro` in Qt Creator and run the project.

---

## File Structure

```
AI-surveillance-system-esp32/
├── esp32cam-firmware/       ESP32 source code
├── server/                  Flask + YOLOv8 detection server
│   ├── app.py
│   ├── detect.py
│   ├── camclass.py
│   └── weights/             YOLOv8 models
├── client/                  Qt GUI Client
│   └── clienteye.cpp/h
└── assets/
    └── system_architecture.png
```

---

## Sample Output
## Client:

<img src="https://github.com/user-attachments/assets/3cdd6a00-c710-4e03-9f47-3e8678b3dac9" width="300"/>
<img src="https://github.com/user-attachments/assets/b7f9a009-42ca-40dd-8443-e18ddcee3766" width="300"/>
<img src="https://github.com/user-attachments/assets/992de30b-985d-44e2-bd70-c6d797486eb8" width="300"/>

## Notifications:

<p align="center">
  <img src="https://github.com/user-attachments/assets/977c62a7-69bb-4223-9128-0c66ba19ec85" width="400"/>
  <img src="https://github.com/user-attachments/assets/cd1e81b0-649b-4dcd-a29a-a53589109fc2" width="400"/>
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/2b3e503d-332c-44e7-a0e5-4ef920c5765d" width="400"/>
  <img src="https://github.com/user-attachments/assets/6335a439-9eb1-473c-be53-58262077d92d" width="400"/>
</p>





---

## Features

- Realtime multi-camera support
- AI detection of people and weapons
- Telegram notifications via bot in case of threat detection
- Offline ESP32 processing (no detection load)
- Smooth cross-platform GUI
- Modular and extensible system: The ESP32-CAM costs around $7, making it a cost-effective option for covering larger areas.

---

## Future Improvements

- HTTPs instead of HTTP
- Cloud upload and remote access
- Mobile version of GUI client
- Add motion detection and smart frame skipping
- Web dashboard (Flask + Bootstrap or React)

---

## License

MIT — Feel free to use, modify, and expand upon.

---

## Author

**Lev Vedrov**  
levvedrov@g.skku.edu

GitHub: [@levvedrov](https://github.com/levvedrov)
