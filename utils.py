import numpy as np
from pykdtree.kdtree import KDTree


def to_rgb1a(im):
    # This should be fsater than 1, as we only
    # truncate to uint8 once (?)
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] =  ret[:, :, 1] =  ret[:, :, 0] =  im
    return ret


def query_kdtree(data_tree, data_query):
    kdtree = KDTree(data_tree)
    dist, idx = kdtree.query(data_query)
    return dist, idx


def rect_similarity(rect1, rect2):
    cx1, cy1, a1 = get_center_area_from_rect(rect1)
    cx2, cy2, a2 = get_center_area_from_rect(rect2)

    c_diff = np.linalg.norm(np.array([cx1, cy1]) - np.array([cx2, cy2]))
    a_ratio = a1/a2
    if c_diff < 10:
        if np.abs(a_ratio-0.1) <= 1:
            return True
        else:
            return False
    else:
        return False


def get_center_area_from_rect(rect):
    print "rect: ", rect
    """ coordinates rect center """
    cx = rect[0] + rect[2] / 2
    cy = rect[1] + rect[3] / 2
    area = area = rect[2] * rect[3]
    return cx, cy, area