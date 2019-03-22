import cv2
import tensorflow
cam = cv2.VideoCapture(0)
cv2.namedWindow('win')
while cv2.waitKey(1) != 97:
    r, f = cam.read()
    cv2.imshow('win', f)

