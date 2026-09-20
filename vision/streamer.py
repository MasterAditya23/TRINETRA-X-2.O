import cv2
import time
import os
import requests
from datetime import datetime
from ultralytics import YOLO

print("[INFO] Loading YOLOv8 model for Multi-Camera Stream...")
model = YOLO("yolov8n.pt")
API_URL = "http://127.0.0.1:5000/api/events"

def generate_frames(camera_source, camera_id):
    """Generator that yields annotated video frames for a specific camera."""
    
    # If the source is '0' (string), convert it to int 0 for local webcam
    if str(camera_source) == '0':
        camera_source = 0
        
    cap = cv2.VideoCapture(camera_source)
    
    # Lower resolution for performance when running multiple cameras
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    track_history = {}
    cooldowns = {}
    COOLDOWN_SECONDS = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[WARNING] Lost connection to {camera_id}. Retrying...")
            time.sleep(2)
            cap = cv2.VideoCapture(camera_source)
            continue

        # Draw Virtual Fence
        FENCE_X = int(frame.shape[1] / 2) # Middle of the frame dynamically
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
                            filepath = os.path.join("data", "snapshots", filename)
                            
                            cv2.putText(frame, "INTRUSION DETECTED", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            cv2.imwrite(filepath, frame)
                            
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