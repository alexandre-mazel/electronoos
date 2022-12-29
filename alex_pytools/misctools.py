# -*- coding: cp1252 -*-
"""
some classic handy classes
(c) 2010-2022 A. Mazel
"""        
import datetime
try: import cv2 # made with cv 3.2.0-dev
except: pass
import os
import platform
import random
import select
import subprocess
import time
import sys
try: import v4l2capture  # can be found here : https://github.com/gebart/python-v4l2capture
except: pass # can be skipped if no use of v4l2 function


try: import pygame_tools
except: pass

"""
sudo apt-get install libv4l-dev
git clone https://github.com/gebart/python-v4l2capture.gitlibv4l-dev
cd python-v4l2capture/
sudo ./setup.py install
"""

global_assert_count = 0

def assert_greater(x,y):
    global global_assert_count
    global_assert_count += 1
    print( "%d: %s >= %s ?" % (global_assert_count,str(x),str(y)) )
    if x<y:
        assert(0)
        
def assert_equal(a,b):
    global global_assert_count
    global_assert_count += 1
    print( "%d: %s == %s ?" % (global_assert_count,str(a),str(b)) )
    if (a)!=(b):
        if type(b) != int:
            print("%s\n!=\n%s"%(a,b))
        else:
            print("%s != %s"%(a,b))
        print("%d: assert_equal: assert error" % global_assert_count )
        
        assert(0)
        
# FileNotFoundError definition for python 2.7
# will be accessible as common.FileNotFoundError
try:
    FileNotFoundError = FileNotFoundError # create an object common.FileNotFoundError = (global.)FileNotFoundError
except NameError:
    FileNotFoundError = IOError
        
        
def getUserHome():
    """
    return a user root folder
    """
    if os.name == "nt":
        ret = "c:/"
    else:
        ret = os.path.expanduser("~/")
    return ret
    
def getThisFilePath(strModuleName = __name__):
    """
    call me with
    - strModuleName: __name__
    """
    strLocalPath = os.path.dirname( sys.modules[__name__].__file__ )
    print( "DBG: misctools.getThisFilePath: file: %s: strLocalPath: %s" % (__name__,strLocalPath) )
    if strLocalPath == "":
        strLocalPath = "."
    if strLocalPath[-1] != '/' and strLocalPath[-1] != '\\':
        strLocalPath += os.sep
    return strLocalPath

def getPathData():
    """
    return the absolute path of electronooos/data
    """
    strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
    if strLocalPath == "": strLocalPath = './'
    ret = os.path.abspath(strLocalPath + "/../data/") + "/"
    #~ print(ret)
    return ret
    
def getPathTemp():
    """
    return a temporary folder
    """
    if os.name == "nt":
        ret = "c:/tmp/"
    else:
        ret = "/tmp/"
    return ret
    
def getPathSave():
    """
    return a nice place to save file
    """
    return getUserHome() + "save" + os.sep
    
def getTempFilename():
    return getPathTemp() + getFilenameFromTime()
    
def loadLocalEnv(strLocalFileName = ".env"):
    """
    load variable from a local file, typically .env
    Return a dict key => value
    """
    if not '/' in strLocalFileName and not '\\' in strLocalFileName:
        # transform localname to abspathname
        path = os.path.dirname(__file__)
        if path == "": path = "./"
        else: path += '/'
        strLocalFileName = path+strLocalFileName
    print( "DBG: loadLocalEnv: opening %s" % strLocalFileName)
    
    dictNewEnv = {}
    try:
        f = open(strLocalFileName,"rt")
    except FileNotFoundError as err:
        return dictNewEnv
    while 1:
        li = f.readline()
        #~ print("DBG: loadLocalEnv: line(%d): '%s'" % (len(li),li) )
        if len(li) < 1:
            break
        if li[0] =='#' or len(li)<2:
            continue
        elems = li.split("=")
        key = elems[0]
        data = elems[1]
        while data[-1] == '\n' or ord(data[-1])<14:
            data = data[:-1]
        if data[0] == '"' and data[-1] == '"':
            data = data[1:-1]
        dictNewEnv[key] = data
        #~ print("DBG: loadLocalEnv: add '%s'=>'%s'" % (key,data) )
    f.close()
    return dictNewEnv
        

def getEnv(strName, strDefault = None ):
    """
    get a value from local env, then from environnement
    """
    dLocal = loadLocalEnv() # from current dir
    try:
        return dLocal[strName]
    except:
        pass
    dLocal = loadLocalEnv(os.environ['USERPROFILE']+os.sep+".env") # from user dir
    try:
        return dLocal[strName]
    except:
        pass
    retVal = os.getenv(strName)
    if retVal == None:
        retVal = strDefault
    return retVal
    

def check(v1,v2):
    if v1==v2:
        print( "GOOD: %s == %s" % (str(v1),str(v2) ) )
        return
    print( "BAD: %s != %s" % (str(v1),str(v2) ) )
    assert(v1==v2)
    return
    
def is_string_as_integer(s):
    try:
        n=int(s)
        return True
    except ValueError:
        pass
    return False
            

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
    print("DBG: isRPI: %s" %  global_bIsRaspberry )
    return global_bIsRaspberry

global_bIsNaoqi = None
def isNaoqi():
    global global_bIsNaoqi
    if global_bIsNaoqi != None:
        return global_bIsNaoqi
    try:
        f = open("/proc/cpuinfo", "rt")
        buf=f.read()
        f.close()
    except:
        global_bIsNaoqi = False
        return global_bIsNaoqi
    print(buf)
    global_bIsNaoqi = "Geode" in buf  or "Intel(R) Atom(TM)" in buf
    print("DBG: isNaoqi: %s" %  global_bIsNaoqi )
    return global_bIsNaoqi
    
    
def getTime():
    """
    return (hour,min,second)
    """
    datetimeObject = datetime.datetime.now()
    return datetimeObject.hour, datetimeObject.minute, datetimeObject.second 

def getDay():
    """
    return (year, month, day)
    """
    datetimeObject = datetime.datetime.now()
    return datetimeObject.year, datetimeObject.month, datetimeObject.day 
    
def getDayStamp():
    """
    return a string representing the date "YYYY_MM_DD"
    """
    datetimeObject = datetime.datetime.now()
    return "%04d_%02d_%02d" % ( datetimeObject.year, datetimeObject.month,  datetimeObject.day )

def getDiffTwoDateStamp(strDayStamp1,strDayStamp2):
    """
    return diff in day between day2 (represented as DayStamp "YYYY_MM_DD") and day1
    """
    strTimeStampFormat = "%Y_%m_%d"
    datetime_object1 = datetime.datetime.strptime( strDayStamp1, strTimeStampFormat )
    datetime_object2 = datetime.datetime.strptime( strDayStamp2, strTimeStampFormat )
    return (datetime_object2-datetime_object1).days
    
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

def cleanText( txt, bEatAll = True):
    """
    remove non character from a text badly encoded
    - bEatAll: when True: remove all char not in the good range
    """
    out = ""
    for c in txt:
        if ord(c) < 254 and ord(c)>0: #255 and 254 (and 0) are specific encoding marks
            out += c
    return out

def getSystemCallReturn( strCommand ):
    f = getTempFilename()+".txt"
    #~ print("DBG: getSystemCallReturn: running '%s' into '%s'" % (strCommand,f) )
    os.system("%s>%s" % (strCommand,f) )
    #file = open(f,"rt", encoding="utf-8", errors="surrogateescape") #cp1252 on windows, latin-1 on linux system
    file = open(f,"rt")
    data = file.read()
    #~ print("DBG: getSystemCallReturn: data (1): %s" % str(data) )
    if len(data) > 0 and ord(data[0]) == 255:
        # command is of the type wmic and so is rotten in a wild burk encoding
        #~ data = data.encode("cp1252", "strict").decode("cp1252", "strict") 
        # can't find working solution for wmic => handling by hand
        data = cleanText(data)
        
        
    #~ print("DBG: getSystemCallReturn: data (2): %s" % str(data) )
    #~ data = data.decode()
    file.close()
    #~ os.unlink(f)
    return str(data)

def getCpuModel(bShort=False):
    """
    return a tuple marketing name, core name
    - bShort: if set, return only the core name
    
    # hint: have a look at cpuinfo (cache size, model, flags)
    # import cpuinfo # pip install py-cpuinfo
    # cpuinfo.get_cpu_info()
    # can be tested with: python -m cpuinfo
    """
    
    if platform.system() == "Windows":
        name1 = platform.processor()
        name2 = getSystemCallReturn( "wmic cpu get name" ).split("\n")[-3]
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        name1 = subprocess.check_output(command).strip()
        name2 = name1
        
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            #~ print("DBG: line: '%s'" % line )
            strLineToSearch = "model name"
            idx = line.find(strLineToSearch)
            if idx != -1:
                name1 = line[idx+len(strLineToSearch)+1:].strip()
                if name1[0] == ':':
                    name1 = name1[1:]
                    name1 = name1.strip()
                break
        name2 = name1
    else:
        name1, name2 =  "TODO:getCpuModel", "todo"
    if bShort: return name2
    return name1, name2
    
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
        strOut += "%d mon " % nVal;
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
    
    mToCheck = (m + nOffsetMin) % 60
        
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
    
    
def playWav( strFilename, bWaitEnd = True, rSoundVolume = 1. ):
    """
    play a wav, return False on error
    """
    import sound_player
    return sound_player.soundPlayer.playFile(strFilename, bWaitEnd = bWaitEnd, rSoundVolume=rSoundVolume)

def ting(rSoundVolume=0.10,bWaitEnd = True):
    """
    play a bell or a simulated one if no bell available
    """
    if playWav(getPathData()+"ting.wav",bWaitEnd=bWaitEnd,rSoundVolume=rSoundVolume):
        return
    beep(1200, 100)
    time.sleep(140)
    
def tic(rSoundVolume=0.10,bWaitEnd = True):
    """
    play a tic or a simulated one if no tic available
    tic is a 120ms short gentle informationnal tic
    """
    
    if playWav(getPathData()+"tic.wav",bWaitEnd=bWaitEnd,rSoundVolume=rSoundVolume):
        return
    beep(1800, 100)
    time.sleep(110)
        
def bell():
    """
    play a bell or a simulated one if no bell available
    """
    if playWav(getPathData()+"bell.wav",rSoundVolume=0.10):
        return
    beep(440, 100)
    time.sleep(200)
        
def deepbell():
    """
    play a bell or a simulated one if no bell available ( as deep bell is long, it's an async method !!! 
    """
    if playWav(getPathData()+"deep_bell.wav", bWaitEnd = False,rSoundVolume=0.10):
        return
    beep(330, 200)
   
def ringTheBell( nTimes ):
    """
    Sonne la cloche d'une certaine heure
    """
    for i in range( nTimes ):
        deepbell()
        time.sleep(2.) # was 1.3
    
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
    if 1:
        ting()
        bell()
        #~ deepbell()
        time.sleep(1)
        
        ringTheBell(3)
        time.sleep(2)
        ringTheBell(7)
        time.sleep(10)
    else:
        for i in range(3):
            t = time.time()
            deepbell()
            print("duration: %5.3fs" % (time.time()-t) )
        
    time.sleep(1) # time to finish some sounds
    
    
def levenshtein( a,b ):
    """
    Calculates the Levenshtein distance between a and b.
    from http://hetland.org/coding/python/levenshtein.py
    """

    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]
# levenshtein - end

def getPhoneticComparison( s1, s2 ):
    """
    return the phonetic equality between of two string: [0., .. 1.] : 0 completely different, from 0 to 1: the more ressembling, 1: equal]
    """
    import metaphone
    #~ print metaphone.dm( unicode(s1) )
    #~ print metaphone.dm( unicode(s2) )
    #~ print( metaphone.dm( s1 ) )
    #~ print( metaphone.dm( s2 ) )
    try:
        meta1 = metaphone.dm( s1 )[0]
        meta2 = metaphone.dm( s2 )[0]
    except BaseException as err:
        print( "ERR: can't metaphone '%s' or '%s': err: %s" % (s1, s2, err ) )
        meta1 = s1
        meta2 = s2
    if meta1 == meta2:
        return 1.

    rMidLen = ( len(meta1) + len( meta2 ) ) / 2;
    if( rMidLen < 1 ):
        return 0.
    rDist = 0.9 - levenshtein( meta1, meta2 )/float(rMidLen)
    if( rDist < 0. ):
        rDist = 0.
    return rDist
# getPhoneticComparison - end

def testPhoneticComparison():
    assert_greater( getPhoneticComparison("Julien", "juliain"), 1. )
    assert_greater( getPhoneticComparison("Dakar", "Daka"), 0.3 )
    assert_greater( getPhoneticComparison("du pain", "Dupain"), 1. )
    assert_greater( getPhoneticComparison("du pain", "Dublin"), 0.5 )
    assert_greater( getPhoneticComparison("checkin please", "chicken please"), 0.99 ) # should be less than 1. !!!
    
if 0:
    testPhoneticComparison()
    print( getPhoneticComparison("Hello", "Ho il") ) # ca devrait pas etre 1., c'est abuse !
    print( getPhoneticComparison("Hello", "Hoil") ) # ca devrait pas etre 1., c'est abuse !
    exit()
    
def getKeystrokeNotBlocking():
    """
    return 0 if not keyboard keys are waiting in the buffer, else return the key
    """
    if os.name == "nt":
        # seems to work only from cli
        import msvcrt
        if not msvcrt.kbhit():
            return 0
        return msvcrt.getch()
    print("getKeystrokeNotBlocking: NDEV linux, use select module...")
    
def isPauseRequired():
    """
    if you want to pause you're program, juste write a file in path temp nammed "pause"
    """
    f = getPathTemp() + "pause"
    try:
        file = open(f,"rt")
        file.close()
        os.unlink(f)
        return True
    except BaseException as err:
        #~ print( "DBG: isPauseRequired: err: %s" % str(err) )
        pass
    return False
    
def isExitRequired():
    """
    if you want to exit you're program, juste write a file in path temp nammed "exit"
    """
    f = getPathTemp() + "exit"
    try:
        file = open(f,"rt")
        file.close()
        os.unlink(f)
        return True
    except BaseException as err:
        #~ print( "DBG: isExitRequired: err: %s" % str(err) )
        pass
    return False
    
def getActionRequired():
    """
    if you want to bang you're program, juste write a file in path temp nammed "interact".
    return False if no action required or a string. NB: the string can be empty, then it's just a bang.
    
    """
    f = getPathTemp() + "interact"
    try:
        file = open(f,"rt")
        data = file.read()
        file.close()
        os.unlink(f)
        return data
    except BaseException as err:
        #~ print( "DBG: getActionRequired: err: %s" % str(err) )
        pass
    return False
    
    
class Cache:
    
    def __init__( self ):
        self.stored = dict()
        
    def get( self, key ):
        try:
            return self.stored[key]
        except: pass
        return False
        
    def store( self, key, data ):
        self.stored[key] = data
# class Cache - end
cache = Cache()


def getWebPage( strAddr ):
    #~ import urllib.request
    from six.moves import urllib
    fp = urllib.request.urlopen(strAddr)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    return mystr
    
def find( list, element ):
    """
    return idx of an element in a list or -1 if not found
    """
    try:
        return list.index(element)
    except ValueError as err:
        pass
    return -1
        
        
def findInNammedList( l, keyname, defaultValue = None ):
    """
    look in a list looking a bit like a dict [ ["toto", 1], ["tutu",1,2] ]
    return keyname keyname => ["toto", 1]
    """
    keyname = keyname.lower()
    for e in l:
        if e[0].lower() == keyname:
            return e
    return defaultValue
    
def findInNammedListAndGetFirst( l, keyname, defaultValue = None ):
    """
    look in a list looking a bit like a dict [ ["toto", 1], ["tutu",1,2] ]
    return keyname keyname => ["toto", 1]
    """
    keyname = keyname.lower()
    for e in l:
        if e[0].lower() == keyname:
            return e[1]
    return defaultValue
    
def shuffle( aList, n = 1 ):
    """
    choose randomly n element in list, prevent double!
    """
    assert(n<=len(aList))
    aList = aList[:] # copy
    out = []
    while 1:
        if len(out) == n:
            break
        idx = random.randint(0,len(aList)-1)
        out.append(aList[idx])
        del aList[idx]
    return out
    
    
def intToHashLike(n):
    """
    generate a hash looking like an hash from an int
    """
    codage = [chr(ord('A')+i) for i in range(26)]
    s = ""
    lencode = len(codage)
    while n>=lencode:
        r = n%26
        s = codage[r] + s
        n = n // 26
    s = codage[n] + s
    return s
     
def dictToString(d,sortByValue=False):
    o = ""
    strPlural = ""
    if len(d)>1:
        strPlural = 's'
    o +="%d item%s:\n" % (len(d),strPlural)
    funcSort = None
    if sortByValue:
        funcSort = lambda x: x[1]
    for k,v in sorted(d.items(),key=funcSort):
        o += "  %s: %s\n" % (str(k),str(v))
    return o
        
#~ print(dictToString({'2022/09/06': 120, '2022/09/07': 43, '2022/09/08': 54, '2022/09/09': 64, '2022/09/12': 91, '2022/09/13': 131},True))

def backupFile( filename ):
    """
    make a backup of a file, erase backup first.
    backup have same name than file, but a with an added .bak
    """
    if not os.path.isfile( filename ):
        # nothing to do
        return
    filenamebak = filename + ".bak"
    if os.path.isfile(filenamebak):
        os.remove(filenamebak)
    os.rename(filename,filenamebak)
    
def eraseFiles( listFiles, strPath = "" ):
    """
    Delete all file content in a list
    the list can contain absolute filename or relative filename then the path to use is strPath
    """
    print("INF: eraseFiles: erasing %d file(s)" % len(listFiles) )
    if len(listFiles) < 1:
        return
    time.sleep(4) # time for people to kill the process
    if strPath != "" and  strPath[-1] != os.sep:
        strPath += os.sep
    for f in listFiles:
        os.unlink(strPath+f)
    print("INF: eraseFiles: erasing %d file(s) - done" % len(listFiles) )
    
def isFileHasSameContent( fn1,fn2 ):
    """
    return True if content are same
    """
    # not always usefull, but can save some time
    #~ print("INF: isFileHasSameContent: comparing '%s' and '%s'" % (fn1,fn2) )
    s1 = os.path.getsize(fn1)
    s2 = os.path.getsize(fn2)
    if s1 != s2:
        return False
        
    strEncoding = "utf-8"
    strAltEncoding = "cp1252"
    strAltEncoding2 = "Latin-1"
        
    f1 = open(fn1,"r", encoding=strEncoding)
    try:
        b1 = f1.read()
    except UnicodeDecodeError as err:
        #~ print("WRN: isFileHasSameContent: got encoding error, trying another encoding.\nErr was: %s" % str(err) ) 
        f1.close()
        strEncoding = strAltEncoding
        f1 = open(fn1,"r", encoding=strEncoding)
        try:
            b1 = f1.read()
        except UnicodeDecodeError as err:
            #~ print("WRN: isFileHasSameContent: got encoding error (2), trying another encoding.\nErr was: %s" % str(err) ) 
            f1.close()
            strEncoding = strAltEncoding2
            f1 = open(fn1,"r", encoding=strEncoding)
            b1 = f1.read()
        
    f1.close()
    f2 = open(fn2,"r", encoding=strEncoding)
    try:
        b2 = f2.read() # if we got an encoding error, then the file are not the same !
    except UnicodeDecodeError as err:
        f2.close()
        return False
        
    f2.close()  
    return b1==b2    
    
def findDuplicate( strPath ):
    """
    find duplicate file in a folder
    - same size
    - same content
    Return the list of duplicate file (longest name of two)
    """
    if strPath[-1] != os.sep:
        strPath += os.sep
        
    out = []
    listFiles = os.listdir(strPath)
    print("INF: findDuplicate: sorting...")
    listFiles = sorted(listFiles, key=lambda f: os.path.getsize(strPath+f),reverse=True)
    nSizePrev = -1
    nCountSameSize = 0
    nNumFile = 0
    nNumTotalFile = len(listFiles)
    while nNumFile < len(listFiles):
        sys.stdout.write("INF: comparing %d/%d\r" % (nNumFile,nNumTotalFile))
        f = listFiles[nNumFile]
        nSize = os.path.getsize(strPath+f)
        # NB: we can have many file same size, but some are equal and some aren't
        if nSize == nSizePrev:
            nCountSameSize += 1
            #~ print("DBG: findDuplicate: file num: %s has same size than previous: nCountSameSize: %d" % (nNumFile,nCountSameSize ))
            for i in range(nCountSameSize):
                strPrevName = listFiles[nNumFile-i-1]
                if isFileHasSameContent(strPath+f,strPath+strPrevName):
                    strOrig = strPrevName
                    strDup = f
                    nToDel = nNumFile
                    if len(f)<len(strPrevName) or (len(f) == len(strPrevName) and f < strPrevName ):
                        strDup = strPrevName
                        strOrig = f
                        nToDel = nNumFile - i - 1

                    print("INF: findDuplicate: find a dup: %s - orig: %s (size:%d)" % (strDup, strOrig,nSize ) )
                    out.append( strDup )
                    # remove this one from the list, helping future comparisons
                    del listFiles[nToDel]
                    nNumFile -= 1
                    nCountSameSize -= 1

                    break #stop comparing with others
        else:
            nCountSameSize = 0
            nSizePrev = nSize
            
        nNumFile += 1
    # while - end
        
        
    print("INF: findDuplicate: duplicate in '%s': %d file(s) / %d" % (strPath, len(out), nNumTotalFile ) )
    return out
    
def guessExtension( filename ):
    """
    mainly image, but not only
    """
    import imghdr
    strExt = imghdr.what(filename)
    if strExt == "jpeg":
        strExt = "jpg"
    return strExt
    
def  correctExtension( strPath ):
    """
    correct wrong file extension in strPath
    """
    if strPath[-1] != os.sep:
        strPath += os.sep
        
    out = []
    listFiles = os.listdir(strPath)
    cpt = 0
    for f in listFiles:
        strExtDetected = guessExtension(strPath+f)
        if strExtDetected != None:
            name,ext = os.path.splitext(f)
            ext = ext.replace(".","")
            if strExtDetected != ext:
                print("INF: correcExtension: correcting %s => %s" % (f, strExtDetected) )
                newf = name+'.'+strExtDetected
                os.rename(strPath+f,strPath+newf)
                cpt += 1
    print("INF: correctExtension: corrected %d extension(s) on %d file(s)" % (cpt,len(listFiles)) ) 
  
if 0:
    strTestPath = "C:\\Users\\alexa\\Downloads\\cv_new"
    listDup = findDuplicate(strTestPath)
    eraseFiles(listDup, strTestPath)
    correctExtension(strTestPath)
    exit(0)      
    
def getCallStackStr():
    import traceback
    #~ print("DBG: getCallStackStr: stack: " + str(sys.exc_info()[2]) )
    #~ print("DBG: getCallStackStr: trace: " + str(traceback.format_exc()) )
    #~ print("DBG: getCallStackStr: trace: " + str(''.join(traceback.format_stack()) ))
    #~ print(sys.exc_info())
    #~ print(sys.exc_info()[2])
    return traceback.format_stack()
    
def printCallStack():
    a = getCallStackStr()
    print("\n*** printCallStack:")
    for i,e in enumerate(a[:-2]): # -2 to prevent printing printCallStack itself
        print("%s" % e )
    print()
    

if 0:
    # test getCallStack
    def dummy1():
        def dummy2():
            printCallStack()
        return dummy2()
            
    def dummyParent():
        dummy1()
    dummyParent()
    exit(0)
    
def isVoyelle(c):
    return c.lower() in "aeiouyéèê"
    
def elision( strFirstWord, strSecondWord ):
    if strFirstWord[-1] == 'e' and isVoyelle(strSecondWord[0]):
        return strFirstWord[:-1] + "'" + strSecondWord
    return strFirstWord + " " + strSecondWord
    
def autoTest():
    print("cpu: %s" % str(getCpuModel()) )
    check(smoothstep(0),0)
    check(smoothstep(-1),0)
    check(smoothstep(0.5),0.5)
    check(smoothstep(0.1),0.1 * 0.1 * (3 - 2 * 0.1))
    check(smoothstep(1),1)
    check(smoothstep(2),1)
    
    check(levenshtein("Alexandre", "Alexandre"),0)
    check(levenshtein("Alexandre", "Alxendr"),3)
    
    print("isRPI: %s" % isRPI())
    print("isNaoqi: %s" % isNaoqi())
    
    testPhoneticComparison()
    actionRequired = getActionRequired()
    print("getActionRequired: '%s'" % actionRequired )
    print("getActionRequired: != False: %s" % (actionRequired != False) )
    print("isPauseRequired: %s" % isPauseRequired() )
    print("isExitRequired: %s" % isExitRequired() )
    
    check(getDiffTwoDateStamp("2022_01_18","2022_02_21"),34)
    
    check(intToHashLike(0),'A')
    check(intToHashLike(1),'B')
    check(intToHashLike(26),'BA') # A is like a 0
    check(intToHashLike(27),'BB')
    check(intToHashLike(26*26*26-1),'ZZZ')
    check(intToHashLike(26*26*26),'BAAA')
    check(intToHashLike(26*26*26+1),'BAAB')
    
    check(find("ab","z"),-1)
    check(find("abezee","z"),3)
    check(find("abezee","zee"),3)
    check(find([1,2,3],3),2)
    check(find([1,2,3],None),-1)
    check(find([],"a"),-1)
    
    ret = shuffle(["a","b","c"],0)
    print("ret shuffle 0: " + str(ret))
    check(len(ret),0)
    
    ret = shuffle(["a","b","c"],2)
    print("ret shuffle 1: " + str(ret))
    check(len(ret),2)
    
    strTestPath = "./autotest_data"
    listDup = findDuplicate(strTestPath)
    assert(len(listDup)==7)
    
    assert_equal(elision("de", "Alice"), "d'Alice")
    assert_equal(elision("de", "Jean-Pierre"), "de Jean-Pierre")
    assert_equal(elision("je", "aime"), "j'aime")
    
if __name__ == "__main__":
    autoTest()
    #~ viewSmoothstep()
    #~ testSound()
