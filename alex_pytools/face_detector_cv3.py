import cv2 # >= cv 3.3.0
import numpy as np
import os
import sys

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
        
    def detect( self, im, bRenderBox = True ):
        blob = cv2.dnn.blobFromImage( im, 1.0, (300, 300), (104.0, 177.0, 123.0) )
        h,w,n=im.shape
        print("DBG: src is %dx%d" % (w,h) )

        print("DBG: computing face detections...")
        self.net.setInput(blob)
        detections = self.net.forward()
        print("INF: detections: %s" % str(detections))
        res = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                res.append((startX, startY, endX, endY))
                print("DBG: box: %s" % str(box))
                print("DBG: x,y: %d,%d" % (startX, startY))
                if bRenderBox:
                    color = 0xFF00000
                    cv2.rectangle(im, (startX,startX),(endX, endY),color)
                    cv2.putText(im,"%.2f"%confidence,(startX, startY),cv2.FONT_HERSHEY_SIMPLEX, 1., color )
        return res
# class FaceDetector - end

facedetector = FaceDetector()

        
if __name__ == "__main__":
    im = cv2.imread("../data/girl_face.jpg")
    facedetector.detect(im)