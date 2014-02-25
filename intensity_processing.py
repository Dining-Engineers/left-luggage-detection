import numpy as np
import bg_models
from const import *
from utils import *
import cv2


class IntensityProcessing:

    def __init__(self, image_shape=(640, 480)):
        # shape have 3 channels
        shape_rgb = image_shape+(3,)

        self.current_frame = np.zeros(shape=shape_rgb, dtype=np.uint8)
        self.proposal = np.zeros(shape=shape_rgb, dtype=np.uint8)

        self.foreground_mask_long_term = np.zeros(shape=image_shape)
        self.foreground_mask_short_term = np.zeros(shape=image_shape)
        self.background_aggregator = np.zeros(shape=image_shape, dtype=np.int8)
        self.proposal_mask = np.zeros(shape=image_shape, dtype=np.uint8)  # mask from aggregator

        # define Zivkovic background subtraction function LONG
        self.f_bg_long = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_LONG_THRESH, False)
        # define zivkovic background subtraction function SHORT
        self.f_bg_short = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_SHORT_THRESH, False)

    def compute_foreground_masks(self, frame):
        """
        Compute foreground masks for term background and short term background following Porikli's method

        :param np.uint8 frame: frame (3 channels) from which extract foregrounds masks
        :returns: foreground masks for long term and short term backgrounds
        :rtype: np.int8
        """

        # get rgb dual background (long and short sensitivity)
        # N.B. background is black (0) and foreground white (1)
        self.foreground_mask_long_term = bg_models.compute_foreground_mask_from_func(self.f_bg_long, frame,
                                                                                BG_ZIV_LONG_LRATE)

        self.foreground_mask_short_term = bg_models.compute_foreground_mask_from_func(self.f_bg_short, frame,
                                                                                 BG_ZIV_SHORT_LRATE)
        return self.foreground_mask_long_term, self.foreground_mask_short_term

    def update_detection_aggregator(self):
        #TODO RETURN VALUE
        self.background_aggregator = update_rgb_detection_aggregator(self.background_aggregator,
                                                                     self.foreground_mask_long_term,
                                                                     self.foreground_mask_short_term)

    def extract_proposal_bbox(self):
        # get rgb proposal
        self.proposal_mask = np.where(self.background_aggregator == AGG_RGB_MAX_E, 1, 0)
        # get rgb blobs
        bbox = bg_models.get_bounding_boxes(self.proposal_mask.astype(np.uint8))

        self.proposal = bg_models.cut_foreground(self.current_frame, self.proposal_mask)

        return bbox



def update_rgb_detection_aggregator(aggregator, foreground_long, foreground_short):

    proposal_candidate = foreground_long * np.int8(np.logical_not(foreground_short))
    other_cases = np.int8(np.logical_not(proposal_candidate))

    # increment aggregator
    result = aggregator + proposal_candidate

    # AVOID REMOVING FROM PROPOSA OF ALREADY DETECTED OBJECT
    # mask of max values (proposal)
    mask_proposal = np.where((result >= AGG_RGB_MAX_E), 1, 0)
    mask_new_pixel_in_bg = np.int32(np.logical_not(foreground_long)) * np.int32(np.logical_not(foreground_short))
    # # pixel of older proposal that are becoming background (FL =0 and FS = 0)
    mask = mask_proposal * mask_new_pixel_in_bg
    # # # avoid previous pixel from being penalized
    other_cases = np.where((other_cases == mask), 0, other_cases)
    # # caso 0 -1
    # mask_penalty = np.int32(np.logical_not(foreground_long)) * np.int32(foreground_short)

    # add penalty to pixel not in proposal
    result = result - other_cases * AGG_RGB_PENALTY #- mask_penalty * (AGG_RGB_MAX_E-1)

    # set aggregate bounds
    result = np.clip(result, 0, AGG_RGB_MAX_E)
    return result
