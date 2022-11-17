import cv2
import math
import numpy as np
import time



cap = cv2.VideoCapture(1) #ouvre la EOS

width = 4000
height = 4000
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FPS,60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


# warmup
for i in range(4):
    ret, img = cap.read() # lis et stocke l'image dans frame

print("img shape: %s" % str(img.shape))

cpt = 0
timeBegin = time.time()
while 1:
    
    ret, img = cap.read() # lis et stocke l'image dans frame
    
    #~ img = cv2.resize(img, None, fx=2,fy=2)
    
    #~ img = cv2.flip(img,0) # flip vertic

    # Display the output
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    
    if key == 27:
        break
        
        
    cpt += 1
    if (cpt %100) == 1:
        fps = cpt/(time.time()-timeBegin)
        print("fps: %.1ffps" % (fps) )
    