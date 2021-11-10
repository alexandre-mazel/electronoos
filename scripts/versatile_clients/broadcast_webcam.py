import cv2
import sys
import time
sys.path.append( "../versatile" )
from versatile import Versatile

def broadcastWebcam( nCameraIndex = 0 ):
    cam = cv2.VideoCapture(nCameraIndex)
    nWidth,nHeight = 640, 480 # VGA    
    #~ nWidth,nHeight = 800, 600
    #~ nWidth,nHeight = 1024,768
    #~ nWidth,nHeight = 1280,1024
    
    print( "Using resolution: %dx%d" % (nWidth, nHeight) )
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,nWidth ) # 2400
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,nHeight ) # 1200
    
    strIP = "localhost"
    nPort = 15000
    v = Versatile( nPort )
    v.connect( strIP )
    id = v.createClientID()[1]
    v.setClientID( id )
    print( "INF: my client id is %s" % id )
    
    nCptImage = 0
    timeBegin = time.time()
    while 1:
        ret_val, img = cam.read()
        vi = Versatile.VersatileImage()
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        vi.addCommand( ["broadcast"] )
        v.sendValue( vi )
        nCptImage += 1
        if nCptImage>100:
            rDuration = time.time() - timeBegin
            print( "INF: fps: %5.2fim/s" % (nCptImage/rDuration) )
            timeBegin = time.time()
            nCptImage = 0
        time.sleep( 0.03 )
# broadcastWebcam - end
        
broadcastWebcam()