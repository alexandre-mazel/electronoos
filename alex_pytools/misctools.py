"""
some classic handy classes
"""        
import datetime
import cv2 # made with cv 3.2.0-dev
import numpy as np
import os
import select
import time
import sys
try: import v4l2capture  # can be found here : https://github.com/gebart/python-v4l2capture
except: pass # can be skipped if no use of v4l2 function

"""
sudo apt-get install libv4l-dev
git clone https://github.com/gebart/python-v4l2capture.gitlibv4l-dev
cd python-v4l2capture/
sudo ./setup.py install
"""

def getPathData():
    """
    return the absolute path of electronooos/data
    """
    strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
    if strLocalPath == "": strLocalPath = './'
    ret = os.path.abspath(strLocalPath + "/../data/") + "/"
    #~ print(ret)
    return ret
    

def check(v1,v2):
    if v1==v2:
        print( "GOOD: %s == %s" % (str(v1),str(v2) ) )
        return
    print( "BAD: %s != %s" % (str(v1),str(v2) ) )
    assert(v1==v2)
    return
        

def mse(imageA, imageB, bDenoise = False):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    if bDenoise:
        # size/2 will average noise
        imageA = cv2.resize(imageA, (0,0),fx=0.25, fy=0.25)
        imageB = cv2.resize(imageB, (0,0),fx=0.25, fy=0.25)
    err = np.sum( ((imageA.astype("int16") - imageB.astype("int16")) ** 2) ) # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return abs(err)
    
global_bIsRaspberry = None
def isRPI():
    global global_bIsRaspberry
    if global_bIsRaspberry != None:
        return global_bIsRaspberry
    try:
        f = open("/proc/cpuinfo", "rt")
        buf=f.read()
        f.close()
    except:
        global_bIsRaspberry = False
        return global_bIsRaspberry
    print(buf)
    global_bIsRaspberry = "Raspberry Pi" in buf
    print("INF: isRPI: %s" %  global_bIsRaspberry )
    return global_bIsRaspberry


    
def getTime():
    """
    return (hour,min,second)
    """
    datetimeObject = datetime.datetime.now()
    return datetimeObject.hour, datetimeObject.minute, datetimeObject.second 
    
def getDayStamp():
    """
    return (hour,min,second)
    """
    datetimeObject = datetime.datetime.now()
    return "%04d_%02d_%02d" % ( datetimeObject.year, datetimeObject.month,  datetimeObject.day )

def getTimeStamp():
    """
    
    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def getFilenameFromTime(timestamp=None):
  """
  get a string usable as a filename relative to the current datetime stamp.
  eg: "2012_12_18-11h44m49s049ms"
  
  timestamp : time.time()
  """
  # old method:
  #~ strTimeStamp = str( datetime.datetime.now() );
  #~ strTimeStamp = strTimeStamp.replace( " ", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ".", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ":", "m" );
  if timestamp is None:
      datetimeObject = datetime.datetime.now()
  elif isinstance(timestamp, datetime.datetime):
      datetimeObject = timestamp
  else:
      datetimeObject = datetime.datetime.fromtimestamp(timestamp)
  strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
  if os.name != "nt": strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no datas for microseconds on some platforms
  return strTimeStamp;
# getFilenameFromTime - end

def is_available_resolution(cam,x,y):
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
    return cam.get(cv2.CAP_PROP_FRAME_WIDTH) == int(x) and cam.get(cv2.CAP_PROP_FRAME_HEIGHT) == int(y)

def get_webcam_available_resolution(videoCaptureCamera):
    aTestRes = [
                            160,120,
                            320,240,
                            640,480,
                            800,600,
                            1024,768,
                            1280,960,
                            1280,1024,
                            1600,1200,
                            1920,1080, # HD
                            1920,1440,
                            2048,1280,
                            2560,1080,
                            4096,2304,
                            ]

    aRes = []
    i = 0
    while i < len(aTestRes ):
        if is_available_resolution( videoCaptureCamera, aTestRes[i], aTestRes[i+1] ):
            aRes.append( [ aTestRes[i], aTestRes[i+1] ] )
        i += 2

    # after testing, set standard camera resolution
    videoCaptureCamera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    videoCaptureCamera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

    return aRes
# get_webcam_available_resolution - end

def list_video_device( bPrintHighestResolution=True ):
    print("list_video_device: begin" )
    import os
    import v4l2capture
    file_names = [x for x in os.listdir("/dev") if x.startswith("video")]
    file_names.sort()
    for file_name in file_names:
        path = "/dev/" + file_name
        print(path)
        try:
            video = v4l2capture.Video_device(path)
            driver, card, bus_info, capabilities = video.get_info()
            print ("    driver:       %s\n    card:         %s" \
                "\n    bus info:     %s\n    capabilities  : %s" % (
                    driver, card, bus_info, ", ".join(capabilities))
                    )
                    
            if bPrintHighestResolution:
                w,h = video.set_format(100000,100000)
                print( "    highest format: %dx%d" % (w,h) );
                    
            video.close()
        except IOError as e:
            print ("    " + str(e) )
            

def get_video_devices():
    import os
    device_path = "/dev"
    file_names = [os.path.join(device_path, x) for x in os.listdir(device_path) if x.startswith("video")]
    return file_names


class WebCam():
    """
    Access webcam(s) using video4linux (v4l2)
    eg:
        webcam = WebCam();
        im = webcam.getImage();
        cv2.imwrite( "/tmp/test.jpg", im )
    """
    def __init__( self, strDeviceName = "/dev/video0", nWidth = 640, nHeight = 480, nNbrBuffer = 1, nFps = 10 ):
        """
        - nNbrBuffer: put a small number to have short latency a big one to prevent missing frames
        """
        print( "INF: WebCam: opening: '%s'" % strDeviceName );
        self.video = v4l2capture.Video_device(strDeviceName)
        # Suggest an image size to the device. The device may choose and
        # return another size if it doesn't support the suggested one.
        self.size_x, self.size_y = self.video.set_format(nWidth, nHeight)
        print( "format is: %dx%d" % (self.size_x, self.size_y) );

        # not working on the webcam device.
        self.video.set_fps(nFps); # can't succeed in changing that on my cheap webcam, but work on my computer
        # framerate = self.video.get(cv2.CAP_PROP_FPS)
        #~ framerate = self.video.get_fps();
        # print( "framerate is: %d" % (framerate) );
        
        # Create a buffer to store image data in. This must be done before
        # calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
        # raises IOError.
        self.video.create_buffers(nNbrBuffer) # would be better to play with fps, but it's not working on mine...
        # Send the buffer to the device. Some devices require this to be done
        # before calling 'start'.
        self.video.queue_all_buffers()
        # Start the device. This lights the LED if it's a camera that has one.
        self.video.start()
        print( "INF: WebCam: opening: '%s' - done" % strDeviceName );
        
    def __del__( self ):
        self.video.close()
    
    def getImage(self, bVerbose =  True ):
        """
        return an image, None on error
        """
        if bVerbose: print("INF: WebCam.getImage: Reading image...")
        # Wait for the device to fill the buffer.
        rStartAcquistion = time.time()
        aRet = select.select((self.video,), (), ()) # Wait for the device to fill the buffer.
        if bVerbose: print( "DBG: WebCam.getImage: select return: %s" % str(aRet) );
        try:
            image_data = self.video.read_and_queue()
        except BaseException as err:
            print( "WRN: skipping image: %s" % str(err) )
            time.sleep( 0.5 )
            return None
            
        rEndAquisition = time.time()
        rImageAquisitionDuration =  rEndAquisition - rStartAcquistion

        #image = Image.fromstring("RGB", (size_x, size_y), image_data)
        #image.save(strFilename)
        
        
        if bVerbose: print( "image_data len: %s" % len(image_data) )
        if len(image_data) == self.size_x * self.size_y * 3:
            # color image
            nparr = np.fromstring(image_data, np.uint8).reshape( self.size_y,self.size_x,3)
            nparr = cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB);
        else:
            # grey on 16 bits (depth on 16 bits)
            nparr = np.fromstring(image_data, np.uint16).reshape( self.size_y,self.size_x,1)
            minv = np.amin(nparr)
            maxv = np.amax(nparr)
#            print( "min: %s, max: %s" % (minv, maxv) )            
            nparr /= 64
            #nparr = cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB);            
        return nparr
# class WebCam - end

def renderGraphBar( cv2_im, listValue, nNbrElementInListMax, tl_corner, br_corner, front_color, back_color = -1 ):
	"""
	render a graph bar of listValue in a cv2 image.
	- nNbrElementInListMax: nbr max to receive in the list (for list who accumulate over time)
	- back_color: if -1: leave transparent
	"""
	w_bar = ( br_corner[0] - tl_corner[0] ) / nNbrElementInListMax
	
	if len(listValue): # if no value, nothing will be printed, or just the background
		max_val = max(listValue)
		rHeightUnit = ( br_corner[1] - tl_corner[1] )  / float(max_val)
		#~ print("DBG: renderGraphBar: w_bar: %s, max_val: %s, rHeightUnit: %s" % (w_bar, max_val, rHeightUnit) )
	
	if back_color != -1:
		cv2.rectangle( cv2_im, tl_corner, br_corner, back_color, -1 )
	
	for i, v in enumerate( listValue ):
		tl = ( int(tl_corner[0] + i*w_bar), int(br_corner[1]-v*rHeightUnit) )
		br = ( int(tl_corner[0] + (i+1)*w_bar), br_corner[1] )
		cv2.rectangle( cv2_im, tl, br, front_color, -1 )		
# renderGraphBar - end


def timeToString( rTimeSec ):
    "convert a time in second to a string"
    "convert to be compact and meaning full"
    "v0.6"
    # we will limit to 2 values
    nCptValue = 0;
    strOut = "";
#    strOut = "(%5.2f) " % rTimeSec;

    if( rTimeSec < 0.001 ):
        return "0 ms";

    nDividend = 60*60*24*30; # 30 day per month as an average!
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d min " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60*60*24;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d j " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60*60;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d hour " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d min " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 1;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d s " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    if( rTimeSec > 0. and nCptValue < 2 ):
        strOut += "%3d ms" % int( rTimeSec*1000 );
        nCptValue += 1;

    return strOut;
# timeToString - end

            
def getDateStamp():
    datetimeObject = datetime.datetime.now()
    strStamp = datetimeObject.strftime( "%Y_%m_%d")
    return strStamp
    
def makeDirsQuiet( strPath ):
    #os.makedirs(strPath,exist_ok=True) # exist_ok only in python3
    try: os.makedirs(strPath)
    except OSError as err: pass
    
def beep(frequency, duration):
    # duration in ms
    if isRPI():
        print("WRN: beep replaced by aplay on RPI")
        os.system("aplay /home/pi/saw_440_100ms.wav")
        return
    import winsound
    winsound.Beep(frequency, duration)

global_dictLastHalfHour = dict() # for each id the last (h,m)    
def isHalfHour(id=1,nOffsetMin = 0):
    """
    return True half an hour
    (NB: use a global, so it can be used only once in a program, or use a different id
    """
    global global_dictLastHalfHour
    h,m,s = getTime()
    
    mToCheck = m + nOffsetMin
        
    if mToCheck == 0 or mToCheck == 30:
        key = "%s_%s"%(id,nOffsetMin)
        try:
            lastVal = global_dictLastHalfHour[key]
        except KeyError as err:
            global_dictLastHalfHour[key] = (-1,-1)
            lastVal = global_dictLastHalfHour[key]    
        if (h,m) == lastVal:
            return False
        global_dictLastHalfHour[key] = (h,m)
        return True
        
    return False
    
global_dictLastQuarterHour = dict() # for each id the last (h,m)    
def isQuarterHour(id=1):
    """
    return True half an hour
    (NB: use a global, so it can be used only once in a program, or use a different id
    """
    global global_dictLastQuarterHour
    h,m,s = getTime()
        
    if m == 0 or m == 15 or m == 30 or m == 45:         
        try:
            lastVal = global_dictLastQuarterHour[id]
        except KeyError as err:
            global_dictLastQuarterHour[id] = (-1,-1)
            lastVal = global_dictLastQuarterHour[id]        
        if (h,m) == lastVal:
            return False
        global_dictLastQuarterHour[id] = (h,m)
        return True
        
    return False

global_dictLast10min = dict() # for each id the last (h,m)    
def isEvery10min(id=1):
    """
    return True half an hour
    (NB: use a global, so it can be used only once in a program, or use a different id
    """
    global global_dictLast10min
    h,m,s = getTime()
        
    if (m%10) == 0:         
        try:
            lastVal = global_dictLast10min[id]
        except KeyError as err:
            global_dictLast10min[id] = (-1,-1)
            lastVal = global_dictLast10min[id]        
        if (h,m) == lastVal:
            return False
        global_dictLast10min[id] = (h,m)
        return True
        
    return False
    
def clamp( x, lowerlimit = 0, upperlimit = 1 ):
    if x < lowerlimit: return lowerlimit
    if x > upperlimit: return upperlimit
    return x
    
def smoothstep( x, edge0 = 0, edge1 = 1 ):
    """
    return a smooth (sigmoide/beziers/acceleration-deceleration like) value of x, resting in the edge0/edge1 boundaries
    """
    #Scale, bias and saturate x to 0..1 range
    x = clamp( (x - edge0) / (edge1 - edge0), 0.0, 1.0)
    # -3x3 + 3x2
    return x * x * (3 - 2 * x)
    

def smootherstep( x, edge0 = 0, edge1 = 1 ):
    """
    cf smoothstep but with more accentuate curve
    """
    #Scale, bias and saturate x to 0..1 range
    x = clamp( (x - edge0) / (edge1 - edge0), 0.0, 1.0)
    # 6x5 - 15 x4 + 10 x3
    return x * x * x * (x * (x * 6 - 15) + 10)
  
def smoothererstep( x, edge0 = 0, edge1 = 1 ):
    """
    cf smoothstep but with more accentuate curve
    """
    #Scale, bias and saturate x to 0..1 range
    x = clamp( (x - edge0) / (edge1 - edge0), 0.0, 1.0)
    # -20x7 + 70 x6 - 84 x5 + 35 x4
    return x * x * x * x * (  x * ( x * ( (x*-20) +70)-84) + 35 )
    
def initPyGamePlayer():
    import pygame as pg
    FREQ = 18000   # play with this for best sound
    BITSIZE = -16  # here unsigned 16 bit
    CHANNELS = 2   # 1 is mono, 2 is stereo
    BUFFER = 1024  # audio buffer size, number of samples

    pg.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
    
def playWavPyGame( strFilename, bWaitEnd = True ):
    """
    will load the whole sound into memory before playback
    """
    try:
        import pygame as pg
        initPyGamePlayer()
        sound = pg.mixer.Sound(strFilename)
        clock = pg.time.Clock()
        sound.play()
        # how often to check active playback
        frame_rate = 30
        if bWaitEnd:
            while pg.mixer.get_busy():
                clock.tick(frame_rate)
        return True
    except BaseException as err:
        print("DBG: misctools.playWavPyGame: err: %s" % str(err) )
    return False
    
def playWav( strFilename, bWaitEnd = True ):
    """
    play a wav, return False on error
    """
    if playWavPyGame(strFilename, bWaitEnd=bWaitEnd):
        return True
        
    import winsound
    flags = winsound.SND_FILENAME
    if not bWaitEnd:
        flags |= winsound.SND_ASYNC | winsound.SND_NOSTOP
    
    try:
        import winsound
        winsound.PlaySound( strFilename, flags )
        return True
    except BaseException as err:
        print("DBG: misctools.playWav: err: %s" % str(err) )
    return False

def ting():
    """
    play a bell or a simulated one if no bell available
    """
    if playWav(getPathData()+"ting.wav"):
        return
    beep(1200, 100)
    time.sleep(200)
        
def bell():
    """
    play a bell or a simulated one if no bell available
    """
    if playWav(getPathData()+"bell.wav"):
        return
    beep(440, 100)
    time.sleep(200)
        
def deepbell():
    """
    play a bell or a simulated one if no bell available ( as deep bell is long, it's an async method !!! 
    """
    if playWav(getPathData()+"deep_bell.wav", bWaitEnd = False):
        return
    beep(330, 200)
   
def ringTheBell(nHour):
    """
    Sonne la cloche d'une certaine heure
    """
    for i in range( nHour ):
        deepbell()
        time.sleep(0.5)
    
def viewSmoothstep():
    # demo de subplot:
    # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.subplots.html#matplotlib.pyplot.subplots
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    # Data for plotting
    xlist = np.arange(-0.5, 1.5, 0.01)
    s1 = []
    s2 = []
    s3 = []
    for x in xlist:
        s1.append( smoothstep(x) )
        s2.append( smootherstep(x) )
        s3.append( smoothererstep(x) )

    fig, ax = plt.subplots()
    ax.plot(xlist, s1,label="smoothstep")
    ax.plot(xlist, s2,label="smootherstep")
    ax.plot(xlist, s3,label="smoothererstep")
    
    ax.set(xlabel='x', ylabel='y', title='smoothstep function')
    ax.grid()
    ax.legend()

    #~ fig.savefig("test.png")
    plt.show()
    
def testSound():
    if 0:
        ting()
        bell()
        deepbell()
        time.sleep(1)
        
        ringTheBell(3)
        time.sleep(2)
        ringTheBell(7)
        
    for i in range(3):
        t = time.time()
        deepbell()
        print("duration: %5.3fs" % (time.time()-t) )
        
    time.sleep(1) # time to finish some sounds
     
    
def autoTest():
    check(smoothstep(0),0)
    check(smoothstep(-1),0)
    check(smoothstep(0.5),0.5)
    check(smoothstep(0.1),0.1 * 0.1 * (3 - 2 * 0.1))
    check(smoothstep(1),1)
    check(smoothstep(2),1)
    
    
if __name__ == "__main__":
    autoTest()
    #~ viewSmoothstep()
    testSound()