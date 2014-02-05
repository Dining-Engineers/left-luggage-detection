import cv2
from SimpleCV import *
import numpy as np
import utils


def get_background_running_average(moving_average, frame):
    # cv.RunningAvg(image, acc, alpha, mask=None) None
    #   Parameters:
    #    src - Input image as 1- or 3-channel, 8-bit or 32-bit floating point.
    #    dst - Accumulator image with the same number of channels as input image, 32-bit or 64-bit floating-point.
    #    alpha - Weight of the input image.
    #    mask - Optional operation mask.
    print frame.shape
    print cv2.cv.GetSize(moving_average)
    cv.RunningAvg(cv.fromarray(frame), moving_average, 0.1, None)
    #cv2.ConvertScaleAbs(moving_average, avg_show) # converting back to 8-bit to show
    pass


# get rgb background
def get_background_zivkovic(f_bg, current_frame):
    #print current_frame
    #f_bg = cv2.BackgroundSubtractorMOG2()
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame)
    # rotate image
    #foreground = foreground.transpose()
    return foreground

def get_background_from_mask(image, mask):
    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    mask2 = np.where((mask == 255), 0, 1)
    return (image * utils.to_rgb1a(mask2))


def get_foreground_from_mask(image, mask):
    mask2 = np.where((mask == 0), 0, 1)
    return (image * utils.to_rgb1a(mask2))





