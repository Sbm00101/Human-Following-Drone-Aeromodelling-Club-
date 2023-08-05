#!/usr/bin/env python3
import cv2
import numpy as np

cv2.namedWindow('win',cv2.WINDOW_NORMAL)
cv2.resizeWindow('win', 1920, 1080)
face_cascade= cv2.CascadeClassifier('facedetection.xml')
cap = cv2.VideoCapture(0)

while (cap.isOpened()):
    ret, frame=cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Only consider the first face detected
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 10)
        area = w*h
        print("area of face=" + str(area))

    cv2.imshow('win', frame)

    
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
