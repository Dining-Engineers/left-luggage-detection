#from reportlab.lib.colors import toColor
from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import bg_models
from const import *
from pykdtree.kdtree import KDTree
from depth_processing import *
from intensity_processing import *
import datetime
import itertools

#create video streams
d = Display(resolution=(1024, 768))

#initialize the camera
cam = Kinect()

# first loop
first_run = True

# DepthProcessing instance
depth = DepthProcessing()
depth2 = DepthProcessing()

# IntensityProcessing instance
rgb = IntensityProcessing()

T1 = np.uint64(0)
T2 = np.uint64(0)
T3 = np.uint64(0)
ENABLE_SECOND_DEPTH = False

# main loop
while not d.isDone():

    # get next video frame
             #current_frame_rgb = cam.getImage()
    rgb.current_frame = cam.getImage().getNumpy()

    # get next depth frame (11-bit precision)
    # N.B. darker => closer

    depth.current_frame = depth2.current_frame = cam.getDepthMatrix()

    #depth_frame = cam.getDepthMatrix()
    #print depth_frame.shape
    #depth_frame = depth_frame[25:, 0:605]
    # TODO correggi offset depth
    #depth.current_frame = depth2.current_frame = cv2.resize(depth_frame, (640, 480))

    #print depth.current_frame.shape, depth.current_frame.dtype

    ###################################
    #
    #    PREPROCESSING: DEPTH MAP
    #
    ###################################

    if first_run:
        # in first run moving average start from first frame
        depth.background_model = depth.current_frame.astype(depth.background_model.dtype)
        depth2.background_model = depth2.current_frame.astype(depth2.background_model.dtype)
        first_run = False

    # get depth background
    depth.update_background_running_average()

    # get depth foreground
    depth.extract_foreground_mask_from_run_avg()

    # apply opening to remove noise
    depth.foreground_mask = bg_models.apply_opening(depth.foreground_mask, 5, cv2.MORPH_ELLIPSE)

    t0 = datetime.datetime.now().microsecond
    depth_proposal_bbox = depth.extract_proposal_bbox(depth.ACCUMULATOR)
    t1 = datetime.datetime.now().microsecond
    #print t1 - t0

    # cut foreground with real values
    foreground_depth_proposal = bg_models.get_foreground_from_mask_depth(depth.current_frame.T, depth.foreground_mask)

#############################  CANC CANC CANC ##########################################
    if ENABLE_SECOND_DEPTH:
        # get depth background
        depth2.update_background_running_average()

        # get depth foreground
        depth2.extract_foreground_mask_from_run_avg()

        # apply opening to remove noise
        depth2.foreground_mask = bg_models.apply_opening(depth2.foreground_mask, 5, cv2.MORPH_ELLIPSE)

        t2 = datetime.datetime.now().microsecond / 1000
        bbox_to_draw2 = depth2.extract_proposal_bbox(depth2.RECT_MATCHING2)
        t3 = datetime.datetime.now().microsecond / 1000
        print t1-t0, t3-t2, len(bbox_to_draw2)
        T1 += abs(t1-t0)
        T2 += abs(t3-t2)

        # cut foreground with real values
        foreground_depth_proposal2 = bg_models.get_foreground_from_mask_depth(depth2.current_frame.T, depth2.foreground_mask)
#############################  CANC CANC CANC ##########################################


    ###################################
    #
    #    PREPROCESSING: RGB MAP
    #
    ###################################

    # get rgb dual background (long and short sensitivity)
    # N.B. background is black (0) and foreground white (1)
    rgb.extract_background_mask_porikli()

    # update rgb aggregator
    rgb.update_detection_aggregator()

    rgb_proposal_bbox, rgb_contours = rgb.extract_proposal_bbox()

    ###################################
    #
    #   Combine proposals
    #
    ###################################

    foreground_rgb_proposal = rgb.proposal
    foreground_depth_proposal = to_rgb1a(foreground_depth_proposal)
    match_rgb = rgb.current_frame.copy()

    # needed by grabcut
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)



    draw_depth_once = False
    watershed_mask = np.zeros(shape=(640, 480), dtype=np.int32)
    # Draws bounding boxes
    for k, s in enumerate(rgb_proposal_bbox):
        cv2.rectangle(foreground_rgb_proposal, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)
        #cv2.drawContours(match_rgb, rgb_contours[k], -1, (0, 255, 0), -1)
        for r in depth_proposal_bbox:
            if not draw_depth_once:
                cv2.rectangle(foreground_depth_proposal, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), 255, 1)
            if rect_similarity2(s, r):
                cv2.rectangle(match_rgb, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), (255, 0, 0), 1)
                # mark rect slice for proposal for watershed segmentation
                watershed_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]] = rgb.proposal_mask[s[1]:s[1]+s[3], s[0]:s[0]+s[2]]*k+1

                # mask = np.zeros(shape=(s[3], s[2]), dtype=np.uint8)
                # #print match_rgb.shape, "-----" , s, r
                # #print s[0], s[0]+s[2], s[1], s[1]+s[3], s
                # img = match_rgb[s[1]:s[1]+s[3], s[0]:s[0]+s[2], :]#.copy()
                # print img.shape, mask.shape, match_rgb[s[0]+s[2], s[1]+s[3]]
                # cv2.grabCut(img, mask, s, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                # mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
                # colors = np.array([[0, 0, 0], [0, 1, 0]]) * 255
                # overlay = colors[np.maximum(mask, 0) % 2]
                # cv2.addWeighted(match_rgb[s[1]:s[1]+s[3], s[0]:s[0]+s[2], :], 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)

        draw_depth_once = True

    watershed_bg_mask = rgb.proposal_mask+depth.foreground_mask
    watershed_mask = np.where(watershed_bg_mask == 0, 1, watershed_mask)
    cv2.watershed(match_rgb, watershed_mask)

    watershed_mask = np.where(watershed_mask == 1, 0, 1)
    colors = np.array([[0, 0, 0], [0, 255, 0]])#[191, 29, 167]])
    overlay = colors[watershed_mask]
    #print overlay.shape, overlay
    match_rgb = cv2.addWeighted(match_rgb, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)


    # overlay = colors[np.maximum(draw_obj_mask, 2)%2]
    # match_rgb = cv2.addWeighted(match_rgb, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)


    # draw_obj_mask = np.zeros(shape=(640, 480), dtype=np.int32)
    #
    # for k, s in enumerate(rgb_proposal_bbox):
    #     for r in depth_proposal_bbox:
    #         if rect_similarity2(s, r):
    #             cv2.rectangle(match_rgb, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), (255, 0, 0), 1)
    #             # nb enumerate start from 0, segment need >0
    #             # we set bg = 1 so other seg start from 2
    #             cv2.drawContours(draw_obj_mask, [rgb_contours[k]], -1, k+2, -1)

    #colors = np.int32(list(np.ndindex(2, 1, 1)) ) * 255

    # colors = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0]]) * 255
    # bg_marker = depth.foreground_mask + rgb.foreground_mask_short_term
    # draw_obj_mask = np.where(bg_marker == 0, 1, draw_obj_mask)
    #
    # cv2.watershed(match_rgb, draw_obj_mask)
    # overlay = colors[np.maximum(draw_obj_mask, 2)%2]
    # match_rgb = cv2.addWeighted(match_rgb, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)


    # for k in itertools.product(rgb_proposal_bbox, depth_proposal_bbox):
    #     if rect_similarity2(k[0], k[1]):
    #         cv2.rectangle(match_rgb, (k[0][0], k[0][1]), (k[0][0]+k[0][2], k[0][1]+k[0][3]), (255, 0, 0), 1)

#############################  CANC CANC CANC ##########################################
    if ENABLE_SECOND_DEPTH:
        foreground_depth_proposal2 = to_rgb1a(foreground_depth_proposal2)
        for s in bbox_to_draw2:
            #print "disegno"
            cv2.rectangle(foreground_depth_proposal2, (s[0], s[1]), (s[0]+s[2], s[1]+s[3]), 255, 1)
#############################  CANC CANC CANC ##########################################

    # convert current_frame_depth and background_depth in octree-based representation
    # (voxel grids)
    # NB DEPTH HA OFFSET RISPETTo A RGB
    # CORREGGI CON img = img.crop(0,25, 605, 455).scale(640,480)

    # applico funzioni C RawDepthToMeters e DepthToWorld
    # ottengo rappresentazione xyz -> creo struttura dati octree sia di background sia di current

    # save images to display
    frame_upper_left = Image(rgb.current_frame)
    frame_upper_right = Image(foreground_rgb_proposal)
    frame_bottom_left = Image(foreground_depth_proposal)

    if ENABLE_SECOND_DEPTH:
        frame_bottom_right = Image(foreground_depth_proposal2)#match_rgb)
    else:
        frame_bottom_right = Image(match_rgb)# rgb.current_frame * to_rgb1a(rgb.foreground_mask_short_term))#

    # rows of display
    frame_up = frame_upper_left.sideBySide(frame_upper_right)
    frame_bottom = frame_bottom_left.sideBySide(frame_bottom_right)

    # save images to display
    frame_up.sideBySide(frame_bottom, side="bottom").save(d)

    # quit if click on display
    if d.mouseLeft:
        #print "FINEE ", T1, T2
        d.done = True

print "Time to draw bounding boxes ", T3
d.quit()