import cv2
from SimpleCV import *
import numpy as np
import utils


def get_background_running_average(moving_average, frame):
    cv2.accumulateWeighted(frame, moving_average, 0.320)
    return moving_average


def get_mask_from_running_average(current_frame, bg_frame):

    diff = np.zeros(shape=(current_frame.shape), dtype=np.float32)
    #np.abs((current_frame-bg_frame), diff)
    cv2.absdiff(current_frame.astype(np.float32), bg_frame, diff)
    #cv2.erode(diff, (150,150), diff)
    mask = np.zeros(shape=(current_frame.shape), dtype=np.float32)
    #mask = np.where((diff < 2), 0, 255).astype(np.float32)
    cv2.threshold(diff, 5, 1, cv2.THRESH_BINARY, mask)
    # smooth values
    #cv2.GaussianBlur(diff, (5,5), 0, diff)
    cv2.erode(mask, (3,3), mask)
    cv2.threshold(diff, 5, 1, cv2.THRESH_BINARY, mask)
    return mask


# get rgb background
def get_background_zivkovic(f_bg, current_frame):
    #print current_frame
    #f_bg = cv2.BackgroundSubtractorMOG2()
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame)
    # rotate image
    #foreground = foreground.transpose()
    return foreground


def get_background_from_mask_rgb(image, mask):
    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    mask2 = np.where((mask == 255), 0, 1)
    return image * utils.to_rgb1a(mask2)


def get_foreground_from_mask_rgb(image, mask):
    mask2 = np.where((mask == 0), 0, 1)
    return image * utils.to_rgb1a(mask2)


def get_background_from_mask(image, mask):
    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    mask2 = np.where((mask == 255), 0, 1)
    return (image * mask2)


def get_foreground_from_mask(image, mask):
    mask2 = np.where((mask == 0), 0, 1)
    return (image * mask2)

def pretty_print(array):
    for i in range(100,110):
        print array[50,i],
    print "\n"