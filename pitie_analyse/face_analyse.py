# -*- coding: cp1252 -*-

import cv2
import os
import sys

sys.path.append("../../electronoos/alex_pytools")
import face_detector_cv3
import cv2_tools

sys.path.append("../../face_tools")
import facerecognition_dlib


class FaceTracker:
    def __init__( self ):
        self.nImageWithFace = 0
        self.nImageLookingAt = 0
        
        self.fdcv3 = face_detector_cv3.facedetector
        self.fdl = facerecognition_dlib.faceRecogniser
        
    def update( self, im, t = 0, name = None, bRenderDebug = True ):
        """
        receive a new image and analyse it
        - t: image time stamp in sec
        - name: name of the image (filename or ...) for optimisation/caching purpose
        """
        res = self.fdcv3.detect(im,bRenderBox=False) # ~0.06s on mstab7 on a VGA one face image
        rConfidence, features, faceshape,facelandmark = self.fdl.extractFeaturesFromImg( im, name ) # ~0.7s on mstab7 on a VGA one face image (no cuda) # average other images: 0.48s, 0.17s when no face
        yaw, pitch,roll = facerecognition_dlib.getFaceOrientation(facelandmark)
        if bRenderDebug:
            self.fdcv3.render_res(im, res)
            im=self.fdl._renderFaceInfo(im,facelandmark)
            if abs(yaw)<10.2 and abs(pitch)<10.2:
                cv2_tools.drawHighligthedText("Looking at", (0,0))
            cv2.imshow("FaceTracker",im)
            key=cv2.waitKey(1) # time for image to refresh even if continuously pressing a key
            key=cv2.waitKey(0)
            print(key)
            if key == 27:
                #~ facerecognition_dlib.storedFeatures.save()
                exit(1)
            
        
        
    def getStats( self ):
        pass
        
# class FaceTracker - end

ft = FaceTracker()

def analyseFolder(folder):
    """
    analyse a folder with a bunch of images
    """
    listFiles = sorted(os.listdir(folder))
    f = "camera_viewer_0__1396576150_45_4656.jpg"
    f = "camera_viewer_0__1396576179_12_4987.jpg"
    idx = listFiles.index(f)
    #~ idx -= 122
    #~ idx = 1
    while 1:
        f = listFiles[idx]
        print("%4d/%4d: %s" % (idx,len(listFiles),f) )
        absf = folder + f
        im = cv2.imread(absf)
        ft.update(im,0,absf,bRenderDebug=1)
        idx += 1
        if (idx % 100)==0:
            facerecognition_dlib.storedFeatures.save()
            

def analyseMovie():
    """
    analyse a movie (mp4)
    """
    
analyseFolder("d:/pitie2/")