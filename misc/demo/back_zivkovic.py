import numpy as np
import cv2
from SimpleCV import *

cap = cv2.VideoCapture('vtest.avi')

fgbg = cv2.BackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()

    fgmask = Image(fgbg.apply(frame)).grayscale()


    cv2.imshow('frame',frame-fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
