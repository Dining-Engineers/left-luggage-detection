__author__ = "Andrea Rizzo, Matteo Bruni"
__copyright__ = "Copyright 2014, Dining Engineers"
__license__ = "GPLv2"

import cv2
import numpy as np
import utils
from const import *


def compute_background_running_average(frame, average, alpha, holes_frame):
    """

    Calculate background using running average technique new background is equal to:

        :math:`bg_{new} = (1-alpha)*bg_{old} + alpha*frame`

    :param np.uint16 frame: current frame for background update
    :param np.float32 average: background model to update
    :param float alpha: update learning rate
    :param frame_holes_mask:
    :type frame_holes_mask: np mask
    :return: updated background model
    :rtype: np.float32
    """

    # def preprocessing(frame, average):
    #     frame_result = np.zeros(shape=frame.shape, dtype=np.float32)
    #     average_result = np.zeros(shape=average.shape, dtype=np.float32)
    #
    #     for i in range(frame.shape[0]):
    #         for j in range(frame.shape[1]):
    #             if frame[i][j] == DEPTH_HOLE_VALUE:
    #                 if average[i][j] != DEPTH_HOLE_VALUE:
    #                     frame_result[i][j] = (average[i][j])
    #                 else:
    #                     frame_result[i][j] = (frame[i][j])
    #             else:
    #                 if average[i][j] == DEPTH_HOLE_VALUE:
    #                     average_result[i][j] = (frame[i][j])
    #                 else:
    #                     average_result[i][j] = (average[i][j])
    #     return frame_result, average_result
    # detect holes in depth map
    # either in current frame and in average frame
    holes_average = np.where(average == DEPTH_HOLE_VALUE, 1, 0)

    # diff to detect if a pixel (x,y) is a:
    #   hole in current frame and not in average = 1
    #   hole in average and not in current frame = -1
    # if holes in current and average leave hole (will be fixed by another frame in the future)
    # replace holes with value of the other one

    # BEST CONFIGURATION BUT SLOWER
    holes_diff = holes_frame - holes_average
    #frame = np.where(holes_diff == 1, average, frame)
    #average = np.where(holes_diff == -1, frame, average)
    # optimize!
    #frame = frame - holes_frame * frame + holes_frame * average
    #average = average - holes_average * average + holes_average * frame
    # MOAR OPTIMIZATIONS!
    frame = frame + holes_frame * (average - frame)
    average = average + holes_average * (frame - average)
    cv2.accumulateWeighted(frame, average, alpha)

    # SPEEDY BUT LESS EFFECTIVE FILTERING HOLES
    ## needed to convert to C_CONTINUOUS AREA
    # holes_diff = holes_frame + holes_average
    # average = average.copy()
    # cv2.accumulateWeighted(frame, average, alpha, holes_diff.astype(np.uint8))

    #cv2.accumulateWeighted(frame, average, alpha)

    return average, holes_average


def compute_holes_mask_in_frame(frame):
    return np.where(frame == DEPTH_HOLE_VALUE, 1, 0)


# get rgb background
def compute_foreground_mask_from_func(f_bg, current_frame, alpha):
    """
    Extract binary foreground mask (1 foreground, 0 background) from f_bg background modeling function and update
    background model.

    :param f_bg: background modeling function
    :param current_frame: current frame from which extract foreground
    :param alpha: update learning rate
    :return: foreground mask
    :rtype: np.uint8
    """
    foreground = np.zeros(shape=current_frame.shape, dtype=np.uint8)
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame, foreground, alpha)
    # NB WITH F_BG SET TO FALSE WE HAVE ONLY 2 POSSIBLE VALUES 0 (bg) or 255 (fg)
    # with shadows == True we get 127
    # convert to 0 1 notation since by default apply => 0 bg, 255fg shadow other value
    foreground = np.where((foreground == 0), 0, 1)
    return foreground



def cut_foreground(image, mask):
    """
    Cut the foreground from the image using the mask supplied

    :param image: image from which cut foreground
    :param mask: mask of the foreground
    :return: image with only the foreground
    :raise: *IndexError* error if the size of the image is wrong
    """
    if len(image.shape) == 2 or image.shape[2] == 1:
        # we have a greyscale image
        return image * mask
    elif len(image.shape) == 3 and image.shape[2] == 3:
        return image * utils.to_rgb(mask)
    else:
        raise IndexError("image has the wrong number of channels (must have 1 or 3 channels")


def apply_opening(image, kernel_size, kernel_type):
    """
    Apply opening to image with the specified kernel type and image

    :param image:   image to which apply opening
    :param kernel_size: size of the structuring element
    :param kernel_type: structuring element
    :return: image with opening applied
    :rtype: np.uint8
    """
    u_image = image.astype(np.uint8)
    #foreground_mask_depth = foreground_mask_depth.astype(np.uint8)
    kernel = cv2.getStructuringElement(kernel_type, (kernel_size, kernel_size))
    u_image = cv2.morphologyEx(u_image, cv2.MORPH_OPEN, kernel)
    return u_image

def apply_dilation(image, kernel_size, kernel_type):
    """
    Apply dilation to image with the specified kernel type and image

    :param image:   image to which apply opening
    :param kernel_size: size of the structuring element
    :param kernel_type: structuring element
    :return: image with opening applied
    :rtype: np.uint8
    """
    u_image = image.astype(np.uint8)
    #foreground_mask_depth = foreground_mask_depth.astype(np.uint8)
    kernel = cv2.getStructuringElement(kernel_type, (kernel_size, kernel_size))
    u_image = cv2.morphologyEx(u_image, cv2.MORPH_DILATE, kernel)
    return u_image


def get_bounding_boxes(image):
    """
    Return Bounding Boxes in the format x,y,w,h where (x,y) is the top left corner

    :param image: image from which retrieve the bounding boxes
    :return: bounding boxes list
    :rtype: list
    """
    bbox = []
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        # filter contours with area less than 50 pixel
        if cv2.contourArea(cnt) > BBOX_MIN_AREA:
            rect = cv2.boundingRect(cnt)
            if rect not in bbox:
                bbox.append(rect)

    return bbox


def get_bounding_boxes2(image):
    """
    Return Bounding Boxes in the format x,y,w,h where (x,y) is the top left corner

    :param image: image from which retrieve the bounding boxes
    :return: bounding boxes array, where each element has the form (x, y, w, h, counter) with counter = 1
    :rtype: np.array
    """
    squares = []
    bbox_elements = np.array([], dtype=int)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # filter contours with area less than 50 pixel
        if cv2.contourArea(cnt) > BBOX_MIN_AREA:
            rect = cv2.boundingRect(cnt)
            if rect not in squares:
                squares.append(rect)
                if bbox_elements.size is 0:
                    # save bbox with a counter set to one
                    bbox_elements = np.array([[rect[0], rect[1], rect[2], rect[3], 1]])
                else:
                    bbox_elements = np.concatenate((bbox_elements, [[rect[0], rect[1], rect[2], rect[3], 1]]))
    return bbox_elements