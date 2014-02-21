import numpy as np
import bg_models
from const import *
from utils import *


class DepthProcessing:
    ACCUMULATOR = 0
    RECT_MATCHING = 1
    RECT_MATCHING2 = 2

    def __init__(self, image_shape=(640, 480)):
        self.current_frame = np.zeros(shape=image_shape, dtype=np.uint16)
        self.accumulator = np.zeros(shape=image_shape, dtype=np.uint8)
        self.background_aggregator = np.zeros(shape=image_shape, dtype=np.int8)
        self.background_model = np.zeros(shape=image_shape, dtype=np.float32)
        self.foreground_mask = np.zeros(shape=image_shape, dtype=np.uint8)
        self.rect_accum = []
        self.rect_accum2 = np.array([], dtype=int)


    def update_background_running_average(self):
        """
            get depth background by running average

        """
        #TODO RETURN VALUE
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
        """
        Sblinda Estrai
        :param method: paremtro che sblinda
        :return: :raise NotImplementedError:
        """
        bbox_to_draw = []

        if method == self.ACCUMULATOR:
            self.accumulator = bg_models.update_depth_detection_aggregator(self.accumulator, self.foreground_mask)
            bbox = bg_models.get_bounding_boxes(np.uint8(self.accumulator))
            bbox_to_draw = bbox

        elif method == self.RECT_MATCHING:

            # temp list of proposal
            results = []

            # get current bbox
            bbox = bg_models.get_bounding_boxes(self.foreground_mask)

            # bool list for each bbox in rect_accumulator
            # if true => we had a match between current and accumulator
            bool_accum = [False]*len(self.rect_accum)
            bool_curr = [False]*len(bbox)

            if len(self.rect_accum) != 0:


                for i in range(len(self.rect_accum)):
                    accum_entry = self.rect_accum[i]
                    for j in range(len(bbox)):
                        curr_entry = bbox[j]
                        if rect_similarity(accum_entry[0], curr_entry):
                            if accum_entry[1] < AGG_DEPTH_MAX_E:
                                val = (curr_entry, accum_entry[1] + 1)
                            else:
                                val = (curr_entry, accum_entry[1])
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
                            val = (self.rect_accum[i][0], self.rect_accum[i][1]-AGG_DEPTH_PENALTY)
                            results.append(val)

            else:
                if len(bbox) is not 0:
                    for rect in bbox:
                        #c_x, c_y, area = get_center_area_from_rect(rect)
                        #query = (c_x, c_y, area, 1)
                        results.append((rect, 1))

            self.rect_accum = results
            for box in self.rect_accum:
                if box[1] >= 7:
                    bbox_to_draw.append(box[0])

        elif method == self.RECT_MATCHING2:

            rect_current = bg_models.get_bounding_boxes2(self.foreground_mask)

            if self.rect_accum2.size != 0:
                # accumulator is not empty check with current rect

                # define an int array (of rect_current lenght)
                # where we will save the index of the best match
                # for each rect in rect_current with rect_accumulator
                # -1 means no match
                current_best_match_idx = [-1]*rect_current.shape[0]

                # define a bool array of rect_accum lenght
                # where we will save whatever the i-th element of the accumulator
                # had a match with rect_current
                accumulator_match = [False]*self.rect_accum2.shape[0]

                for i, r_curr in enumerate(rect_current):
                    max_value = 0
                    max_idx = -1
                    #print "da cur. "
                    for j, r_acc in enumerate(self.rect_accum2):
                        # keep track of the best match for the current rect
                        distance = similarity_measure_rect(r_curr, r_acc)
                        #print distance,
                        if distance > 0.5:
                        #if rect_similarity(r_curr, r_acc):
                            #print r_curr, r_acc
                            # save in accumulator_match that we have a match
                            accumulator_match[j] = True
                            if max_value < distance:
                                max_idx = j
                                #max_value = distance
                    current_best_match_idx[i] = max_idx

                # increment counter of the matched rect and add the new ones found in current
                for i, idx in enumerate(current_best_match_idx):
                    if idx == -1:
                        # this rect has no match in accumulator
                        # add it to accumul
                        # print "rect current: ", self.rect_accum2, rect_current[i]
                        self.rect_accum2 = np.concatenate((self.rect_accum2, [rect_current[i]]))
                    else:
                        # we had a match in accumulator
                        # increment counter
                        if self.rect_accum2[idx][-1] < AGG_DEPTH_MAX_E:
                            self.rect_accum2[idx][-1] += 1
                        # update coords with the new values
                        self.rect_accum2[idx][0:4] = rect_current[i][0:4]


                # now update the accumulator:
                element_to_delete = []
                for j, match in enumerate(accumulator_match):
                    if not match:
                        # get the counter for the rect without match
                        counter = self.rect_accum2[j][-1]
                        if counter > 1:
                            # decrement counter
                            self.rect_accum2[j][-1] -= 1  # self.rect_accum2[j][-1] - 1
                        else:
                            element_to_delete.append(j)

                # delete rect that reached 0 counter
                self.rect_accum2 = np.delete(self.rect_accum2, element_to_delete, 0)

            else:
                # accumulator is empty, fill it with current rect
                #print "fill accum with curr", rect_current
                self.rect_accum2 = np.copy(rect_current)  # np.append(self.rect_accum2, rect_current)

            #print self.rect_accum2.shape
            # extract bounding box
            for box in self.rect_accum2:
                #print box
                # if counter at leas THRESHOLD print it
                if box[-1] > AGG_DEPTH_BBOX:
                    bbox_to_draw.append(box[0:4])



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