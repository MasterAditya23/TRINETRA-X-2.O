import cv2

def test_camera():
    print("[INFO] Starting Trinetra X camera test...")
    
    # Open the default webcam (0). 
    # If you don't have a webcam, we will switch this to a video file later.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Camera connected. Press 'q' to quit.")

    while True:
        # Read a single frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Display the frame in a window named 'TRINETRA X - Video Input'
        cv2.imshow("TRINETRA X - Video Input", frame)

        # Wait for 1 millisecond, and check if the user pressed the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quitting camera test.")
            break

    # Clean up and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()