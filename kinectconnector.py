import freenect
import numpy as np


class KinectConnector():
    """
    **SUMMARY**

    This is an experimental wrapper for the Freenect python libraries
    you can getImage() and getDepth() for separate channel images

    """
    def __init__(self, device_number=0):
        self.device_number = device_number

    # this code was borrowed from
    # https://github.com/amiller/libfreenect-goodies
    def get_image(self):
        video = freenect.sync_get_video(self.device_number)[0]
        #video = video[:, :, ::-1]  # RGB -> BGR
        return video.transpose([1, 0, 2])

    # low bits in this depth are stripped so it fits in an 8-bit image channel
    def get_depth(self):
        depth = freenect.sync_get_depth(self.device_number)[0]
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8).transpose()
        return depth

    # we're going to also support a higher-resolution (11-bit) depth matrix
    # if you want to actually do computations with the depth
    def get_depth_matrix(self):
        return freenect.sync_get_depth(self.device_number)[0]
