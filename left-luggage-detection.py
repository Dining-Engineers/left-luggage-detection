from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import background_models


#create video streams
d = Display(resolution=(1280, 960))

#initialize the camera
cam = Kinect()

background_depth_frames = ImageSet()  # buffer of frames for running average
background_depth = np.zeros(shape=(480, 640), dtype=np.float32)
depth_accumulator = np.zeros(shape=(640, 480), dtype=np.float32)
f_bg = cv2.BackgroundSubtractorMOG2(1, 900, False)  # define zivkovic background subs function
first_run = True  # first loop

print type(f_bg)
print help(f_bg)

# main loop
while not d.isDone():

    # get next video frame
    current_frame_rgb = cam.getImage()

    # get next depth frame (11-bit precision)
    # NB darker => closer
    current_frame_depth = cam.getDepthMatrix()

    if first_run:
        # in first run moving average start from first frame
        background_depth = np.float32(current_frame_depth)
        first_run = False

    # get depth background
    background_depth = background_models.get_background_running_average(background_depth, current_frame_depth)

    # get depth foreground
    # 0 = background - 1 = foreground
    foreground_mask_depth = background_models.get_foreground_mask_from_running_average(current_frame_depth, background_depth)

    # get rgb background
    # NB background is black (0) and foreground white (255) and shadows (graylevel)
    background_mask_rgb = background_models.get_background_mask_zivkovic(f_bg, current_frame_rgb.getNumpy())



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


    ## cut foreground
    foreground_rgb = background_models.get_foreground_from_mask_rgb(current_frame_rgb.getNumpy(), background_mask_rgb)
    foreground_depth = background_models.get_foreground_from_mask_depth(current_frame_depth.T, foreground_mask_depth,)

    frame_upper_left = current_frame_rgb
    frame_upper_right = Image(current_frame_depth.T)
    frame_bottom_left = Image(foreground_rgb)
    frame_bottom_right = Image(foreground_depth)


    frame_up = frame_upper_left.sideBySide(frame_upper_right)
    frame_bottom = frame_bottom_left.sideBySide(frame_bottom_right)
    frame_up.sideBySide(frame_bottom, side="bottom").save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True
        d.quit()