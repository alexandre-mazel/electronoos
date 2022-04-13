import cv2
import math
import numpy as np
import random
import sys
import time


sys.path.append("../alex_pytools")
import misctools
            

def recordImages():
    
    zoom = 2

    # Load the cascade
    face_cascade = cv2.CascadeClassifier('../oia/haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0) #ouvre la webcam
    
    screen_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    screen_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print("INF: cam_fps: %s" % cam_fps )
    
    
    nCptFrame = 0
    timeFps = time.time()
    
    while 1:
        ret, img = cap.read() # lis et stocke l'image dans frame
        cv2.imwrite("/tmp/"+misctools.getFilenameFromTime()+".jpg", img )

            
        nCptFrame += 1
        if nCptFrame == 100:
            duration = time.time()-timeFps
            fps = nCptFrame/duration
            print("INF: fps: %.2ffps" % fps ) # 22/24 fps on suface7
            
            nCptFrame = 0
            timeFps = time.time()
            
            
recordImages()