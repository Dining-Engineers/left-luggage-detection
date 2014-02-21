#!/usr/bin/env python
import freenect
import sys
import numpy as np

import cv
import cv2

from misc.demo import frame_convert


threshold = 100
current_depth = 0
depth_image = 0;

# windows and their initial states
depth_window = 0;
threshold_window = 0;
detector_window = 0;

def cv2array(im):
  depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

  arrdtype=im.depth
  a = np.fromstring(
         im.tostring(),
         dtype=depth2dtype[im.depth],
         count=im.width*im.height*im.nChannels)
  a.shape = (im.height,im.width,im.nChannels)
  return a

def array2cv(a):
  dtype2depth = {
        'uint8': cv.IPL_DEPTH_8U,
        'int8': cv.IPL_DEPTH_8S,
        'uint16': cv.IPL_DEPTH_16U,
        'int16': cv.IPL_DEPTH_16S,
        'int32': cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }
  try:
    nChannels = a.shape[2]
  except:
    nChannels = 1
  cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
dtype2depth[str(a.dtype)], nChannels)
  cv.SetData(cv_im, a.tostring(),a.dtype.itemsize*nChannels*a.shape[1])
  return cv_im










# OPENCV GUI callbacks
def toggle_depth_window(value):
    global depth_window
    
    #window is opened and has to be closed
    if depth_window == 1 and value == 0:
        cv.DestroyWindow('Depth')
        depth_window = 0
    elif depth_window == 0 and value == 1:
        cv.NamedWindow('Depth')
        depth_window = 1
    
# OPENCV GUI callbacks
def toggle_detector_window(value):
    global detector_window
    
    #window is opened and has to be closed
    if detector_window == 1 and value == 0:
        cv.DestroyWindow('Detector')
        detector_window = 0
    elif detector_window == 0 and value == 1:
        cv.NamedWindow('Detector')
        detector_window = 1
    


def toggle_threshold_window(value):
    global threshold_window
    
    #window is opened and has to be closed
    if threshold_window == 1 and value == 0:
        cv.DestroyWindow('Threshold')
        threshold_window = 0
    elif threshold_window == 0 and value == 1:
        cv.NamedWindow('Threshold')
        cv.CreateTrackbar('threshold', 'Threshold', threshold, 500, change_threshold)
        cv.CreateTrackbar('depth', 'Threshold', current_depth, 2048, change_depth)
        threshold_window = 1

def change_threshold(value):
    global threshold
    threshold = value
# print 'threshold changed to: {0}'.format(threshold)

def change_depth(value):
    global current_depth
    current_depth = value
# print 'depth changed to: {0}'.format(current_depth)








# window content rendering section
def show_depth():
    global depth_image
    
    depth, timestamp = freenect.sync_get_depth()
    depth_image = frame_convert.pretty_depth_cv(depth);
    cv.ShowImage('Depth', resize_image(depth_image))


def resize_image(image, height = 240, width = 320):
    imageBuffer = image;
    smallerImage = cv.CreateImage((width, height), imageBuffer.depth, imageBuffer.nChannels);
    cv.Resize(imageBuffer, smallerImage, interpolation=cv.CV_INTER_CUBIC);
    return smallerImage;


def show_video():
    image = frame_convert.video_cv(freenect.sync_get_video()[0]);
    cv.ShowImage('Video', resize_image(image))

def show_detector():
    image = frame_convert.video_cv(freenect.sync_get_video()[0]);

    # cascade classifiers
    face_cascade = cv2.CascadeClassifier('opencv_data/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('opencv_data/haarcascades/haarcascade_eye.xml')

    # convert image to grayscale to use it with classifers
    gray = cv2.cvtColor(cv2array(image), cv2.COLOR_BGR2GRAY);

    # save previous image and use copy
    img = image;

    # detect and highlight faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5);
    for (x,y,w,h) in faces:
        cv.Rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)

    # detect and highlight eyes
    eyes = eye_cascade.detectMultiScale(gray)
    for (ex,ey,ew,eh) in eyes:
        cv.Rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    # show detector window
    cv.ShowImage('Detector', img)


def show_threshold():
    global threshold
    global current_depth

    depth, timestamp = freenect.sync_get_depth()
    depth = 255 * np.logical_and(depth >= current_depth - threshold,
                                 depth <= current_depth + threshold)
    depth = depth.astype(np.uint8)
    threshold_image = cv.CreateImageHeader((depth.shape[1], depth.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 1)
    cv.SetData(threshold_image, depth.tostring(),
              depth.dtype.itemsize * depth.shape[1])
    cv.ShowImage('Threshold', resize_image(threshold_image))

# parse command line arguments
arguments = sys.argv

if '-h' in arguments or '--help' in arguments:
    #print help/welcome message to command line
    print """
MyKinect v0.0.1
---------------
Usage:
sudo python my_kinect.py [-h --help -d -t]

-h, --help - display this message
-d - display depth window at start
-t - display threshold window at start

Controls:

- ESC in window to close
- "s" key to save RGB image to RGB.jpg in current directory
- "d" key to save DEPTH image to DEPTH.jpg in current directory."""
    exit();

if '-d' in arguments:
    toggle_depth_window(1)
if '-t' in arguments:
    toggle_threshold_window(1)

# open initial window with controls to open additional windows - opencv doesnt have buttons, so we use trackbars
cv.NamedWindow('Video')
cv.CreateTrackbar('Depth Window', 'Video', depth_window, 1, toggle_depth_window)
cv.CreateTrackbar('Threshold Window', 'Video', threshold_window, 1, toggle_threshold_window)
cv.CreateTrackbar('Detector Window', 'Video', detector_window, 1, toggle_detector_window)


 

# main program loop
while 1:

    if depth_window:
        show_depth()
    
    if threshold_window:
        show_threshold();

    if detector_window:
        show_detector();
    
    show_video()
    
    key = cv.WaitKey(5) & 0xFF
    if key == 27:
        break;
    elif key == 115:
        print '"s" key pressed, saving RGB image to file RGB.jpg'
        cv2.imwrite('RGB.jpg', freenect.sync_get_video()[0]);
    elif key == 100 and depth_window:
        print '"d" key pressed, saving depth image to file DEPTH.jpg'
        cv.SaveImage('DEPTH.jpg', depth_image)