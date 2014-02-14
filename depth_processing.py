import numpy as np
import bg_models
from const import *
from utils import *


class DepthProcessing:

    ACCUMULATOR = 0
    RECT_MATCHING = 1


    def __init__(self):
        self.current_frame = np.zeros(shape=(640, 480), dtype=np.uint16)
        self.accumulator = np.zeros(shape=(640, 480), dtype=np.uint8)
        self.background_aggregator = np.zeros(shape=(640, 480), dtype=np.int8)
        self.background_model = np.zeros(shape=(480, 640), dtype=np.float32)
        self.foreground_mask = np.zeros( shape=(640, 480), dtype=np.uint8)
        self.rect_accum = []

    def update_background_running_average(self):
        """
        get depth background by running average
        """
        self.background_model = bg_models.get_background_running_average(self.current_frame,
                                                                         self.background_model, BG_RUN_AVG_LRATE)

    def extract_foreground_mask_from_run_avg(self):
        """
        get depth foreground mask from running average computed
        with get_background_running_average
        the mask:
         - 0 = background
         - 1 = foreground
        """
        self.foreground_mask = bg_models.get_foreground_mask_from_running_average(self.current_frame,
                                                                                   self.background_model,
                                                                                   BG_MASK_THRESHOLD)

        return self.foreground_mask

    def extract_proposal_bbox(self, method=ACCUMULATOR):

        bbox_to_draw = []

        if method == self.ACCUMULATOR:
            self.accumulator = bg_models.update_depth_detection_aggregator( self.accumulator, self.foreground_mask)
            bbox, _, bbox_pixels = bg_models.get_bounding_boxes( np.uint8(self.accumulator))
            bbox_to_draw = bbox

        elif method == self.RECT_MATCHING:
            # temp list of proposal
            results = []

            bbox, _, bbox_pixels = bg_models.get_bounding_boxes(self.foreground_mask)


            print len(bbox), len(self.rect_accum)

            bool_accum = [False]*len(self.rect_accum)
            bool_curr = [False]*len(bbox)

            if len(self.rect_accum) != 0:
                for i in range(len(self.rect_accum)):
                    accum_entry = self.rect_accum[i]
                    for j in range(len(bbox)):
                        curr_entry = bbox[j]
                        if rect_similarity(accum_entry[0], curr_entry):
                            val = (curr_entry, accum_entry[1] + 1)
                            results.append(val)
                            bool_accum[i] = bool_curr[j] = True

                for i, rect_match in enumerate(bool_curr):
                    if not rect_match:
                        val = (bbox[i], 1)
                        results.append(val)

                for i, rect_match in enumerate(bool_accum):
                    if not rect_match:
                        counter = self.rect_accum[i][1]
                        if counter > 0:
                            val = (self.rect_accum[i][0], self.rect_accum[i][1]-1)
                            results.append(val)

            else:
                if len(bbox) is not 0:
                    for rect in bbox:
                        #c_x, c_y, area = get_center_area_from_rect(rect)
                        #query = (c_x, c_y, area, 1)
                        results.append((rect, 1))

            self.rect_accum = results
            for box in self.rect_accum:
                if box[1] >= 5:
                    bbox_to_draw.append(box[0])

        else:
            raise NotImplementedError("Not implemented")

        return bbox_to_draw

## per fare get and set
    # @property
    # def background_depth(self):
    #     return self._background_depth
    #
    # @background_depth.setter
    # def background_depth(self, value):
    #     self._background_depth = value