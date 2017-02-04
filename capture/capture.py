# -*- coding: utf-8 -*-
import cv2
import mutex
import numpy as np
import os
import time
import threading

#~ from skimage.measure import structural_similarity as ssim # apt-get install python-skimage
#~ import paramiko

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

def sendFileToRemoteParamiko( server, user, srcfilename, dstfilename ):
    import paramiko
    def createSSHClient(server, port, user, password):
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client
    ssh = createSSHClient("protolab.aldebaran.com", 22, "", "")
    scp = SCPClient(ssh.get_transport())
    #~ Then call scp.get() or scp.put() to do scp operations.
    # TODO: finish me !
    
def sendFileToRemote( server, user, srcfilename, dstfilename ):
    strCommand = "scp %s %s@%s:%s" % (srcfilename, user, server,  dstfilename) # -C for large image could be usefull
    print( "INF: running command: '%s'" % strCommand )
    os.system( strCommand )
    
import subprocess
    
    
class BackgroundSender:
    """
    Permis to ask to send a bunch of files, but it send only one at a time.
    After the file is finished to send, it try to send the last(s) one
    """
    def __init__( self, servername, username, nQueueLen = 40, nNbrSimultaneousSend = 1 ):
        self.nQueueLen = nQueueLen
        self.nNbrSimultaneousSend = nNbrSimultaneousSend # NDEV
        self.servername = servername
        self.username = username
        
        self.listWaiting = [] # a list of pair src/dst file(s) to be send
        self.mutex = mutex.mutex()
        
        self.bst = None
        self.launchBackgroundThread()
        
    def launchBackgroundThread(self):
        class BackgroundSenderThread( threading.Thread ):
            def __init__(self, backgroundSender ):
                threading.Thread.__init__( self );
                self.backgroundSender = backgroundSender
            # init - end

            def run ( self ):
                print( "DBG: launchBackgroundThread.run: start" );
                
                while( 1 ):
                    while self.backgroundSender.mutex.testandset() == False:
                        print( "DBG: wait mutex in thread" )
                        time.sleep( 0.001 )

                    if len(self.backgroundSender.listWaiting) > 0:
                        # send always the last
                        srcfilename, dstfilename = self.backgroundSender.listWaiting[-1]
                        self.backgroundSender.listWaiting = self.backgroundSender.listWaiting[:-1]
                        print( "DBG: launchBackgroundThread.run: remaining in queue: %s" % len(self.backgroundSender.listWaiting) )
                        self.backgroundSender.mutex.unlock()
                        
                        strCommandAndArgs =  "scp %s %s@%s:%s" % (srcfilename, self.backgroundSender.username, self.backgroundSender.servername,  dstfilename) # -C for large image could be usefull
                        print( "DBG: launchBackgroundThread.run: launching sub command: '%s'" % (strCommandAndArgs) )
                        newProcess = subprocess.Popen( strCommandAndArgs, shell=True ) # , stdin=subprocess.PIPE
                        try:
                            sts = os.waitpid( newProcess.pid, 0 )
                        except:
                            pass # pid already finished or some erros occurs or under windows ?
                        print( "DBG: %s => %s [OK]" % (srcfilename,dstfilename) )                            
                    else:
                        self.backgroundSender.mutex.unlock()                        
                        time.sleep( 0.4 )
                print( "DBG: launchBackgroundThread.run: stop" );
            # run - end        
        # class BackgroundSenderThread - end
        self.bst = BackgroundSenderThread(self)
        self.bst.start()
        
    # launchBackgroundThread  - end
        
    def addFile( self, src, dst ):
        """
        Add a new transfer command
        """
        while self.mutex.testandset() == False:
            print( "DBG: wait mutex addFile" )
            time.sleep( 0.001 )
        print( "DBG: BackgroundSender.addFile: adding '%s'->'%s' task" % (src, dst) )
        if len(self.listWaiting) == self.nQueueLen:
            # clear older one
            self.listWaiting = self.listWaiting[1:] # drop
        self.listWaiting.append( (src, dst) )
        self.mutex.unlock()
# class BackgroundSender - end
    


def watchAndSend( nNumCameraPort ):
    #Number of frames to throw away while the camera adjusts to light levels
    ramp_frames = 1 # 30
    
    print("INF: Opening...")            
     
    # Now we can initialize the camera capture object with the cv2.VideoCapture class.
    # All it needs is the index to a camera port.
    camera = cv2.VideoCapture(camera_port)
    camera.set(3,640)
    camera.set(4,480)    

    print("INF: Warming up...")         
    # Ramp the camera - these frames will be discarded and are only used to allow v4l2
    # to adjust light levels, if necessary
    for i in xrange(ramp_frames):
         temp = get_image(camera)
         #~ time.sleep( 0.05 )

    bStoreTmp = False
    
    if not bStoreTmp:
        bgs = BackgroundSender( "protolab.aldebaran.com", "amazel" )
        
    print("INF: Taking image for real...")
    
    imPrev = get_image(camera)
    imPrevGrey = cv2.cvtColor( imPrev, cv2.COLOR_BGR2GRAY )

    while( 1 ):
        #~ print( "DBG: %s: getting..." % ti    me.time() )
        im = get_image(camera) # it seems like we've got a buffer of 6 images, so even if taking time to send, we've got 6 images of moving datas in raw stored! great
    
        #~ print( "DBG: %s: analysing..." % time.time() )
        imGrey = cv2.cvtColor( im, cv2.COLOR_BGR2GRAY )
        #rDiff = computeDiff( imGrey, imPrevGrey )
        rDiff = mse( imGrey, imPrevGrey )
        #~ rDiff = ssim(mGrey, imPrevGrey )
        print( "DBG: %5.02f: rDiff: %5.1f" % ( time.time(), rDiff) )
        
        if rDiff > 120: # 120 dans une piece, 50 sur une vue d'ensemble
            timeBegin = time.time()
            print( "DBG: %s: storing..." % time.time() )
            dstFile = "~/images/%09.03f.jpg"  % time.time()            
            if bStoreTmp:
                # store in tmp, send image on the fly
                file = "/tmp/last.jpg" # to store nothing locally enable this line                
            else:
                # store locally every images and send last one to remote
                file = "/home/pi/images/%09.03f.jpg" % time.time()                
            cv2.imwrite(file, im,[int(cv2.IMWRITE_JPEG_QUALITY), 50])
            if bStoreTmp:
                sendFileToRemote( "protolab.aldebaran.com", "amazel", file, dstFile )
            else:
                bgs.addFile( file, dstFile )
                
            duration = time.time() - timeBegin
            print( "DBG: time to store: %5.2fs" % duration )      
            
        imPrevGrey = imGrey
        time.sleep( 0.03 ) # leave a bit of cpu to background task
     
    # You'll want to release the camera, otherwise you won't be able to create a new
    # capture object until your script exits
    del(camera)
 
# Camera 0 is the integrated web cam on my netbook
camera_port = 0

watchAndSend( camera_port )

