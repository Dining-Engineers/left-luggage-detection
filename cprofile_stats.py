import profile
import pstats
#from profile_fibonacci_memoized import fib, fib_seq

# Read all 5 stats files into a single object
stats = pstats.Stats('kinect_pygame_5_marzo_NOT.profile')

stats.strip_dirs()
stats.sort_stats('cumulative')

# limit output to lines with "(fib" in them
stats.print_stats()#'\(fib')

# print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
# 1    0.175    0.175    1.644    1.644 left-luggage-detection.py:24(left_luggage_detection)
# # Read all 5 stats files into a single object
# stats = pstats.Stats('kinect_pygame_5_marzo.profile')
#
# stats.strip_dirs()
# stats.sort_stats('cumulative')
#
# # limit output to lines with "(fib" in them
# stats.print_stats()#'\(fib')