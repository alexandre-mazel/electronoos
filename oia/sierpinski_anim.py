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
    
    d = int(dist(p1,p2))/2

    pm = [(p1[0]+p2[0])//2,(p1[1]+p2[1])//2]
    
    a0 = [pm[0]+int(d*math.cos(angle)),pm[1]+int(d*math.sin(angle))]
    a1 = [pm[0]+int(d*math.cos(angle+angleinc)),pm[1]+int(d*math.sin(angle+angleinc))]
    a2 = [pm[0]+int(d*math.cos(angle-angleinc)),pm[1]+int(d*math.sin(angle-angleinc))]
    
    cv2.line(im,pm,a0,color,1)
    cv2.line(im,pm,a1,color,1)
    cv2.line(im,pm,a2,color,1)
    
    colorDim = (color[0]//2,color[1]//2,color[2]//2)
    colorDim = (int(color[0]*0.8),int(color[0]*0.8),int(color[0]*0.8))
    
    
    if 0:
        time.sleep(0.5)
        cv2.imshow("painting", im)
        k = cv2.waitKey(1)
        if k == 27:
            exit(0)
    
    if d > 3:
        #~ sierpin_anim(im,pm,p2,angle,color,angleinc)
        sierpin_anim(im,pm[:],a0[:],angle,colorDim,angleinc)
        sierpin_anim(im,pm[:],a1[:],angle+angleinc,colorDim,angleinc)
        sierpin_anim(im,pm[:],a2[:],angle-angleinc,colorDim,-angleinc)

        


def paint():
    w = 1280
    h = 880

    color = (255,255,255)
    angle = 0
    step = 0.005

    while 1:
        im = np.zeros((h,w,3), np.uint8)
        pt1 = [w//2,h]
        pt2 = [w//2,0]
        #~ angle = math.pi/10
        #~ cv2.line(im,pt1,pt2,color,2)
        sierpin_anim(im,pt1,pt2,-math.pi/2,color,angle)
        cv2.imshow("painting", im)
        #~ print(angle)
        k = cv2.waitKey(1)
        if abs(angle - math.pi*2/3)<step:
            time.sleep(3)
        if k == 27:
            break
            
        angle += step
        if angle>2*math.pi:
            angle -= 2*math.pi
    
paint()
k = cv2.waitKey(0)