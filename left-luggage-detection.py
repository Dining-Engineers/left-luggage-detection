from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import background_models


#create video streams
d = Display(resolution = (1280, 480))

#initialize the camera
cam = Kinect()

background_depth_frames = ImageSet()                # buffer of frames for running average
background_depth = np.zeros(shape=(480, 640), dtype=np.float32)
accul = np.zeros(shape=(640, 480), dtype=np.float32)
f_bg = cv2.BackgroundSubtractorMOG2(5, 900, False)  # define zivkovic background subs function
first_run = True                                    # first loop

# main loop
while not d.isDone():

    # get next video frame
    current_frame_rgb = cam.getImage()
    # get next depth frame (11-bit precision)
    current_frame_depth = cam.getDepthMatrix()

    if first_run:
        background_depth = np.float32(current_frame_depth)
        first_run = False

    # get rgb background
    # NB background is black (0) and foreground white (255) and shadows (graylevel)
    background_rgb_mask = background_models.get_background_zivkovic(f_bg, current_frame_rgb.getNumpy())

    # get depth background
    background_depth = background_models.get_background_running_average(background_depth, current_frame_depth)

    # convert current_frame_depth and background_depth in octree-based representation
    # (voxel grids)
    # NB DEPTH HA OFFSET RISPETTo A RGB
    # CORREGGI CON img = img.crop(0,25, 605, 455).scale(640,480)

    # applico funzioni C RawDepthToMeters e DepthToWorld
    # ottengo rappresentazione xyz -> creo struttura dati octree sia di background sia di current


    # get depth frame to draw
    mask_depth = background_models.get_mask_from_running_average(current_frame_depth.T, background_depth.T)
    #accul = accul - mask_depth

    cv2.accumulate(mask_depth-accul, accul)
    visual_accul = np.zeros(shape=(accul.shape), dtype=np.float32)
    cv2.threshold(accul, 2, 255, cv2.THRESH_BINARY, visual_accul)
    frame_draw_depth = Image(accul*255)

    # get rgb frame to draw
    frame_draw_rgb = Image(background_models.get_foreground_from_mask_rgb(current_frame_rgb.getNumpy(),
                                                                          background_rgb_mask))

    # draw next frame
    frame_draw_rgb.sideBySide(frame_draw_depth).save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True
        d.quit()