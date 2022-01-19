# -*- coding: cp1252 -*-

import cv2
import os
import sys

sys.path.append("../../electronoos/alex_pytools")
import face_detector_cv3



class FaceTracker:
    def __init__( self ):
        self.nImageWithFace = 0
        self.nImageLookingAt = 0
        
        self.fdcv3 = face_detector_cv3.facedetector
        
    def update( self, im, t = 0, name = None ):
        """
        receive a new image and analyse it
        - t: image time stamp in sec
        - name: name of the image (filename or ...) for optimisation/caching purpose
        """
        res = self.fdcv3.detect(im)
        cv2.imshow("FaceTracker",im)
        cv2.waitKey(0)
        
        
        
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
    idx = listFiles.find(f)
    while 1:
        f = listFiles[idx]
        im = cv2.imread(f)
        ft.update(im)
        idx += 1

def analyseMovie():
    """
    analyse a movie (mp4)
    """
    
analyseFolder("d:/pitie2/")