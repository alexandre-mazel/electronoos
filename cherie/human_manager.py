"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.
On AGX:
cd ~/dev/git/electronoos/scripts/versatile
nohup python3 run_cloud_server.py

"""
import cv2
import sys
import time


sys.path.append("../scripts/versatile")
import cloud_services

sys.path.append("../../electronoos/alex_pytools")
import face_detector_cv3

class HumanManager:
    def __init__( self ):
        self.cs = cloud_services.CloudServices( "robot-enhanced-education.org", 25340 )
        self.cs.setVerbose( True )
        self.cs.setClientID( "test_on_the_fly" )
        self.fdcv3 = face_detector_cv3.facedetector


    def updateImage( self, img, bAddDebug = False ):
        """
        return False on server problem
        """
        #~ if not self.cs.isRunning():
            #~ return False
        resDetect = self.fdcv3.detect(img,bRenderBox=False,confidence_threshold=0.4) # ~0.06s on mstab7 on a VGA one face image
        if len(resDetect) > 0:
            if 0:
                # select only centered faces
                faces = [face_detector_cv3.selectFace(resDetect,img.shape)]
            else:
                # all faces
                faces = resDetect
            for face in faces:
                startX, startY, endX, endY, confidence = face
                # ajoute un peu autour du visage
                nAddedOffsetY = int((endY-startY)*0.25)
                nAddedOffsetX = int(nAddedOffsetY*0.6)
                x1,y1,x2,y2=startX, startY, endX, endY
                x1 = max(x1-nAddedOffsetX,0)
                y1 = max(y1-nAddedOffsetY,0)
                x2 = min(x2+nAddedOffsetX,img.shape[1])
                y2 = min(y2+nAddedOffsetY,img.shape[0])
                
                imgFace = img[y1:y2,x1:x2]
                timeBegin = time.time()
                retVal = self.cs.imageReco_continuousLearn(imgFace)
                print( "reco ret: %s, duration: %.2fs\n" % (str(retVal), time.time()-timeBegin ))
                if retVal != False:
                    nHumanID = retVal[1][0][1]
                    cv2.putText(img,"%d"%nHumanID,(int((startX+endX)/2)-10, endY+5),cv2.FONT_HERSHEY_SIMPLEX, 0.8, color=(255,255,255), thickness = 2 )
            
# class HumanManager - end



def realLifeTestWebcam():
    hm = HumanManager()
    cap = cv2.VideoCapture(0) #ouvre la webcam
    while 1:
        ret, img = cap.read() # lis et stocke l'image dans frame
        print(img.shape)
        
        #~ img = cv2.resize(img, None, fx=0.5,fy=0.5)
        
        hm.updateImage(img)
        
        # Display the output
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break



if __name__ == "__main__":
    realLifeTestWebcam()