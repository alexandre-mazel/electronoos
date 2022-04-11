# -*- coding: cp1252 -*-

import cv2
import os
import sys
import time

sys.path.append("../../electronoos/alex_pytools")
import face_detector_cv3
import cv2_tools

sys.path.append("../../face_tools")
import facerecognition_dlib

def analyseFolder(folder):
    """
    analyse a folder with a bunch of images
    """
    bSpeedTest = 1
    bSpeedTest = 0
    
    
    bRenderDebug = 1
    bRenderDebug = 0
    
    fdl = facerecognition_dlib.faceRecogniser
    
    
    
    timeBegin = time.time()
    
    listFiles = sorted(os.listdir(folder))
    
    bRender = 0
    
    idx_end = 0
    
    
    idx = 0
    
    while idx<len(listFiles):
        f = listFiles[idx]
        print("%4d/%4d: %s" % (idx,len(listFiles),f) )
        if not "jpg" in f:
            idx += 1
            continue
        absf = folder + f
        im = cv2.imread(absf)
        
        rConfidence, features, faceshape,facelandmark = fdl.extractFeaturesFromImg( im, absf, bForceRecompute = 0 ) # ~0.7s on mstab7 on a VGA one face image (no cuda) # average other images: 0.48s, 0.17s when no face

        if bRender:
            cv2.imshow("FaceTracker",im)
            key=cv2.waitKey(5) # time for image to refresh even if continuously pressing a key
            #~ key=cv2.waitKey(0)
            if key == 27:
                break

        idx += 1
        
        if (idx %100) == 0:
            facerecognition_dlib.storedFeatures.save()

                
        if idx_end != 0 and idx>idx_end:
            break

    
    facerecognition_dlib.storedFeatures.save()
# analyseFolder - end
    
if os.name == "nt":
    strPath = "d:/face_swap_test/f2/"
analyseFolder(strPath)