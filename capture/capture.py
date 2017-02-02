import cv2
import numpy as np
import time

# Captures a single image from the camera and returns it in PIL format
def get_image(camera):
     # read is the easiest way to get a full image out of a VideoCapture object.
     retval, im = camera.read()
     return im
    
def computeDiff( im1, im2 ):
    print( "im1: %s" % im1[:16] )
    print( "im2: %s" % im1[:16] )
    diff = im1 - im2
    
    print( "diff: %s" % diff[:16] )    
    ret,thresh1 = cv2.threshold(diff,32,1,cv2.THRESH_BINARY)
    print( "thresh1: %s" % thresh1[:16] )
    return cv2.mean(thresh1)
    

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def watchAndSend( nNumCameraPort ):
    #Number of frames to throw away while the camera adjusts to light levels
    ramp_frames = 1 # 30
    
    print("INF: Opening...")            
     
    # Now we can initialize the camera capture object with the cv2.VideoCapture class.
    # All it needs is the index to a camera port.
    camera = cv2.VideoCapture(camera_port)

    print("INF: Warming up...")         
    # Ramp the camera - these frames will be discarded and are only used to allow v4l2
    # to adjust light levels, if necessary
    for i in xrange(ramp_frames):
         temp = get_image(camera)
         #~ time.sleep( 0.05 )
    
    print("INF: Taking image for real...")
    
    imPrev = get_image(camera)
    imPrevGrey = cv2.cvtColor( imPrev, cv2.COLOR_BGR2GRAY )
    while( 1 ):
        print( "DBG: %s: getting..." % time.time() )
        im = get_image(camera)
    
        print( "DBG: %s: analysing..." % time.time() )
        imGrey = cv2.cvtColor( im, cv2.COLOR_BGR2GRAY )
        #rDiff = computeDiff( imGrey, imPrevGrey )
        rDiff = mse( imGrey, imPrevGrey )
        print( "DBG: rDiff: %s" % str(rDiff) )
        
        if rDiff > 100:
            print( "DBG: %s: storing..." % time.time() )
            file = "/home/pi/images/%s/%s.jpg" % time.time() )
            cv2.imwrite(file, im)
        
        imPrevGrey = imGrey
     
    # You'll want to release the camera, otherwise you won't be able to create a new
    # capture object until your script exits
    del(camera)
 
# Camera 0 is the integrated web cam on my netbook
camera_port = 0

watchAndSend( camera_port )

