import cv2

print("1. START")

cap = cv2.VideoCapture(0)

print("2. CAMERA:", cap.isOpened())

while True:
    print("3. LOOP")

    ret, frame = cap.read()

    print("4. FRAME:", ret)

    if not ret:
        print("ERROR: camera frame")
        break

    cv2.imshow("Camera Test", frame)

    key = cv2.waitKey(30) & 0xFF

    print("5. KEY:", key)

    if key == 27:
        print("ESC PRESSED")
        break

cap.release()
cv2.destroyAllWindows()

print("6. END")
