import cv2
from ultralytics import YOLO

def test_yolo():
    print("[INFO] Loading YOLOv8 nano model...")
    # This will download 'yolov8n.pt' to your folder the first time it runs
    model = YOLO("yolov8n.pt") 
    
    # Open the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] AI Detection started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Run YOLO on the frame. 
        # classes=[0, 2, 3, 5, 7] filters detection to: person, car, motorcycle, bus, truck
        results = model(frame, classes=[0, 2, 3, 5, 7], verbose=False)
        
        # YOLOv8 provides a built-in method to draw the bounding boxes
        for result in results:
            annotated_frame = result.plot()

        # Display the AI-annotated frame
        cv2.imshow("TRINETRA X - AI Detection Test", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting detection test.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_yolo()