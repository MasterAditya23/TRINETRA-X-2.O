import cv2
from ultralytics import YOLO

def test_virtual_fence():
    print("[INFO] Loading YOLOv8 model for virtual fence...")
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    # Dictionary to store the previous center point of each tracked object
    # Format: {track_id: (prev_cx, prev_cy)}
    track_history = {}

    print("[INFO] Virtual Fence active. Move left and right across the line. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Define our virtual fence (A vertical line in the middle of the frame)
        # We assume a standard webcam width of 640 pixels, so middle is 320.
        FENCE_X = 320 
        
        # Draw the fence on the frame (Blue line, thickness 2)
        cv2.line(frame, (FENCE_X, 0), (FENCE_X, frame.shape[0]), (255, 0, 0), 2)
        
        # Label the restricted zone (Right side)
        cv2.putText(frame, "RESTRICTED ZONE ->", (FENCE_X + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        results = model.track(frame, persist=True, classes=[0, 2, 3, 5, 7], verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = map(int, box)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # Draw bounding box and center dot
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # -- FENCE CROSSING LOGIC --
                # If we have seen this object before, check its previous position
                if track_id in track_history:
                    prev_cx, prev_cy = track_history[track_id]
                    
                    # Check if it moved from Left (less than FENCE_X) to Right (greater than FENCE_X)
                    if prev_cx < FENCE_X and cx >= FENCE_X:
                        print(f"[ALERT] ID {track_id} crossed into Restricted Zone!")
                        
                # Update the history with the current position for the next frame
                track_history[track_id] = (cx, cy)

        cv2.imshow("TRINETRA X - Virtual Fence Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting fence test.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_virtual_fence()