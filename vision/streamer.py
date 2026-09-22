import cv2
import time
import os
import requests
import numpy as np
from datetime import datetime
from ultralytics import YOLO

print("[INFO] Loading YOLOv8 model for Multi-Camera Stream...")
model = YOLO("yolov8n.pt")
API_URL = "http://127.0.0.1:5000/api/events"

# NEW: Global state to control Night Vision from Flask
CAMERA_SETTINGS = {
    "night_vision": False
}

def apply_night_vision(frame):
    """Applies low-light enhancement and tactical green phosphor effect."""
    # 1. Gamma Correction (boosts dark shadows without blowing out highlights)
    gamma = 1.8
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    bright_frame = cv2.LUT(frame, table)

    # 2. CLAHE (Adaptive Contrast)
    lab = cv2.cvtColor(bright_frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l)
    enhanced_lab = cv2.merge((enhanced_l, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # 3. Tactical Green Effect
    gray = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2GRAY)
    tactical = np.zeros_like(enhanced_bgr)
    tactical[:, :, 1] = gray # Map intensity strictly to Green channel
    tactical[:, :, 0] = (gray * 0.15).astype("uint8") # Subtle blue ambient
    return tactical

def generate_frames(camera_source, camera_id):
    if str(camera_source) == '0':
        camera_source = 0
        
    cap = cv2.VideoCapture(camera_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    track_history = {}
    cooldowns = {}
    COOLDOWN_SECONDS = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(2)
            cap = cv2.VideoCapture(camera_source)
            continue

        # NEW: Apply Night Vision if toggled ON
        if CAMERA_SETTINGS.get("night_vision", False):
            frame = apply_night_vision(frame)
            cv2.putText(frame, "TACTICAL NIGHT VISION: ON", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw Virtual Fence
        FENCE_X = int(frame.shape[1] / 2)
        cv2.line(frame, (FENCE_X, 0), (FENCE_X, frame.shape[0]), (255, 0, 0), 2)
        cv2.putText(frame, "RESTRICTED ZONE ->", (FENCE_X + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"{camera_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        results = model.track(frame, persist=True, classes=[0, 2, 3, 5, 7], verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            class_indices = results[0].boxes.cls.cpu().numpy()
            
            for box, track_id, conf, cls_idx in zip(boxes, track_ids, confidences, class_indices):
                x1, y1, x2, y2 = map(int, box)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                object_type = model.names[int(cls_idx)]
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                current_time = time.time()
                is_in_cooldown = False
                text_color = (0, 255, 0)
                
                if track_id in cooldowns and (current_time - cooldowns[track_id]) < COOLDOWN_SECONDS:
                    is_in_cooldown = True
                    text_color = (0, 165, 255)

                cv2.putText(frame, f"ID:{track_id} {object_type}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
                
                if track_id in track_history:
                    prev_cx, prev_cy = track_history[track_id]
                    if prev_cx < FENCE_X and cx >= FENCE_X:
                        if not is_in_cooldown:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{camera_id}_{timestamp}_id{track_id}.jpg"
                            
                            BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                            SNAPSHOT_DIR = os.path.join(BASE_DIR, "data", "snapshots")
                            os.makedirs(SNAPSHOT_DIR, exist_ok=True) 
                            filepath = os.path.join(SNAPSHOT_DIR, filename)
                            
                            cv2.putText(frame, "INTRUSION DETECTED", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            success = cv2.imwrite(filepath, frame)
                            if success:
                                print(f"[INFO] Evidence Snapshot saved successfully: {filename}")
                            
                            event_payload = {
                                "camera_id": camera_id,
                                "event_type": "INTRUSION",
                                "object_type": object_type,
                                "confidence": float(conf),
                                "zone": "Restricted Zone",
                                "snapshot_path": filepath
                            }
                            try:
                                requests.post(API_URL, json=event_payload, timeout=1)
                            except Exception as e:
                                pass
                            
                            cooldowns[track_id] = current_time
                            
                track_history[track_id] = (cx, cy)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')