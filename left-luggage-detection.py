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

f_bg = cv2.BackgroundSubtractorMOG2()   # define zivkovic background subs function



#print help(f_bg)
# main loop
while not d.isDone():

    # get next video frame
    current_frame_rgb = cam.getImage()
    # get next depth frame (11-bit precision)
    current_frame_depth = cam.getDepthMatrix()

    # get rgb background
    # NB background is black (0) and foreground white (255) and shadows (graylevel)
    background_rgb_mask = background_models.get_background_zivkovic(f_bg, current_frame_rgb.getNumpy())

    # get depth background
    background_depth = background_models.get_background_running_average()

    # convert current_frame_depth and background_depth in octree-based representation
    # (voxel grids)
    # NB DEPTH HA OFFSET RISPETTo A RGB
    # CORREGGI CON img = img.crop(0,25, 605, 455).scale(640,480)

    # applico funzioni C RawDepthToMeters e DepthToWorld
    # ottengo rappresentazione xyz -> creo struttura dati octree sia di background sia di current

    ##

    # dove where(x,y,z) dove si verifica x sostituisci y, il resto mettilo a z
    mask2 = np.where((background_rgb_mask == 255), 0, 1)
    draw = current_frame_rgb.getNumpy() * to_rgb1a(mask2)


    #fgmask = fgbg.apply(frame_np)
    #frame = frame.applyBinaryMask(Image(Image(fgmask).getGrayNumpyCv2()) )
    #lol = frame.getNumpyCv2() - to_rgb1a(fgmask)
    # background zivovic
    #frame = Image(lol.transpose(1,0,2))
    #foreground
    #frame = Image(to_rgb1a(fgmask).transpose(1,0,2))

    #frame - Image(to_rgb1a(fgmask))
    #Image(Image(fgmask).toRGB().getNumpyCv2().transpose(1,0,2))
    #frame.save(d)
    #Image(fgmask).save(d)
    #cv2.imshow('frame',fgmask)

    #draw = draw.transpose([1,0,2])#.transpose(0,1,2)
    #draw = draw[:, :, ::-1]
    frame_draw = Image(draw)#background_rgb_mask)# current_frame_rgb

    # draw next frame
    frame_draw.save(d)

    # quit if click on display
    if d.mouseLeft:
        d.done = True
        d.quit()
        #pg.quit()
