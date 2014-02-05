from SimpleCV import *
from SimpleCV.Display import Display
from utils import *
import background_models


#create video streams
d = Display()
#initialize the camera
cam = Kinect()

background_frames = 4                   # number of frames to build background model
background_depth_frames = ImageSet()    # buffer of frames for running average

f_bg = cv2.BackgroundSubtractorMOG2(1, 900, False)   # define zivkovic background subs function
background_depth = cv.CreateImage((640, 480), 32, 1)
avg_show = cv.CreateImage((640, 480),8, 1)

#print help(f_bg)
# main loop
while not d.isDone():

    # get next video frame
    current_frame_rgb = cam.getImage()
    # get next depth frame (11-bit precision)
    current_frame_depth = cam.getDepth()

    depth_ = current_frame_depth.getGrayNumpyCv2()
    #print depth_.shape

    #cam.getDepth().getNumpyCv2()[:, :, 1].copy()# cam.getDepthMatrix()

    # get rgb background
    # NB background is black (0) and foreground white (255) and shadows (graylevel)
    background_rgb_mask = background_models.get_background_zivkovic(f_bg, current_frame_rgb.getNumpy())

    # get depth background
    background_depth = background_models.get_background_running_average(background_depth, depth_)
    #current_frame_rgb.getGrayNumpyCv2())

    # convert current_frame_depth and background_depth in octree-based representation
    # (voxel grids)
    # NB DEPTH HA OFFSET RISPETTo A RGB
    # CORREGGI CON img = img.crop(0,25, 605, 455).scale(640,480)

    # applico funzioni C RawDepthToMeters e DepthToWorld
    # ottengo rappresentazione xyz -> creo struttura dati octree sia di background sia di current

    ##



    #fgmask = fgbg.apply(frame_np)
    #frame = frame.applyBinaryMask(Image(Image(fgmask).getGrayNumpyCv2()) )
    #lol = frame.getNumpyCv2() - to_rgb1a(fgmask)
    # background zivovic
    #frame = Image(lol.transpose(1,0,2))
    #foreground
    #frame = Image(to_rgb1a(fgmask).transpose(1,0,2))

    cv.ConvertScaleAbs(background_depth, avg_show)
    frame_draw = current_frame_depth#-Image(avg_show)
    #frame_draw = Image(background_models.get_background_from_mask(current_frame_rgb.getNumpy(), background_rgb_mask))
    #background_rgb_mask)#draw)#background_rgb_mask)# current_frame_rgb

    # draw next frame
    frame_draw.save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True
        d.quit()
        #pg.quit()
