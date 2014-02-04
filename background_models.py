import cv2
from SimpleCV import *
import utils

def get_background_running_average():
    pass


# get rgb background
def get_background_zivkovic(f_bg, current_frame):
    #print current_frame
    #f_bg = cv2.BackgroundSubtractorMOG2()
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame)
    # rotate image
    foreground = foreground.transpose(1, 0)

    return foreground


    #print foreground

    #print foreground.shape
    # convert to rgb
    #to_rgb1a(fgmask)

