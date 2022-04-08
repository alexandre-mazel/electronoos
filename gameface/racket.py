import cv2
import math
import numpy as np
import time

import bleedfacedetector as fd # pip install bleedfacedetector

def runGame():

    # Load the cascade
    face_cascade = cv2.CascadeClassifier('../oia/haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0) #ouvre la webcam
    
    nCptFrame = 0
    timeFps = time.time()
    
    #  info racket
    rx = 320
    ry = 240
    sx = 70
    sy = 30

    while 1:
        
        ret, img = cap.read() # lis et stocke l'image dans frame
        
        #~ img = cv2.resize(img, None, fx=2,fy=2)
        
        #~ img = cv2.flip(img,0) # flip vertic

        # Convert into grayscale

        timeProcess = time.time()
        # Detect faces
        
        if 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # < 0.00000s
            faces = face_cascade.detectMultiScale(gray, 1.1, 10) # 0.05s
        else:
            faces = fd.ssd_detect(img,conf=0.5) # 0.03s
        
        #~ print("DBG: time analysis: %.5fs" % (time.time()-timeProcess))

        if 0:
            # Draw rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
        if 1:
            # the game !
            for (x, y, w, h) in faces:
                dw = int(0.3*w)
                #~ rx = x+int(dw)
                rx = x+w//2
                rx -=sx//2
                ry = y+int(h*0.7)
                #cv2.rectangle(img, (x+dw, y+int(h*0.7)), (x+(w-dw), y+int(h*0.8)), (255, 0, 0), -1)
                
        cv2.rectangle(img, (rx, ry), (rx+sx, ry+sy), (255, 0, 0), -1)
            
            
        # Display the output
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break
            
        nCptFrame += 1
        if nCptFrame == 100:
            duration = time.time()-timeFps
            fps = nCptFrame/duration
            print("INF: fps: %.2ffps" % fps )
            
            nCptFrame = 0
            timeFps = time.time()
            
            
runGame()