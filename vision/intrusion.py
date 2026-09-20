import cv2
import time
from ultralytics import YOLO

def test_intrusion_engine():
    print("[INFO] Loading YOLOv8 model for Intrusion Engine...")
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    track_history = {}
    
    # NEW: Dictionary to store the last time an ID triggered an alert
    # Format: {track_id: timestamp_of_last_alert}
    cooldowns = {}
    COOLDOWN_SECONDS = 5

    print("[INFO] Intrusion Engine active. Cooldown is 5 seconds per ID. Press 'q' to quit.")

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
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                # Default color for text (Green)
                text_color = (0, 255, 0)
                
                # Check if this ID is currently in a cooldown period
                current_time = time.time()
                is_in_cooldown = False
                if track_id in cooldowns:
                    time_since_last_alert = current_time - cooldowns[track_id]
                    if time_since_last_alert < COOLDOWN_SECONDS:
                        is_in_cooldown = True
                        text_color = (0, 165, 255)  # Orange color indicates cooldown

                # Draw the Tracking ID with the appropriate color
                cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                
                # -- INTRUSION LOGIC WITH COOLDOWN --
                if track_id in track_history:
                    prev_cx, prev_cy = track_history[track_id]
                    
                    # If it crossed the line AND is NOT in cooldown
                    if prev_cx < FENCE_X and cx >= FENCE_X:
                        if not is_in_cooldown:
                            print(f"[🚨 INTRUSION CONFIRMED] ID {track_id} crossed into Restricted Zone!")
                            # Update the cooldown timer for this ID
                            cooldowns[track_id] = current_time
                        else:
                            # Silently ignore the duplicate crossing
                            pass
                            
                track_history[track_id] = (cx, cy)

        cv2.imshow("TRINETRA X - Intrusion Engine Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting intrusion test.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_intrusion_engine()