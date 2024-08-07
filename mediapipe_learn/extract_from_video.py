import cv2
import mediapipe_fx
import mediapipe as mp

from mediapipe_fx import computeBaryChest, landmarkToListPoints

import os
import time

def myLandmarksDraw( img, poseLandmarkerResult ):
    img2 = img.copy()
    result = poseLandmarkerResult.pose_landmarks
    h,w = img.shape[:2]
    for skel in result:
        for num, pt in enumerate(skel):
            ptint = ( int(pt.x*w),int(pt.y*h))
            cv2.circle( img2,ptint, 10, (255,0,0))
            cv2.putText( img2, "%d"%num, ptint,  fontFace = cv2.FONT_HERSHEY_DUPLEX, fontScale = 1.0,color = (255,255,0), thickness = 1 )
    return img2

def exportResult( poseLandmarkerResult, file ):
    result = poseLandmarkerResult.pose_landmarks
    for skel in result:
        s = ""
        for pt in skel:
            s += "[%s,%s,%s,%5.2f,%5.2f]," % (pt.x,pt.y,pt.z,pt.presence,pt.visibility)
        #~ print(s)
        file.write(s+"\n")
        break # quit after first skeleton

def extractFromVideo( strFilename, detector, bOutputSkel = 1 ):
    print( "INF: extractFromVideo: processing '%s'" % strFilename )
    nNumFrame = 0
    cap = cv2.VideoCapture( strFilename )
    # Check if camera opened successfully
    if not cap.isOpened():
      print("ERR: extractFromVideo: Error opening video file '%s'" % strFilename )
      return
      
    if bOutputSkel: outfile = open(strFilename.replace(".mkv",".skl").replace(".mp4",".skl"),"wt")
    
    prevBaryChest = [0.5,0.5,0.5]
 
    while(cap.isOpened()):
            
        ret, img = cap.read()
        if not ret:
            break
            
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        imagebuf = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        detection_result = detector.detect(imagebuf)
        print("detection_result:" + str(detection_result) );
        print("detection_result.pose_landmarks:" + str(detection_result.pose_landmarks) );
        print("detection_result len pose_landmarks: %s" % len(detection_result.pose_landmarks) );
        
        if len(detection_result.pose_landmarks) < 1:
            continue
        
        
        baryChest = computeBaryChest(landmarkToListPoints(detection_result.pose_landmarks))
        print("baryChest: %s" % baryChest )
        if baryChest[0] < 0.2 or baryChest[0] > 0.8:
            print("DBG: bary not centered !!!")
            # blackened the skeleton on the side
            imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            h,w = imgRGB.shape[:2]
            if baryChest[0] > 0.8:
                x1 = int((baryChest[0]-0.05)*w)
                x2 = w
            else:
                x1 = 0
                x2 = int((baryChest[0]+0.05)*w)
                
            imgRGB[:,x1:x2]= (0,0,0)
            imagebuf = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
            detection_result = detector.detect(imagebuf)
            baryChest = computeBaryChest(landmarkToListPoints(detection_result.pose_landmarks))
            print("baryChest (2): %s" % baryChest )
            if baryChest[0] < 0.2 or baryChest[0] > 0.8:
                print("DBG: skipping !!! \n")
        
        
        if bOutputSkel: exportResult(detection_result,outfile)
        
        img[:] = (0,0,0)
        img2 = mediapipe_fx.draw_landmarks_on_image(img,detection_result)
        img2 = myLandmarksDraw(img2,detection_result)
        
        

        img2 = cv2.resize(img2,(0,0),fx=0.5,fy=0.5)
        cv2.imshow( 'detection on ' + strFilename, img2 )

        # Press ESC on keyboard to  exit
        key = cv2.waitKey(10)
        if key == 27:
            break
            
        nNumFrame += 1
           
    if bOutputSkel: outfile.close()
    cap.release()
    cv2.destroyAllWindows()


detector = mediapipe_fx.init()
strPath = "C:/seq_vid2/sms/"
#~ strPath = "C:/seq_vid2/phone/"
strPath = "d:/seq_vid/eat/"
#~ strPath = "d:/seq_vid/sleep/"
#~ strPath = "d:/seq_vid/stretch/"
if 0:
    # loop all files
    for f in os.listdir(strPath):
        if not ".mkv" in f:
            continue
        print("DBG: %s" % f)
        extractFromVideo( strPath + f, detector)
if 0:
    # just see one file
    file = "sms_01.mkv"
    file = "sms_02.mkv"
    file = "eat_01.mkv"
    extractFromVideo( strPath + file, detector,bOutputSkel=0)
    
absfile = "C:/seq_vid2/test.mp4"
extractFromVideo( absfile, detector,bOutputSkel=1)