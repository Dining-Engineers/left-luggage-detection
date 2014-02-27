__author__ = "Andrea Rizzo, Matteo Bruni"
__copyright__ = "Copyright 2014, Dining Engineers"
__license__ = "GPLv2"

""" Program constant """

DEPTH_HOLE_VALUE = 2**11-1      #: Depth holes in openfreenect have maximum value in 11 bit

BG_OPEN_KSIZE = 5               #: Structuring element size used to apply opening

# Background (Depth) Paramethers
BG_RUN_AVG_LRATE = 0.001        #: Learning rate for running average in depth processing
#: Minimum threshold to consider a pixel foreground in running average
#: e.g. :math:`|pixel - average(pixel)| \ge BG\_MASK\_THRESHOLD`
BG_MASK_THRESHOLD = 3


# Dual Background Porikli method using Zivkovich model background for (RGB) Paramethers
BG_ZIV_LONG_LRATE = 0.001       #: Background learning rate in Zivkovich method for long background model
BG_ZIV_SHORT_LRATE = 0.01       #: Background learning rate in Zivkovich method for short background model
BG_ZIV_HIST = 1                 #: History for Zivkovick background method
BG_ZIV_LONG_THRESH = 900        #: Threshold for Zivkovich method for long background model
BG_ZIV_SHORT_THRESH = 200       #: Threshold for Zivkovich method for short background model

#: Aggregator parameters
AGG_RGB_MAX_E = 15              #: number of frames after which a pixel is considered an left item in rgb domain
AGG_RGB_PENALTY = 1            #: penalty in the accumulator for a pixel not in current foreground in rgb domain
AGG_DEPTH_MAX_E = 30            #: number of frames after which a pixel is considered an left item in depth domain
AGG_DEPTH_PENALTY = 30           #: penalty in the accumulator for a pixel not in current foreground in depth domain
AGG_DEPTH_BBOX = 5              #: accumulator threshold for RECT_MATCHING/RECT_MATCHING2 in depth detection

# Bounding Boxes
BBOX_MIN_AREA = 50              #: minimum area in pixel to create a bounding box

# Display Options
DISPLAY_TYPE = "PYGAME"         #: Default display type: can be PYGAME or SIMPLECV

# shape of the image obtained from kinect
IMAGE_SHAPE = (640, 480)        #: Default image size retrieved from kinect

# Pygame Options
PYGAME_LAYOUT = 4               #: number of images to show in the output can be 2 or 4