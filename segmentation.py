import numpy as np
from const import *
import cv2


def create_watershed_seed(bbox_current_frame_proposals, proposal_mask, bbox_not_moved, watershed_last_frame_seed_mask):
    watershed_mask_seed = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)

    for k, s in enumerate(bbox_current_frame_proposals):
        watershed_mask_seed[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]*(k+5)

    # get seeds from older detection
    for s in bbox_not_moved:
        watershed_mask_seed[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = watershed_last_frame_seed_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]

    return watershed_mask_seed


def watershed_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask, bbox_not_moved, watershed_last_frame_seed_mask):
    # segmentation
    watershed_mask_seed = create_watershed_seed(bbox, rgb_proposal_mask, bbox_not_moved, watershed_last_frame_seed_mask)
    watershed_bg_mask = rgb_proposal_mask + depth_proposal_mask

    # set the background to 1 the luggage pixel to the values found before
    # the unknown pixel are still 0
    #watershed_mask_seed = np.where(watershed_bg_mask == 0, 1, watershed_mask_seed)
    watershed_mask_seed += 1
    # apply watershed - result overwrite in mask
    cv2.watershed(image, watershed_mask_seed)

    # OUTPUT MASK FOR FURTHER STUDY
    return np.where(watershed_mask_seed == 1, 0, 1)

#
# def region_growing_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask):
#     mask = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)
#     for box in bbox:
#         mask += simple_region_growing(image, box)
#     return np.where(mask == 255, 1, 0)


def get_segmentation_mask(TYPE, image, bbox, rgb_proposal_mask, depth_proposal_mask,
                          bbox_not_moved=None, watershed_last_frame_seed_mask=None):

    if TYPE == "watershed":
        mask = watershed_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask, bbox_not_moved, watershed_last_frame_seed_mask)
    else:
        # region growing
        # CURRENTLY NOT WORKING
        #mask = region_growing_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask)

    return mask