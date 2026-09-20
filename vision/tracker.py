import cv2
from ultralytics import YOLO

def test_tracking():
    print("[INFO] Loading YOLOv8 model for tracking...")
    model = YOLO("yolov8n.pt")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Tracking started. Move around to test IDs. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # model.track() assigns unique IDs across frames (persist=True)
        results = model.track(frame, persist=True, classes=[0, 2, 3, 5, 7], verbose=False)
        
        # Check if any objects were detected AND assigned an ID
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()      # Bounding box coordinates
            track_ids = results[0].boxes.id.int().cpu().numpy() # Unique Tracking IDs
            
            # Loop through each detected object
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = map(int, box)
                
                # Calculate the exact center point (cx, cy)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # Draw the bounding box (Green)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw the center point (Red Dot)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                # Draw the Tracking ID above the box
                label = f"ID: {track_id}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("TRINETRA X - Tracking Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting tracking test.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_tracking()