import cv2 # >= cv 3.3.0
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
        strPath = "/home/pi/dev/git/electronoos/alex_pytools/"
        if strPath == "": strPath = '.'
        strPath += "/../models/"
        strProtoTxt = strPath + "facedetect_deploy.prototxt.txt"
        strModel = strPath + "facedetect_res10_300x300_ssd_iter_140000.caffemodel"
        self.net = cv2.dnn.readNetFromCaffe( strProtoTxt, strModel )
        
    def detect( self, im ):
        pass
        
# class FaceDetector - end

facedetector = FaceDetector()

        
if __name__ == "__main__":
    facedetector.detect(im)