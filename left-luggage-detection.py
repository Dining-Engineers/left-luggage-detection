from reportlab.lib.colors import toColor
from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import bg_models
from const import *
from pykdtree.kdtree import KDTree
from depth_processing import *
from intensity_processing import *

#create video streams
d = Display(resolution=(1024, 768))

#initialize the camera
cam = Kinect()

#f_bg = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)
# f_bg2 = cv2.BackgroundSubtractorMOG2(BG_ZIV_HIST, BG_ZIV_THRESH, False)  # define zivkovic background subs function
background_rgb_aggregator = np.zeros(shape=(640, 480), dtype=np.int32)

# first loop
first_run = True

# DepthProcessing instance
depth = DepthProcessing()

# IntensityProcessing instance
rgb = IntensityProcessing()

# main loop
while not d.isDone():

    # get next video frame
             #current_frame_rgb = cam.getImage()
    rgb.current_frame = cam.getImage().getNumpy()

    # get next depth frame (11-bit precision)
    # N.B. darker => closer
    depth.current_frame = cam.getDepthMatrix()

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
    depth.update_background_running_average()

    # get depth foreground
    depth.extract_foreground_mask_from_run_avg()

    ## apply opening to remove noise
    depth.foreground_mask = bg_models.apply_opening( depth.foreground_mask, 5, cv2.MORPH_ELLIPSE)

    bbox_to_draw = depth.get_proposal_bbox()

    # if bbox_depth_val.size is not 0:
    #     for rect in bbox_depth_val:
    #         c_x = rect[0]
    #         c_y = rect[1]
    #         area = rect[2]
    #         query = (c_x, c_y, area)
    #         if query in bbox_dict.keys():
    #             bbox_dict[query] = bbox_dict[(c_x, c_y, area)] + 1
    #         else:
    #             bbox_dict[query] = 1



    #        cv2.rectangle(foreground_depth_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)


    # # get depth old accumulator proposal
    # old_proposal_depth_mask = np.where(background_depth_aggregator >= 5, 1, 0)
    #
    # # get bounding boxes accumulator depth frame
    # bbox_old_depth, bbox_old_depth_val, bbox_old_pixels = bg_models.get_bounding_boxes(old_proposal_depth_mask.astype(np.uint8))
    #
    # # update depth aggregator
    # background_depth_aggregator = bg_models.update_depth_detection_aggregator(background_depth_aggregator,
    #                                                                           foreground_mask_depth_current)
    #
    # # get depth proposal
    # proposal_depth_mask = np.where(background_depth_aggregator >= 5, 1, 0)
    #
    # # get bounding boxes current depth frame
    # bbox_new_depth, bbox_new_depth_val, bbox_new_pixels = bg_models.get_bounding_boxes(proposal_depth_mask.astype(np.uint8))
    #
    # bbox_depth = []
    # final_proposal_depth_mask = (np.zeros(shape=(640, 480), dtype=np.uint8))
    # if bbox_new_depth_val.size is not 0:
    #     if bbox_old_depth_val.size is not 0:
    #         # compare bounding boxes of: current frame vs accumulator
    #         # and keep only the ones that have almost the same center and area
    #         kdtree_curr = KDTree(bbox_new_depth_val)
    #         # idx is a list of index of match in kdtree
    #         dist, idx = kdtree_curr.query(bbox_old_depth_val, k=2)
    #         for i in range(len(idx)):
    #             match = idx[i][0]
    #             if dist[i][0]/dist[i][1] <= 0.8:  # aka no record in this distance
    #                 #print "tengo ",
    #                 #print " aa", idx, len(bbox_old_pixels), len(bbox_new_pixels), match
    #                 #print type(bbox_curr_depth)
    #                 #print match, bbox_curr_depth[match].shape
    #                 cv2.drawContours(final_proposal_depth_mask, [bbox_new_pixels[match]], -1, 1, -1)
    #                 bbox_depth.append(bbox_new_depth[match])
    #                 # select the right pixels
    #                 #for s in bbox_curr_pixels[match]:
    #                 #    b = s[0, 0]
    #                 #    a = s[0, 1]
    #                 #    proposal_depth_mask[a, b] = 1
    #             #else:
    #                 #print "scarto"
    #         #print "-"
    # #print len(bbox_new_depth), len(bbox_depth)
    # #final_proposal_depth_mask = proposal_depth_mask
    # #bbox_depth = bbox_new_depth
    #
    # #proposal_depth_mask = proposal_depth_mask[:, :, 0]
    # #print proposal_depth_mask.shape
    #
    # # get bounding boxes
    # #bbox_depth, bbox_depth_element, _ = bg_models.get_bounding_boxes(proposal_depth_mask.astype(np.uint8))

    proposal_depth_mask = depth.foreground_mask
    final_proposal_depth_mask = (np.zeros(shape=(640, 480), dtype=np.uint8))

    ## cut foreground with real values
    foreground_depth_proposal = bg_models.get_foreground_from_mask_depth(depth.current_frame.T, proposal_depth_mask)

    ###################################
    #
    #    PREPROCESSING: RGB MAP
    #
    ###################################

    # get rgb dual background (long and short sensitivity)
    # NB background is black (0) and foreground white (1)

    # foreground_mask_rgb_long = bg_models.get_background_mask_zivkovic(f_bg, current_frame_rgb.getNumpy(),
    #                                                                   BG_ZIV_LONG_LRATE)


    #foreground_mask_rgb_short = bg_models.get_background_mask_zivkovic(f_bg2, current_frame_rgb.getNumpy(),
    #                                                                       BG_ZIV_SHORT_LRATE)


    rgb.extract_background_mask_porikli()

    # update rgb aggregator
    # background_rgb_aggregator = bg_models.update_rgb_detection_aggregator(background_rgb_aggregator,
    #                                                                       foreground_mask_rgb_long,
    #                                                                       foreground_mask_rgb_short)


    # update rgb aggregator
    rgb.update_detection_aggregator()

    foreground_rgb_proposal = rgb.extract_proposal()

    ###################################
    #
    #   Combine proposals
    #
    ###################################

    # Draws bounding boxes
    for s in rgb.bbox_to_draw:
        cv2.rectangle(foreground_rgb_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)

    foreground_depth_proposal = to_rgb1a(foreground_depth_proposal)
    for s in bbox_to_draw:
        cv2.rectangle(foreground_depth_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)


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

    # save images to display
    frame_upper_left = Image(rgb.current_frame)
    frame_upper_right = Image(foreground_rgb_proposal)
    frame_bottom_left = Image(foreground_depth_proposal)
    frame_bottom_right = Image(proposal_depth_mask*255)

    # rows of display
    frame_up = frame_upper_left.sideBySide(frame_upper_right)
    frame_bottom = frame_bottom_left.sideBySide(frame_bottom_right)

    # save images to display
    frame_up.sideBySide(frame_bottom, side="bottom").save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True


d.quit()