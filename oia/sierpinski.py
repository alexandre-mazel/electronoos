import cv2
import numpy as np
import random
import time

def sierpin(im, p1,p2,p3,color=(255,255,255)):
    #~ print("sierpin %s, %s, %s" % (str(p1),str(p2),str(p3)))
    cv2.drawContours(im, [np.array([p1, p2, p3])], 0, (199,171,226), -1)
    
    p1c  = ( (p1[0]+p2[0])//2, (p1[1]+p2[1])//2 )
    p2c = ( (p1[0]+p3[0])//2, (p1[1]+p3[1])//2 )
    p3c = ( (p2[0]+p3[0])//2, (p2[1]+p3[1])//2 )
    
    cv2.drawContours(im, [np.array([p1c, p2c, p3c])], 0, color, -1)
    
    if 0:
        cv2.circle(im,((p1c[0]*2+p2c[0]+p3c[0])//4,(p1c[1]*2+p2c[1]+p3c[1])//4), abs(p1c[0]-p2c[0])//12, (0,0,0), -1)
        cv2.circle(im,((p1c[0]+p2c[0]*2+p3c[0])//4,(p1c[1]*2+p2c[1]+p3c[1])//4), abs(p1c[0]-p2c[0])//12, (0,0,0), -1)
    
    if p1[0]%4==0 and 1:
        time.sleep(0.1)
        cv2.imshow("painting", im)
        k = cv2.waitKey(1)
        if k == 27:
            exit(0)
    
    if abs(p1c[0]-p2c[0])>3: # lazy test
        sierpin(im,p1c, p1, p2c,(116,90,118))
        sierpin(im,p1c, p2, p3c,(120,97,163))
        sierpin(im,p2c, p3, p3c,(121,102,195))
        


def paint():
    w = 1024
    h = 800
    im = np.zeros((h,w,3), np.uint8)
    pt1 = [w//2,0]
    pt2 = [0,h-1]
    pt3 = [w-1,h-1]

    sierpin(im,pt1,pt2,pt3,(213,204,226))
    cv2.imshow("painting", im)
    cv2.waitKey(0)
    
paint()