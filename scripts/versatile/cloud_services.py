"""
flavouring Versatile to become a cloud services on remote server
"""

from versatile import Versatile

import cv2
import os
import time

class CloudServices:
    
    def __init__( self, strIP, nPort = 13000 ):
        self.v = Versatile( nPort )
        self.strIP = strIP
        self.v.connect( strIP )
        
    def setVerbose( self, bVal ):
        self.v.setVerbose( bVal )
        
    def isRunning( self ):
        return self.v.isRunning()
        
    def createClientID( self ):
        """
        Produce an id for this client
        If you want to reuse one day previous learning, you will have to fullfill this client ID !!!
        """
        client = self.v.createClientID()[1]
        return client
        
    def setClientID( self, id ):
        """
        set a previously produced client ID
        """
        return self.v.setClientID(id)
        
    def imageReco_learn( self, img, strName ):
        print( "imageReco_learn: sending image to learn" )
        vi = Versatile.VersatileImage()
        bRet = vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        if not bRet:
            return False # image not found...
        vi.addCommand( ["facerecognition", "dbtemp", "learn", strName] )
        return self.v.sendValueGeneratingResults( vi )
        
    def imageReco_learnFromFile( self, strImageFile, strName ):
        print( "imageReco_learnFromFile: sending image to learn" )
        img = cv2.imread( strImageFile )
        return self.imageReco_learn( img, strName )
        
    def imageReco_recognise( self, img ):
        """
        TODO: document me !!!
        return: 
                - (-1,None) in case of error
                - (1, [[]]) in case of no face found
                - (1, [[[-1, '', 0.0575826105086, 0.123968691869, [249, 326, 285, 362], None]]]) in case of one face not recognised
                - (1, [[[6, 'alexandre_m', 0.0371563399693, 1.0, [279, 314, 331, 366], None]]]) if recognised
                with for each recognised face:
                [id, "firstname", dist squared, confidence, pos in image, optionnal_learned_filename]
        """
        print( "imageReco_recognise: sending image to recognise" )
        vi = Versatile.VersatileImage()
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        vi.addCommand( ["facerecognition", "dbtemp", "recognise"] )
        return self.v.sendValueGeneratingResults( vi )  

    def imageReco_recogniseFromFile( self, strImageFile ):
        print( "imageReco_recogniseFromFile: sending image to recognise" )
        img = cv2.imread( strImageFile )
        return self.imageReco_recognise( img )
        
    def imageReco_continuousLearn( self, img ):
        """
        TODO: document me !!!
        return: ?
        """
        print( "INF: imageReco_continuousLearn: sending image to recognise" )
        if img is None or img.shape[0] < 0:
            print( "ERR: imageReco_recognise: image is empty")
            return False
        vi = Versatile.VersatileImage()
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        vi.addCommand( ["facerecognition", "dbtemp", "continuous_learn"] )
        return self.v.sendValueGeneratingResults( vi )  

    def imageReco_continuousLearnFromFile( self, strImageFile ):
        print( "INF: imageReco_continuousLearnFromFile: sending image to recognise" )
        img = cv2.imread( strImageFile )
        return self.imageReco_continuousLearn( img )
        
    def imageReco_clearDB( self, dbname ):
        print( "imageReco_clearDB: entering" )
        vi = Versatile.VersatileImage() # will create a buffer without images
        vi.addCommand( ["facerecognition", dbname, "clear_db"] )
        return self.v.sendValueGeneratingResults( vi )  
     
    def imageFaceDetect_analyse( self, strImageFile ):
        print( "imageFaceDetect_analyse: sending image to analyse" )
        img = cv2.imread( strImageFile )
        if img is None:
            print("ERR: imageFaceDetect_analyse: image '%s' not found or bad format" % strImageFile )
            return None
        vi = Versatile.VersatileImage()
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        vi.addCommand( ["facedetection"] )
        return self.v.sendValueGeneratingResults( vi )   
        
def ping( hostname ):
    ret = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1" )    
    print( "DBG: ping %s => %s" % (hostname, ret) )
    return ret == 0

def _createAndConnect(listExtraAdress=[], nSpecificPort = 13000):
    """
    create a cloud services and autoconnect to the accessible computer (sbre oriented)
    """
    listToConnect = ["20.0.0.10", "10.0.161.8", "robot-prog.com"] # NDEV
    listToConnect = [listExtraAdress]
    for strHost in listToConnect: # edge, fog, cloud
        if ping( strHost ): 
            cs = CloudServices( strHost, nPort= nSpecificPort) # try edge
            bIsRunning = cs.isRunning()
            print( "INF: CloudServices.createAndConnect: is running: %s" % bIsRunning )
            return cs
    return None
    
global_cs = None
def createAndConnect():
    global global_cs
    global_cs = _createAndConnect()
    return global_cs
    
def getInstance():
    global global_cs
    return global_cs
    

def autoTest():
    #cs = CloudServices( "robot-prog.com" )
    #cs = CloudServices( "10.0.160.60" )
    cs = CloudServices( "localhost" )
    cs = CloudServices( "robot-enhanced-education.org", 25340 )
    cs.setVerbose( True )
    cs.setClientID( "autotest" )

    if not cs.isRunning():
        exit( -1 )

    bTestCreateClientID = False
    #~ bTestCreateClientID = True
    
    if bTestCreateClientID:
        # first time
        id = cs.createClientID()
        id2 = cs.createClientID()
        assert( id2==id)
        
        print( "INF: Remember your client ID: %s" % id )
        cs.setClientID( id )        
        id = cs.getClientID()
        assert( id2==id)
        
    
    bTestFaceDetect = False
    #~ bTestFaceDetect = True
    
    bTestFaceReco = False
    bTestFaceReco = True
    
    if bTestFaceDetect:
        retVal = cs.imageFaceDetect_analyse( "../../../face_tools/faces/0_alexandre0.jpg" )
        print("DBG: cloud return: retVal: %s" % str(retVal))
        #~ time.sleep(4.5)
        retVal = cs.imageFaceDetect_analyse( "D:/gaia_mask/IMG_0433.jpg" )
        #~ time.sleep(4.5)
        retVal = cs.imageFaceDetect_analyse( os.path.expanduser("~/family_01.JPG" ) )
        retVal = cs.imageFaceDetect_analyse( os.path.expanduser("~/family_02.JPG" ) )
        retVal = cs.imageFaceDetect_analyse( os.path.expanduser("~/family_03.JPG" ) )
        
   
    if bTestFaceReco:
        
        print( "INF: before learning: cleaning previous test" )
        cs.imageReco_clearDB("test")
        #~ exit(0)
        
        print( "INF: first pass: learning stuffs" )

        retVal = cs.imageReco_continuousLearnFromFile( "../../../face_tools/faces/0_alexandre0.jpg" ) # will be learned in the client db
        print( "learn ret: %s\n\n" % str(retVal) )
        assert(retVal[1][0][1]==0)
        retVal = cs.imageReco_continuousLearnFromFile( "../../../face_tools/faces/1_edouard0.jpg")
        print( "learn ret: %s\n\n" % str(retVal) )
        assert(retVal[1][0][1]==1)

        print( "INF: second pass: recognizing stuffs" )

        retVal = cs.imageReco_continuousLearnFromFile( "../../../face_tools/faces/0_alexandre4.jpg" )
        print( "reco ret: %s\n" % str(retVal) )
        assert(retVal[1][0][1]==0)

        if 1:
            timeBegin = time.time()
            nNbrCall = 6
            for i in range(nNbrCall):
                retVal = cs.imageReco_continuousLearnFromFile( "../../../face_tools/faces/0_alexandre4.jpg" )
                print( "reco ret: %s\n" % str(retVal) )
                assert(retVal[1][0][1]==0)
            duration = time.time()-timeBegin
            print("INF: duration per call: %.2fs" % (duration/nNbrCall))
            # mstab7=>mstab7: 0.56
            # mstab7=>xavier nvpmodel 0: 0.38
            # mstab7=>xavier nvpmodel 1: 0.65-067            
            # mstab7=>xavier nvpmodel 2: 0.65
    
if( __name__ == "__main__" ):
    autoTest()
