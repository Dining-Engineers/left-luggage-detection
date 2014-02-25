import freenect
import numpy as np


class KinectConnector():
    """
        Wrapper for the Freenect python libraries
        you can get_image() and get_depth() for separate channel images
    """

    def __init__(self, device_number=0):
        self.device_number = device_number

    # this code was borrowed from
    # https://github.com/amiller/libfreenect-goodies
    def get_image(self):
        """
        Get the next available rgb frame from the kinect, as a numpy array.

        :return: A numpy array, shape:(640, 480, 3)
        :rtype: np.uint8
        """
        video = freenect.sync_get_video(self.device_number)[0]
        #video = video[:, :, ::-1]  # RGB -> BGR
        return video.transpose([1, 0, 2])

    #
    def get_depth(self):
        """
        Get the next available depth frame from the kinect, as a numpy array.
        Low bits in this depth are stripped so it fits in an 8-bit image channel

        :return: A numpy array, shape:(640, 480)
        :rtype: np.uint8
        """
        depth = freenect.sync_get_depth(self.device_number)[0]
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8).transpose()
        return depth


    def get_depth_matrix(self):
        """
        Get the next available depth frame from the kinect, as a numpy array.

        :return: A numpy array, shape:(640, 480)
        :rtype: np.uint16
        """
        # NB: TRASPOSE THE MATRIX
        return freenect.sync_get_depth(self.device_number)[0].T
