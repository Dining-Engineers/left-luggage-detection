#!/usr/bin/python

from SimpleCV import Kinect, Image, pg, np, time
from SimpleCV.Display import Display


d = Display()
#create video streams

cam = Kinect()
#initialize the camera

# porto a bianco tutte le sfumature in depth da 200 a 2048
depth = cam.getDepth()#.stretch(0,1800)
while True:
    new_depth = cam.getDepth()#.stretch(0,1800)
    img = cam.getImage()
    diff_1 = new_depth - depth
    diff_2 = depth - new_depth
    diff = diff_1 + diff_2
    img_filter = diff.binarize(0)

    motion_img = img - img_filter
    motion_img_open = motion_img.morphOpen()
    motion_img_open.show()
    depth = new_depth
