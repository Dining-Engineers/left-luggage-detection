# Depth holes in openfreenect have maximum value in 11 bit
DEPTH_HOLE_VALUE = 2**11-1

# Background (Depth) Paramethers
BG_RUN_AVG_LRATE = 0.001
BG_RUN_AVG_OPENING_KSIZE = 5
BG_MASK_THRESHOLD = 3

# Background Zivkovich (RGB) Paramethers
BG_ZIV_LONG_LRATE = 0.001
BG_ZIV_SHORT_LRATE = 0.01
BG_ZIV_HIST = 1
BG_ZIV_THRESH = 900
BG_ZIV_OPEN_KSIZE = 5       # not used

# Aggregator parameters
AGG_RGB_MAX_E = 15          # number of frames after which a pixel is considered an left item
AGG_RGB_PENALTY = 1
AGG_DEPTH_MAX_E = 30          # number of frames after which a pixel is considered an left item
AGG_DEPTH_PENALTY = 1
AGG_DEPTH_BBOX = 5