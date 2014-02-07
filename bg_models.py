import cv2
from SimpleCV import *
import numpy as np
import utils
from const import *



def get_background_running_average(frame, average, alpha):
    # detect holes in depth map
    # either in current frame and in average frame
    holes_frame = np.where(frame == DEPTH_HOLE_VALUE, 1, 0)
    holes_average = np.where(average == DEPTH_HOLE_VALUE, 1, 0)

    # diff to detect if a pixel (x,y) is a:
    #   hole in current frame and not in average = 1
    #   hole in average and not in current frame = -1
    # if holes in current and average leave hole (will be fixed by another frame in the future)
    holes_diff = holes_frame - holes_average
    frame = np.where(holes_diff == 1, average, frame)
    average = np.where(holes_diff == -1, frame, average)

    # get running average
    #average = (1-alpha)*average + alpha*frame
    cv2.accumulateWeighted(frame, average, alpha)
    return average


def get_foreground_mask_from_running_average(current_frame, bg_frame, threshold_filter):

    print np.sum(np.where(bg_frame == DEPTH_HOLE_VALUE, 1, 0))
    current_frame_filtered = (np.where(current_frame == DEPTH_HOLE_VALUE, bg_frame, current_frame)).astype(np.float32)
    diff = (current_frame_filtered.T - bg_frame.T)
    diff_filter = (np.where(np.abs(diff) >= threshold_filter, 1, 0))
    return diff_filter


def get_foreground_from_mask_depth(foreground, mask):
    return foreground*mask


# get rgb background
def get_background_mask_zivkovic(f_bg, current_frame, alpha):

    #print current_frame
    foreground = np.zeros(shape=current_frame.shape, dtype=np.float32)
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame, foreground, alpha)
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

#cv2.MORPH_ELLIPSE
def apply_opening(image, kernel_size, kernel_type):
    # get uint image because cv2 needs it
    u_image = image.astype(np.uint8)
    #foreground_mask_depth = foreground_mask_depth.astype(np.uint8)
    kernel = cv2.getStructuringElement(kernel_type, (kernel_size, kernel_size))
    u_image = cv2.morphologyEx(u_image, cv2.MORPH_OPEN, kernel)
    return u_image




















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