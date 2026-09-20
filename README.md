# 👁️ TRINETRA X - AI Surveillance System

> **Smart India Hackathon (SIH) 2026 Prototype**
> An end-to-end, multi-node AI security perimeter system utilizing Edge computing and computer vision.

## 🚀 Overview
TRINETRA X transforms standard IP cameras (including mobile devices) into an intelligent, multi-node surveillance network. Built for high-security perimeters, it utilizes YOLOv8 to track intrusions across custom virtual tripwires, logs evidence locally, and streams live feeds to a centralized React dashboard with automated alerting and PDF report generation.

## ✨ Key Features
* **Multi-Node IP Streaming:** Supports up to 4 simultaneous MJPEG network camera streams.
* **Edge AI Processing:** Real-time object detection and tracking using YOLOv8.
* **Custom Perimeter Geometry:** Configurable polygonal restriction zones (math-based intrusion logic).
* **Automated Evidence Logging:** Captures high-res snapshots of intruders and logs metadata to a SQLite database.
* **Live Command Dashboard:** React frontend featuring live video playback, metric polling, and a dynamic grid.
* **Critical Alert System:** Visual flashing UI and synthesized Web Audio API sirens on detection.
* **Enterprise Reporting:** One-click dynamic PDF generation with embedded snapshot evidence.

## 🛠️ Tech Stack
* **AI & Vision:** Python, OpenCV, Ultralytics YOLOv8, NumPy
* **Backend API:** Flask, Flask-CORS, SQLite3
* **Frontend:** React, Vite, Axios, Lucide-React, jsPDF
* **Infrastructure:** IP Webcam (Android Edge Nodes), Git

## ⚙️ Quick Start Setup

### 1. Backend Initialization
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Start the Flask API and AI Streamer
python backend\app.py