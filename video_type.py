from const import *
import numpy as np

PYGAME = "PYGAME"
SIMPLECV = "SIMPLECV"

if DISPLAY_TYPE == PYGAME:
    import pygame
    import pygame.camera
    from pygame.locals import *
else:
    from SimpleCV import *



class VideoDisplay:

    def __init__(self, v_type):

        if v_type == PYGAME:
            self.screen = pygame.display.set_mode([1280, 960])
            pygame.init()
            self.type = v_type
            pygame.display.set_caption("Left Luggage Detection")

        else:
            self.screen = Display(resolution=(1280, 960))
            self.type = v_type

    def show(self, frame_upper_left, frame_upper_right, frame_bottom_left, frame_bottom_right):

        if self.type == PYGAME:

            frame = np.zeros(shape=(1280, 960, 3))
            frame[:640, :480] = frame_upper_left
            frame[640:, :480] = frame_upper_right
            frame[:640, 480:] = frame_bottom_left
            frame[640:, 480:] = frame_bottom_right

            surface = pygame.surfarray.make_surface(frame)
            self.screen.blit(surface, (0, 0))

            text_color = (255, 0, 0)
            # pick a font you have and set its size
            myfont = pygame.font.SysFont("Comic Sans MS", 15)
            # apply it to text on a label
            label_tl = myfont.render("Video Stream RGB", 1, text_color)
            label_tr = myfont.render("RGB foreground and Detection Proposals", 1, text_color)
            label_bl = myfont.render("DEPTH foreground and Detection Proposals", 1, text_color)
            label_br = myfont.render("Final proposals", 1, text_color)

            # put the label object on the screen at point x=100, y=100
            self.screen.blit(label_tl, (20, 10))
            self.screen.blit(label_tr, (660, 10))
            self.screen.blit(label_bl, (20, 490))
            self.screen.blit(label_br, (660, 490))


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

            return True

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
        if self.type == PYGAME:
            # from meliae import scanner
            # scanner.dump_all_objects( "kinect_memory_pygame" )
            pygame.display.quit()
        else:
            self.screen.done = True
            self.screen.quit()