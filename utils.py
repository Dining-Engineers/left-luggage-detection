import numpy as np
from pykdtree.kdtree import KDTree


def to_rgb(im):
    # This should be fsater than 1, as we only
    # truncate to uint8 once (?)
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret


def query_kdtree(data_tree, data_query):
    kdtree = KDTree(data_tree)
    dist, idx = kdtree.query(data_query)
    return dist, idx


def get_center_area_from_rect(rect):
    #print "rect: ", rect
    """ coordinates rect center """
    cx = rect[0] + rect[2] / 2
    cy = rect[1] + rect[3] / 2
    area = area = rect[2] * rect[3]
    return cx, cy, area


# (s[0], s[1]), (s[0]+s[2], s[1]+s[3])
def boxes_intersect(bbox1, bbox2):
    """ Return if two rect overlap """
    return ((np.abs(bbox1[0]-bbox2[0])*2) < (bbox1[2]+bbox2[2])) and ((np.abs(bbox1[1]-bbox2[1])*2) < (bbox1[3]+bbox2[3]))


def boxes_intersect2(bbox1, bbox2):
    """ Return if two rect overlap """
    def in_range(value, min, max):
        return (value >= min) and (value <= max)

    x_overlap = in_range(bbox1[0], bbox2[0], bbox2[0]+bbox2[2]) or in_range(bbox2[0], bbox1[0], bbox1[0]+bbox1[2])
    y_overlap = in_range(bbox1[1], bbox2[1], bbox2[1]+bbox2[3]) or in_range(bbox2[1], bbox1[1], bbox1[1]+bbox1[3])

    return x_overlap and y_overlap


def rect_similarity(rect1, rect2):
    """Check whatever two rect are similar with a tolerance of 10px in center distance and 0.1 in area ratio """
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


def rect_similarity2(r1, r2):
    """ Return if r1 and r2 satisfy overlapping criterion """
    if boxes_intersect(r1, r2):
        # return similarity
        if similarity_measure_rect(r1, r2) > 0.5:
            return True
        return False
    return False


def similarity_measure_rect(bbox_test, bbox_target):

    def gen_box(bbox):
        from shapely.geometry import box
        box = box(bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3])
        return box

    bbtest = gen_box(bbox_test)
    bbtarget = gen_box(bbox_target)

    return bbtarget.intersection(bbtest).area/bbtarget.union(bbtest).area

