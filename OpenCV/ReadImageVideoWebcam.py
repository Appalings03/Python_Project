import cv2

frameWidth = 640
frameHeight = 360

cap = cv2.VideoCapture(0)


while True:
    sucess, img = cap.read()
    img = cv2.resize(img, (frameWidth, frameHeight))
    cv2.imshow("Video", img)

    if cv2.waitKey(1) and 0xFF == ord('q'):
        break