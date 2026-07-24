import cv2

# Open webcam
camera = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not camera.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read a frame
    ret, frame = camera.read()

    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Display the frame
    cv2.imshow("Web Camera", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close windows
camera.release()
cv2.destroyAllWindows()