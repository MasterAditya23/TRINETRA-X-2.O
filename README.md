# TRINETRA-X | AI Surveillance System

### AI-Based Intelligent Video Analytics for Border Surveillance
**Smart India Hackathon 2026 Prototype | Problem Statement: SIH 26187**

TRINETRA-X transforms a compatible IP camera into an AI-assisted surveillance system. It uses computer vision to detect and track objects, identify configured virtual-fence intrusions, capture evidence, and present events through a centralized web dashboard.

**Our approach:** Convert continuous surveillance video into actionable intelligence while supporting local processing and evidence-based monitoring.

**Repository:** [MasterAditya23/TRINETRA-X-2.O](https://github.com/MasterAditya23/TRINETRA-X-2.O)

---

## 1. Key Features

- **AI Object Detection:** Detect supported objects using YOLOv8.
- **Object Tracking:** Track detected objects across video frames.
- **Virtual Fence:** Evaluate object movement against configured restricted zones.
- **Intrusion Alerts:** Generate visual and audible alerts when configured rules are triggered.
- **Evidence Capture:** Save snapshots associated with relevant events.
- **Local Event Database:** Store event information using SQLite.
- **Live Dashboard:** View available camera feeds and event information.
- **PDF Reports:** Export supported event records through the dashboard.

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| AI and Vision | Python, OpenCV, YOLOv8, NumPy |
| Backend | Flask, Flask-CORS |
| Database | SQLite |
| Frontend | React, Vite, Axios |
| Reporting | jsPDF and applicable table plugins |
| Camera Input | Android IP Webcam over local Wi-Fi |

## 3. System Architecture

```text
Android IP Webcam
        ↓
 Local HTTP Video Stream
        ↓
 OpenCV Frame Processing
        ↓
 YOLOv8 Detection and Tracking
        ↓
 Virtual Fence and Event Logic
        ↓
 Alerts + Evidence Snapshots
        ↓
 Flask API + SQLite Database
        ↓
 React Dashboard + PDF Reports
```

The architecture separates the presentation, processing, and data layers, making the system easier to maintain and extend.

## 4. Requirements

- Windows 10/11 laptop or desktop.
- Python compatible with the project's dependencies.
- Node.js and npm.
- Git.
- Android smartphone with IP Webcam installed.
- Phone and laptop connected to the same reachable Wi-Fi network.
- Internet access for initial downloads and package installation.

A GPU is not mandatory for every configuration, but performance depends on the computer, model, resolution, and processing load.

## 5. Download the Project

Open PowerShell and run:

```powershell
git clone https://github.com/MasterAditya23/TRINETRA-X-2.O.git
cd TRINETRA-X-2.O
```

If the repository's actual Git URL differs, copy the clone URL from its GitHub page.

## 6. Install Dependencies

### Backend — Python

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Ensure `requirements.txt` exists in the project root. If your downloaded repository places it elsewhere, use its actual location.

### Frontend — React

Open a second terminal:

```powershell
cd path\to\TRINETRA-X-2.O\frontend
npm install
```

Replace `path\to\TRINETRA-X-2.O` with your actual project directory.

## 7. Connect Your Phone as the Camera

**For the current demonstration, configure only ONE phone and ONE camera stream.** Leave the other camera entries disabled to avoid unnecessary processing load.

### Step 1 — Install IP Webcam

1. Open Google Play Store on your Android phone.
2. Search for **IP Webcam** and install the compatible application.
3. Connect the phone to the same Wi-Fi network as the laptop.
4. Open IP Webcam and select its server-start option.
5. Note the local IP address and port displayed on the phone.

App search: [IP Webcam on Google Play](https://play.google.com/store/search?q=IP%20Webcam&c=apps)

### Step 2 — Test the video stream

The typical stream URL is:

```text
http://PHONE_IP:8080/video
```

For example:

```text
http://192.168.43.47:8080/video
```

**The example IP is not universal.** Use the current address shown by your phone.

Open the URL in the laptop's browser. If the stream is accessible, proceed to the next step.

### Step 3 — Enter your phone's IP in the code

1. Open the project in VS Code.
2. Open this file:

   `backend/app.py`

3. Find the camera configuration section near the top of the file:

```python
CAMERAS = {
    'CAM-01': None,
    'CAM-02': 'http://192.168.43.47:8080/video',
    'CAM-03': None,
    'CAM-04': None
}
```

4. Replace the example URL with the actual video URL displayed by your phone. Keep only one camera enabled:

```python
CAMERAS = {
    'CAM-01': 'http://YOUR_PHONE_IP:8080/video',
    'CAM-02': None,
    'CAM-03': None,
    'CAM-04': None
}
```

Replace `YOUR_PHONE_IP` with your phone's actual IP address. For example, if your phone displays `192.168.43.47`, use:

```python
'CAM-01': 'http://192.168.43.47:8080/video',
```

5. Save the file using `Ctrl + S`.

**Important:** Keep the dictionary keys and `None` values as shown. Do not enter the URL outside the quotation marks or add a second active camera for this demonstration.

If your current source code requires a particular camera identifier, preserve the identifier expected by its camera-processing logic.

### Step 4 — Restart the backend

If the backend is already running, stop it with `Ctrl + C`. Start it again after saving the configuration.

If the phone receives a new IP address after reconnecting to Wi-Fi, update the URL and restart the backend.

## 8. Run the Complete Application

Keep the phone's IP Webcam server running throughout the demonstration.

### Terminal 1 — Backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

The terminal should show the backend startup output. Resolve any initialization or camera-connection errors before proceeding.

### Terminal 2 — Frontend

Open a new terminal:

```powershell
cd path\to\TRINETRA-X-2.O\frontend
npm run dev
```

Open the local URL printed by Vite, commonly:

```text
http://localhost:5173
```

Keep both terminals open while using the dashboard.

## 9. Demonstrate the Prototype

Follow this sequence during evaluation:

1. **Camera Input:** Show the live smartphone camera stream.
2. **AI Detection:** Place a supported object within the camera's view.
3. **Tracking:** Show the detection and tracking information, if enabled.
4. **Virtual Fence:** Demonstrate movement across the configured boundary.
5. **Alert:** Show the intrusion event and the configured audible or visual alert.
6. **Evidence:** Verify that the associated snapshot is saved.
7. **Event History:** Show the event recorded in the dashboard.
8. **PDF Report:** Export a report using the available report-generation control.

Actual output depends on the current configuration and successful operation of each component.

## 10. Troubleshooting

| Problem | What to check |
|---|---|
| Phone stream unavailable | Confirm IP Webcam is running and the URL is correct. |
| Phone and laptop cannot connect | Check Wi-Fi connectivity, router client isolation, and firewall rules. |
| Camera stops working | Check whether the phone's IP address has changed. |
| Backend fails to start | Verify Python environment and dependency installation. |
| Dashboard does not load | Check the frontend terminal and Vite URL. |
| Dashboard shows no events | Verify camera input, backend status, detection, and virtual-fence settings. |
| Intrusion alert does not trigger | Check object detection, boundary configuration, and event rules. |
| PDF export fails | Check frontend dependencies and browser-console errors. |
| Processing is slow | Start with one camera and reduce supported processing resolution if necessary. |

## 11. Current Prototype vs. Future Scope

### Current Prototype

The demonstration uses a smartphone as an IP camera, a Python/OpenCV/YOLOv8 processing pipeline, virtual-fence event logic, local SQLite storage, and a React dashboard with reporting functionality.

### Future Scope

- Integration with compatible CCTV, PTZ, and thermal cameras.
- Edge AI deployment on suitable hardware.
- Automatic Number Plate Recognition (ANPR).
- Advanced behaviour and movement analysis.
- Secure access controls, audit logs, and operational monitoring.
- Carefully validated multi-camera deployment.

These future capabilities require additional implementation and testing; they should not be interpreted as completed or officially deployed features.

## 12. Potential Impact

TRINETRA-X aims to support security operators by prioritizing relevant events, preserving evidence, and reducing dependence on uninterrupted manual video observation.

Its software-first architecture may allow compatible existing camera infrastructure to be reused, potentially reducing additional hardware requirements. Any real deployment would require performance validation, cybersecurity assessment, and the relevant approvals.

**TRINETRA-X — From Continuous Video to Actionable Intelligence.**

*Prototype status: Developed for demonstration and evaluation. It is not a substitute for established security procedures or a certified forensic system.*
