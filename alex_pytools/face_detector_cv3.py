import cv2
import os

class Detector:
    
    def __init__( self ):
        self.load()
        
    def load( self ):
        strPath = strLocalPath = os.path.dirname(sys.modules[__name__].__file__) + "/../models/"
        strProtoTxt = ""
        strModel = ""
        self.net = cv2.dnn.readNetFromCaffe( strProtoTxt, strModel )
        
    def detect( self, im ):
        