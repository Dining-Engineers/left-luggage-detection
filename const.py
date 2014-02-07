# Depth holes in openfreenect has maximum value in 11 bit
DEPTH_HOLE_VALUE = 2**11-1

# Background (Depth) Paramethers
BG_RUN_AVG_LRATE = 0.001
BG_RUN_AVG_OPENING_KSIZE = 5
BG_MASK_THRESHOLD = 2

# Background Zivkovich (RGB) Paramethers
BG_ZIV_LRATE = 0.001
BG_ZIV_HIST = 1
BG_ZIV_THRESH = 900
BG_ZIV_OPEN_KSIZE = 5