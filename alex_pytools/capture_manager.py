##########################################
# Handles a flow from a webcam or from disk:
# - save interesting images
# - Draw them on screen
##########################################

import cv2
import datetime
import math
import numpy as np
import os
import time

def computeImageDifference( im1, im2 ):
    """
    return difference between two images expressed in a [0..1] coefficient
    """
    # resizing enables noise removal and to compare two different images
    im1 = cv2.resize(im1, (160,120) )
    im2 = cv2.resize(im2, (160,120) )
    err = np.sum( ( im1.astype("uint16") - im2.astype("uint16") ) ** 2 ) # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s
    #~ print("err1:%s"%err)
    err /= float(im1.shape[0] * im1.shape[1])
    err=math.sqrt(err)/512.
    #~ print("err2:%s"%err)
    return err
    
    
def getFilenameFromTime():
    """
    get a string usable as a filename relative to the current datetime stamp.
    eg: "2012_12_18-11h44m49s049ms"

    timestamp : time.time()
    """

    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
    strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds
    return strTimeStamp;
# getFilenameFromTime - end


class CaptureManager:
    """
    exemple:
        cm = CaptureManager( "c:/tmp/")
        cm.newImage( image1, "camera1")
        cm.newImage( image2, "camera2")
        cm.newImage( image1b, "camera1")
        => image are then saved
    """
    
    nextPosition = [0,0]
    
    @classmethod
    def findNewPosition(cls,img = None):
        x,y = CaptureManager.nextPosition
        
        if not isinstance( img, np.ndarray ):
            sx = 320
            sy = 240
        else:
            sy,sx = img.shape[:2]
            
        cls.nextPosition[0] += sx
        if cls.nextPosition[0] > 1024:
            cls.nextPosition[0] = 0
            cls.nextPosition[1] += sy
        return (x,y)
    

    class SourceManager:
        """
        handle image from one source
        """
        
        def __init__( self,  strPathToSaveToDisk = None, strSourceName = None ):
            if strPathToSaveToDisk != None:
                if strPathToSaveToDisk[-1] != os.sep:
                    strPathToSaveToDisk += os.sep
            self.strPathToSaveToDisk = strPathToSaveToDisk
            self.screenPosition = None
            self.strSourceName = ""
            if strSourceName != None:
                self.strSourceName = "__" + str(strSourceName)
            self.nCptImage = 0
            self.timeBegin = time.time()
            
            
            
        def newImage( self, img, rThresholdDifferenceToSave = 0.01, strOptionalFileName = None  ):
            """
            receive a new image
            """
            if self.screenPosition == None:
                # first image
                self.screenPosition = CaptureManager.findNewPosition(img)
                self.strWindowName = "source_" + self.strSourceName
                cv2.namedWindow( self.strWindowName )
                cv2.moveWindow( self.strWindowName, self.screenPosition[0], self.screenPosition[1] )
                self.prevImage = np.zeros(img.shape,dtype=np.uint8)
                self.prevImage[:] = 255
                
            if self.strPathToSaveToDisk != None:
                rDiff = computeImageDifference( self.prevImage, img )
                print("DBG: Source: %s, rDiff: %5.3f" % (self.strSourceName,rDiff) )
                if rDiff > rThresholdDifferenceToSave:
                    fn = self.strPathToSaveToDisk + getFilenameFromTime() + self.strSourceName + ".png"
                    print("INF: Source: %s, saving to: '%s'" % (self.strSourceName, fn ) )
                    cv2.imwrite(fn,img)
                self.prevImage = img.copy()
            
            cv2.imshow( self.strWindowName, img )
            self.nCptImage += 1
            if self.nCptImage > 60:
                t = time.time() - self.timeBegin
                print("INF: Source: %s, %5.2ffps" % ( self.strSourceName, (self.nCptImage / t) ) )
                self.nCptImage = 0
                self.timeBegin = time.time()
            
                
    
    # class SourceManager - end


    
    def __init__( self, strPathToSaveToDisk = None ):
        """
        - strPathToSaveToDisk: c:/tmp/ or None to not save to disk
        """
        self.strPathToSaveToDisk = strPathToSaveToDisk
        self.rThresholdDifferenceToSave = 0.01 # put +inf to never save, -1 to always save
        self.dictSource = dict() # a sourcemanager for each sourcename

        
    def newImage( self, img, strSourceName = None, strOptionalFileName = None  ):
        """
        receive a new image
        """
        if strSourceName not in self.dictSource.keys():
            self.dictSource[strSourceName] = CaptureManager.SourceManager(strPathToSaveToDisk=self.strPathToSaveToDisk, strSourceName=strSourceName)
        self.dictSource[strSourceName].newImage( img, rThresholdDifferenceToSave = self.rThresholdDifferenceToSave, strOptionalFileName = strOptionalFileName )
        
    def render( self ):
        """
        return False if user want to quit
        """
        if ( cv2.waitKey(1) & 0xFF ) == ord('q'):
            return False
        return True
    
# class CaptureManager - end


def showAndSaveAllCameras( strSavePath = None ):
    """
    a utility method as an example but very usefull...
    """
    
    cm = CaptureManager(strSavePath)
    aCap = []
    
    for i in range(10):
        oneCap = cv2.VideoCapture(i) #or 0 + cv2.CAP_DSHOW
        oneCap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        oneCap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        if oneCap.isOpened():
            aCap.append(oneCap)
            print("INF: found one camera...")

    print("INF: showAndSaveAllCamera: nbr cam found: %d" % len(aCap))
    if len(aCap) < 1:
        exit(0)

    while 1:
        #~ print("loop")
        for i in range(len(aCap)):        
            ret, frame = aCap[i].read()
            if ret:
                cm.newImage(frame, strSourceName = i )
        if not cm.render():
            return
#showAndSaveAllCameras - end


if __name__ == "__main__":
    #~ showAndSaveAllCameras() # not saving
    showAndSaveAllCameras("c:\\tmpi8\\")
    
    
