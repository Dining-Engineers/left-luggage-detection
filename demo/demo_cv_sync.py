#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy

cv.NamedWindow('Depth')
cv.NamedWindow('Video')
print('Press ESC in window to stop')


def get_depth():
    return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])


def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])


while 1:
    video = freenect.sync_get_video()[0]
    video = video[:, :, ::-1]  # RGB -> BGR
    image = cv.CreateImageHeader((video.shape[1], video.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 3)
    cv.SetData(image, video.tostring(),
               video.dtype.itemsize * 3 * video.shape[1])


    cv.ShowImage("asd", image)
    #cv.WaitKey(3)
    #video = freenect.sync_get_depth()[0]
    #print video
    #print image.width
    #cv.ShowImage('Depth', get_depth())
    #cv.ShowImage('Video', get_video())
    if cv.WaitKey(1) == 27:
        break