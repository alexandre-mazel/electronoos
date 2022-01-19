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
        # Discriminative Correlation Filter (with Channel and Spatial Reliability). Tends to be more accurate than KCF but slightly slower. (minimum OpenCV 3.4.2)
        self.tracker = cv2.TrackerCSRT_create() # python -m pip install opencv-contrib-python
        self.bTrackerRunning = False
        self.nCptFrameOnlyOnTracking = 0
        
    def update( self, im, t = 0, name = None, bRenderDebug = True ):
        """
        receive a new image and analyse it
        - t: image time stamp in sec
        - name: name of the image (filename or ...) for optimisation/caching purpose
        """
        res = self.fdcv3.detect(im,bRenderBox=False) # ~0.06s on mstab7 on a VGA one face image
        rConfidence, features, faceshape,facelandmark = self.fdl.extractFeaturesFromImg( im, name ) # ~0.7s on mstab7 on a VGA one face image (no cuda) # average other images: 0.48s, 0.17s when no face
        
        bFaceFound = 0
        bLookAt = 0
        bRenderSquare = 0
            
        
        if facelandmark != []:
            yaw, pitch,roll = facerecognition_dlib.getFaceOrientation(facelandmark)
            print("yaw: %5.2f, pitch: %5.2f,roll: %5.2f" % (yaw, pitch,roll) )
            bLookAt = abs(yaw)<0.55 and abs(pitch)<0.2
            
        
        tracker_box = []
        if self.bTrackerRunning:
            success, tracker_box = self.tracker.update(im)
            print("DBG: tracker success: %s" % success )
            if success:
                if bRenderDebug and bRenderSquare:
                    (x, y, w, h) = [int(v) for v in tracker_box]
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                self.bTrackerRunning = False
            
        if len(res) > 0:     
            startX, startY, endX, endY, confidence = res[0]
            if confidence > 0.55:
                bFaceFound = 1
                self.nCptFrameOnlyOnTracking = 0
            
            if not self.bTrackerRunning: # or confidence > 0.95 # le réapprentissage fait trop de bug
                if confidence > 0.8: # ne surtout pas apprendre sur un visage pas completement sur
                    # reset tracking
                    bb = (startX, startY, endX-startX, endY-startY)
                    self.tracker.init(im,bb)
                    self.bTrackerRunning = True
        else:
            # no face found
            # use info from tracking
            if self.bTrackerRunning:
                self.nCptFrameOnlyOnTracking += 1
                if self.nCptFrameOnlyOnTracking < 6:
                    bFaceFound = 1
                
                if self.nCptFrameOnlyOnTracking > 24:
                    self.bTrackerRunning = False

            
        
        if bFaceFound:
            self.nImageWithFace += 1
            
        if bLookAt:
            self.nImageLookingAt += 1
            
        if bRenderDebug:
            if bRenderSquare:
                self.fdcv3.render_res(im, res)
                im=self.fdl._renderFaceInfo(im,facelandmark)
            if bLookAt:
                facerect = facerecognition_dlib.getFaceRect(facelandmark)
                cv2_tools.drawHighligthedText(im,"Looking at Pepper", (facerect[0] - 100,facerect[1]-50), color_back=(255,0,0) )
            
            cv2_tools.drawHighligthedText(im, "face: %d" % self.nImageWithFace, (30,30))
            cv2_tools.drawHighligthedText(im, "look: %d" % self.nImageLookingAt, (30,60))
            
            
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
    idx += 260
    f="camera_viewer_0__1396576205_70_5284.jpg"  # pour aller sur une frame ou quelques une apres on va la perdre
    #~ f="camera_viewer_0__1396576244_54_5643.jpg" #bug du facedetect puis du tracker
    f="camera_viewer_0__1396576218_27_5382.jpg" # debut d'un pan
    f="camera_viewer_0__1396576320_50_6246.jpg" # bug de tracking sur fausse detection
    f="camera_viewer_0__1396576503_70_7383.jpg" # start to look at pepper
    idx = listFiles.index(f)
    idx -= 10
    #~ idx = 1
    
    #~ camera_viewer_0__1396576251_08_5712.jpg # has a fake face vith 0.77 of confidence
    while idx<len(listFiles):
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