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
    """
    get foreground substracting current frame from background model
    where the difference is above threshold_filter
    """

    current_frame_filtered = (np.where(current_frame == DEPTH_HOLE_VALUE, bg_frame, current_frame)).astype(np.float32)
    diff = (current_frame_filtered.T - bg_frame.T)
    diff_filter = (np.where(np.abs(diff) >= threshold_filter, 1, 0))
    return diff_filter


def get_foreground_from_mask_depth(foreground, mask):
    return foreground * mask


# get rgb background
def get_background_mask_zivkovic(f_bg, current_frame, alpha):

    foreground = np.zeros(shape=current_frame.shape, dtype=np.float32)
    # get foreground in numpy array
    foreground = f_bg.apply(current_frame, foreground, alpha)
    # convert to 0 1 notation since by default apply => 0 bg, 255fg shadow other value
    foreground = np.where((foreground == 0), 0, 1)
    return foreground


def get_background_from_mask_rgb(image, mask):
    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    #mask2 = np.where((mask == 255), 0, 1)
    return image * utils.to_rgb1a(mask)


def get_foreground_from_mask_rgb(image, mask):
    return image * utils.to_rgb1a(mask)


def apply_opening(image, kernel_size, kernel_type):
    # get uint image because cv2 needs it
    u_image = image.astype(np.uint8)
    #foreground_mask_depth = foreground_mask_depth.astype(np.uint8)
    kernel = cv2.getStructuringElement(kernel_type, (kernel_size, kernel_size))
    u_image = cv2.morphologyEx(u_image, cv2.MORPH_OPEN, kernel)
    return u_image


def update_rgb_detection_aggregator(aggregator, foreground_long, foreground_short):

    proposal_candidate = foreground_long * np.int8(np.logical_not(foreground_short))
    other_cases = np.int8(np.logical_not(proposal_candidate))

    # increment aggregator
    result = aggregator + proposal_candidate

    # # AVOID REMOVING FROM PROPOSA OF ALREADY DETECTED OBJECT
    # # mask of max values (proposal)
    # mask_proposal = np.where((result >= AGG_RGB_MAX_E), 1, 0)
    # mask_new_pixel_in_bg = np.int32(np.logical_not(foreground_long)) * np.int32(np.logical_not(foreground_short))
    # # pixel of older proposal that are becoming background (FL =0 and FS = 0)
    # mask = mask_proposal * mask_new_pixel_in_bg
    # # avoid previous pixel from being penalized
    # other_cases = np.where((other_cases == mask), 0, other_cases)

    # add penalty to pixel not in proposal
    result = result - other_cases * AGG_RGB_PENALTY

    # set aggregate bounds
    result = np.clip(result, 0, AGG_RGB_MAX_E)
    return result


def update_depth_detection_aggregator(aggregator, foreground_current):
    not_in_current_foreground = np.int64(np.logical_not(foreground_current))
    # increment aggregator
    result = aggregator + foreground_current - not_in_current_foreground * AGG_DEPTH_PENALTY
    # set aggregate bounds
    result = np.clip(result, 0, AGG_DEPTH_MAX_E)
    return result


def apply_morph_reconstruction(seed, image):
    pass


def get_bounding_boxes(image):
    squares = []
    cnt_selected = []
    kdtree_elements = np.array([])  #np.zeros(shape=(1,3))
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:

        # filter contours with area less than 50 pixel
        if cv2.contourArea(cnt) > 50:
            #M = cv2.moments(cnt)
            #cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            #cv2.circle(foreground_depth, (cx, cy), 20, 255, 1)
            # rect[0],rect[1] => bottom left vertex; rect[2], rect[3] => width, height
            rect = cv2.boundingRect(cnt)
            if rect not in squares:

                area = rect[2] * rect[3]
                squares.append(rect)
                cnt_selected.append(cnt)

                # coordinates rect center
                cx = rect[0] + rect[2] / 2
                cy = rect[1] + rect[3] / 2
                if kdtree_elements.size is 0:
                    kdtree_elements = np.array([[cx, cy, area]])
                else:
                    kdtree_elements = np.concatenate((kdtree_elements, [[cx, cy, area]]))

    return squares, kdtree_elements, cnt_selected


# def get_depth_proposal( foreground_mask_depth_current )
#     return depth_mask_foreground, bbox


    # but if the saved object is removed we need to decrement the accumulator
    # case of FL = 0 and FS = 1
    #mask_remove_proposal = np.int64(np.logical_not(foreground_long))*foreground_short
    #mask2 = mask_proposal*mask_remove_proposal
    #other_cases = np.where((other_cases == mask2), 0, other_cases)


## delete
def get_background_from_mask(image, mask):
    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    mask2 = np.where((mask == 255), 0, 1)
    return (image * mask2)


def get_foreground_from_mask(image, mask):
    mask2 = np.where((mask == 0), 0, 1)
    return (image * mask2)


def pretty_print(array):
    for i in range(100, 110):
        print array[50, i],
    print "\n"