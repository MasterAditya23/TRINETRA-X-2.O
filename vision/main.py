import cv2
import time
import os
import requests
from datetime import datetime
from ultralytics import YOLO

# The URL of our local Flask backend
API_URL = "http://127.0.0.1:5000/api/events"

def run_vision_system():
    print("[INFO] Starting TRINETRA X Integrated Vision System...")
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    track_history = {}
    cooldowns = {}
    COOLDOWN_SECONDS = 5
    CAMERA_ID = "CAM-01"

    print("[INFO] System Active. Cross the line to trigger an end-to-end event. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        FENCE_X = 320 
        cv2.line(frame, (FENCE_X, 0), (FENCE_X, frame.shape[0]), (255, 0, 0), 2)
        cv2.putText(frame, "RESTRICTED ZONE ->", (FENCE_X + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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
                
                # Get object name (e.g., 'person', 'car')
                object_type = model.names[int(cls_idx)]
                confidence_pct = round(float(conf) * 100, 2)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                current_time = time.time()
                is_in_cooldown = False
                text_color = (0, 255, 0)
                
                if track_id in cooldowns and (current_time - cooldowns[track_id]) < COOLDOWN_SECONDS:
                    is_in_cooldown = True
                    text_color = (0, 165, 255)

                cv2.putText(frame, f"ID: {track_id} {object_type} {confidence_pct}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
                
                # -- INTEGRATED INTRUSION LOGIC --
                if track_id in track_history:
                    prev_cx, prev_cy = track_history[track_id]
                    
                    if prev_cx < FENCE_X and cx >= FENCE_X:
                        if not is_in_cooldown:
                            print(f"\n[🚨 INTRUSION] ID {track_id} ({object_type}) crossed the line!")
                            
                            # 1. Save Snapshot
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{CAMERA_ID}_{timestamp}_intrusion_id{track_id}.jpg"
                            filepath = os.path.join("data", "snapshots", filename)
                            
                            cv2.putText(frame, "EVIDENCE: INTRUSION DETECTED", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            cv2.imwrite(filepath, frame)
                            print(f"[📸 EVIDENCE SAVED] {filename}")
                            
                            # 2. Send Data to Backend API
                            event_payload = {
                                "camera_id": CAMERA_ID,
                                "event_type": "INTRUSION",
                                "object_type": object_type,
                                "confidence": float(conf),
                                "zone": "Restricted Zone",
                                "snapshot_path": filepath
                            }
                            
                            try:
                                response = requests.post(API_URL, json=event_payload)
                                if response.status_code == 201:
                                    print(f"[✅ API SUCCESS] Event stored in database: {response.json().get('event_id')}")
                                else:
                                    print(f"[❌ API ERROR] Backend returned {response.status_code}")
                            except Exception as e:
                                print(f"[❌ API FAILED] Could not reach backend: {e}")
                            
                            cooldowns[track_id] = current_time
                            
                track_history[track_id] = (cx, cy)

        cv2.imshow("TRINETRA X - Integrated Vision", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_vision_system()