#!/usr/bin/env python

import numpy as np
import cProfile
import calibkinect

from depth_processing import *
from intensity_processing import *
from kinectconnector import *
from video_type import VideoDisplay
from region_growing import simple_region_growing

__author__ = "Andrea Rizzo, Matteo Bruni"
__copyright__ = "Copyright 2014, Dining Engineers"
__credits__ = ["Andrea Rizzo", "Matteo Bruni", "Lorenzo Seidenari",
                    "Lamberto Ballan", "Alberto Del Bimbo"]
__license__ = "GPLv2"
__version__ = "0.0.1"
__maintainer__ = "Andrea Rizzo, Matteo Bruni"
__email__ = "diningengineers@gmail.com, andrearizzo@outlook.com, matteo.bruni@gmail.com"
__status__ = "Development"


def left_luggage_detection():

    # Initialize video display
    screen = VideoDisplay(DISPLAY_TYPE, 4)

    # initialize the camera
    cam = KinectConnector()

    # first loop
    first_run = True

    # DepthProcessing instance
    depth = DepthProcessing(IMAGE_SHAPE)
    # IntensityProcessing instance
    rgb = IntensityProcessing(IMAGE_SHAPE)

    bbox_last_frame_proposals = []

    loop = True
    # main loop
    while loop:

        # get next video frame
        rgb.current_frame = cam.get_image()     # .getNumpy()

        # get next depth frame (11-bit precision)
        # N.B. darker => closer
        # the depth matrix obtained is transposed so we cast the right shape
        depth.current_frame = cam.get_depth_matrix()

        # xyz, uv = calibkinect.depth2xyzuv(depth.current_frame)
        # print xyz.shape, uv.shape, xyz[0][:], uv[0][:]

        # TODO correggi offset depth
        #depth_frame = depth_frame[25:, 0:605]
        #depth.current_frame = depth2.current_frame = cv2.resize(depth_frame, (640, 480))

        ###################################
        #
        #    PREPROCESSING: DEPTH MAP
        #
        ###################################

        if first_run:
            # in first run moving average start from first frame
            depth.background_model = depth.current_frame.astype(depth.background_model.dtype)

            # in first run the old_frame is the current frame
            old_frame = rgb.current_frame.copy()
            watershed_last_frame_seed_mask = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)
            first_run = False

        # get depth background
        depth.update_background_model(depth.current_frame)

        # get depth foreground
        depth.extract_foreground_mask_from_run_avg(depth.current_frame)

        # apply opening to remove noise
        depth.foreground_mask = bg_models.apply_opening(depth.foreground_mask, BG_OPEN_KSIZE, cv2.MORPH_ELLIPSE)

        depth_proposal_bbox = depth.extract_proposal_bbox(depth.ACCUMULATOR)

        # cut foreground with real values
        foreground_depth_proposal = bg_models.cut_foreground(depth.current_frame, depth.foreground_mask)

        ###################################
        #
        #    PREPROCESSING: RGB MAP
        #
        ###################################

        # get rgb dual background (long and short sensitivity)
        # N.B. background is black (0) and foreground white (1)
        rgb.compute_foreground_masks(rgb.current_frame)

        # update rgb aggregator
        rgb.update_detection_aggregator()

        # extract bounding box proposals
        rgb_proposal_bbox = rgb.extract_proposal_bbox()

        ###################################
        #
        #   Combine proposals
        #
        ###################################

        foreground_rgb_proposal = rgb.proposal_foreground

        # convert to rgb to draw colored boxes
        foreground_depth_proposal = to_rgb(foreground_depth_proposal)

        # extract current frame proposal: bbox that match PASCAL overlapping criterion between the
        # bbox in rgb and in depth
        bbox_current_frame_proposals = extract_proposal_bbox(rgb_proposal_bbox, depth_proposal_bbox)

        # image where will draw the combined proposal
        final_result_image = rgb.current_frame.copy()


        bbox_last_frame_proposals = bbox_current_frame_proposals + check_bbox_not_moved(bbox_last_frame_proposals,
                                                                                bbox_current_frame_proposals,
                                                                                old_frame,
                                                                                rgb.current_frame.copy())

        # get segmentation mask where each pixel is:
        #       - 0 unknown area
        #       - 1 background area
        #       - >1 item detection (luggage)
        final_result_mask = get_segmentation_mask("watershed", final_result_image, bbox_last_frame_proposals,
                                                  rgb.proposal_mask, depth.foreground_mask, watershed_last_frame_seed_mask)

        # apply overlay of [0, 0, 0] for no info
        # [0, 255, 0] for left luggage
        colors = np.array([[0, 0, 0], [0, 255, 0]])
        overlay = colors[final_result_mask]
        final_result_image = cv2.addWeighted(final_result_image, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)



        watershed_last_frame_seed_mask = final_result_mask.copy()

        # draw the proposals bbox in the image
        for s in bbox_current_frame_proposals:
            cv2.rectangle(final_result_image, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), (255, 0, 0), 1)

        # save the old frame
        old_frame = rgb.current_frame.copy()

        frame_upper_left = rgb.current_frame
        frame_upper_right = foreground_rgb_proposal
        frame_bottom_left = foreground_depth_proposal
        frame_bottom_right = final_result_image

        loop = screen.show(frame_upper_left, frame_upper_right, frame_bottom_left, frame_bottom_right)
        #loop = screen.show(to_rgb(rgb.foreground_mask_long_term*255), to_rgb(rgb.foreground_mask_short_term*255), frame_bottom_left, frame_bottom_right)

        if not loop:
            screen.quit()


def extract_proposal_bbox(rgb_proposal_bbox, depth_proposal_bbox):

    bbox_current_frame_proposals = []

    # Draws bounding boxes
    for k, s in enumerate(rgb_proposal_bbox):
        # Draw BBOX on RGB
        #cv2.rectangle(foreground_rgb_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)

        for r in depth_proposal_bbox:
            #if not draw_depth_once:
                # Draw BBOX on DEPTH
                #cv2.rectangle(foreground_depth_proposal, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), 255, 1)
            if rect_similarity2(s, r):
                # Draw BBOX on COMBINED proposal image
                #cv2.rectangle(final_result_image, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), (255, 0, 0), 1)
                # mark rect slice for proposal for watershed segmentation
                # set segment to k+1 since we use 1 for sure background segment
                #watershed_mask_seed[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = rgb.proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]*k+1

                bbox_current_frame_proposals.append(s)

        #draw_depth_once = True

    return bbox_current_frame_proposals


def check_bbox_not_moved(bbox_last_frame_proposals, bbox_current_frame_proposals, old_frame, current_frame):
    """ A bounding box can disappear because:

            - a left item is removed
            - the item detected is standing still for a long amount of time. After this time the item became part of
              the depth and rgb background. When the item became part of the background model we can't detect
              its presence doing current_frame-bg_model so we need a way to retain the information previously discovered
              If a Bounding box is present at the frame t-1 but not in the frame t, we check if pixels in the area
              defined by this bbox are still the same (i.e. the luggage is still there): this check is performed by
              using the normalized correlation between the pixel in the t-1 and t frame.
              If the similarity is above a certain threshold (i.e. 0.9) we keep drawing the old bbox

    """
    #bounding box present in old frame but not in the new frame
    bbox_to_add = []

    # not on first frame of video
    if len(bbox_last_frame_proposals) > 0:
        #print "ciclo vecchie proposte che sono:", len(bbox_last_frame_proposals)
        for old in bbox_last_frame_proposals:
            old_drawn = False
            for curr in bbox_current_frame_proposals:

                if rect_similarity2(old, curr):
                    old_drawn = True
                    break

            if not old_drawn:
                # Check if the area defined by the bounding box in the old frame and in the new one
                # is still the same
                old_section = old_frame[old[1]:old[1]+old[3], old[0]:old[0]+old[2]].flatten()
                new_section = current_frame[old[1]:old[1]+old[3], old[0]:old[0]+old[2]].flatten()

                if norm_correlate(old_section, new_section)[0] > 0.9:
                    #cv2.rectangle(final_result_image, (old[0], old[1]), (old[0]+old[2], old[1]+old[3]), (255, 0, 0), 1)
                    bbox_current_frame_proposals.append(old)

    return bbox_to_add


def create_watershed_seed(bbox_current_frame_proposals, proposal_mask, watershed_last_frame_seed_mask):
    watershed_mask_seed = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)
    for k, s in enumerate(bbox_current_frame_proposals):
        if np.sum(proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]) == 0:
            watershed_mask_seed[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = watershed_last_frame_seed_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]
            print "mi manca uso seed vecchi"
        else:
            watershed_mask_seed[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]*(k+5)

    return watershed_mask_seed


def watershed_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask, watershed_last_frame_seed_mask):
    # segmentation
    watershed_mask_seed = create_watershed_seed(bbox, rgb_proposal_mask, watershed_last_frame_seed_mask)
    watershed_bg_mask = rgb_proposal_mask + depth_proposal_mask
    # for s in bbox:
    #     if np.sum(rgb_proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]) == 0 or   \
    #        np.sum(depth_proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]) == 0:
    #         #watershed_bg_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = 1

    # set the background to 1 the luggage pixel to the values found before
    # the unknown pixel are still 0
    watershed_mask_seed = np.where(watershed_bg_mask == 0, 1, watershed_mask_seed)
    # apply watershed - result overwrite in mask
    cv2.watershed(image, watershed_mask_seed)

    # OUTPUT MASK FOR FURTHER STUDY
    return np.where(watershed_mask_seed == 1, 0, 1)


def region_growing_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask):
    mask = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)
    for box in bbox:
        mask += simple_region_growing(image, box)
    return np.where(mask == 255, 1, 0)


def get_segmentation_mask(TYPE, image, bbox, rgb_proposal_mask, depth_proposal_mask, watershed_last_frame_seed_mask):

    if TYPE == "watershed":
        mask = watershed_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask, watershed_last_frame_seed_mask)
    else:
        # region growing
        mask = region_growing_segmentation(bbox, image, rgb_proposal_mask, depth_proposal_mask)

    return mask



if __name__ == "__main__":
    left_luggage_detection()

    # PROFILING
    # cProfile.run('left_luggage_detection()')
    # command = """left_luggage_detection()"""
    # cProfile.runctx( command, globals(), locals(), filename="kinect_pygame.profile" )

    ## GRAFO CHIAMATE
    # from pycallgraph import PyCallGraph
    # from pycallgraph.output import GraphvizOutput
    # from pycallgraph import Config
    # from pycallgraph import GlobbingFilter
    #
    # config = Config()
    # config.trace_filter = GlobbingFilter(exclude=[
    #     'pycallgraph.*',
    #     '*.secret_function',
    #     'logging.*',
    #     'threading.*',
    #     'ctypes.*'
    #     're*',
    #     'distutils.*',
    #     'weakref.*',
    #     'atexit.*',
    #     'pkgutil.*',
    #     'codecs.*',
    #     'functools.*',
    #     'posixpath.*',
    #     'UserDict.*',
    #     'encodings.*',
    #     'string.*',
    #     'sre_parse.*',
    #     'ctypes*',
    #     'genericpath*',
    #     'stat*',
    #     'sre_compile*',
    #     'mpl_toolkits*'
    # ])
    #
    # graphviz = GraphvizOutput(output_file='filter_exclude_2.png')
    #
    # with PyCallGraph(output=graphviz, config=config):
    #     left_luggage_detection()


