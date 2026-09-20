import cv2
import time
import os
from datetime import datetime
from ultralytics import YOLO

def test_evidence_snapshot():
    print("[INFO] Loading YOLOv8 model for Evidence Snapshot...")
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    track_history = {}
    cooldowns = {}
    COOLDOWN_SECONDS = 5
    CAMERA_ID = "CAM-01"

    print("[INFO] Snapshot Engine active. Cross the line to capture evidence. Press 'q' to quit.")

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
            
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = map(int, box)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # Draw visual elements on the frame BEFORE saving it
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                current_time = time.time()
                is_in_cooldown = False
                text_color = (0, 255, 0)
                
                if track_id in cooldowns:
                    if (current_time - cooldowns[track_id]) < COOLDOWN_SECONDS:
                        is_in_cooldown = True
                        text_color = (0, 165, 255)

                cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                
                # -- INTRUSION & SNAPSHOT LOGIC --
                if track_id in track_history:
                    prev_cx, prev_cy = track_history[track_id]
                    
                    if prev_cx < FENCE_X and cx >= FENCE_X:
                        if not is_in_cooldown:
                            print(f"[🚨 INTRUSION CONFIRMED] ID {track_id} crossed the line!")
                            
                            # 1. Generate a unique filename with a timestamp
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{CAMERA_ID}_{timestamp}_intrusion_id{track_id}.jpg"
                            
                            # 2. Define the exact path to save the image
                            # os.path.join handles Windows slashes safely: data\snapshots\filename.jpg
                            filepath = os.path.join("data", "snapshots", filename)
                            
                            # 3. Add a red alert banner to the frame right before saving
                            cv2.putText(frame, "EVIDENCE: INTRUSION DETECTED", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            
                            # 4. Save the image to the hard drive
                            cv2.imwrite(filepath, frame)
                            print(f"[📸 EVIDENCE SAVED] Saved to: {filepath}")
                            
                            # Start cooldown
                            cooldowns[track_id] = current_time
                            
                track_history[track_id] = (cx, cy)

        cv2.imshow("TRINETRA X - Snapshot Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting snapshot test.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_evidence_snapshot()