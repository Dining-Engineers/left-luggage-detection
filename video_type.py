__author__ = "Andrea Rizzo, Matteo Bruni"
__copyright__ = "Copyright 2014, Dining Engineers"
__license__ = "GPLv2"

import numpy as np
from const import *


PYGAME = "PYGAME"
SIMPLECV = "SIMPLECV"

if DISPLAY_TYPE == PYGAME:
    import pygame
    import pygame.camera
    from pygame.locals import *
else:
    from SimpleCV import *


class VideoDisplay:
    """
    Video Display class. Depending on the method choosed (PYGAME or SIMPLECV)
    Initialize a screen type to show the output.
    """

    def __init__(self, v_type, n_views):

        self.n_views = n_views
        self.type = v_type
        self.frame_count = 0

        if v_type == PYGAME:
            pygame.init()
            if n_views == 2:
                self.screen = pygame.display.set_mode([1280, 480])
            else:
                self.screen = pygame.display.set_mode([1280, 960])

            pygame.display.set_caption("Left Luggage Detection")

            self.clock = pygame.time.Clock()

        else:

            if n_views == 2:
                self.screen = Display(resolution=(1280, 480))
            else:
                self.screen = Display(resolution=(1280, 960))

    def show(self, frame_upper_left, frame_upper_right, frame_bottom_left=None, frame_bottom_right=None):
        """
        Display the four frames in a 1280x960 display

        :param frame_upper_left:
        :param frame_upper_right:
        :param frame_bottom_left:
        :param frame_bottom_right:
        :return: True if the drawing succeed or False if the user choose to exit
        :rtype: boolean
        :raise SystemExit:
        """
        self.frame_count += 1
        if self.type == PYGAME:

            tickFPS = self.clock.tick()
            #print "fps:", self.clock.get_fps()

            if self.n_views == 2:

                # show only 2 frames

                frame = np.zeros(shape=(1280, 480, 3))
                frame[:640, :480] = frame_upper_left
                frame[640:, :480] = frame_upper_right

                surface = pygame.surfarray.make_surface(frame)
                self.screen.blit(surface, (0, 0))

                # pick a font you have and set its size
                myfont = pygame.font.SysFont("Arial", 15)
                # apply it to text on a label
                label_tl = myfont.render("Video Stream RGB", 1, (255, 255, 255))
                label_tr = myfont.render("Final proposals", 1, (255, 255, 255))

                # put the label object on the screen at point x=100, y=100
                self.screen.blit(label_tl, (20, 10))
                self.screen.blit(label_tr, (660, 10))

            else:

                # show all 4
                frame = np.zeros(shape=(1280, 960, 3))
                frame[:640, :480] = frame_upper_left
                frame[640:, :480] = frame_upper_right
                frame[:640, 480:] = frame_bottom_left
                frame[640:, 480:] = frame_bottom_right

                surface = pygame.surfarray.make_surface(frame)
                self.screen.blit(surface, (0, 0))

                # pick a font you have and set its size
                myfont = pygame.font.SysFont("Arial", 15)
                # apply it to text on a label
                label_tl = myfont.render("Video Stream RGB", 1, (255, 255, 255))
                label_tr = myfont.render("Final proposals", 1, (255, 255, 255))
                label_bl = myfont.render("DEPTH foreground and detection Proposals", 1, (255, 255, 255))
                label_br = myfont.render("RGB foreground and detection Proposals", 1, (255, 255, 255))


                # put the label object on the screen at point x=100, y=100
                self.screen.blit(label_tl, (20, 10))
                self.screen.blit(label_tr, (660, 10))
                self.screen.blit(label_bl, (20, 490))
                self.screen.blit(label_br, (660, 490))

            if SHOW_FPS:
                label_fps = myfont.render("FPS: "+str(self.clock.get_fps()), 1, (255, 255, 255))
                self.screen.blit(label_fps, (1100, 10))

            pygame.display.flip()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    pygame.display.quit()
                    return False
                 # exit conditions --> windows titlebar x click
                if event.type == pygame.QUIT:
                    return False
                    raise SystemExit

            if ENABLE_PROFILING:
                # profile only the first 100 frames
                if self.frame_count == 100:
                    return False
            return True

        else:

            # SIMPLECV
            if self.n_views == 2:
                # save images to display
                i_frame_upper_left = Image(frame_upper_left)
                i_frame_upper_right = Image(frame_upper_right)


                # rows of display
                frame_up = i_frame_upper_left.sideBySide(i_frame_upper_right)

                # save images to display
                frame_up.save(self.screen)
            else:

                # save images to display
                i_frame_upper_left = Image(frame_upper_left)
                i_frame_upper_right = Image(frame_upper_right)
                i_frame_bottom_left = Image(frame_bottom_left)
                i_frame_bottom_right = Image(frame_bottom_right)

                # rows of display
                frame_up = i_frame_upper_left.sideBySide(i_frame_upper_right)
                frame_bottom = i_frame_bottom_left.sideBySide(i_frame_bottom_right)

                # save images to display
                frame_up.sideBySide(frame_bottom, side="bottom").save(self.screen)

            # quit if click on display
            if self.screen.mouseLeft:
                return False
            return True

    def quit(self):
        """
        Quit the video stream

        """
        if self.type == PYGAME:
            # from meliae import scanner
            # scanner.dump_all_objects( "kinect_memory_pygame" )
            pygame.display.quit()
        else:
            self.screen.done = True
            self.screen.quit()