import cv2
from SimpleCV import *
import numpy as np
import utils


def get_background_running_average(moving_average, frame):
    #frame = np.where(mask > 0, 0, frame)
    # get holdes in depth map
    moving_average = running_average(frame, moving_average, 0.001)
    #cv2.accumulateWeighted(frame, moving_average, 0.10)
    return moving_average


def running_average(frame, average, alpha):
    # detect holes in depth map
    # either in current frame and in average frame
    holes_frame = np.where(frame == 2**11-1, 1, 0)
    holes_average = np.where(average == 2**11-1, 1, 0)

    # diff to detect if a pixel (x,y) is a:
    #   hole in current frame and not in average = 1
    #   hole in average and not in current frame = -1
    # if holes in current and average leave hole (will be fixed by another frame in the future)
    holes_diff = holes_frame - holes_average
    frame = np.where(holes_diff == 1, average, frame)
    average = np.where(holes_diff == -1, frame, average)

    # get running average
    average = (1-alpha)*average + alpha*frame
    return average


def get_foreground_mask_from_running_average(current_frame, bg_frame):

    print np.sum(np.where(bg_frame == 2**11-1, 1, 0))
    current_frame_filtered = (np.where(current_frame == 2**11-1, bg_frame, current_frame)).astype(np.float32)

    diff = (current_frame_filtered.T - bg_frame.T)
    diff_filter = (np.where(np.abs(diff) >= 3, 1, 0))

    return diff_filter

def get_foreground_from_mask_depth(foreground, mask):
    return foreground*mask


# get rgb background
def get_background_mask_zivkovic(f_bg, current_frame):

    #print current_frame
    #f_bg = cv2.BackgroundSubtractorMOG2()
    foreground = np.zeros(shape=(current_frame.shape), dtype=np.float32)
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame, foreground, 0.001)
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



## delete
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