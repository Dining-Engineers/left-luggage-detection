#!

# This is statement is required by the build system to query build info
if __name__ == '__build__':
    raise Exception

import string
__version__ = string.split('$Revision: 1.1.1.1 $')[1]
__date__ = string.join(string.split('$Date: 2007/02/15 19:25:21 $')[1:3], ' ')
__author__ = 'Tarn Weisner Burton <twburton@users.sourceforge.net>'

#
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from Image import *
import freenect
import cv
import frame_convert

keep_running = True
bool_new_rgb = False
bool_new_depth = False

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

texture = 0

def LoadTextures(data):

    #global texture

    video = data;#freenect.sync_get_video()[0]
    video = video[:, :, ::-1]  # RGB -> BGR
    #image = cv.CreateImageHeader((video.shape[1], video.shape[0]), cv.IPL_DEPTH_8U, 3)
    #cv.SetData(image, video.tostring(), video.dtype.itemsize * 3 * video.shape[1])
    #cv.ShowImage("asd", image)
    ix = video.shape[0]
    iy = video.shape[1]
    #im = image

    #im = open("sblinda.ppm")
    #ix = im.size[0]
    #iy = im.size[1]

    #image = image.tostring("raw", "RGBX", 0, -1)
    #image = video
    #try:
    #    image = image.tostring("raw", "RGBA", 0, -1)
    #except SystemError:
    #    image = image.tostring("raw", "RGBX", 0, -1)

    # Create Texture
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    #print "lol"
    ## errore
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, video)
    ##
    #print "bbb"
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    ## quale filtro usare se va ridimensionata
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)


# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL(Width, Height):				# We call this right after our OpenGL window is created.

    glEnable(GL_TEXTURE_2D)

    glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
    glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
    #glEnable(GL_DEPTH_TEST)				# Enables Depth Testing

    glDisable(GL_DEPTH_TEST);   ## WAT
    glEnable(GL_BLEND);         ## WAT
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); ## WAT
    glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
    print "aaa"

    im = open("NeHe.bmp")
    ix = im.size[0]
    iy = im.size[1]

    try:
        image = im.tostring("raw", "RGBA", 0, -1)
    except SystemError:
        image = im.tostring("raw", "RGBX", 0, -1)

    # Create Texture
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    #print "lol"
    ## errore
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    ##
    #print "bbb"
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    ## quale filtro usare se va ridimensionata
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    print "ccc"
    ReSizeGLScene(Width, Height)



# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(0, 1280, 0, 480, 0, 1)
    glMatrixMode(GL_MODELVIEW)

# The main drawing function.
def DrawGLScene():
    global xrot, yrot, zrot, texture

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
    glLoadIdentity()					# Reset The View

    glEnable(GL_TEXTURE_2D);        #WAT

    glBegin(GL_TRIANGLE_FAN)			    # Start Drawing The Cube

    glColor4f(255.0, 255.0, 255.0, 255.0);  #WAT
    glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0, 0.0) #glVertex3f(-2.0, -1.0,  1.0)	# Bottom Left Of The Texture and Quad
    glTexCoord2f(1.0, 0.0); glVertex3f(640, 0.0, 0.0) #glVertex3f( 1.0, -1.0,  1.0)	# Bottom Right Of The Texture and Quad
    glTexCoord2f(1.0, 1.0); glVertex3f(640, 480, 0.0) #glVertex3f( 1.0,  1.0,  1.0)	# Top Right Of The Texture and Quad
    glTexCoord2f(0.0, 1.0); glVertex3f(0.0, 480, 0.0) #glVertex3f(-1.0,  1.0,  1.0)	# Top Left Of The Texture and Quad

    glEnd()				# Done Drawing The Cube

    #  since this is double buffered, swap the buffers to display what just got drawn.
    glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
# If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        sys.exit()

def main():
    # Start kinect recording
    # freenect.runloop(depth=display_depth, video=display_rgb, body=body)
    # start opengl
    # init_gl()
    freenect.runloop(depth=display_depth,
                 video=display_rgb,
                 body=body)

def display_depth(dev, data, timestamp):
    if cv.WaitKey(10) == 27:
        keep_running = False


def display_rgb(dev, data, timestamp):
    print "new frame"
    LoadTextures(data)
    if cv.WaitKey(10) == 27:
        keep_running = False


def body(*args):
    init_gl()
    if not keep_running:
        raise freenect.Kill


def init_gl():
    global window
    glutInit(sys.argv)

    # Select type of Display mode:
    #  Double buffer
    #  RGBA color
    # Alpha components supported
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)

    # get a 640 x 480 window
    glutInitWindowSize(1280, 480)

    # the window starts at the upper left corner of the screen
    glutInitWindowPosition(0, 0)

    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")

    # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.
    glutDisplayFunc(DrawGLScene)

    # Uncomment this line to get full screen.
    # glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(DrawGLScene)

    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)

    # Register the function called when the keyboard is pressed.
    glutKeyboardFunc(keyPressed)

    # Initialize our window.
    InitGL(1280, 480)

    # Start Event Processing Engine
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."
main()
