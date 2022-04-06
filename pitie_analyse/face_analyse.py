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
import face_detector
import emotion_detector


class FaceTracker:
    def __init__( self ):
        self.nImageAnalysed = 0
        self.nImageWithFace = 0
        self.nImageLookingAt = 0
        self.nImageSmile = 0
        self.nImageHappy = 0
        
        self.fdcv3 = face_detector_cv3.facedetector
        self.fdl = facerecognition_dlib.faceRecogniser
        self.haar_face_detect = face_detector.FaceDetectOpenCV(bVerbose=True)
        self.haar_profile_detect = face_detector.FaceDetectOpenCV(bVerbose=True,strCascadeFile="haarcascade_profileface.xml")
        self.haar_smile_ndev = face_detector.FaceDetectOpenCV(bVerbose=True,strCascadeFile="haarcascade_smile.xml")
        # Discriminative Correlation Filter (with Channel and Spatial Reliability). Tends to be more accurate than KCF but slightly slower. (minimum OpenCV 3.4.2)
        self.tracker = cv2.TrackerCSRT_create() # python -m pip install opencv-contrib-python OR export PYTHONPATH=/usr/local/lib/python3.8/site-packages/cv2/python-3.8/:$PYTHONPATH 
        self.bTrackerRunning = False
        self.nCptFrameOnlyOnTracking = 0
        self.nCptFrameSinceRestartTracking = 0
        
        self.timefacedlib = 0
        self.timefacedetectcv3 = 0
        self.timehaar = 0
        
        
    def detectSmileInImage( self, im, faces ):
        #~ faces from = face_cascade.detectMultiScale(gray, 1.3, 5)
        # untested
        for (x, y, w, h) in faces:
            roi_gray = im[y:y + h, x:x + w]
            smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), ((sx + sw), (sy + sh)), (0, 0, 255), 2)
        return frame

        
    def update( self, im, t = 0, name = None, bRenderDebug = True ):
        """
        receive a new image and analyse it
        - t: image time stamp in sec
        - name: name of the image (filename or ...) for optimisation/caching purpose
        return 0 if user want to exit
        """
        if im is None or im.shape[0] < 1:
            print("WRN: this image is empty!!!")
            return 1
            
        self.nImageAnalysed += 1
        t = time.time()
        res = self.fdcv3.detect(im,bRenderBox=False,confidence_threshold=0.1) # ~0.06s on mstab7 on a VGA one face image
        if self.nImageAnalysed > 1: self.timefacedetectcv3 += time.time() - t
        t = time.time()
        rConfidence, features, faceshape,facelandmark = self.fdl.extractFeaturesFromImg( im, name, bForceRecompute = 0 ) # ~0.7s on mstab7 on a VGA one face image (no cuda) # average other images: 0.48s, 0.17s when no face
        if self.nImageAnalysed > 1: self.timefacedlib += time.time() - t
        
        bFaceFound = 0
        bLookAt = 0
        bSmile = 0
        bHappy = 0
        bRenderSquare = 1
        bActivateTracker = 1
            
         
        rSmile = 0
        rRatioSmile = 0
        if facelandmark != []:
            yaw, pitch,roll = facerecognition_dlib.getFaceOrientation(facelandmark)
            print("yaw: %5.2f, pitch: %5.2f,roll: %5.2f" % (yaw, pitch,roll) )
            bLookAt = abs(yaw)<0.55 and abs(pitch)<0.2
            rSmile, rRatioSmile = facerecognition_dlib.getSmileAmount(facelandmark)
            print("rSmile: %.2f (ratio: %.2f)" % (rSmile,rRatioSmile) )
            if rSmile > 0.34: bSmile = 1
            

        detectedEmotions = emotion_detector.detectEmotion( im )
        if detectedEmotions != []:
            if bRenderDebug: emotion_detector.renderEmotion(im,detectedEmotions,40)
            nEmoID = detectedEmotions[0][1]
            rConfEmo = detectedEmotions[0][2]
            if nEmoID == 1 and rConfEmo > 0.6:
                bHappy = 1
        
            
        
        tracker_box = []
        if self.bTrackerRunning:
            success, tracker_box = self.tracker.update(im)
            print("DBG: tracker success: %s" % success )
            if success:
                if bRenderDebug and bRenderSquare and 1:
                    (x, y, w, h) = [int(v) for v in tracker_box]
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                self.bTrackerRunning = False
            
        if len(res) > 0:     
            startX, startY, endX, endY, confidence = res[0]
            if confidence > 0.55:
                bFaceFound = 1
                self.nCptFrameOnlyOnTracking = 0
            
            if not self.bTrackerRunning or (confidence > 0.95 and self.nCptFrameSinceRestartTracking > 20):
                # or confidence > 0.95 : le réapprentissage fait trop de bug
                # mais de pas réapprendre c'est dommage aussi.
                if (confidence > 0.95 and self.nCptFrameSinceRestartTracking > 20):
                    print("DBG: forcing a tracker reset")
                if confidence > 0.8: # ne surtout pas apprendre sur un visage pas completement sur
                    # reset tracking
                    bb = (startX, startY, endX-startX, endY-startY)
                    self.tracker.init(im,bb)
                    self.bTrackerRunning = True
                    self.nCptFrameSinceRestartTracking = 0
            else:
                self.nCptFrameSinceRestartTracking += 1
                    
        facesProfile = []
        facesHaar = []
        if not bFaceFound or 0:
            # try profile
            t = time.time()
            #~ facesHaar=self.haar_face_detect.detect_face(im,bCompleteSearch=True)
            #~ facesProfile=self.haar_profile_detect.detect_face(im,bCompleteSearch=False)
            #~ assert(len(resProfile)==0)
            if self.nImageAnalysed > 1: self.timehaar += time.time() - t
            pass
                    
        if not bFaceFound and bActivateTracker:
            # no face found
            # use info from tracking
            
            if self.bTrackerRunning:
                self.nCptFrameOnlyOnTracking += 1
                
                # if we have a match between a face, even with a low confidence and a tracker, we keep it.
                if len(res) > 0 and tracker_box != []:
                    # tracker box is origin/size, and rect are origin/end
                    trackerbox_to_rect = (tracker_box[0],tracker_box[1],tracker_box[0]+tracker_box[2],tracker_box[1]+tracker_box[3])
                    res_inter = face_detector_cv3.findCloser(res,trackerbox_to_rect)
                    if res_inter != []:
                        intersection, original_rect, ratio_inter, confidence_of_rect_with_intersection = res_inter
                        if ratio_inter > 0.3 and confidence_of_rect_with_intersection > 0.13:
                            # we had a match, so this tracker information seems good, let keep it
                            self.nCptFrameOnlyOnTracking //= 2
                            print("DBG: FaceTracker.update: tracker match poor detect, but validating it, nCptFrameOnlyOnTracking: %d" % self.nCptFrameOnlyOnTracking )
                        
                if self.nCptFrameOnlyOnTracking < 6:
                    bFaceFound = 1
                
                if self.nCptFrameOnlyOnTracking > 24:
                    self.bTrackerRunning = False

            
        
        if bFaceFound:
            self.nImageWithFace += 1
            
        if bLookAt:
            self.nImageLookingAt += 1
            
        if bSmile:
            self.nImageSmile += 1

        if bHappy:
            self.nImageHappy += 1
            
        if bRenderDebug:
            #~ im = cv2.resize(im,(0,0),fx=2,fy=2)
            if bRenderSquare:
                self.fdcv3.render_res(im, res)
                im = self.fdl._renderFaceInfo(im,facelandmark,bRenderNumber=False,nAddOffset=-80)
                if facesHaar != []: im = face_detector.drawRectForFaces( im, facesHaar, color = (255,255,0) )
                if facesProfile != []: im = face_detector.drawRectForFaces( im, facesProfile )
                pass
            if bLookAt:
                facerect = facerecognition_dlib.getFaceRect(facelandmark)
                cv2_tools.drawHighligthedText(im,"Looking at Pepper", (facerect[0] - 100,facerect[1]-50), color_back=(255,0,0) )
            
            cv2_tools.drawHighligthedText(im, "analysed: %d" % self.nImageAnalysed, (30,30))
            cv2_tools.drawHighligthedText(im, "face: %d" % self.nImageWithFace, (30,60))
            cv2_tools.drawHighligthedText(im, "look: %d" % self.nImageLookingAt, (30,90))
            cv2_tools.drawHighligthedText(im, "smile: %d" % self.nImageSmile, (30,120))
            cv2_tools.drawHighligthedText(im, "happy: %d" % self.nImageHappy, (30,150))
            cv2_tools.drawHighligthedText(im, "rSmile: %.2f (ratio: %.2f)" % (rSmile,rRatioSmile), (30,180))
            
            
            im = cv2.resize(im,(0,0),fx=2,fy=2)
            cv2.imshow("FaceTracker",im)
            key=cv2.waitKey(1) # time for image to refresh even if continuously pressing a key
            key=cv2.waitKey(0)
            print(key)
            if key == 27:
                #~ facerecognition_dlib.storedFeatures.save()
                return 0
        return 1
            
        
        
    def getStats( self ):
        """
        return nbr analysed, nbr face, nbr look
        """
        return self.nImageAnalysed, self.nImageWithFace, self.nImageLookingAt, self.nImageSmile, self.nImageHappy
        
    def getAvgDuration(self):
        n = self.nImageAnalysed - 1
        print("INF: FaceTracker.getAvgDuration per frame:")
        print( "    face fdcv2: %.3fs" % (self.timefacedetectcv3/n) )
        print( "    face dlib : %.3fs" % (self.timefacedlib/n) )
        print( "    face haar : %.3fs" % (self.timehaar/n) )
        
        return self.timefacedetectcv3/n,self.timefacedlib/n,self.timehaar/n
        
        
# class FaceTracker - end

ft = FaceTracker()

def analyseFolder(folder):
    """
    analyse a folder with a bunch of images
    """
    bSpeedTest = 1
    bSpeedTest = 0
    
    
    bRenderDebug = 1
    bRenderDebug = 0
    
    
    
    timeBegin = time.time()
    
    listFiles = sorted(os.listdir(folder))
    f = "camera_viewer_0__1396576150_45_4656.jpg"
    f = "camera_viewer_0__1396576179_12_4987.jpg"
    #~ idx = listFiles.index(f)
    #~ idx -= 122
    #~ idx = 1
    #~ idx += 260
    f="camera_viewer_0__1396576205_70_5284.jpg"  # pour aller sur une frame ou quelques une apres on va la perdre
    #~ f="camera_viewer_0__1396576244_54_5643.jpg" #bug du facedetect puis du tracker
    #~ f="camera_viewer_0__1396576218_27_5382.jpg" # debut d'un pan
    #~ f="camera_viewer_0__1396576320_50_6246.jpg" # bug de tracking sur fausse detection
    f="camera_viewer_0__1396576503_70_7383.jpg" # start to look at pepper
    #~ f= "camera_viewer_0__1396576535_31_7629.jpg" # side face with hair => not found [OK]
    #~ f = "camera_viewer_0__1396576341_74_6448.jpg" # tres mauvaise detection serie
    #~ f = "camera_viewer_0__1396576342_16_6453.jpg" # direct sur la mauvaise detection
    f = "camera_viewer_0__1396576519_11_7505.jpg" # sophie regard par en dessous
    #~ idx = listFiles.index(f)
    #~ idx -= 10
    #~ idx = 1
    idx = 0
    
    
    #######################
    # pitie4
    idx = 145 # pour un humain
    idx = 2061 # pour un visage (pas forcément le premier)
    idx = 2088 # pour un regard vers le robot (mais regard en coin)
    idx = 0
    #~ idx = 18670
    
    # result on all images:
    """
    nImageAnalysed : 18716
    nImageWithFace : 7139 ( 38.1%)
    nImageLookingAt: 1644 (  8.8%) ( 23.0%)
    """

    #######################    
    # pitie5
    idx = 0
    idx = 2985 # regard en coin
    idx = 3019 # autre regard en coin
    idx = 3100 # bug du tracker qui part sur la main
    idx = 3448 # regard face

    
    # result on all images:
    """
    nImageAnalysed : 7203
    nImageWithFace : 1306 ( 18.1%)
    nImageLookingAt: 3 (  0.0%) (  0.2%)
    """
    
    #######################    
    # img_pitie/2022_03_11_9h - regard tout le temps en coin.
    # a partir de 0.35 inclus, c'est un sourire pour elle
    idx = 0
    #~ idx = 950 # presque debut interaction
    idx = 1050 # debut interaction
    #~ idx = 1375 # exemple de regard en coin
    #~ idx = 1750
    
    # result on all images:
    """
    # 2022/03/23: redone with enhancement on smile detection:
    nImageAnalysed : 7127
    nImageWithFace : 2665 ( 37.4%)
    nImageLookingAt: 104 (  1.5%) (  3.9%)
    nImageSmile    : 326 (  4.6%) ( 12.2%)
    """
    
    #######################    
    # img_pitie/2022_03_04_00h bien souriante ?
    if 1:
        idx = 0
        idx = 500 # ff
        idx = 600 # bug de tracking qui commence sur un demi visage et reste coincé dessus - corrigé avec nCptFrameSinceRestartTracking
        idx = 890 # int
    
    idx = 0
    
    # result on all images:
    """
    nImageAnalysed : 9826
    nImageWithFace : 6438 ( 65.5%)
    nImageLookingAt: 1462 ( 14.9%) ( 22.7%)
    nImageSmile    : 3578 ( 36.4%) ( 55.6%)
    
    # 2022/03/23: redone with enhancement on smile detection:
    nImageAnalysed : 9826
    nImageWithFace : 6438 ( 65.5%)
    nImageLookingAt: 1462 ( 14.9%) ( 22.7%)
    nImageSmile    : 2747 ( 28.0%) ( 42.7%)
    nImageHappy    : 2182 ( 22.2%) ( 33.9%)
    """
    
    #######################    
    # img_pitie/2022_03_25_9h/m1 comparaison avec annotation manuelle Clara
    if 1:
        idx = 0
    
    """
    # computed on 2022/03/23:
    # m1:
    nImageAnalysed : 2993
    nImageWithFace : 2128 ( 71.1%)
    nImageLookingAt: 120 (  4.0%) (  5.6%)
    nImageSmile      : 871 ( 29.1%) ( 40.9%)
    nImageHappy    : 416 ( 13.9%) ( 19.5%)
    
    # m2:
    nImageAnalysed : 3817
    nImageWithFace : 3229 ( 84.6%)
    nImageLookingAt: 187 (  4.9%) (  5.8%)
    nImageSmile      : 677 ( 17.7%) ( 21.0%)
    """
    

    
    
    if bSpeedTest: idx = 0
    if bSpeedTest: bRenderDebug = 0
    
    #~ camera_viewer_0__1396576251_08_5712.jpg # has a fake face vith 0.77 of confidence
    while idx<len(listFiles):
        f = listFiles[idx]
        print("%4d/%4d: %s" % (idx,len(listFiles),f) )
        if not "jpg" in f:
            idx += 1
            continue
        absf = folder + f
        im = cv2.imread(absf)
        if bSpeedTest: absf = None
        bRet = ft.update(im,0,absf,bRenderDebug=bRenderDebug)
        if not bRet:
            break
        idx += 1
        if (idx % 100)==0:
            facerecognition_dlib.storedFeatures.save()
        
        if bSpeedTest:
            if idx > 30:
                ft.getAvgDuration()
                duration = time.time() - timeBegin
                print("    Avg time:   %.2fs" % (duration/idx) )
                print("    Total time: %.1fs" % (duration) )
                break

    facerecognition_dlib.storedFeatures.save()                
    nImageAnalysed, nImageWithFace, nImageLookingAt, nSmile, nHappy = ft.getStats()
    print("nImageAnalysed : %d" % (nImageAnalysed) )
    print("nImageWithFace : %d (%5.1f%%)" % (nImageWithFace,100*nImageWithFace/nImageAnalysed) )
    print("nImageLookingAt: %d (%5.1f%%) (%5.1f%%)" % (nImageLookingAt,100*nImageLookingAt/nImageAnalysed,100*nImageLookingAt/nImageWithFace) )
    print("nImageSmile    : %d (%5.1f%%) (%5.1f%%)" % (nSmile,100*nSmile/nImageAnalysed,100*nSmile/nImageWithFace) )
    print("nImageHappy    : %d (%5.1f%%) (%5.1f%%)" % (nHappy,100*nHappy/nImageAnalysed,100*nHappy/nImageWithFace) )


"""
result:
mstab7:
    face fdcv2: 0.021s
    face dlib : 0.494s
    face haar : 0.006s
    Avg time:   0.55s
    Total time: 16.5s
    
bigA:
    face fdcv2: 0.087s
    face dlib : 0.285s
    face haar : 0.131s
    Avg time:   0.57s
    Total time: 17.6s
    
champion:
    cpu mode (card removed):
        face fdcv2: 0.008s # seems not to use gpu
        face dlib : 0.000s # impossible to measure: fail without gpu (with my current compilation)
        face haar : 0.044s # seems not to use gpu
        Avg time:   0.06s
        Total time: 1.7s

    gpu mode:
        face fdcv2: 0.009s
        face dlib : 0.109s
        face haar : 0.044s
        Avg time:   0.20s
        Total time: 5.9s
"""
            

def analyseMovie():
    """
    analyse a movie (mp4)
    """
    pass
    
if os.name == "nt":
    strPath = "d:/pitie5/"
    #~ strPath = "d:/img_pitie/2022_03_11_9h/"
    strPath = "d:/img_pitie/2022_03_04_00h/"
    strPath = "d:/img_pitie/2022_03_25_9h/m2/"
else:
    strPath = os.path.expanduser("~/pitie4/")
analyseFolder(strPath)