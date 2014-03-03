#!/usr/bin/env python

import numpy as np
import cProfile
import calibkinect

from depth_processing import *
from intensity_processing import *
from kinectconnector import *
from video_type import VideoDisplay
from region_growing import simple_region_growing

__author__ = "Andrea Rizzo, Matteo Bruni"
__copyright__ = "Copyright 2014, Dining Engineers"
__credits__ = ["Andrea Rizzo", "Matteo Bruni", "Lorenzo Seidenari",
                    "Lamberto Ballan", "Alberto Del Bimbo"]
__license__ = "GPLv2"
__version__ = "0.0.1"
__maintainer__ = "Andrea Rizzo, Matteo Bruni"
__email__ = "diningengineers@gmail.com, andrearizzo@outlook.com, matteo.bruni@gmail.com"
__status__ = "Development"


def left_luggage_detection():

    # Initialize video display
    screen = VideoDisplay(DISPLAY_TYPE, 2)

    # initialize the camera
    cam = KinectConnector()

    # first loop
    first_run = True

    # DepthProcessing instance
    depth = DepthProcessing(IMAGE_SHAPE)
    # IntensityProcessing instance
    rgb = IntensityProcessing(IMAGE_SHAPE)

    bbox_last_frame_proposals = []

    loop = True
    # main loop
    while loop:

        # get next video frame
        rgb.current_frame = cam.get_image()     # .getNumpy()

        # get next depth frame (11-bit precision)
        # N.B. darker => closer
        # the depth matrix obtained is transposed so we cast the right shape
        depth.current_frame = cam.get_depth_matrix()


        frame_upper_left = rgb.current_frame
        frame_upper_right = depth.current_frame

        loop = screen.show(to_rgb(frame_upper_right), frame_upper_left )
        #loop = screen.show(to_rgb(rgb.foreground_mask_long_term*255), to_rgb(rgb.foreground_mask_short_term*255), frame_bottom_left, frame_bottom_right)

        if not loop:
            screen.quit()



if __name__ == "__main__":

    left_luggage_detection()


