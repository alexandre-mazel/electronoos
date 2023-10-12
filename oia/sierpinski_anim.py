import cv2
import math
import numpy as np
import random
import time

def dist(a,b):
    dx = (b[0]-a[0])
    dy = (b[1]-a[1])
    return math.sqrt(dx*dx+dy*dy)

def sierpin_anim(im, p1, p2, angle, color, angleinc):
    #~ print("sierpin %s, %s, %s" % (str(p1),str(p2),str(p3)))

    #~ cv2.line(im,p1,p2,color,2)


    
    if p1[0]%4==0 and 1:
        time.sleep(0.1)
        cv2.imshow("painting", im)
        k = cv2.waitKey(1)
        if k == 27:
            exit(0)
    
    d = int(dist(p1,p2))/2

    pm = [(p1[0]+p2[0])//2,(p1[1]+p2[1])//2]
    
    a1 = [pm[0]+int(d*math.cos(angle)),pm[1]+int(d*math.sin(angle))]
    a2 = [pm[0]-int(d*math.cos(angle)),pm[1]+int(d*math.sin(angle))]
    
    cv2.line(im,pm,a1,color,2)
    cv2.line(im,pm,a2,color,2)
    
    colorDim = (color[0]//2,color[1]//2,color[2]//2)
    
    
    if 1:
        time.sleep(1)
        cv2.imshow("painting", im)
        k = cv2.waitKey(1)
        if k == 27:
            exit(0)
    
    if d > 50:
        #~ sierpin_anim(im,pm,p2,angle,color,angleinc)
        sierpin_anim(im,pm[:],a1[:],angle+angleinc,colorDim,angleinc)
        sierpin_anim(im,pm[:],a2[:],angle-angleinc,colorDim,-angleinc)

        


def paint():
    w = 1024
    h = 800
    im = np.zeros((h,w,3), np.uint8)
    pt1 = [w//2,h//2]
    pt2 = [w//2,0]

    color = (255,255,255)
    angle = math.pi/4
    #~ angle = math.pi/10
    cv2.line(im,pt1,pt2,color,2)
    sierpin_anim(im,pt1,pt2,-angle,color, angle)
    cv2.imshow("painting", im)
    print("finito")
    cv2.waitKey(0)
    
paint()