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
