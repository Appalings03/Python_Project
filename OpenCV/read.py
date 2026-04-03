import cv2 as cv

# Readig image
img = cv.imread('Resources/engi.png')

cv.imshow('Engi', img)

cv.waitKey(0)

# Reading video
# webcam : 0
cap = cv.VideoCapture(0)
# video : path
# cap = cv.videoCapture('PATH/TO/VIDEO')

while True:
    isTrue, fram = cap.read()
    cv.imshow()


cap = cv

cv.waitKey(0)