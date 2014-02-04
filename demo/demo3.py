import freenect
import cv
import numpy as np
cv.NamedWindow('RGB')

def video_kin(dev,video, timestamp):
    global run
    print timestamp
    cv.ShowImage('RGB',cv.fromarray(video))
    cv.WaitKey(10)
    freenect.runloop(video=video_kin)