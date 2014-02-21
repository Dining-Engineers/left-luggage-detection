__author__ = 'hunter'


from cv2.cv import *

img = LoadImage("res/img.png")
NamedWindow("opencv")
ShowImage("opencv",img)
WaitKey(0)


CreateImage