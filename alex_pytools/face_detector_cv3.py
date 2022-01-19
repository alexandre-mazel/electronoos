import cv2 # >= cv 3.3.0
import numpy as np
import os
import sys
import time

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
print("strLocalPath: " + strLocalPath)

class FaceDetector:
    """
    detect face using dnn included in cv3 since the 3.3.0
    """
    
    def __init__( self ):
        self.load()
        
    def load( self ):
        # load coffee models
        print( "ING: FaceDetectorCV3: Loading face models" )
        strPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ strPath = "/home/pi/dev/git/electronoos/alex_pytools/"
        if strPath == "": strPath = '.'
        strPath += "/../models/"
        strProtoTxt = strPath + "facedetect_deploy.prototxt.txt"
        strModel = strPath + "facedetect_res10_300x300_ssd_iter_140000.caffemodel"
        self.net = cv2.dnn.readNetFromCaffe( strProtoTxt, strModel )
        
    def render_res( self, im, res, color = 0xFF00000 ):
        """
        render result from a previous analyse in im
        return im (as given)
        """
        for oneres in res:
            startX, startY, endX, endY, confidence = oneres
            cv2.rectangle(im, (startX,startY),(endX, endY),color)
            # etiquette and confidence
            cv2.rectangle(im,(startX, startY-14),(startX+40, startY), color, thickness=-1 )
            cv2.putText(im,"%.2f"%confidence,(startX+2, startY-2),cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(255,255,255), thickness = 1 )
        return im
        
    def detect( self, im, bRenderBox = True ):
        blob = cv2.dnn.blobFromImage( im, 1.0, (300, 300), (104.0, 177.0, 123.0) )
        h,w,n=im.shape
        print("DBG: src is %dx%d" % (w,h) )

        print("DBG: computing face detections...")
        timeBegin = time.time()
        self.net.setInput(blob)
        detections = self.net.forward()
        print("INF: detections: %s\nanalyse takes: %5.2fs\n" % (str(detections),time.time()-timeBegin))
        res = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                res.append((startX, startY, endX, endY, confidence))
                print("DBG: box: %s" % str(box))
                print("DBG: x,y: %d,%d" % (startX, startY))
                
        if bRenderBox: self.render_res( im, res )
        return res
# class FaceDetector - end

facedetector = FaceDetector()

        
if __name__ == "__main__":
    im = cv2.imread("../data/girl_face.jpg")
    facedetector.detect(im)