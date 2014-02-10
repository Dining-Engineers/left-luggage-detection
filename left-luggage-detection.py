from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import bg_models
from const import *

#create video streams
d = Display(resolution=(1280, 960))

#initialize the camera
cam = Kinect()

# variables
background_depth = np.zeros(shape=(480, 640), dtype=np.float32)
depth_accumulator = np.zeros(shape=(640, 480), dtype=np.float32)

f_bg = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)  # define zivkovic background subs function
f_bg2 = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)  # define zivkovic background subs function
background_aggregator = np.zeros(shape=(640, 480), dtype=np.int64)

# first loop
first_run = True

# main loop
while not d.isDone():

    # get next video frame
    current_frame_rgb = cam.getImage()
    # get next depth frame (11-bit precision)
    # NB darker => closer
    current_frame_depth = cam.getDepthMatrix()


    ###################################
    #
    #    PREPROCESSING: DEPTH MAP
    #
    ###################################

    if first_run:
        # in first run moving average start from first frame
        background_depth = np.float32(current_frame_depth)
        first_run = False

    # get depth background
    background_depth = bg_models.get_background_running_average(current_frame_depth, background_depth, BG_RUN_AVG_LRATE)

    # get depth foreground
    # 0 = background - 1 = foreground
    foreground_mask_depth = bg_models.get_foreground_mask_from_running_average(current_frame_depth,
                                                                               background_depth, BG_MASK_THRESHOLD)

    ## apply opening to remove noise
    foreground_mask_depth = bg_models.apply_opening(foreground_mask_depth, 10, cv2.MORPH_ELLIPSE)
    ## cut foreground
    foreground_depth = bg_models.get_foreground_from_mask_depth(current_frame_depth.T, foreground_mask_depth)
    # get
    bbox_depth, bbox_depth_areas = bg_models.get_bounding_boxes(foreground_mask_depth)


    ###################################
    #
    #    PREPROCESSING: RGB MAP
    #
    ###################################

    # get rgb dual background (long and short sensitivity)
    # NB background is black (0) and foreground white (1)
    foreground_mask_rgb_long = bg_models.get_background_mask_zivkovic(f_bg, current_frame_rgb.getNumpy(),
                                                                      BG_ZIV_LONG_LRATE)
    foreground_mask_rgb_short = bg_models.get_background_mask_zivkovic(f_bg2, current_frame_rgb.getNumpy(),
                                                                       BG_ZIV_SHORT_LRATE)

    # update rgb aggregator
    background_aggregator = bg_models.update_rgb_detection_aggregator(background_aggregator, foreground_mask_rgb_long,
                                                                      foreground_mask_rgb_short)
    # get rgb proposal
    proposal_rgb_mask = np.where(background_aggregator == AGG_MAX_E, 1, 0)
    # get rgb blobs
    bbox_rgb, bbox_rgb_areas = bg_models.get_bounding_boxes(proposal_rgb_mask.astype(np.uint8))

    ## cut foreground
    foreground_rgb_long = bg_models.get_foreground_from_mask_rgb(current_frame_rgb.getNumpy(), foreground_mask_rgb_long)
    foreground_rgb_proposal = bg_models.get_foreground_from_mask_rgb(current_frame_rgb.getNumpy(), proposal_rgb_mask)

    #background_mask_rgb = bg_models.apply_opening(background_mask_rgb, 3, cv2.MORPH_ELLIPSE)
    #background_mask_rgb2 = bg_models.apply_opening(background_mask_rgb2, 3, cv2.MORPH_ELLIPSE)

    ###################################
    #
    #   Combine proposals
    #
    ###################################

    # Draws bounding boxes
    for s in bbox_rgb:
        cv2.rectangle(foreground_rgb_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)

    for s in bbox_depth:
        cv2.rectangle(foreground_depth, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)







    # convert current_frame_depth and background_depth in octree-based representation
    # (voxel grids)
    # NB DEPTH HA OFFSET RISPETTo A RGB
    # CORREGGI CON img = img.crop(0,25, 605, 455).scale(640,480)

    # applico funzioni C RawDepthToMeters e DepthToWorld
    # ottengo rappresentazione xyz -> creo struttura dati octree sia di background sia di current





    #accul = accul - mask_depth
    #background_models.pretty_print(accul)
    #background_models.pretty_print(mask_depth)

    ####

    #depth_accumulator = depth_accumulator + np.where((mask_depth == 0), -1, mask_depth).astype(np.float32)
    #depth_accumulator = np.where((depth_accumulator < 0 ), 0, depth_accumulator).astype(np.float32)

    ##
    #cv2.accumulate(depth_accumulator - mask_depth, depth_accumulator)
    #visual_accul = np.zeros(shape=(depth_accumulator.shape), dtype=np.float32)
    #cv2.threshold(np.abs(depth_accumulator), 5, 255, cv2.THRESH_BINARY, visual_accul)
    ###

    #np.where((accul < 5), 0, 255).astype(np.float32)
    #background_models.pretty_print(accul)
    #print accul.shape
    #background_models.pretty_print(accul)
    #print np.amax(accul)

    ###
    #cv2.erode(depth_accumulator, (3,3), depth_accumulator)
    # save images to display
    frame_upper_left = current_frame_rgb
    frame_upper_right = Image(foreground_rgb_proposal)#current_frame_depth.T)
    frame_bottom_left = Image(foreground_depth)#foreground_rgb_long)
    frame_bottom_right = Image(foreground_depth)    #foreground_mask_depth*255)#foreground_depth)

    # rows of display
    frame_up = frame_upper_left.sideBySide(frame_upper_right)
    frame_bottom = frame_bottom_left.sideBySide(frame_bottom_right)

    # save images to display
    frame_up.sideBySide(frame_bottom, side="bottom").save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True
        d.quit()