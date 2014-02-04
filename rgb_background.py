import numpy as np
import cv2
from operator import add
from SimpleCV import *
from SimpleCV.Display import Display


def to_rgb1a(im):
    # This should be fsater than 1, as we only
    # truncate to uint8 once (?)
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] =  ret[:, :, 1] =  ret[:, :, 0] =  im
    return ret


d = Display()
#create video streams

cam = Kinect()
#initialize the camera


#cap = cv2.VideoCapture('vtest.avi')

fgbg = cv2.BackgroundSubtractorMOG2(1, 5)

while(1):
    #ret, frame = cap.read()
    frame = cam.getImage()
    frame_np = frame.getNumpyCv2()

    fgmask = fgbg.apply(frame_np)

    #frame = frame.applyBinaryMask(Image(Image(fgmask).getGrayNumpyCv2()) )


    lol = frame.getNumpyCv2() - to_rgb1a(fgmask)

    # background zivovic
    #frame = Image(lol.transpose(1,0,2))

    #foreground
    frame = Image(to_rgb1a(fgmask).transpose(1,0,2))

    #frame - Image(to_rgb1a(fgmask))
    #Image(Image(fgmask).toRGB().getNumpyCv2().transpose(1,0,2))
    frame.save(d)
    #Image(fgmask).save(d)
    #cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break


#cv2.destroyAllWindows()


