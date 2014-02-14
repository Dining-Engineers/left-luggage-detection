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


def rect_similarity4(rect1, rect2):
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
    #print "rect: ", rect
    """ coordinates rect center """
    cx = rect[0] + rect[2] / 2
    cy = rect[1] + rect[3] / 2
    area = area = rect[2] * rect[3]
    return cx, cy, area


# (s[0], s[1]), (s[0]+s[2], s[1]+s[3])
def boxes_intersect(bbox1, bbox2):
    return ((np.abs(bbox1[0]-bbox2[0])*2) < (bbox1[2]+bbox2[2])) and ((np.abs(bbox1[1]-bbox2[1])*2) < (bbox1[3]+bbox2[3]))


def rect_similarity2(r1, r2):
    if boxes_intersect(r1,r2):

        left = max(r1[0], r2[0])
        right = min(r1[0]+r1[2], r2[0]+r2[2])
        bottom = max(r1[1], r2[1])
        top = min(r1[1]+r1[3], r2[1]+r2[3])
        intersection = (top-bottom)*(right-left)
        r1_area = r1[2]*r1[3]
        r2_area = r2[2]*r2[3]
        union = r1_area + r2_area - intersection
        # return similarity
        if intersection/union > 0.5:
            print "vero"
            return True
        print "falso"
        return False
    print "falso"
    return False


def rect_similarity(bbox_test,bbox_target):

    def gen_box(bbox):
        from shapely.geometry import box
        box = box(bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3])
        return box

    bbtest=gen_box(bbox_test)
    bbtarget=gen_box(bbox_target)

    if bbtarget.intersection(bbtest).area/bbtarget.union(bbtest).area > 0.5:
        return True
    else:
        return False