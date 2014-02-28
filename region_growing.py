"""
simple_region_growing modified from tippy implementation
http://www.lengrand.fr/2011/11/simple-region-growing-implementation-in-python/
by Julien Lengrand-Lambert
"""

import sys
import cv
import numpy as np
from utils import rgb2gray

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enque(self, item):
        self.items.insert(0, item)

    def deque(self):
        return self.items.pop()

    def qsize(self):
        return len(self.items)

    def isInside(self, item):
        return item in self.items


def simple_region_growing(img, bbox, threshold=10):
    """
    A (very) simple implementation of region growing.
    Extracts a region of the input image depending on a start position and a stop condition.
    The input should be a single channel 8 bits image and the seed a pixel position (x, y).
    The threshold corresponds to the difference between outside pixel intensity and mean intensity of region.
    In case no new pixel is found, the growing stops.
    Outputs a single channel 8 bits binary (0 or 255) image. Extracted region is highlighted in white.
    """


    img = rgb2gray(img)
    dims = img.shape

    # # CONVERTI IN GRAYSCALE SE RGB!
    #
    # # threshold tests
    # if not isinstance(threshold, int):
    #     raise TypeError("(%s) Int expected!" % sys._getframe().f_code.co_name)
    # elif threshold < 0:
    #     raise ValueError("(%s) Positive value expected!" % sys._getframe().f_code.co_name)
    #
    # # seed tests
    # if not((isinstance(seed, tuple)) and (len(seed) is 2) ) :
    #     raise TypeError("(%s) (x, y) variable expected!" % sys._getframe().f_code.co_name)
    # if (seed[0] or seed[1] ) < 0 :
    #     raise ValueError("(%s) Seed should have positive values!" % sys._getframe().f_code.co_name)
    # elif (seed[0] > dims[0]) or (seed[1] > dims[1]):
    #     raise ValueError("(%s) Seed values greater than img size!" % sys._getframe().f_code.co_name)

    # IMG DI REGISTRAZIONE
    # reg = cv.CreateImage(dims, cv.IPL_DEPTH_8U, 1)
    # cv.Zero(reg)

    reg = np.zeros(shape=img.shape)
    if len(bbox) == 0:
        return reg

    # area of rectangle we don't want to exceed
    pix_area =dims[0]*dims[1]


    # seed is the central region of a 3x3 grid
    seed = [bbox[0]+bbox[2]/3, bbox[1]+bbox[3]/3, bbox[2]/3, bbox[3]/3]

    # parameters
    mean_reg = np.mean(img[seed[1]:seed[1]+seed[3], seed[0]:seed[0]+seed[2]]) #float(img[seed[1], seed[0]])
    # initial region size
    size = img[seed[1]:seed[1]+seed[3], seed[0]:seed[0]+seed[2]].size


    contour = [] # will be [ [[x1, y1], val1],..., [[xn, yn], valn] ]
    contour_val = []
    dist = 0
    # TODO: may be enhanced later with 8th connectivity
    orient = [(1, 0), (0, 1), (-1, 0), (0, -1)] # 4 connectivity

    pixel_to_check = []
    for y in range(seed[1], seed[1]+seed[3]+1):
        for x in range(seed[0], seed[0]+seed[2]):
            pixel_to_check.append([x, y])

    #cur_pix = [seed[0], seed[1]]

    #Spreading
    while dist < threshold and size < pix_area:
        #adding pixels
        try:
            cur_pix = pixel_to_check.pop()
        except:
            break
        for j in range(4):
            #select new candidate
            temp_pix = [cur_pix[0] + orient[j][0], cur_pix[1] + orient[j][1]]

            #check if it belongs to the image
            is_in_img = dims[0] > temp_pix[0] > 0 and dims[1] > temp_pix[1] > 0 #returns boolean

            is_in_bbox = bbox[1] < temp_pix[1] and bbox[1] + bbox[3] > temp_pix[1] and \
                         bbox[0] < temp_pix[0] and bbox[0] + bbox[2] > temp_pix[0]

            #candidate is taken if not already selected before
            if is_in_img and reg[temp_pix[1], temp_pix[0]] == 0:
                contour.append(temp_pix)
                contour_val.append(img[temp_pix[1], temp_pix[0]])
                reg[temp_pix[1], temp_pix[0]] = 150

        #add the nearest pixel of the contour in it
        #dist = abs(int(numpy.mean(contour_val)) - mean_reg) # distanza punto medio temp da punto mean_reg (dei valori in scala di grigio

        dist_list = [abs(i - mean_reg) for i in contour_val]
        dist = min(dist_list)    #get min distance
        #print dist
        index = dist_list.index(min(dist_list)) #mean distance index
        size += 1 # updating region size
        reg[cur_pix[1], cur_pix[0]] = 255

        #updating mean MUST BE FLOAT
        mean_reg = (mean_reg*size + float(contour_val[index]))/(size+1)
        #updating seed

        cur_pix.append(contour[index])

        #removing pixel from neigborhood
        del contour[index]
        del contour_val[index]

    return reg
