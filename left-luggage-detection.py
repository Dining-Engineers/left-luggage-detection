from depth_processing import *
from intensity_processing import *

#create video streams
d = Display(resolution=(1024, 768))

# initialize the camera
cam = Kinect()
# shape of the image obtained from kinect
IMAGE_SHAPE = (640, 480)

# first loop
first_run = True

# DepthProcessing instance
depth = DepthProcessing(IMAGE_SHAPE)
# IntensityProcessing instance
rgb = IntensityProcessing(IMAGE_SHAPE)

# main loop
while not d.isDone():

    # get next video frame
    rgb.current_frame = cam.getImage().getNumpy()

    # get next depth frame (11-bit precision)
    # N.B. darker => closer
    # the depth matrix obtained is transposed so we cast the right shape
    depth.current_frame = cam.getDepthMatrix().T


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
    depth.update_background_running_average()

    # get depth foreground
    depth.extract_foreground_mask_from_run_avg()

    # apply opening to remove noise
    depth.foreground_mask = bg_models.apply_opening(depth.foreground_mask, 5, cv2.MORPH_ELLIPSE)

    depth_proposal_bbox = depth.extract_proposal_bbox(depth.ACCUMULATOR)

    # cut foreground with real values
    foreground_depth_proposal = bg_models.get_foreground_from_mask_depth(depth.current_frame, depth.foreground_mask)

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

    # extract bounding box proposals
    rgb_proposal_bbox = rgb.extract_proposal_bbox()

    ###################################
    #
    #   Combine proposals
    #
    ###################################

    foreground_rgb_proposal = rgb.proposal
    # convert to rgb to draw colored boxes
    foreground_depth_proposal = to_rgb1a(foreground_depth_proposal)

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

    final_result_mask = np.where(watershed_mask == 1, 0, 1)
    colors = np.array([[0, 0, 0], [0, 255, 0]])#[191, 29, 167]])
    overlay = colors[final_result_mask]
    final_result_image = cv2.addWeighted(final_result_image, 0.5, overlay, 0.5, 0.0, dtype=cv2.CV_8UC3)


    # save images to display
    frame_upper_left = Image(rgb.current_frame)
    frame_upper_right = Image(foreground_rgb_proposal)
    frame_bottom_left = Image(foreground_depth_proposal)

    frame_bottom_right = Image(final_result_image)

    # rows of display
    frame_up = frame_upper_left.sideBySide(frame_upper_right)
    frame_bottom = frame_bottom_left.sideBySide(frame_bottom_right)

    # save images to display
    frame_up.sideBySide(frame_bottom, side="bottom").save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True

d.quit()