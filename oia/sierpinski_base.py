import cv2
import numpy as np
import random

def paint():
    w = 640
    h = 480
    im = np.zeros((h,w,3), np.uint8)
    pt1 = [0,0]
    pt2 = [0,0]
    pt3 = [0,0]
    cpt = 128
    while 1:
        pt1[0] = random.randint(0,w-1)
        pt1[1] = random.randint(0,h-1)
        pt2[0] = random.randint(0,w-1)
        pt2[1] = random.randint(0,h-1)
        pt3[0] = random.randint(0,w-1)
        pt3[1] = random.randint(0,h-1)
        triangle_cnt = np.array( [pt1, pt2, pt3] )
        cv2.drawContours(im, [triangle_cnt], 0, (0,cpt%255,0), -1)

        cv2.imshow("painting", im)
        k = cv2.waitKey(500)
        if k == 27:
            break	 
        cpt += 15
        
paint()
