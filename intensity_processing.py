import numpy as np
import bg_models
from SimpleCV import *
from const import *
from utils import *
import cv2


class IntensityProcessing:

    def __init__(self):
        self.current_frame = np.zeros(shape=(640, 480, 3))
        self.foreground_mask_long_term = np.zeros(shape=(640, 480), dtype=np.int8)
        self.foreground_mask_short_term = np.zeros(shape=(640, 480), dtype=np.int8)
        self.background_aggregator = np.zeros(shape=(640, 480), dtype=np.int8)
        self.proposal = np.zeros(shape=(640, 480, 3), dtype=np.uint8)

        # define Zivkovic background subtraction function
        self.f_bg = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)

        # define zivkovic background subtraction function
        self.f_bg2 = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)

    def extract_background_mask_porikli(self):

        self.foreground_mask_long_term = bg_models.get_background_mask_zivkovic(self.f_bg, self.current_frame,
                                                                                BG_ZIV_LONG_LRATE)

        self.foreground_mask_short_term = bg_models.get_background_mask_zivkovic(self.f_bg2, self.current_frame,
                                                                                 BG_ZIV_SHORT_LRATE)

    def update_detection_aggregator(self):
        self.background_aggregator = bg_models.update_rgb_detection_aggregator(self.background_aggregator,
                                                                               self.foreground_mask_long_term,
                                                                               self.foreground_mask_short_term)

    def extract_proposal_bbox(self):
        # get rgb proposal
        proposal_mask = np.where(self.background_aggregator == AGG_RGB_MAX_E, 1, 0)
        # get rgb blobs
        bbox, bbox_element, _ = bg_models.get_bounding_boxes(proposal_mask.astype(np.uint8))

        self.proposal = bg_models.get_foreground_from_mask_rgb(self.current_frame, proposal_mask)
        return bbox