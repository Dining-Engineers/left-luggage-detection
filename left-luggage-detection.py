from depth_processing import *
from intensity_processing import *
import cProfile
from kinectconnector import *
import numpy as np
from video_type import VideoDisplay


def left_luggage_detection():

    # Initialize video display
    screen = VideoDisplay(DISPLAY_TYPE)

    # initialize the camera
    cam = KinectConnector()

    # first loop
    first_run = True

    # DepthProcessing instance
    depth = DepthProcessing(IMAGE_SHAPE)
    # IntensityProcessing instance
    rgb = IntensityProcessing(IMAGE_SHAPE)

    n_frame = 1
    loop = True
    # main loop
    while loop:

        # get next video frame
        rgb.current_frame = cam.get_image()#.getNumpy()

        # get next depth frame (11-bit precision)
        # N.B. darker => closer
        # the depth matrix obtained is transposed so we cast the right shape
        depth.current_frame = cam.get_depth_matrix()

        n_frame += 1
        # if n_frame == 80:
        #     loop = False

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
            first_run = False

        # get depth background
        depth.update_background_model(depth.current_frame)

        # get depth foreground
        depth.extract_foreground_mask_from_run_avg(depth.current_frame)

        # apply opening to remove noise
        #depth.foreground_mask = bg_models.apply_opening(depth.foreground_mask, BG_OPEN_KSIZE, cv2.MORPH_ELLIPSE)

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

        # image where will draw the combined proposal
        final_result_image = rgb.current_frame.copy()

        draw_depth_once = False
        watershed_mask = np.zeros(shape=IMAGE_SHAPE, dtype=np.int32)

        # Draws bounding boxes
        for k, s in enumerate(rgb_proposal_bbox):
            # Draw BBOX on RGB
            cv2.rectangle(foreground_rgb_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)

            for r in depth_proposal_bbox:
                if not draw_depth_once:
                    # Draw BBOX on DEPTH
                    cv2.rectangle(foreground_depth_proposal, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), 255, 1)
                if rect_similarity2(s, r):
                    # Draw BBOX on COMBINED proposal image
                    cv2.rectangle(final_result_image, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), (255, 0, 0), 1)
                    # mark rect slice for proposal for watershed segmentation
                    # set segment to k+1 since we use 1 for sure background segment
                    watershed_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = rgb.proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]*k+1

            draw_depth_once = True

        watershed_bg_mask = rgb.proposal_mask+depth.foreground_mask
        watershed_mask = np.where(watershed_bg_mask == 0, 1, watershed_mask)

        # apply watershed - result overwrite in mask
        cv2.watershed(final_result_image, watershed_mask)

        # OUTPUT MASK FOR FURTHER STUDY
        final_result_mask = np.where(watershed_mask == 1, 0, 1)
        colors = np.array([[0, 0, 0], [0, 255, 0]])
        overlay = colors[final_result_mask]
        final_result_image = cv2.addWeighted(final_result_image, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)

        frame_upper_left = rgb.current_frame
        frame_upper_right = foreground_rgb_proposal
        frame_bottom_left = foreground_depth_proposal
        frame_bottom_right = final_result_image

        loop = screen.show(frame_upper_left, frame_upper_right, frame_bottom_left, frame_bottom_right)

        if not loop:
            screen.quit()


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


