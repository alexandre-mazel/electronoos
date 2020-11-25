##########################################
# Handles a flow from a webcam or from disk:
# - save interesting images
# - Draw them on screen
##########################################

import cv2
print( "INF: cv2 version: %s" % cv2.__version__)
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

def isPixelBlack(pixel):
    """
    return True if pixel is at zero.
    pix can be an int, a float or a rgb component
    """
    if type(pixel) == np.ndarray:
        return int(sum(pixel)) == 0
    return int(pixel) == 0


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
        
        def __init__( self,  strPathToSaveToDisk = None, strSourceName = None, bLosslessSave = True ):
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
            self.bLosslessSave = bLosslessSave
            if bLosslessSave:
                self.strSaveExt = ".png"
            else:
                self.strSaveExt = ".jpg"
                
            self.bBlinkIsLighten = False
            
            
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
                
            bSaved = False
            if self.strPathToSaveToDisk != None:
                rDiff = computeImageDifference( self.prevImage, img )
                print("DBG: Source: %s, rDiff: %5.3f" % (self.strSourceName,rDiff) )
                if rDiff > rThresholdDifferenceToSave:
                    if strOptionalFileName != None:
                        strSkullName = strOptionalFileName
                    else:
                        strSkullName = getFilenameFromTime()
                    fn = self.strPathToSaveToDisk + strSkullName + self.strSourceName + self.strSaveExt
                    print("INF: Source: %s, saving to: '%s'" % (self.strSourceName, fn ) )
                    if img.dtype == np.uint16:
                        imgpseudo = img.copy()
                        if imgpseudo.shape[0] == 122:
                            imgpseudo = imgpseudo[:-2]
                        cv2.normalize(imgpseudo, imgpseudo, 0, 65535, cv2.NORM_MINMAX) # extend contrast # don't do that if saving to raw is required!!!
                        imgpseudo = (imgpseudo/256).astype('uint8')
                        imgpseudo = cv2.applyColorMap(imgpseudo, cv2.COLORMAP_JET) # only for 8bits
                        retVal = cv2.imwrite(fn,imgpseudo)
                    else:
                        retVal = cv2.imwrite(fn,img)
                        
                    if img.dtype != np.uint8:
                        fn = self.strPathToSaveToDisk + strSkullName + self.strSourceName + ".raw"
                        print("INF: Source: %s, saving type %s to RAW: '%s', first byte is 0x%X" % (self.strSourceName, img.dtype, fn, img[0,0] ) )
                        f = open(fn,'wb')
                        img.tofile(f) # file.write(a.tobytes())
                        f.close()
                    assert(retVal)
                    bSaved = True
                self.prevImage = img.copy()


            # tranformation for a better rendering
            
            if img.shape[0] == 122:
                img = img[:-2]
                
            if img.dtype == np.uint16:
                cv2.normalize(img, img, 0, 65535, cv2.NORM_MINMAX) # extend contrast # don't do that if saving to raw is required!!!
                if img.shape[1] < 640:
                    nZoom = 640 // img.shape[1]
                    img = cv2.resize(img, None, fx=nZoom, fy=nZoom )
                img = (img/256).astype('uint8')
                img = cv2.applyColorMap(img, cv2.COLORMAP_JET) # only for 8bits

            # The following line remove the RPI CV3.2.0 bug: "TypeError: Layout of the output array img is incompatible with cv::Mat"
            # occuring when we want to draw in this image (circle, line...) type was good, dtype was good, shape was good but...
            img = img.copy() 
            
            if bSaved: 
                cv2.circle( img, (20,20), 10,(0,0,255), -1 )
                
                
            # add a blincking dot
            if not self.bBlinkIsLighten:
                cv2.circle( img, (40,20), 10,(255,0,0), -1 )
            self.bBlinkIsLighten = not self.bBlinkIsLighten
                
            cv2.imshow( self.strWindowName, img )
                
            
            # fps counting
            self.nCptImage += 1
            if self.nCptImage > 60:
                t = time.time() - self.timeBegin
                print("INF: Source: %s, %5.2ffps" % ( self.strSourceName, (self.nCptImage / t) ) )
                self.nCptImage = 0
                self.timeBegin = time.time()
                
        #newImage - end
                
    
    # class SourceManager - end


    
    def __init__( self, strPathToSaveToDisk = None, rThresholdDifferenceToSave = 0.01, bLosslessSave = True ):
        """
        - strPathToSaveToDisk: c:/tmp/ or None to not save to disk
        - rThresholdDifferenceToSave: put +inf to never save, -1 to always save
        """
        if strPathToSaveToDisk != None:
            try: os.makedirs(strPathToSaveToDisk)
            except BaseException as err: pass ; print("DBG: makedirs: err:%s" % str(err))
        self.strPathToSaveToDisk = strPathToSaveToDisk
        self.bLosslessSave = bLosslessSave
        
        self.rThresholdDifferenceToSave = rThresholdDifferenceToSave
        self.dictSource = dict() # a sourcemanager for each sourcename
        self.bSlowRender = False
        self.nSlowRenderCountSkip = 0

        
    def newImage( self, img, strSourceName = None, strOptionalFileName = None  ):
        """
        receive a new image
        """
        if strSourceName not in self.dictSource.keys():
            self.dictSource[strSourceName] = CaptureManager.SourceManager(strPathToSaveToDisk=self.strPathToSaveToDisk, strSourceName=strSourceName, bLosslessSave=self.bLosslessSave )
        self.dictSource[strSourceName].newImage( img, rThresholdDifferenceToSave = self.rThresholdDifferenceToSave, strOptionalFileName = strOptionalFileName )
        
    def render( self ):
        """
        return False if user want to quit
        """
        if self.bSlowRender:
            self.nSlowRenderCountSkip += 1
            if self.nSlowRenderCountSkip < 6:
                return True
            self.nSlowRenderCountSkip = 0
                
        timeBegin = time.time()            
        key = ( cv2.waitKey(1) & 0xFF )
        duration = time.time()-timeBegin
        if duration > 0.1:
            self.bSlowRender = True
            print("DBG: Time render: %5.2fs" % duration )
        elif:
            self.bSlowRender = False
        
        
        if key == ord('q') or key == 27:
            return False
        return True
    
# class CaptureManager - end


def showAndSaveAllCameras( strSavePath = None ):
    """
    a utility method as an example but very usefull...
    """
    
    cm = CaptureManager(strSavePath)
    aCap = []
    nFirst = 0
    #~ nFirst = 2
    for i in range(nFirst,10):
        cap = cv2.VideoCapture(i) #or 0 + cv2.CAP_DSHOW
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        if cap.isOpened():
            if os.name == "nt": print("GOOD: found one camera: '%s'" % cap.getBackendName() )
            # removed cv2.CAP_PROP_SAR_NUM 
            propList = [cv2.CAP_PROP_FPS, cv2.CAP_PROP_FOURCC,cv2.CAP_PROP_GAIN,cv2.CAP_PROP_GUID,cv2.CAP_PROP_FRAME_WIDTH,cv2.CAP_PROP_FRAME_HEIGHT,
                                cv2.CAP_PROP_MODE,cv2.CAP_PROP_RECTIFICATION,
                                cv2.CAP_PROP_FORMAT,cv2.CAP_PROP_OPENNI_FOCAL_LENGTH,cv2.CAP_PROP_IMAGES_BASE ]
            if os.name == "nt":
                # flag not on my Raspberry (or at list not in this cv2 version)
                propList.extend( [cv2.CAP_PROP_SAR_NUM,cv2.CAP_PROP_CODEC_PIXEL_FORMAT,cv2.CAP_PROP_BACKEND] )
                
            for prop in propList:
                retVal = cap.get(prop)
                if prop == 9:
                    print("") # saut de ligne
                print("INF: prop %d: %s (0X%X)" % (prop,str(retVal),int(retVal)) )
                
            w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if w == 160:
                # thermal camera
                print("INF: Thermal camera detected: changing format")
                if os.name == "nt":
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','1','6',' '))
                    cap.set(cv2.CAP_PROP_CONVERT_RGB, False)
                fps = 9
                
            if fps < 1:
                print("INF: this camera has no fps, skipping it...\n" )
                continue
                
            print("")
            aCap.append(cap)

    print("INF: showAndSaveAllCamera: nbr cam kept: %d\n" % len(aCap))
    if len(aCap) < 1:
        exit(0)

    while 1:
        #~ print("loop")
        for i in range(len(aCap)):        
            ret, frame = aCap[i].read()
            if ret:
                bAutoRotateFishEyePatchCrado = True
                if bAutoRotateFishEyePatchCrado and frame.shape[1] > 160:
                    # we use a properties my laptop camera are in 16/9 thus there's black border around images
                    pix = frame[0,frame.shape[1]//2]
                    #~ print("pix: %s" % pix )
                    if not isPixelBlack(pix):
                        frame = np.rot90(frame)
                        
                if frame.shape[0] == 122 and 1:
                    #~ print("DBG extra lines: %s" % frame[-2:-1] )
                    #~ frame = frame[:-2]
                    #cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX) # extend contrast # don't do that if saving to raw is required!!!
                    pass
                        
                cm.newImage(frame, strSourceName = i )
        if not cm.render():
            return
#showAndSaveAllCameras - end

def copyInterestingImage( strSrcPath, strDstPath, rThresholdDifferenceToSave = 0.01, bLosslessSave = True ):
    """
    take all images in a folder and output only interesting one in another path
    (interesting == enough difference)
    - rThresholdDifferenceToSave: 0.01 or 0.02 for fish eye in daylight
    
    NB: if not lossless, jpg will be reencoded thus image is changed a bit. 
    (it's not an exact file copy)
    
    """
    cm = CaptureManager( strDstPath, bLosslessSave=bLosslessSave, rThresholdDifferenceToSave=rThresholdDifferenceToSave )
    for f in sorted(  os.listdir(strSrcPath) ):
        if ".png" in f.lower() or ".jpg" in f.lower():
            tf = strSrcPath + f
            print("INF: loading '%s'" % tf )
            im = cv2.imread(tf)
            #f_wo_ext = '.'.join(f.split('.')[:-1])
            f_wo_ext = os. path. splitext(f)[0]
            cm.newImage(im, strOptionalFileName = f_wo_ext )
            if not cm.render():
                break
            
            
# copyInterestingImage - end


if __name__ == "__main__":
    showAndSaveAllCameras() # not saving
    #~ showAndSaveAllCameras("c:\\tmpi13\\") #saving
    
    # remove static image with same content from a folder
    #~ copyInterestingImage( "c:/tmpi7/", "c:/tmpi7b/", rThresholdDifferenceToSave = 0.02, bLosslessSave=False )
    
    if 0:
        # test reouverture
        for name in ["2020_11_17-11h43m13s571561ms__2", "2020_11_17-11h43m43s540418ms__2"]:
            im = cv2.imread("c:\\tmpi11\\%s.png" % name)
            print(im.dtype)
    
    
    
