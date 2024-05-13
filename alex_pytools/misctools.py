# -*- coding: cp1252 -*-
"""
some classic handy classes
(c) 2010-2022 A. Mazel
"""
import datetime
try: import cv2 # made with cv 3.2.0-dev
except: pass
try: import numpy as np
except: print("WRN: No numpy found!")
import os
import platform
import random
import select
import subprocess
import time
import sys
try: import v4l2capture  # can be found here : https://github.com/gebart/python-v4l2capture
except: pass # can be skipped if no use of v4l2 function


#~ try: import pygame_tools
#~ except: pass

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
        
        
def getSystemHostName():
    import socket
    return socket.gethostname()
        
def getUserHome():
    """
    return a user root folder
    """
    if os.name == "nt":
        ret = "c:/"
    else:
        ret = os.path.expanduser("~/")
        if ret == '/root/':
            ret = "/tmp/"
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
    if os.name == "nt":
        ret = "c:/save/"
    else:
        ret = os.path.expanduser("~/save/")
    return ret
    
def getPathSave():
    """
    return a nice place to save file
    """
    return getUserHome() + "save" + os.sep
    
def getTempFilename():
    import threading
    return getPathTemp() + getFilenameFromTime() + "_" + str(threading.get_ident()) # if multithreading, two can have same time
    
def cleanForFilename(s):
    """
    change a string to a normal filename
    """
    o = s
    for c in " ?:/\\;*!|-=~&<>'\"":
        o = o.replace(c, "_")
    return o
    
def loadLocalEnv(strLocalFileName = ".env", bVerbose=False):
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
    if bVerbose: print( "DBG: loadLocalEnv: opening %s" % strLocalFileName)
    
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
        

def getEnv(strName, strDefault = None, bVerbose = 0 ):
    """
    get a value from local env, then from environnement
    """
    dLocal0 = loadLocalEnv("./.env",bVerbose=bVerbose) # from current dir
    try:
        return dLocal0[strName]
    except KeyError as err:
        pass
        
    dLocal1 = loadLocalEnv(bVerbose=bVerbose) # from alextools dir
    try:
        return dLocal1[strName]
    except KeyError as err:
        pass
    dLocal2 = loadLocalEnv(os.environ['USERPROFILE']+os.sep+".env",bVerbose=bVerbose) # from user dir
    try:
        return dLocal2[strName]
    except KeyError as err:
        pass
    retVal = os.getenv(strName)
    if retVal == None:
        if bVerbose: print("WRN: getEnv: key not found, dict0:\n%s\ndict1:\n%s\ndict2:\n%s" % (dLocal0,dLocal1,dLocal2) )
        retVal = strDefault
    return retVal
    

global_count_check = 0
def check(v1,v2):
    global global_count_check
    global_count_check += 1
    if v1==v2:
        print( "%s: GOOD: %s == %s" % (global_count_check,str(v1),str(v2) ) )
        return
    print( "%s: BAD: %s != %s" % (global_count_check,str(v1),str(v2) ) )
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
    global_bIsRaspberry = "Raspberry Pi" in buf or "ARMv7 Processor rev 4 (v7l)" in buf # v4 or v3
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
    
def getNumDayOfWeek(year,month,day):
    """
    return the num of week:0: lundi, 6: dimanche
    """
    given_date = datetime.datetime(year, month, day)
    return given_date.weekday()
    
def getNumWeek():
    """
    return the num of week in the year 1..52 ou 53
    """
    datetimeObject = datetime.datetime.now()
    return datetimeObject.isocalendar()[1]
    
if 0:
    print(getNumDayOfWeek(2024,3,31)) # it's a sunday => 6
    print(getNumDayOfWeek(1974,8,20)) # it's a monday => 0
    print(getNumWeek()) # current week number
    exit(1)


def getYMD(strDate):
    """
    separate a date "YYYY/MM/DD" to year, month, day
    return (year, month, day) as tuple of int
    REM: work with any separators
    """
    y = int(strDate[:4])
    m = int(strDate[5:7])
    d = int(strDate[8:10])
    
    return y,m,d
#~ print(getYMD("1974/08/19"))
#~ exit(0)

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
    
def getWeekDay():
    """
    return the number 1..7 of the day in the week (beginning on monday)
    """
    return datetime.datetime.today().weekday() + 1
"""
matlab for a given date:
day_name={'Sun','Mon','Tue','Wed','Thu','Fri','Sat'}
month_offset=[0 3 3 6 1 4 6 2 5 0 3 5];  % common year

% input date
y1=2022
m1=11
d1=22

% is y1 leap
if mod(y1,4)==0 && mod(y1,100)==0 && mod(y1,400)==0
    month_offset=[0 3 4 0 2 5 0 3 6 1 4 6];  % offset for leap year
end

% Gregorian calendar
weekday_gregor=rem( d1+month_offset(m1) + 5*rem(y1-1,4) +  4*rem(y1-1,100) + 6*rem(y1-1,400),7)

day_name{weekday_gregor+1}
"""
"""
python for a given date:
>>> import datetime
>>> datetime.datetime.today()
datetime.datetime(2012, 3, 23, 23, 24, 55, 173504)
>>> datetime.datetime.today().weekday()
"""

def getCurrentTimeZoneName():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo


def convertEpochToSpecificTimezone( timeEpoch, bRemoveNever=0 ):
    time.localtime()
    if timeEpoch == "" or timeEpoch == None:
        timeEpoch = 0
    timeEpoch = float(timeEpoch)
    if timeEpoch < 100 and not bRemoveNever:
        return "jamais"
        
    # theoriquement fromtimestamp assume que c'est en heure locale
    # mais ca ne semble pas etre le cas
    dtd = datetime.datetime.fromtimestamp(timeEpoch)
    
    # on RPI, epoch seems to be at 1h in the morning (tested during summertime)
    # we could do this patch, but then current time from time.time() is not good!
    # todo: retester en hiver !
    #~ if isRPI() and time.localtime().tm_isdst:
        #~ dtd += datetime.timedelta(hours=-2)
        
    print("DBG: convertEpochToSpecificTimezone: avant: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )
    # on lui dit que c'est de l'utc
    #~ dtd = dtd.replace(tzinfo=datetime.timezone.utc)
    try:
        dtd = dtd.astimezone(datetime.timezone.utc) # on lui dit que c'est de l'utc
    except OSError:
        # on windows, you can't ask for something before 1 janv 1h ! so hard setting manually a date
        #~ print("WRN: convertEpochToSpecificTimezone: platform (windows) error: date may be wrong...")
        return "1970/01/01: 02h00m00s" # en été, retourne 2h, sinon ? a tester en hiver
        
    #~ print("DBG: convertEpochToSpecificTimezone: apres: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )
    dtd = dtd.astimezone(getCurrentTimeZoneName()) # on le convert en local
    
    #~ print("DBG: convertEpochToSpecificTimezone: apres2: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )

        
    strTimeStamp = dtd.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def convertTimeStampToEpoch(strTimeStamp):
    """
    assume: le timestamp est celui local, et on le stocke en epoch (qui est basé sur utc heure d'hiver)
    """
    if len(strTimeStamp)<=10:
        #~ print("WRN: convertTimeStampToEpoch: only date received => adding 00h00!")
        strTimeStamp += ": 00h00m00s"
    if '_' in strTimeStamp:
        print("DBG: convertTimeStampToEpoch: converting '_' to '/'")
        strTimeStamp = strTimeStamp.replace("_","/")
    
    dtd = datetime.datetime.strptime(strTimeStamp, "%Y/%m/%d: %Hh%Mm%Ss" )
    # denaive l'heure
    #~ print("DBG: convertTimeStampToEpoch: before: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )
    dtd = dtd.replace(tzinfo=getCurrentTimeZoneName())
    # la passe en utc heure d'hiver, bug ? non semble ok
    #~ if isRPI() and time.localtime().tm_isdst:
        #~ dtd += datetime.timedelta(hours=-1)
    #~ print("DBG: convertTimeStampToEpoch: after: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )
    # le passe en utc:
    
    #~ import pytz
    #~ utc = pytz.timezone('UTC')
    #~ dtd = utc.localize(dtd)
    #~ dtd = dtd.replace(tzinfo=None)
    dtd = dtd.astimezone(datetime.timezone.utc) # convert to utc
    #~ print("DBG: convertTimeStampToEpoch: after2: time: %s, dtd.tzinfo: %s" % (dtd,dtd.tzinfo) )
    dtd = dtd.replace(tzinfo=None) # transforme en naif, on aurait pu aussi passer le 1 janvier de naif en utc
    return (dtd-datetime.datetime(1970,1,1)).total_seconds()
    
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

def getSystemCallReturnOld( strCommand ):
    # TODO: replace os.system by subprocess.call cf ping_multi
    f = getTempFilename()+".txt"
    #~ print("DBG: getSystemCallReturn: running '%s' into '%s'" % (strCommand,f) )
    os.system("%s>%s" % (strCommand,f) )
    #file = open(f,"rt", encoding="utf-8", errors="surrogateescape") #cp1252 on windows, latin-1 on linux system
    file = open(f,"rt")
    data = file.read()
    file.close()
    #~ print("DBG: getSystemCallReturn: data (1): %s" % str(data) )
    if len(data) > 0 and ord(data[0]) == 255:
        # command is of the type wmic and so is rotten in a wild burk encoding
        #~ data = data.encode("cp1252", "strict").decode("cp1252", "strict") 
        # can't find working solution for wmic => handling by hand
        data = cleanText(data)
        
        
    #~ print("DBG: getSystemCallReturn: data (2): %s" % str(data) )
    #~ data = data.decode()
    os.unlink(f)
    return str(data)
    
def getSystemCallReturn(strCommand):
    command = strCommand.split(" ")
    outfilename = getTempFilename() + ".txt"
    outfile = open(outfilename, "wt")
    ret = subprocess.call(command, stdout=outfile)
    outfile.close()
    outfile = open(outfilename, "rt")
    data = outfile.read()
    #~ print("DBG: ping: buf: %s" % buf)
    outfile.close()
    os.unlink(outfilename)
    if len(data) > 0 and ord(data[0]) == 255:
        # command is of the type wmic and so is rotten in a wild burk encoding
        #~ data = data.encode("cp1252", "strict").decode("cp1252", "strict") 
        # can't find working solution for wmic => handling by hand
        data = cleanText(data)
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
        #~ name2 = getSystemCallReturn( "wmic cpu get name" ).split("\n")[-3]
        #  a bit quicker:
        #~ name2 = subprocess.check_output(["wmic","cpu","get", "name"]).strip().decode(encoding='utf-8', errors='strict').split("\n")[1]
        name2 = subprocess.check_output(["wmic","cpu","get", "name"]).strip().decode(encoding='utf-8', errors='strict')
        idx = name2.find("\n")
        name2 = name2[idx+1:]
        
        #~ print("name1: '%s'" % name1)
        #~ print("name2: '%s'" % name2)
        if 0:
            # same info than wmic cpu, but way longer
            import cpuinfo
            name3 =  cpuinfo.get_cpu_info()['brand_raw']
            print("name3: '%s'" % name3)
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
            if idx == -1:
                strLineToSearch = "Model\t"
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
    
def getCpuTemp():
    #~ import wmi # pip install wmi
    #~ w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    #~ temperature_infos = w.Sensor()
    #~ for sensor in temperature_infos:
        #~ if sensor.SensorType==u'Temperature':
            #~ print(sensor.Name)
            #~ print(sensor.Value)
    #~ import wmi
    #~ w = wmi.WMI()
    #~ prob = w.Win32_TemperatureProbe()
    #~ print(prob)
    #~ print(prob[0].CurrentReading)
    import wmi
    w = wmi.WMI(namespace="root\wmi")
    temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
    print(temperature_info.CurrentTemperature)

#~ getCpuTemp()
#~ exit(1)
            
    
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
    
    
    
def addToDict(d,k,inc_value=1):
    """
    add a numeric value to a specific key
    """
    try:
        d[k] += inc_value
    except KeyError as err:
        d[k] = inc_value
        
def appendToDict(d,k,value,bRemoveDup):
    """
    append an element to a list in a specific key
    """
    try:
        if not bRemoveDup or not value in d[k]: # on aurait pu faire un set
            d[k].append(value)
    except KeyError as err:
        d[k] = [value]
        


    
def beep(frequency, duration):
    # duration in ms
    if isRPI():
        print("WRN: beep replaced by aplay on RPI")
        strDirHome = os.path.expanduser("~")
        print(strDirHome)
        if not os.path.isdir(strDirHome):
            strDirHome = "/home/pi"
        
        os.system("aplay %s/saw_440_100ms.wav" % strDirHome) # scp d:/sounds/saw_440_100ms.wav ...
        return
    import winsound
    winsound.Beep(frequency, duration)
    #~ try that: win32api.Beep(880,100)
    
def multiBeep(nbr):
    for i in range(nbr):
        beep(880,400)
        time.sleep(0.4)
        
def beepError(nbrError = 4):
    for i in range(nbrError):
        multiBeep(3)
        time.sleep(1)

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
    if bWaitEnd: time.sleep(0.110)
        
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
        
def microWave():
    # it's not exactly as alarm_microwave.wav (added saturation)
    for i in range(4):
        beep(2000, 500)
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

def backupFile( filename, bQuiet = 0 ):
    """
    make a backup of a file, erase backup first.
    backup have same name than file, but a with an added .bak
    """
    if not os.path.isfile( filename ) or os.path.getsize(filename)<=0:
        # nothing to do
        return
    filenamebak = filename + ".bak"
    if os.path.isfile(filenamebak):
        onedayinsec = 60*60*24
        modtime = os.path.getmtime(filenamebak)
        if not bQuiet: print("DBG: backupFile: modtime: %s" % modtime)
        if time.time() - modtime > onedayinsec:
            # fait un backup du backup
            try:
                os.rename(filenamebak,filenamebak+".time_"+ str(int(modtime)))
            except FileExistsError as err: 
                print("WRN: backupFile: rename error (1): on a deja sauvé ce fichier, et pourtant il est encore la...\nerr:%s" % err)
        else:
            os.remove(filenamebak)
    try:
        os.rename(filename,filenamebak)
    except FileExistsError as err: 
        print("WRN: backupFile: rename error (2): on a deja sauvé ce fichier, et pourtant il est encore la...\nerr:%s" % err)
    
#~ backupFile("/tmp/test.txt")
#~ exit(1)

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
    return True if content are same.
    Return False if content are different or one file isn't a file !
    """
    # not always usefull, but can save some time
    #~ print("INF: isFileHasSameContent: comparing '%s' and '%s'" % (fn1,fn2) )
    if not os.path.isfile(fn1) or not os.path.isfile(fn2):
        return False
        
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
    nTotalSizeDup = 0
    while nNumFile < len(listFiles):
        
        if nNumFile % 1000 == 0: sys.stdout.write("INF: comparing %d/%d\r" % (nNumFile,nNumTotalFile))
        f = listFiles[nNumFile]
        if not os.path.isfile(strPath+f):
            nNumFile += 1
            continue
            
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

                    nTotalSizeDup += nSize
                    if nSize > 0:
                        try:
                            print("INF: findDuplicate: find a dup: %s - orig: %s (size:%d)" % (strDup, strOrig,nSize ) )
                        except UnicodeEncodeError as err:
                            import stringtools
                            print("INF: findDuplicate: find a dup (accent removed): %s - orig: %s (size:%d)" % (stringtools.removeAccentString(strDup), stringtools.removeAccentString(strOrig),nSize ) )
                    else:
                        print("INF: findDuplicate: file empty: %s" % strDup )
                        
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
    if nTotalSizeDup >  0: print("INF: findDuplicate: total duplicated size taken: %.1fMB" % (nTotalSizeDup/1024/1024. ) )
    return out
    
def guessExtension( filename ):
    """
    mainly image, but not only.
    Return extension, eg: "jpg", "png", "pdf", ...
    Return None if unknown file
    """
    f = open(filename,"rb")
    buf = f.read(10)
    f.close()
    if len(buf)<4:
        return None
    tableHeaderFileStart = [ # pair of ext, first char
        ("pdf",b"%PDF-"),
        ("docx",b'PK\x03\x04\x14\x00\x06\x00\x08\x00'),
        ("doc",b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00'),
        ("rtf",b'{\\rtf1\\ans'),
    ]
    for pot in tableHeaderFileStart:
        ext, start = pot
        #~ print(buf[:len(start)])
        if buf[:len(start)] == start:
            return ext
            
    print("DBG: guessExtension: %s: first: %s" % (filename,buf))
        
    import imghdr
    strExt = imghdr.what(filename)
    if strExt == "jpeg":
        strExt = "jpg"
    return strExt
   
if 0:       
    s = guessExtension("C:/cvs/cvs_obo/cv__Baillard__Paola__paolabaillard06_AT_gmail_DOT_com__2022_11_17__from_obo__dnow__tvendeur__x1m__cjob__f5__e3__s74000__a_74.pdf")
    print(s)
    exit(0)
    
def correctExtension( strPath ):
    """
    correct wrong file extension in strPath
    """
    print("INF: correctExtension: starting in '%s'" % strPath)
    if strPath[-1] != os.sep:
        strPath += os.sep
        
    out = []
    listFiles = os.listdir(strPath)
    cpt = 0
    for f in listFiles:
        #~ if f[-4:].lower() == ".pdf": # skip this classical extension, sometimes we could have error on this one also
            #~ continue
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
    
def eraseFileInAnotherFolder(path1,path2):
    """
    erase file in path1 that are in path2 (same size and same contents, but date can differ)
    """
    if os.path.abspath(path1) == os.path.abspath(path2):
        print("WRN: eraseFileInAnotherFolder: path1 and path2 are the same!\n%s\n%s" % (path1,path2))
        return
    if path1[-1] != os.sep:
        path1 += os.sep

    if path2[-1] != os.sep:
        path2 += os.sep
        
    out = []
    listFiles = os.listdir(path1)
    cpt = 0
    for f in listFiles:
        fn1 = path1+f
        fn2 = path2+f
        if not os.path.isfile(fn1) or not os.path.isfile(fn2):
            continue
        n1 = os.path.getsize(fn1)
        n2 = os.path.getsize(fn2)
        if n1 != n2:
            continue
        f1 = open(fn1,"rb")
        b1 = f1.read()
        f1.close()
        f2 = open(fn2,"rb")
        b2 = f2.read()
        f2.close()
        for i in range(len(b1)):
            if b1[i] != b2[i]:
                continue
        # f1 and f2 are the same
        print("INF: eraseFileInAnotherFolder: deleting '%s' of size %d from path1, because it's in path2" % (f,n1))
        os.unlink(fn1)
        cpt += 1
    print("INF: eraseFileInAnotherFolder: erased %d file(s)" % cpt )
#~ eraseFileInAnotherFolder - end
        
    
    
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
    
class ExclusiveLock:
    # inspired by https://github.com/drandreaskrueger/lockbydir
    
    def __init__( self, lockname="alextools.lck"):
        """
            get an exclusive opening of a lock, so no other process can access a critival ressources
            call close to the returned object to release the lock
            return None if a timeout was set and impossible to get the lock
                - lockname: the lockname (will be shared among the whole system)
        """
        if os.name == "nt":
            lockdir = "/tmp/"
        else:
            #~ lockdir = "/var/www/html/obo/www/tmp/" # good for a webserver, eg apache...
            lockdir = "/tmp/" # good for a linux standard when no webserver
            
            
        self.acquired = False
            
        self.lockname = lockdir+os.path.basename(lockname) # need to be accessible from everywhere and every process
            
    def __del__( self ):
        if self.acquired:
            print("WRN:common.ExclusiveLock: releasing from ExclusiveLock.destructor '%s' " % self.lockname)
            self.release()
            
    def acquire( self, timeout = 0, bVerbose=True ):
        """
        return True if the lock is get or False if not get (timeout)
        
            - timeout: time out in sec, 0 for no timeout
            
        """
        if bVerbose: import threading
        
        timeStart = time.time()
        cptLoop = 0
        while 1:

            try:
                os.mkdir(self.lockname)
                if bVerbose: print("%s: DBG: Lock.acquire: %s: locking '%s'" % ( getTimeStamp(), threading.current_thread().ident,self.lockname))
                self.acquired = True
                return True
            except BaseException as err:
                if bVerbose: print("%s: DBG: Lock.acquire: %s: normal err: %s" % ( getTimeStamp(), threading.current_thread().ident,str(err) ) )
                pass
                
            if timeout > 0 and time.time()-timeStart > timeout:
                break
                
            time.sleep(0.05)
            cptLoop += 1
            if(cptLoop % 100) == 99: print("%s: WRN: Lock.acquire: self.lockname: %s, seems locked for a longtime?" % ( getTimeStamp(), self.lockname ) )
            
        return False
        
        
    def release(self, bForceReleaseAny = False, bVerbose = False):
        """
        bForceRelease: release even if the lock is not from himself
        """
        if bVerbose: import threading
        
        if not self.acquired and not bForceReleaseAny:
            import threading
            print("%s: ERR: Lock.release: %s: can't release an unacquired lock %s" % ( getTimeStamp(), threading.current_thread().ident,self.lockname))
            return False
        if bVerbose:
            print("%s: INF: Lock.release: %s: removing %s" % ( getTimeStamp(), threading.current_thread().ident,self.lockname) ) 
        try:
            os.rmdir(self.lockname)
        except (FileNotFoundError,OSError) as err:
            print("%s: WRN: Lock.release: %s: while removing %s: the lock is not locked" % ( getTimeStamp(), threading.current_thread().ident,self.lockname) ) 
            if not bForceReleaseAny:
                print("%s: ERR: Lock.release: Fatal in this case" % getTimeStamp())
                assert(0)
        self.acquired = False
        return True
        
    def isLocked(self):
        return self.acquired
        
    def isLockedBySomeone(self):
        """
        someone or me
        """
        return os.path.isdir(self.lockname)
        
    def isLockedBySomeoneElse(self):
        """
        someone but not me
        """
        return not self.acquired and self.isLockedBySomeone()
        
        
# class ExclusiveLock - end

    
def eraseFileLongerLine(filename,sizemax):
    """
    """
    print("INF: eraseFileLongerLine: checking file '%s' for line bigger than %s" % (filename,sizemax) )
    f = open(filename,"rt")
    lines = []
    nNumLine = 0
    nSumLine = 0
    nLineErased = 0
    nMaxLenRemaining = 0
    while 1:
        line = f.readline()
        nLenLine = len(line)
        nSumLine += nLenLine
        nNumLine += 1
        print("INF: eraseFileLongerLine: line %d: len: %d" % (nNumLine,nLenLine) )
        if nLenLine < 1:
            break
        if nLenLine > sizemax:
            print("INF: erasing this line")
            nLineErased += 1
            continue
        nMaxLenRemaining = max(nMaxLenRemaining,nLenLine)
        lines.append(line)
    f.close()
    print("INF: eraseFileLongerLine: average before erasing: %d" % (nSumLine//nNumLine))
    print("INF: eraseFileLongerLine: nLineErased: %d" % (nLineErased))
    print("INF: eraseFileLongerLine: max after erasing: %d" % (nMaxLenRemaining))
    if nLineErased > 0:
        print("INF: will write new one, waiting 5 sec so you can stop it...")
        time.sleep(5)
        f = open(filename,"wt")
        for line in lines:
            f.write(line)
        f.close()
    print("INF: eraseFileLongerLine: done")
# eraseFileLongerLine - end
    
#~ eraseFileLongerLine("/tmp/data_offers.py",10000)
#~ exit(0)


def gaussian(x):
    # inspired by https://codepen.io/zapplebee/pen/ByvmMo
    # returns values along a bell curve from 0 - 1 - 0 with an input of 0 - 1.
    # 
    # for reference:
    # midpoint: 0.31332853432887503 (js & python)
    # 
    # gaussian(0.125*0): 0.00033546262790251196 (js)    0.00033546443310615646 (python)     0.0003354645 (mega 2560)
    # gaussian(0.125*1): 0.011108996538242308 (js)          0.01110903016452842 (python)            0.0111090314 (mega 2560)
    # gaussian(0.125*2): 0.1353352832366127 (js)               0.13533546530402737 (python)            0.1353354573 (mega 2560)
    # gaussian(0.125*3): 0.6065306597126334 (js)              0.6065308637049162 (python)             0.6065308570 (mega 2560)
    # gaussian(0.125*4): 1
    # gaussian(0.90): # 0.005976043476356159 (python) 0.0059760446 (mega 2560)

    stdD = .125
    mean = .5
    pi = 3.141592653589793
    e =  2.71828
    
    def sq(a):
        return a*a

    # midpoint = 1 / (( 1/( stdD * np.sqrt(2 * pi) ) ) * pow(e , -1 * sq(0.5 - mean) / (2 * sq(stdD))));
    midpoint = 0.31332853432887503 # it's a constant !

    #~ print("midpoint: %s" % midpoint );
    #~ print("-1 * sq(x - mean): %s" % (-1 * sq(x - mean)) );

    # res =  (( 1/( stdD * np.sqrt(2 * pi) ) ) * pow(e , -1 * sq(x - mean) / (2 * sq(stdD)))) * midpoint;
    
    # precalcFirst = 1/( stdD * np.sqrt(2 * pi) )
    precalcFirst = 3.1915382432114616
    # precalcSecond = 2 * sq(stdD)
    precalcSecond = 0.03125
    
    res =  (( precalcFirst ) * pow(e , -1 * sq(x - mean) / (precalcSecond))) * midpoint;
    #~ print( "DBG: gaussian %s => %s" % (x,res) )
    return res
# gaussian - end

if 0:
    for i in range(100):
        x = i / 100.
        gaussian(x)
    for i in range(5):
        gaussian(i*0.125)
    gaussian(0.9)
        
    if 1:
        timeBegin = time.time()
        x = 1.
        for i in range(1000000):
            y = gaussian(x)
        duration = time.time() - timeBegin
        print("DBG: time gaussian: %.3fs" % duration ) 
        # mstab7 for 1 million: 3.033s; 1.581s with the optimisation of  midpoint; 0.413s with precalcFirst & Second
        # RPI 3.0 (python2): 13.63s (precalc...)
        # RPI 3.0 (python3): 11.89s (precalc...)
        # RPI 4.0 (python3): 1.870s (precalc...)
        # RPI 5.0 (python3): 0.483s (precalc...)
        # mega 2560: 2.090s for 10000, so 209.0s for 1 million

    exit(1)
    
def autoTest():
    s = str(getCpuModel())
    print("cpu: %s" % s )
    # attention ce test ne fonctionne que sur mes machines !
    if os.name == "nt":
        assert( "Intel64 Family 6 Model 126 Stepping 5, GenuineIntel" in s)
    else:
        assert( "ARMv7" in s) # RPI
    
    if 1:
        timeBegin = time.time()
        for i in range(10):
            getCpuModel()
        print("cpu model takes %.4fms per call" % ((time.time()-timeBegin)*1000/10)) 
        # depuis scite
        # 203ms per call avec un system call
        # 194ms per call avec un subprocess
        
        # depuis le shell
        # 143ms system call
        # 109ms subprocess
        
        
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
        
    check(convertEpochToSpecificTimezone(0,bRemoveNever=1),"1970/01/01: 02h00m00s") # en local ca fait 2h en été
    
    print("getCurrentTimeZoneName: %s" % getCurrentTimeZoneName() )
    check(convertTimeStampToEpoch("1974_08_19"),146095200.0)
    check(convertEpochToSpecificTimezone(146095200+90),"1974/08/19: 00h01m30s")
    
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
    assert(len(listDup)==8)
    
    assert_equal(elision("de", "Alice"), "d'Alice")
    assert_equal(elision("de", "Jean-Pierre"), "de Jean-Pierre")
    assert_equal(elision("je", "aime"), "j'aime")
    
    for i in range(1,7):
        assert("pdf"==guessExtension("autotest_data/cv_%d.pdf"%i))
        
    for i in range(1,3):
        assert("docx"==guessExtension("autotest_data/cv_%d.docx"%i))
        
    for i in range(1,2):
        assert("doc"==guessExtension("autotest_data/cv_%d.doc"%i))

    for i in range(1,2):
        assert("rtf"==guessExtension("autotest_data/cv_%d.rtf"%i))
        
    assert(None==guessExtension("autotest_data/empty_file"))
    
    
    
    print("current time is (assert with your eyes): %s" % convertEpochToSpecificTimezone(time.time()) )
    
    
if __name__ == "__main__":
    autoTest()
    #~ viewSmoothstep()
    #~ testSound()
    
    if 0:
        # clean some folder:
        strPath = "D:/tmp_from_c/"
        strPath = "D:/tmp_from_ms4/tmp/"
        strPath = "D:/tmp_from_ms4/tmp_scr/"
        strPath = "c:/scr/"
        #~ strPath = "c:/Users/alexa/downloads/"
        
        listDup = findDuplicate(strPath)
        #~ eraseFiles(listDup, strPath)
