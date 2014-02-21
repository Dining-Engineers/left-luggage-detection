import numpy as np
import bg_models
from SimpleCV import *
from const import *
from utils import *
import cv2


class IntensityProcessing:

    def __init__(self, image_shape=(640, 480)):
        # shape have 3 channels
        shape_rgb = image_shape+(3,)

        self.current_frame = np.zeros(shape=shape_rgb, dtype=np.uint8)
        self.proposal = np.zeros(shape=shape_rgb, dtype=np.uint8)

        self.foreground_mask_long_term = np.zeros(shape=image_shape, dtype=np.int8)
        self.foreground_mask_short_term = np.zeros(shape=image_shape, dtype=np.int8)
        self.background_aggregator = np.zeros(shape=image_shape, dtype=np.int8)
        self.proposal_mask = np.zeros(shape=image_shape, dtype=np.uint8)  # mask from aggregator


        # define Zivkovic background subtraction function LONG
        self.f_bg = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)

        # define zivkovic background subtraction function SHORT
        self.f_bg2 = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_SHORT_THRESH, False)

    def extract_background_mask_porikli(self):
        #TODO RETURN VALUE
        """
        Lol

        """
        self.foreground_mask_long_term = bg_models.get_background_mask_zivkovic(self.f_bg, self.current_frame,
                                                                                BG_ZIV_LONG_LRATE)

        self.foreground_mask_short_term = bg_models.get_background_mask_zivkovic(self.f_bg2, self.current_frame,
                                                                                 BG_ZIV_SHORT_LRATE)

    def update_detection_aggregator(self):
        #TODO RETURN VALUE
        self.background_aggregator = bg_models.update_rgb_detection_aggregator(self.background_aggregator,
                                                                               self.foreground_mask_long_term,
                                                                               self.foreground_mask_short_term)

    def extract_proposal_bbox(self):
        # get rgb proposal
        self.proposal_mask = np.where(self.background_aggregator == AGG_RGB_MAX_E, 1, 0)
        # get rgb blobs
        bbox = bg_models.get_bounding_boxes(self.proposal_mask.astype(np.uint8))

        self.proposal = bg_models.get_foreground_from_mask_rgb(self.current_frame, self.proposal_mask)

        return bbox