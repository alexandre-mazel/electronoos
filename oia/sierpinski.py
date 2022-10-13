import cv2
import numpy as np
import random

def sierpin(im, p1,p2,p3):
    #~ print("sierpin %s, %s, %s" % (str(p1),str(p2),str(p3)))
    cv2.drawContours(im, [np.array([p1, p2, p3])], 0, (0,255,0), -1)
    
    p1c  = ( (p1[0]+p2[0])//2, (p1[1]+p2[1])//2 )
    p2c = ( (p1[0]+p3[0])//2, (p1[1]+p3[1])//2 )
    p3c = ( (p2[0]+p3[0])//2, (p2[1]+p3[1])//2 )
    
    cv2.drawContours(im, [np.array([p1c, p2c, p3c])], 0, (255,255,255), -1)
    cv2.imshow("painting", im)
    k = cv2.waitKey(1)
    if k == 27:
        exit(0)
    
    if abs(p1c[0]-p2c[0])>4: # lazy test
        sierpin(im,p1c, p1, p2c)
        sierpin(im,p1c, p2, p3c)
        sierpin(im,p2c, p3, p3c)

        


def paint():
    
    w = 640
    h = 480
    im = np.zeros((h,w,3), np.uint8)
    pt1 = [w//2,0]
    pt2 = [0,h-1]
    pt3 = [w-1,h-1]
    cpt = 128
    while 1:
        sierpin(im,pt1,pt2,pt3)
        cv2.imshow("painting", im)
        k = cv2.waitKey(0)
        break
        if k == 27:
            break
            
        cpt += 15
    
    
paint()