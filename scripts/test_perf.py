# -*- coding: cp1252 -*- 
# cp1252 ou utf-8

#
# Sound Acceptance test
# v0.81: add core handling
#
# Author: A. Mazel

import sys
import os
import struct
import time
import multiprocessing

import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
strLocalPath += "/../alex_pytools/"
#~ print("DBG: adding to path: '%s'" % strLocalPath )
sys.path.append(strLocalPath )
try: import misctools # just for cpumodel
except Exception as err: print("WRN: importing misctools => err: %s" % str(err))

def getFreeDiskSpace():
    """
    return current disk space in bytes
    """
    if os.name == 'posix':
        s = os.statvfs('/')
        nSize = (s.f_bavail * s.f_frsize)
        return nSize
    try:
        import psutil # pip install psutil
        usa = psutil.disk_usage('/')
        return usa.free
    except ImportError as err: pass
    return -1


class FlushableFile:
    """
    A flushable multi os multi python version file encapsulation
    """
    def __init__( self, strFilename, strMode ):
        import platform
        self.bWindows = "windows" in platform.system().lower()
        if self.bWindows:
            import win32file # pip install pywin32
            flag = win32file.GENERIC_READ
            if 'w' in strMode:
                flag = win32file.GENERIC_WRITE
            elif'a' in strMode:
                flag = win32file.GENERIC_APPEND
            self.handle = win32file.CreateFile( strFilename, flag, 0, None,  win32file.CREATE_ALWAYS, win32file.FILE_ATTRIBUTE_NORMAL, None )
        else:
            self.handle = open(strFilename, strMode)
            
    def read( self, nSize = 0 ):
        if self.bWindows:
            import win32file
            return win32file.ReadFile( self.handle, nSize )
        return self.handle.read(nSize)
    
    def write( self, data ):
        if self.bWindows:
            import win32file
            #~ print(dir(win32file))
            return win32file.WriteFile( self.handle, data.encode("ascii"), None)
        return self.handle.write(data)
        
    def flush( self ):
        if self.bWindows:
            import win32file
            try:
                #~ print("flush 1")
                win32file.FlushFileBuffers( self.handle )
                #~ print("flush 2")
                #~ os.fsync( win32file._get_osfhandle(self.handle) ) # _get_osfhandle to go from fd from file.open() to system handle not from this win32 handle...
                #~ print("flush 3")
                pass
            except win32file.error as err:
                #~ print("WRN: flush: during flush error: %s" % str(err) )
                pass
            return

        self.handle.flush()
        os.fsync(self.handle.fileno())
        
    def close( self ):
        if self.bWindows:
            import win32file
            win32file.CloseHandle( self.handle )
            self.handle = None
            return
        self.handle.close()  
        self.handle = None        
        
# class FlushableFile - end


def clear_caches():
    if os.name != 'posix':
        return;
    cmd1 = 'sudo sync'
    cmd2 = 'sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"'
    os.popen(cmd1)
    os.popen(cmd2)
    

def print_version():
    print( "python version   : %d.%d.%d (%dbits) (%d core(s))" % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro,8 * struct.calcsize("P"),multiprocessing.cpu_count()) )
    
def print_cpu():
    try:
        strCpuModel = misctools.getCpuModel(bShort=True)
    except BaseException as err:
        print("ERR: %s" % err)
        strCpuModel = "TODO"
    print( "cpu              : %s" % strCpuModel )
    
def print_ram():
    GB=1024*1024*1024.
    try:
        import psutil
        infomem = psutil.virtual_memory()
        avail = infomem.available
        tot = infomem.total
        #~ avail = tot-avail # seems like it's reverted at least on raspberry [but not exactly !?!]
        print("ram              : %.2f / %.2f GB" % (avail/GB,tot/GB))
        #~ raise("toto") # to test the exception code check
    except BaseException as err:
        #~ print("ERR: %s" % err)
        import os
        avail = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES') 
        tot = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') 
        print("ram              : %.2f / %.2f GB" % (avail/GB,tot/GB))

    
def test_cpu_int( bPrint = True ):
    if bPrint: sys.stdout.write( "test_cpu_int2    : " )
    timeBegin = time.time();
    x = 18
    for i in range( 20 ):
        for i in range(4000):
            x *= 13;
        if bPrint: sys.stdout.write( "#" );
        if bPrint: sys.stdout.flush();
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs" % rDuration);
    return rDuration;
#test_cpu_int - end

def test_cpu_float( bPrint = True ):
    if bPrint: sys.stdout.write( "test_cpu_float2  : " )
    timeBegin = time.time();
    x = 18.2
    for i in range( 20 ):
        for i in range(100000):
            x *= 13.5;
        if bPrint: sys.stdout.write( "#" );
        if bPrint: sys.stdout.flush();
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs" % rDuration);
    return rDuration;
#test_cpu_float - end

def test_crypt( bPrint = True ):
    try:
        import bcrypt
    except:
        if bPrint: print( "bcrypt        : not found")
        return 0
        
    if bPrint: sys.stdout.write( "test_crypt       : " )
    timeBegin = time.time();
    x = 18.2
    for i in range( 20 ):
        password = "cazaekncecd".encode()
        salt ="$2b$12$DTK1eFh7Xf5IJcHwDjy7x.".encode()
        bcrypt.hashpw(password,salt)
        if bPrint: sys.stdout.write( "#" );
        if bPrint: sys.stdout.flush();
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs" % rDuration);
    return rDuration;
#test_crypt - end

def test_ram( sizeGB = 1, bPrint = True ):
    try:
        import numpy
        import numpy.random
    except:
        if bPrint: print( "numpy        : not found")
        return 0
    if bPrint: sys.stdout.write( "test_cpu_ram%2dG  : " % sizeGB )
    if bPrint: sys.stdout.flush();
    timeBegin = time.time();
    try:
        a = []
        b = []
        size_packet = sizeGB * 1024*1024//4//2 # div by 4 because 32bits, div by 2 because we alloc 2 arrays
        a = numpy.zeros((1024,size_packet),dtype=numpy.uint32)
        if bPrint: sys.stdout.write( "#" )
        if bPrint: sys.stdout.flush()
        
        if 0:
            b = a.copy()
            
            if bPrint: sys.stdout.write( "#"*19 )
            if bPrint: sys.stdout.flush()
        else:
            # plus lent, mais on voit la progression
            b = numpy.zeros((1024,size_packet),dtype=numpy.uint32)
            if bPrint: sys.stdout.write( "#" )
            if bPrint: sys.stdout.flush()
            j = 0
            while j < 1024:
                i = 0
                #~ while i < size_packet:
                    #~ a[j,i] = b[j,i]
                    #~ i += 1
                b[j,] = a[j,]
                j += 1
                if (j %55)==54:
                    if bPrint: sys.stdout.write( "#" );
                    if bPrint: sys.stdout.flush();
        rDuration = time.time() - timeBegin;
        if bPrint: print("%7.2fs" % rDuration);
    #~ except numpy.core._exceptions.MemoryError as err:
    except BaseException as err:
        #~ print("Memory Error: %s" % err )
        print(" Memory Error..." )
        rDuration = 0
    return rDuration;
#test_ram - end

def test_numpy( bPrint = True ):
    try:
        import numpy
        import numpy.random
    except:
        if bPrint: print( "numpy        : not found")
        return 0

    try:
        import scipy.fftpack
    except:
        if bPrint: print( "scipy.fftpack    : not found")
        return 0
        
    
    if bPrint: sys.stdout.write( "test_scipy_xxt   : " )
    timeBegin = time.time();
    nLengthSec = 10
    for i in range(20):
        nSizeArray = nLengthSec*48000*2
        n = numpy.random.randint( -32000,32000+1,nSizeArray)
        res = scipy.fftpack.fft(n)
        n = numpy.zeros(nSizeArray, dtype=numpy.float64) # was numpy.float => float or numpy.float64
        res = scipy.fftpack.dct(n)
        if bPrint: sys.stdout.write( "#" );
        sys.stdout.flush();
    
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs (%5.2fx)" % (rDuration,(20*10*2)/rDuration));
    return rDuration;
    
def test_opencv_orb( bPrint = True ):
    try:
        import cv2
    except:
        if bPrint: print( "opencv (for orb)      : not found")
        return 0
        
    import math
    import numpy
    
    if bPrint: sys.stdout.write( "test_orb%-9s: " % cv2.__version__ )
    h = 640
    w = 480    
    img = numpy.zeros((h,w,1), numpy.uint8)
    for j in range(h):
        for i in range(w):
            img[j,i,0] = (math.sin(w*h)*1000) % 256
    
    timeBegin = time.time();
    for i in range(20):
        nFramePerRound = 5
        for j in range(nFramePerRound):
            try:
                # opencv3
                orb = cv2.ORB_create()            
                kp = orb.detect(img,None)
                kp, des = orb.compute(img, kp)            
            except:
                # opencv2
                detector = "ORB"
                descriptor = "ORB"
                nfeatures = 2000 # No way to pass to detector...?
                detector = cv2.FeatureDetector_create(detector)
                descriptorExtractor = cv2.DescriptorExtractor_create(descriptor)
                keypoints = detector.detect(img)
                (keypoints, descriptors) = descriptorExtractor.compute(img, keypoints)
        if bPrint: sys.stdout.write( "#" );
        sys.stdout.flush();
    
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs (%5.2ffps)" % (rDuration, (20*nFramePerRound)/rDuration));
    return rDuration;
    
bFirstTime=True
def test_opencv_orb_realcase( bPrint = True ):
    try:
        import cv2
    except:
        if bPrint: print( "opencv (orb)    : not found")
        return 0
        
    import math
    import numpy
    
    global bFirstTime
    if bFirstTime:
        bFirstTime = False
        if bPrint: sys.stdout.write( "test_orbcv imgs  : " )
    else:
        if bPrint: sys.stdout.write( "test_orbcv bis   : " )
    h = 640
    w = 480    
    img = numpy.zeros((h,w,1), numpy.uint8)
    for j in range(h):
        for i in range(w):
            img[j,i,0] = (math.sin(w*h)*1000)% 256
    
    try:
        img1 = cv2.imread( "test_perf_vga_01.png" )
        img2 = cv2.imread( "test_perf_vga_02.png" )
        if img1 is None or img2 is None:
            raise BaseException("")
    except:
        if bPrint: print( "test_perf_vga_*.png: not found")
        return 0
    timeBegin = time.time();
    bOpenCV3 = True
    
    try:
        # opencv3
        orb = cv2.ORB_create()            
    except:
        # opencv2
        bOpenCV3 = False
        detector = "ORB"
        descriptor = "ORB"
        detector = cv2.FeatureDetector_create(detector)
        descriptorExtractor = cv2.DescriptorExtractor_create(descriptor)
   
    for i in range(20):
        nFramePerRound = 5
        for j in range(nFramePerRound):
            if (j & 1) == 0:
                img = img1.copy()
            else:
                img = img2.copy()
            if bOpenCV3:
                kp = orb.detect(img,None)
                kp, des = orb.compute(img, kp)
            else:
                keypoints = detector.detect(img)
                (keypoints, descriptors) = descriptorExtractor.compute(img1, keypoints)
        if bPrint: sys.stdout.write( "#" );
        sys.stdout.flush();
    
    rDuration = time.time() - timeBegin;
    if bPrint: print("%7.2fs (%5.2ffps)" % (rDuration, (20*nFramePerRound)/rDuration));
    return rDuration;    

        

def test_disk_write( nMB=200, nPacketSize = 1024 ):
    sys.stdout.write( "disk_write %4dKB: " %  (nPacketSize/1024) )
    timeBegin = time.time();
    file = FlushableFile( "temp.tmp", "w" );
    nTimePerLoop = int(1024*1024*nMB / (20*nPacketSize));
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            file.write( "A" * nPacketSize );
        sys.stdout.write( "#" );
        sys.stdout.flush();
    file.flush();
    file.close();
    rDuration = time.time() - timeBegin;
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*nPacketSize/(rDuration*1024*1024)));
    return rDuration;
#test_disk_write - end
        
        
        
def test_disk_read( nMB=200, nPacketSize = 1024 ):
    sys.stdout.write( "disk_read  %4dKB: " %  (nPacketSize/1024) )
    clear_caches()
    timeBegin = time.time();
    file = FlushableFile( "temp.tmp", "r" );
    nTimePerLoop = int(1024*1024*nMB / (20*nPacketSize));
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            dummy = file.read(1*nPacketSize);
        sys.stdout.write( "#" );
        sys.stdout.flush();
    file.flush();
    strMsg = ""
    #~ try:
        #~ strMsg = "";
        #~ os.fsync(file.fileno()); 
    #~ except BaseException as err:
        #~ strMsg = "ERR: test_disk_read: while fsyncing: %s" % str(err);
    file.close();
    rDuration = time.time() - timeBegin;
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*nPacketSize/(rDuration*1024*1024)));
    if( strMsg != "" ):
        print( strMsg )
    return rDuration;
#test_disk_read - end

def simple_test(bToto):
    print("test!!!")

def test_multithreading():
    # It shows us that
    import platform
    if platform.system() == 'Windows' or 0:
        return 0

    rTotalDuration = 0
    for nNbrProcessInParalell in [1,4,8,32]:
        sys.stdout.write( "multiprocess x%-2d:" % nNbrProcessInParalell  )    
        bFirstInLine = True
        all_process = []
        for func_to_test in (test_cpu_int,test_cpu_float,test_crypt, test_numpy,test_opencv_orb,test_opencv_orb_realcase,test_opencv_orb_realcase):
            if not bFirstInLine: sys.stdout.write(" /" )
            bFirstInLine = False
            timeBegin = time.time()        
            for i in range(nNbrProcessInParalell):
                p = multiprocessing.Process(target=func_to_test, args=(False,))
                p.start()
                all_process.append(p)
            # wait for the last one to finish
            for p in all_process:
                p.join()
            rDuration = time.time() - timeBegin
            sys.stdout.write("%6.2fs" % rDuration)
            sys.stdout.flush()
            rTotalDuration += rDuration
        print(" => %7.2fs (per thread:%.2fs)" % (rTotalDuration,rTotalDuration/nNbrProcessInParalell ) )
    return rTotalDuration
    

def test_perf(nDiskTestSizeMB=200,bTestMultiThreading=True):
    print_version()
    print_cpu()
    print_ram()
    rTotalTime = 0;
    rTotalTime += test_cpu_int();
    rTotalTime += test_cpu_float();
    rTotalTime += test_crypt();
    rTotalTime += test_ram(2);
    rTotalTime += test_ram(4);
    rTotalTime += test_ram(6);
    rTotalTime += test_ram(8);
    rTotalTime += test_ram(10);
    rTotalTime += test_ram(12);
    rTotalTime += test_ram(14);
    rTotalTime += test_ram(16);
    rTotalTime += test_numpy();
    rTotalTime += test_opencv_orb();
    rTotalTime += test_opencv_orb_realcase();
    rTotalTime += test_opencv_orb_realcase(); # because on some computer the previous one takes time initialise stuffs
    if bTestMultiThreading:
        # multithreading
        rTotalTime += test_multithreading();
            
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB, nPacketSize=1024);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB, nPacketSize=1024);
    
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB, nPacketSize=1024*1024);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB, nPacketSize=1024*1024);
    
    os.unlink( "temp.tmp" );
# test_perf - end
    
"""
Syntaxe: <script_name> [size of disk test in MB] [no_multithreading]
"""
nDiskTestSizeMB = 1000;
bMultitreading = True
if( len(sys.argv)> 1 ):
    for i in range( 1, len(sys.argv)):
        if sys.argv[i].isdigit():
            nDiskTestSizeMB=int(sys.argv[i]);
            print( "INF: Changing disk test size to %d MB" % nDiskTestSizeMB );
        elif "multi" in sys.argv[i].lower() or "thread" in sys.argv[i].lower(): 
            bMultitreading = False
    
if getFreeDiskSpace() /(1024*1024) < nDiskTestSizeMB:
    nDiskTestSizeMB = int( (getFreeDiskSpace()*0.9)/(1024*1024) )
    print( "INF: Due to low empty disk space, reducing disk test size to %d MB" % nDiskTestSizeMB );
    
test_perf(nDiskTestSizeMB=nDiskTestSizeMB,bTestMultiThreading=bMultitreading);

#####################################
"""

*** Some results sur la Surface Pro 4 ***

C:>python test_perf.py
INF: Due to low empty disk space, reducing disk test size to 373 MB
python version   : 3.8.2 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.04s
test_cpu_float2  : ####################   0.48s
scipy.fftpack    : not found
test_orb4.2.0    : ####################   0.42s (240.35fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  22.77s (16.38 Mo/s)
disk_read     1KB: ####################   1.56s (238.94 Mo/s)
disk_write 1024KB: ####################   9.49s (37.95 Mo/s)
disk_read  1024KB: ####################   0.20s (1797.94 Mo/s)

therm_test (blob detection et threshold) sur images_thermal_from_sbre_accueil:
INF: detectHuman total: 2274 file(s), duration:  6.38s, im/sec: 356.67 (en ligne de commande)
INF: detectHuman total: 2274 file(s), duration:  2.43s, im/sec: 934.42 (depuis scite (buffering output)
INF: detectHuman total: 2274 file(s), duration:  2.15s, im/sec: 1058.93 (en ligne de commande > tutu)

c:>python c:test_perf.py
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.03s
test_cpu_float2: ####################   0.47s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.34s (290.88fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: ####################   9.55s (19.98 Mo/s)
test_disk_read : ####################   6.55s (29.13 Mo/s)


C:>python test_perf.py 5000
Changing disk test size to 5000 MB
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.36s
test_cpu_float2: ####################   0.50s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.38s (266.61fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: #################### 232.90s (20.47 Mo/s)
test_disk_read : #################### 154.94s (30.78 Mo/s)


SD 128
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.19s
test_cpu_float2: ####################   0.48s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.36s (278.07fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: ####################  25.77s ( 7.40 Mo/s)
test_disk_read : ####################   6.02s (31.68 Mo/s)



D:>python c:test_perf.py
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.02s
test_cpu_float2: ####################   0.48s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.36s (278.26fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: ####################  15.38s (12.40 Mo/s)
test_disk_read : ####################   5.83s (32.72 Mo/s)


USB NVIDIA
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.05s
test_cpu_float2: ####################   0.48s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.36s (278.23fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: ####################  30.93s ( 6.17 Mo/s)
test_disk_read : ####################   6.11s (31.22 Mo/s)

Changing disk test size to 4000 MB
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2  : ####################   1.03s
test_cpu_float2: ####################   0.45s
scipy.fftpack: not found
test_orb4.2.0  : ####################   0.40s (248.76fps)
test_orbcv imgs: test_perf_vga_*.png: not found
test_orbcv bis : test_perf_vga_*.png: not found
test_disk_write: #################### 562.11s ( 6.79 Mo/s)
test_disk_read : #################### 123.60s (30.86 Mo/s)


D:/>python c:test_perf.py
INF: Due to low empty disk space, reducing disk test size to 439 MB
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.06s
test_cpu_float2  : ####################   0.45s
scipy.fftpack    : not found
test_orb4.2.0    : ####################   0.36s (278.26fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  21.37s (20.55 Mo/s)
disk_read     1KB: ####################   1.58s (278.03 Mo/s)
disk_write 1024KB: ####################  17.76s (23.65 Mo/s)
disk_read  1024KB: ####################   0.20s (2069.58 Mo/s)

SSD
python version   : 3.8.2 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.03s
test_cpu_float2  : ####################   0.45s
scipy.fftpack    : not found
test_orb4.2.0    : ####################   0.36s (278.23fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################   9.49s (105.35 Mo/s)
disk_read     1KB: ####################   3.72s (268.89 Mo/s)
disk_write 1024KB: ####################   7.05s (141.80 Mo/s)
disk_read  1024KB: ####################   0.47s (2134.67 Mo/s)


SD128
INF: Due to low empty disk space, reducing disk test size to 439 MB
python version : 3.8.2 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.06s
test_cpu_float2  : ####################   0.45s
scipy.fftpack    : not found
test_orb4.2.0    : ####################   0.36s (278.26fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  21.37s (20.55 Mo/s)
disk_read     1KB: ####################   1.58s (278.03 Mo/s)
disk_write 1024KB: ####################  17.76s (23.65 Mo/s)
disk_read  1024KB: ####################   0.20s (2069.58 Mo/s)

USB nvidia
python version   : 3.8.2 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.05s
test_cpu_float2  : ####################   0.45s
scipy.fftpack    : not found
test_orb4.2.0    : ####################   0.36s (278.23fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: #################### 154.01s ( 6.49 Mo/s)
disk_read     1KB: ####################   4.83s (207.25 Mo/s)
disk_write 1024KB: #################### 144.02s ( 6.94 Mo/s)
disk_read  1024KB: ####################   1.58s (633.58 Mo/s)



therm_test (blob detection et threshold) sur images_thermal_from_sbre_accueil:
INF: detectHuman total: 2274 file(s), duration:  6.46s, im/sec: 352.01 (en ligne de commande)
INF: detectHuman total: 2274 file(s), duration:  2.12s, im/sec: 1072.19 (en ligne de commande >tutu)




Raspberry3:

Use raspi-config to set the country before use.

pi@rasp3thermal:~ $ python3 therm_test.py
python3: can't open file 'therm_test.py': [Errno 2] No such file or directory
pi@rasp3thermal:~ $ python test_perf.py
python version   : 2.7.16 (32bits) (4 core(s))
test_cpu_int2    : #################### 327.49s
test_cpu_float2  : ####################   0.95s
scipy.fftpack    : not found
test_orb3.2.0    : ####################   2.70s (37.08fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  80.71s (12.39 Mo/s)
disk_read     1KB: ####################  46.41s (21.55 Mo/s)
disk_write 1024KB: ####################  79.09s (12.64 Mo/s)
disk_read  1024KB: ####################  44.53s (22.45 Mo/s)
pi@rasp3thermal:~ $ python test_perf.py
python version   : 2.7.16 (32bits) (4 core(s))
test_cpu_int2    : ####################   5.60s
test_cpu_float2  : ####################   0.94s
scipy.fftpack    : not found
^C^C^Copencv  : not found
test_orbcv imgs  : test_perf_vga_*.png: not found
^Ctest_orbcv bis   : Traceback (most recent call last):
  File "test_perf.py", line 379, in <module>
    test_perf(nDiskTestSizeMB=nDiskTestSizeMB);
  File "test_perf.py", line 356, in test_perf
    rTotalTime += test_opencv_orb_realcase(); # because on some computer the previous one takes time initialise stuffs
  File "test_perf.py", line 224, in test_opencv_orb_realcase
    img[j,i,0] = math.sin(w*h)*1000
KeyboardInterrupt
^C
pi@rasp3thermal:~ $ python3 test_perf.py
python version   : 3.7.3 (32bits) (4 core(s))
test_cpu_int2    : ####################   5.59s
test_cpu_float2  : ####################   1.02s
numpy        : not found
opencv  : not found
opencv: not found
opencv: not found
disk_write    1KB: ####################  79.74s (12.54 Mo/s)
disk_read     1KB: ####################  46.46s (21.53 Mo/s)





*** biga ***

am@biga:~$ sudo python test_perf.py
python version   : 2.7.12 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.55s
test_cpu_float2  : ####################   0.13s
scipy.fftpack    : not found
test_orb2.4.9.1  : ####################   0.29s (347.60fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  12.05s (82.98 Mo/s)
disk_read     1KB: ####################  11.55s (86.58 Mo/s)
disk_write 1024KB: ####################  10.57s (94.59 Mo/s)
disk_read  1024KB: ####################   9.88s (101.20 Mo/s)

am@biga:~$ sudo python3 test_perf.py
python version   : 3.5.2 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.54s
test_cpu_float2  : ####################   0.15s
numpy        : not found
opencv  : not found
opencv: not found
opencv: not found
disk_write    1KB: ####################  12.30s (81.28 Mo/s)
disk_read     1KB: ####################  10.74s (93.13 Mo/s)
disk_write 1024KB: ####################  11.36s (88.00 Mo/s)
disk_read  1024KB: ####################   0.77s (1291.93 Mo/s)


*** biga ubuntu18, ssd 120Go ***

python version   : 2.7.17 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.57s
test_cpu_float2  : ####################   0.11s
scipy.fftpack    : not found
test_orb3.2.0    : ####################   0.26s (387.43fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  18.50s (54.06 Mo/s)
disk_read     1KB: ####################   4.80s (208.50 Mo/s)
disk_write 1024KB: ####################  16.43s (60.86 Mo/s)
disk_read  1024KB: ####################   4.30s (232.83 Mo/s)

python version   : 3.6.9 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.58s
test_cpu_float2  : ####################   0.13s
scipy.fftpack    : not found
test_orb3.2.0    : ####################   0.27s (365.51fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  15.39s (65.00 Mo/s)
disk_read     1KB: ####################   4.82s (207.60 Mo/s)
disk_write 1024KB: ####################  14.99s (66.69 Mo/s)
disk_read  1024KB: ####################   3.60s (277.75 Mo/s)
am@amT7500:~/dev/git/electronoos$ nano scripts/test_perf.py 

python version   : 3.6.9 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.57s
test_cpu_float2  : ####################   0.13s
scipy.fftpack    : not found
test_orb3.2.0    : ####################   0.27s (369.71fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
multiprocess x4 :  0.82s /  0.23s /  0.01s /  0.67s / 0.22s /  0.25s =>    2.22s
multiprocess x8 :  1.18s /  0.32s /  0.02s /  0.95s /  0.33s /  0.34s =>    5.35s
multiprocess x32:  4.30s /  1.06s /  0.06s /  3.53s /  1.21s /  1.20s =>   16.71s
disk_write    1KB: ####################  18.05s (55.41 Mo/s)
disk_read     1KB: ####################   4.77s (209.54 Mo/s)
disk_write 1024KB: ####################  13.26s (75.44 Mo/s)
disk_read  1024KB: ####################   4.32s (231.54 Mo/s)


*** Raspberry1-web ***
(sd card de 32Go)

pi@rasp2 ~/dev/git $ python ~/test_perf.py
python version   : 2.7.3 (32bits) (1 core(s))
test_cpu_int2    : ####################  22.58s
test_cpu_float2  : ####################   4.33s
scipy.fftpack    : not found
test_orb2.4.1    : ####################   9.60s (10.41fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: #################### 113.29s ( 8.83 Mo/s)
disk_read     1KB: ####################  63.54s (15.74 Mo/s)
disk_write 1024KB: ####################  97.65s (10.24 Mo/s)
disk_read  1024KB: ####################  60.82s (16.44 Mo/s)

pi@rasp2 ~/dev/git $ sudo python3 ~/test_perf.py
python version   : 3.2.3 (32bits) (1 core(s))
test_cpu_int2    : ####################  22.83s
test_cpu_float2  : ####################   6.68s
scipy.fftpack    : not found
opencv           : not found
opencv           : not found
opencv: not found
disk_write    1KB: #################### 151.80s ( 6.59 Mo/s)
disk_read     1KB: #################### 234.50s ( 4.26 Mo/s)
disk_write 1024KB: #################### 106.76s ( 9.37 Mo/s)
disk_read  1024KB: #################### 222.23s ( 4.50 Mo/s)



*** Raspberry3-ree ***

pi@robot-enhanced-education:~/dev/git/electronoos $ python scripts/test_perf.py 
INF: Due to low empty disk space, reducing disk test size to 290 MB
python version   : 2.7.13 (32bits) (4 core(s))
test_cpu_int2    : ####################  15.37s
test_cpu_float2  : ####################   2.79s
scipy.fftpack    : not found
test_orb3.3.0    : ####################   5.98s (16.71fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  32.02s ( 9.06 Mo/s)
disk_read     1KB: ####################  15.61s (18.57 Mo/s)
disk_write 1024KB: ####################  29.93s ( 9.36 Mo/s)
disk_read  1024KB: ####################  15.84s (17.68 Mo/s)

therm_test (blob detection et threshold) sur images_thermal_from_sbre_accueil:
INF: detectHuman total: 2274 file(s), duration: 25.80s, im/sec: 88.13 (cli)
INF: detectHuman total: 2274 file(s), duration: 24.30s, im/sec: 93.57 (cli>tutu)


pi@robot-enhanced-education:~/dev/git/electronoos $ python3 scripts/test_perf.py
INF: Due to low empty disk space, reducing disk test size to 557 MB
python version   : 3.5.3 (32bits) (4 core(s))
test_cpu_int2    : ####################  10.64s
test_cpu_float2  : ####################   2.83s
scipy.fftpack    : not found
opencv  : not found
opencv: not found
opencv: not found
disk_write    1KB: ####################  59.25s ( 9.40 Mo/s)
disk_read     1KB: ####################  38.92s (14.31 Mo/s)
disk_write 1024KB: ####################  59.05s ( 9.15 Mo/s)
disk_read  1024KB: ####################  35.36s (15.27 Mo/s)

therm_test (blob detection et threshold) sur images_thermal_from_sbre_accueil:
INF: detectHuman total: 2274 file(s), duration: 20.95s, im/sec: 108.56 (cli)
INF: detectHuman total: 2274 file(s), duration: 19.63s, im/sec: 115.82 (cli>tutu)




*** Raspberry4-therm ***

pi@raspberrypi:~/dev/git/electronoos/scripts $ python test_perf.py
python version   : 2.7.16 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.28s
test_scipy_xxt   : ####################   6.99s (57.19x)
test_orb3.2.0    : ####################   1.34s (74.62fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
multiprocess x1 :  1.73s /  0.29s /  0.01s /  0.01s /  0.01s /  0.01s =>    2.06s
multiprocess x4 :  1.76s /  0.36s /  0.02s /  0.02s /  0.02s /  0.02s =>    4.26s
multiprocess x8 :  3.51s /  0.75s /  0.03s /  0.03s /  0.03s /  0.03s =>    8.64s
multiprocess x32: 14.27s /  2.99s /  0.11s /  0.11s /  0.11s /  0.11s =>   26.33s
disk_write    1KB: ####################  83.26s (12.01 Mo/s)
disk_read     1KB: ####################  24.85s (40.24 Mo/s)
disk_write 1024KB: ####################  78.17s (12.79 Mo/s)
disk_read  1024KB: ####################  22.93s (43.62 Mo/s)
# sur la sandisk 64Go:
disk_write    1KB: ####################  34.41s (29.06 Mo/s)
disk_read     1KB: ####################  24.42s (40.95 Mo/s)
disk_write 1024KB: ####################  35.02s (28.56 Mo/s)
disk_read  1024KB: ####################  22.90s (43.68 Mo/s)


pi@raspberrypi:~/dev/git/electronoos/scripts $ LD_PRELOAD=/usr/lib/gcc/arm-linux-gnueabihf/8/libatomic.so python3 test_perf.py
python version   : 3.7.3 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.26s
test_scipy_xxt   : ####################   8.82s (45.35x)
test_orb4.1.1    : ####################   1.12s (88.94fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
multiprocess x1 :  1.76s /  0.26s /  0.01s /  0.01s /  0.01s /  0.01s =>    2.06s
multiprocess x4 :  1.75s /  0.28s /  0.02s /  0.02s /  0.02s /  0.02s =>    4.19s
multiprocess x8 :  3.51s /  0.57s /  0.04s /  0.05s /  0.04s /  0.05s =>    8.44s
multiprocess x32: 14.23s /  2.24s /  0.15s /  0.14s /  0.14s /  0.15s =>   25.49s
disk_write    1KB: ####################  79.69s (12.55 Mo/s)
disk_read     1KB: ####################  24.57s (40.71 Mo/s)
disk_write 1024KB: ####################  78.36s (12.76 Mo/s)
disk_read  1024KB: ####################  22.93s (43.61 Mo/s)
# sur la sandisk 64Go:
disk_write    1KB: ####################  36.18s (27.64 Mo/s)
disk_read     1KB: ####################  24.33s (41.10 Mo/s)
disk_write 1024KB: ####################  36.37s (27.49 Mo/s)
disk_read  1024KB: ####################  22.96s (43.55 Mo/s)

disk_write    1KB: #################### 443.24s ( 2.26 Mo/s)
disk_read     1KB: ####################  27.89s (35.86 Mo/s)
disk_write 1024KB: #################### 481.10s ( 2.08 Mo/s)
disk_read  1024KB: ####################  27.08s (36.93 Mo/s)


therm_test (blob detection et threshold) sur images_thermal_from_sbre_accueil:
INF: detectHuman total: 2274 file(s), duration:  4.85s, im/sec: 468.76
INF: detectHuman total: 2274 file(s), duration:  4.46s, im/sec: 509.36 (output > tutu)




RPI4-thenardier/obo (avec le site obo qui tourne derriere):
python version   : 3.7.3 (32bits) (4 core(s))
cpu              : ARMv7 Processor rev 3 (v7l)
test_cpu_int2    : ####################   1.73s
test_cpu_float2  : ####################   0.26s
test_crypt       : ####################  11.91s
test_scipy_xxt   : ####################   7.41s (53.96x)
test_orb4.6.0    : ####################   1.60s (62.38fps)
test_orbcv imgs  : ####################   6.03s (16.57fps)
test_orbcv bis   : ####################   6.01s (16.64fps)
multiprocess x1 :  1.75s /  0.28s /  7.40s /  2.50s /  7.48s /  7.45s =>   26.87s (per thread:26.87s)
multiprocess x4 :  1.80s /  0.31s / 17.64s /  2.68s /  7.84s /  7.86s =>   64.99s (per thread:16.25s)
multiprocess x8 :  3.56s /  0.62s / 35.13s /  5.43s / 15.63s / 15.65s =>  141.01s (per thread:17.63s)
multiprocess x32: 14.38s /  2.49s /140.56s / 21.47s / 69.00s / 73.29s =>  462.20s (per thread:14.44s)
disk_write    1KB: #################### 298.61s ( 3.35 Mo/s)
disk_read     1KB: ####################  28.25s (35.40 Mo/s)
disk_write 1024KB: #################### 289.99s ( 3.45 Mo/s)
disk_read  1024KB: ####################  26.61s (37.59 Mo/s)

avec 50MB:
disk_write    1KB: ####################  12.97s ( 3.86 Mo/s)
disk_read     1KB: ####################   1.18s (42.39 Mo/s)
disk_write 1024KB: ####################  12.89s ( 3.10 Mo/s)
disk_read  1024KB: ####################   3.69s (10.85 Mo/s)

pen drive sur port usb3 avec 50MB (plus assez de places disk):
disk_write    1KB: ####################   2.96s (16.87 Mo/s)
disk_read     1KB: ####################   0.79s (63.29 Mo/s)
disk_write 1024KB: ####################  26.20s ( 1.53 Mo/s)
disk_read  1024KB: ####################   0.61s (65.22 Mo/s)

disk_write    1KB: ####################  27.24s ( 1.84 Mo/s)
disk_read     1KB: ####################   0.77s (64.84 Mo/s)
disk_write 1024KB: ####################  27.45s ( 1.46 Mo/s)
disk_read  1024KB: ####################   0.67s (59.79 Mo/s)

au boot avec juste apache2:

python version   : 2.7.16 (32bits) (4 core(s))
cpu              : ARMv7 Processor rev 3 (v7l)
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.28s
test_scipy_xxt   : ####################   6.96s (57.50x)
opencv (orb)      : not found
opencv (orb)    : not found
opencv (orb)    : not found
multiprocess x1 :  1.74s /  0.29s /  6.88s /  0.01s /  0.01s /  0.01s =>    8.96s (per thread:8.96s)
multiprocess x4 :  1.78s /  0.46s / 21.31s /  0.03s /  0.03s /  0.03s =>   32.59s (per thread:8.15s)
multiprocess x8 :  3.55s /  0.75s / 42.69s /  0.05s /  0.05s /  0.05s =>   79.73s (per thread:9.97s)
multiprocess x32: 14.40s /  3.04s /170.88s /  0.17s /  0.17s /  0.17s =>  268.55s (per thread:8.39s)
disk_write    1KB: #################### 137.62s ( 7.27 Mo/s)
disk_read     1KB: ####################  24.53s (40.76 Mo/s)
disk_write 1024KB: #################### 259.54s ( 3.85 Mo/s)
disk_read  1024KB: ####################  23.03s (43.42 Mo/s)
pi@thenardier:~/dev/git/electronoos/scripts $ python3 test_perf.py
python version   : 3.7.3 (32bits) (4 core(s))
cpu              : ARMv7 Processor rev 3 (v7l)
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.26s
test_scipy_xxt   : ####################   7.76s (51.56x)
test_orb4.6.0    : ####################   1.67s (59.92fps)
test_orbcv imgs  : ####################   6.10s (16.40fps)
test_orbcv bis   : ####################   6.05s (16.52fps)
multiprocess x1 :  1.75s /  0.28s /  7.79s /  2.49s /  7.49s /  7.50s =>   27.30s (per thread:27.30s)
multiprocess x4 :  1.79s /  0.30s / 20.52s /  2.79s /  7.84s /  7.90s =>   68.44s (per thread:17.11s)
multiprocess x8 :  3.57s /  0.62s / 41.34s /  5.39s / 15.81s / 15.83s =>  151.00s (per thread:18.88s)
multiprocess x32: 14.41s /  2.36s /165.75s / 21.55s / 64.19s / 69.25s =>  488.52s (per thread:15.27s)
disk_write    1KB: #################### 297.09s ( 3.37 Mo/s)
disk_read     1KB: ####################  28.29s (35.35 Mo/s)
disk_write 1024KB: #################### 305.95s ( 3.27 Mo/s)
disk_read  1024KB: ####################  22.97s (43.54 Mo/s)
pi@thenardier:~/dev/git/electronoos/scripts $

*** RPI4 ***
(recomputed)


*** RPI5 ***

python version   : 3.11.2 (64bits) (4 core(s))
cpu              : Raspberry Pi 5 Model B Rev 1.0
ram              : 7.36 / 7.86 GB
test_cpu_int2    : ####################   0.40s
test_cpu_float2  : ####################   0.08s
test_crypt       : ####################   6.65s
test_cpu_ram 2G  : ####################   0.68s
test_cpu_ram 4G  : ####################   1.37s
test_cpu_ram 6G  : ####################   2.04s
test_cpu_ram 8G  : ####################   2.74s
test_cpu_ram10G  : ####################   3.43s
test_cpu_ram12G  : ####################   4.11s
test_cpu_ram14G  : ####################   5.86s
test_cpu_ram16G  :  Memory Error...
test_scipy_xxt   : ####################   3.20s (124.89x)
test_orb4.6.0    : ####################   0.27s (365.58fps)
test_orbcv imgs  : ####################   1.28s (78.07fps)
test_orbcv bis   : ####################   1.28s (78.15xfps)
multiprocess x1 :  0.42s /  0.09s /  3.21s /  0.47s /  1.59s /  1.59s =>    7.36s (per thread:7.36s)
multiprocess x4 :  0.43s /  0.11s / 13.81s /  0.72s /  2.09s /  2.09s =>   26.60s (per thread:6.65s)
multiprocess x8 :  0.85s /  0.20s / 27.95s /  1.44s /  4.26s /  4.55s =>   65.84s (per thread:8.23s)
multiprocess x32:  3.97s /  0.89s /111.97s /  6.66s / 20.86s / 21.01s =>  231.21s (per thread:7.23s)
disk_write    1KB: ####################  16.24s (61.59 Mo/s)
disk_read     1KB: ####################  12.49s (80.09 Mo/s)
disk_write 1024KB: ####################  15.98s (62.58 Mo/s)
disk_read  1024KB: ####################  10.63s (94.11 Mo/s)






*** Jetson AGX ***
power mode 2 (15W) 
am@am-desktop:~/dev/git/electronoos$ sudo python scripts/test_perf.py
python version   : 2.7.17 (64bits) (4 core(s))
test_cpu_int2    : ####################   0.91s
test_cpu_float2  : ####################   0.35s
scipy.fftpack    : not found
test_orb4.1.1    : ####################   0.60s (165.99fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
multiprocess x4 :  1.01s /  1.12s /  0.04s /  1.18s /  0.36s /  0.35s =>    4.05s
multiprocess x8 :  1.83s /  0.80s /  0.08s /  2.10s /  0.71s /  0.70s =>   10.26s
multiprocess x32:  7.35s /  3.23s /  0.24s /  8.60s /  3.14s /  2.65s =>   35.47s
disk_write    1KB: ####################  14.69s (68.08 Mo/s)
disk_read     1KB: ####################   4.14s (241.62 Mo/s)
disk_write 1024KB: ####################  10.99s (90.98 Mo/s)
disk_read  1024KB: ####################   3.47s (288.31 Mo/s)

python version   : 3.6.9 (64bits) (4 core(s))
test_cpu_int2    : ####################   0.88s
test_cpu_float2  : ####################   0.37s
test_scipy_xxt   : ####################   3.25s (122.89x)
test_orb4.1.1    : ####################   0.65s (154.49fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
multiprocess x4 :  0.93s /  0.36s /  2.77s /  0.98s /  0.36s /  0.37s =>    5.79s
multiprocess x8 :  2.10s /  0.68s /  4.92s /  2.03s /  0.78s /  0.76s =>   17.05s
multiprocess x32:  7.29s /  2.69s / 19.25s /  8.57s /  3.03s /  3.06s =>   60.94s
disk_write    1KB: ####################  16.14s (61.97 Mo/s)
disk_read     1KB: ####################   7.33s (136.34 Mo/s)
disk_write 1024KB: ####################  11.51s (86.87 Mo/s)
disk_read  1024KB: ####################   3.46s (288.89 Mo/s)

power mode 0
python version   : 2.7.17 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.44s
test_cpu_float2  : ####################   0.17s
scipy.fftpack    : not found
test_orb4.1.1    : ####################   0.32s (310.59fps)
test_orbcv imgs  : ####################   1.29s (77.45fps)
test_orbcv bis   : ####################   1.22s (82.13fps)
multiprocess x4 :  0.45s /  0.18s /  0.02s /  0.50s /  0.17s /  0.17s =>    1.50s
multiprocess x8 :  0.48s /  0.21s /  0.03s /  0.54s /  0.20s /  0.19s =>    3.14s
multiprocess x32:  1.90s /  0.83s /  0.09s /  2.04s /  0.72s /  0.68s =>    9.39s
disk_write    1KB: ####################  12.80s (78.11 Mo/s)
disk_read     1KB: ####################   3.59s (278.74 Mo/s)
disk_write 1024KB: ####################  10.40s (96.12 Mo/s)
disk_read  1024KB: ####################   3.35s (298.24 Mo/s)

python version   : 3.6.9 (64bits) (8 core(s))
test_cpu_int2    : ####################   0.66s
test_cpu_float2  : ####################   0.19s
test_scipy_xxt   : ####################   1.27s (315.92x)
test_orb4.1.1    : ####################   0.33s (300.27fps)
test_orbcv imgs  : ####################   1.63s (61.32fps)
test_orbcv bis   : ####################   1.35s (74.16fps)
multiprocess x4 :  0.47s /  0.18s /  1.16s /  0.55s /  0.23s /  0.22s =>    2.83s
multiprocess x8 :  0.49s /  0.20s /  1.79s /  0.57s /  0.24s /  0.24s =>    6.37s
multiprocess x32:  1.94s /  0.68s /  7.15s /  2.24s /  0.88s /  0.86s =>   20.12s
disk_write    1KB: ####################  13.29s (75.26 Mo/s)
disk_read     1KB: ####################   4.25s (235.43 Mo/s)
disk_write 1024KB: ####################  10.66s (93.84 Mo/s)
disk_read  1024KB: ####################   3.35s (298.94 Mo/s)


xenia@xenia-test-server:~/alex/git/electronoos/scripts$ python3 test_perf.py 50000
INF: Changing disk test size to 50000 MB
python version   : 3.8.5 (64bits) (8 core(s))
cpu              : todo
test_cpu_int2    : ####################   0.23s
test_cpu_float2  : ####################   0.05s
scipy.fftpack    : not found
test_orb4.5.1    : ####################   0.09s (1172.23fps)
opencv (orb)    : not found
opencv (orb)    : not found
multiprocess x1 :  0.23s /  0.05s /  0.00s /  0.00s /  0.00s /  0.00s =>    0.29s
multiprocess x4 :  0.24s /  0.05s /  0.00s /  0.00s /  0.00s /  0.00s =>    0.59s
multiprocess x8 :  0.25s /  0.06s /  0.00s /  0.00s /  0.00s /  0.00s =>    0.91s
multiprocess x32:  1.00s /  0.22s /  0.01s /  0.01s /  0.01s /  0.01s =>    2.19s
disk_write    1KB: ####################  36.40s (1373.69 Mo/s)
disk_read     1KB: ####################  38.64s (1294.00 Mo/s)
disk_write 1024KB: ####################  45.93s (1088.53 Mo/s)
disk_read  1024KB: ####################  45.87s (1090.02 Mo/s)
xenia@xenia-test-server:~/alex/git/electronoos/scripts$

xenia@xenia-test-server:~/alex/git/electronoos/scripts$ python3 test_perf.py
python version   : 3.8.5 (64bits) (8 core(s))
cpu              : todo
test_cpu_int2    : ####################   0.23s
test_cpu_float2  : ####################   0.05s
scipy.fftpack    : not found
test_orb4.5.1    : ####################   0.09s (1172.23fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
multiprocess x1 :  0.28s /  0.05s /  0.00s /  0.15s /  0.06s /  0.06s =>    0.60s
multiprocess x4 :  0.24s /  0.05s /  0.00s /  0.16s /  0.06s /  0.06s =>    1.18s
multiprocess x8 :  0.25s /  0.06s /  0.00s /  0.18s /  0.06s /  0.06s =>    1.80s
multiprocess x32:  1.00s /  0.22s /  0.02s /  0.77s /  0.24s /  0.24s =>    4.30s
disk_write    1KB: ####################   2.58s (387.25 Mo/s)
disk_read     1KB: ####################   1.67s (600.11 Mo/s)
disk_write 1024KB: ####################   2.29s (436.47 Mo/s)
disk_read  1024KB: ####################   1.41s (708.34 Mo/s)


*** Black portable Dell ***

a@black:~/dev/electronoos/scripts$ cat /proc/cpuinfo 
processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 37
model name	: Intel(R) Core(TM) i5 CPU       M 480  @ 2.67GHz
stepping	: 5
microcode	: 0x2
cpu MHz		: 1197.000
cache size	: 3072 KB
physical id	: 0
siblings	: 4
core id		: 0
cpu cores	: 2
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 11
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm pcid sse4_1 sse4_2 popcnt lahf_lm ida arat dtherm tpr_shadow vnmi flexpriority ept vpid
bogomips	: 5319.90
clflush size	: 64
cache_alignment	: 64
address sizes	: 36 bits physical, 48 bits virtual
power management:

a@black:~/dev/electronoos/scripts$ sudo python test_perf.py 
[sudo] password for a: 
INF: Due to low empty disk space, reducing disk test size to 648 MB
python version   : 2.7.6 (64bits) (4 core(s))
cpu              : Intel(R) Core(TM) i5 CPU       M 480  @ 2.67GHz
ram              : 5.07 / 5.63 GB # added 2GB
test_cpu_int2    : ####################   0.55s
test_cpu_float2  : ####################   0.14s
scipy.fftpack    : not found
test_orb2.4.8    : ####################   0.28s (358.00fps)
test_orb2.4.8    : ####################  11.24s ( 8.90fps) ?
test_orbcv imgs  : ####################   2.41s (41.56fps)
test_orbcv bis   : ####################   1.27s (78.62fps)
multiprocess x1 :  0.55s /  0.14s /  0.00s /  0.42s /  0.13s /  0.12s =>    1.38s
multiprocess x4 :  1.08s /  0.30s /  0.01s /  0.89s /  0.27s /  0.27s =>    4.20s
multiprocess x8 :  2.15s /  0.61s /  0.02s /  1.78s /  0.55s /  0.55s =>    9.85s
multiprocess x32:  8.72s /  2.43s /  0.05s /  7.18s /  2.18s /  2.18s =>   32.61s
disk_write    1KB: ####################   9.38s (69.10 Mo/s)
disk_read     1KB: ####################   9.82s (66.00 Mo/s)
disk_write 1024KB: ####################  11.18s (57.24 Mo/s)
disk_read  1024KB: ####################   9.90s (64.64 Mo/s)

# Champion1
python version   : 3.8.10 (64bits) (8 core(s))
cpu              : Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz
test_cpu_int2    : ####################   0.23s
test_cpu_float2  : ####################   0.05s
test_scipy_xxt   : ####################   0.63s (638.44x)
test_orb4.5.5    : ####################   0.08s (1184.57fps)
test_orbcv imgs  : ####################   0.48s (209.40fps)
test_orbcv bis   : ####################   0.37s (268.87fps)
multiprocess x1 :  0.24s /  0.05s /  0.55s /  0.16s /  0.46s /  0.46s =>    1.93s
multiprocess x4 :  0.25s /  0.06s /  2.11s /  0.17s /  0.51s /  0.50s =>    5.52s
multiprocess x8 :  0.26s /  0.06s /  4.52s /  0.21s /  0.61s /  0.61s =>   11.79s
multiprocess x32:  1.02s /  0.24s / 18.39s /  0.85s /  2.45s /  2.45s =>   37.19s

disk_write    1KB: ####################   1.07s (934.86 Mo/s)
disk_read     1KB: ####################   0.77s (1299.69 Mo/s)
disk_write 1024KB: ####################   0.75s (1341.12 Mo/s)
disk_read  1024KB: ####################   0.52s (1940.41 Mo/s)


ms tab7:
low perf:
INF: Changing disk test size to 1000 MB
python version   : 3.9.5 (64bits) (8 core(s))
cpu              : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
test_cpu_int2    : ####################   0.62s
test_cpu_float2  : ####################   0.09s
test_crypt       : ####################   7.89s
test_scipy_xxt   : ####################   1.06s (377.83x)
test_orb4.5.2    : ####################   0.27s (373.96fps)
test_orbcv imgs  : ####################   1.25s (80.10fps)
test_orbcv bis   : ####################   1.30s (76.75fps)
disk_write    1KB: ####################  11.84s (84.43 Mo/s)
disk_read     1KB: ####################   5.89s (169.72 Mo/s)
disk_write 1024KB: ####################   6.11s (163.76 Mo/s)
disk_read  1024KB: ####################   0.37s (2671.59 Mo/s)


high perf:
INF: Changing disk test size to 1000 MB
python version   : 3.9.5 (64bits) (8 core(s))
cpu              : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
ram              : 11.02 / 15.60 GB
ram              : 10.73 / 15.60 GB
test_cpu_int2    : ####################   0.46s
test_cpu_float2  : ####################   0.07s
test_crypt       : ####################   5.68s
test_cpu_ram 2G  : ####################   0.37s
test_cpu_ram 4G  : ####################   0.65s
test_cpu_ram 6G  : ####################   0.94s
test_cpu_ram 8G  : ####################   1.25s
test_cpu_ram10G  : ####################   2.29s
test_cpu_ram12G  : ####################   3.77s
test_cpu_ram14G  : ####################   5.76s
test_cpu_ram16G  : ####################   7.93s  # require some of empty spaces (for swap)
test_scipy_xxt   : ####################   0.89s (449.65x)
test_orb4.5.2    : ####################   0.20s (490.18fps)
test_orbcv imgs  : ####################   1.10s (91.16fps)
test_orbcv bis   : ####################   1.11s (90.49fps)
disk_write    1KB: ####################  20.61s (48.51 Mo/s)
disk_read     1KB: ####################   5.24s (190.85 Mo/s)
disk_write 1024KB: ####################   4.75s (210.67 Mo/s)
disk_read  1024KB: ####################   0.27s (3640.21 Mo/s)


# same 23/10/2023 after fresh reboot

python version   : 3.9.5 (64bits) (8 core(s))
cpu              : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
ram              : 11.96 / 15.60 GB
test_cpu_int2    : ####################   0.42s
test_cpu_float2  : ####################   0.06s
test_cpu_ram 2G  : ####################   0.36s
test_cpu_ram 4G  : ####################   0.68s
test_cpu_ram 6G  : ####################   0.95s
test_cpu_ram 8G  : ####################   1.23s
test_cpu_ram10G  : ####################   1.77s
test_cpu_ram12G  : ####################   1.91s
test_cpu_ram14G  : ####################   4.43s
test_cpu_ram16G  : ####################   6.93s
test_scipy_xxt   : ####################   0.85s (468.08x)
test_orb4.5.5    : ####################   0.27s (376.54fps)
test_orbcv imgs  : ####################   0.90s (110.98fps)
test_orbcv bis   : ####################   0.64s (157.29fps)
disk_write    1KB: ####################   9.46s (105.73 Mo/s)
disk_read     1KB: ####################   5.77s (173.38 Mo/s)
disk_write 1024KB: ####################   4.76s (210.16 Mo/s)
disk_read  1024KB: ####################   0.33s (3047.28 Mo/s)


comparison test writing on ms tab 4:

new sandisk fit mini usb 128Go sur port usb
E:/>python c:test_perf.py 1000
disk_write    1KB: ####################  19.55s (51.16 Mo/s)
disk_read     1KB: ####################   3.59s (278.21 Mo/s)
disk_write 1024KB: ####################  20.55s (48.66 Mo/s)
disk_read  1024KB: ####################   0.67s (1488.13 Mo/s)

microsd nintendo switch 128 avec adapteur usb de Sophie
E:/>python c:test_perf.py 1000
disk_write    1KB: ####################  72.02s (13.89 Mo/s)
disk_read     1KB: ####################   3.81s (262.24 Mo/s)
disk_write 1024KB: ####################  72.97s (13.70 Mo/s)
disk_read  1024KB: ####################   0.47s (2133.94 Mo/s)

microsd nintendo switch 128 dans slot microsd
D:/>python c:test_perf.py 1000
disk_write    1KB: ####################  16.71s (59.85 Mo/s)
disk_read     1KB: ####################   3.34s (298.99 Mo/s)
disk_write 1024KB: ####################  16.58s (60.31 Mo/s)
disk_read  1024KB: ####################   0.44s (2283.54 Mo/s)

microsd sandisk extreme 256 (celle de ms tab) dans slot microsd
D:/>python c:test_perf.py 1000
disk_write    1KB: ####################  17.18s (58.22 Mo/s)
disk_read     1KB: ####################   3.38s (296.26 Mo/s)
disk_write 1024KB: ####################  16.47s (60.70 Mo/s)
disk_read  1024KB: ####################   0.45s (2205.17 Mo/s)

*** surface7:
sur c:
python version   : 3.9.5 (64bits) (8 core(s))
cpu              : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
test_cpu_int2    : ####################   0.47s
test_cpu_float2  : ####################   0.07s
test_scipy_xxt   : ####################   0.96s (418.01x)
test_orb4.5.2    : ####################   0.21s (466.26fps)
test_orbcv imgs  : ####################   0.87s (114.65fps)
test_orbcv bis   : ####################   0.65s (154.20fps)
disk_write    1KB: ####################   6.09s (164.19 Mo/s)
disk_read     1KB: ####################   5.46s (183.12 Mo/s)
disk_write 1024KB: ####################   1.64s (608.30 Mo/s)
disk_read  1024KB: ####################   0.31s (3219.90 Mo/s)

microsd Sandisk Extreme 256 (celle de ms tab) dans slot microsd:
disk_write    1KB: ####################  17.16s (58.26 Mo/s)
disk_read     1KB: ####################   2.91s (343.35 Mo/s)
disk_write 1024KB: ####################  15.15s (66.01 Mo/s)
disk_read  1024KB: ####################   0.30s (3330.45 Mo/s)
sur 4000MB:
disk_write    1KB: ####################  61.57s (64.96 Mo/s)
disk_read     1KB: ####################  12.43s (321.69 Mo/s)
disk_write 1024KB: ####################  62.84s (63.65 Mo/s)
disk_read  1024KB: ####################   1.42s (2822.87 Mo/s)
sur 4000MB (2nd run):
disk_write    1KB: ####################  58.17s (68.76 Mo/s)
disk_read     1KB: ####################  12.23s (327.03 Mo/s)
disk_write 1024KB: ####################  60.98s (65.59 Mo/s)
disk_read  1024KB: ####################   1.47s (2718.76 Mo/s)

microsd Sandisk Extreme Pro 256 dans slot microsd:
disk_write    1KB: ####################  17.76s (56.32 Mo/s)
disk_read     1KB: ####################   3.38s (295.91 Mo/s)
disk_write 1024KB: ####################  15.08s (66.32 Mo/s)
disk_read  1024KB: ####################   0.38s (2660.04 Mo/s)
sur 4000MB:
disk_write    1KB: ####################  59.47s (67.26 Mo/s)
disk_read     1KB: ####################  12.91s (309.82 Mo/s)
disk_write 1024KB: ####################  61.63s (64.90 Mo/s)
disk_read  1024KB: ####################   1.35s (2973.70 Mo/s)

new sandisk fit mini usb 256Go sur port usb (depuis anyplus c'est kifkif):
disk_write    1KB: ####################  16.45s (60.78 Mo/s)
disk_read     1KB: ####################   3.20s (312.69 Mo/s)
disk_write 1024KB: ####################   9.80s (102.09 Mo/s)
disk_read  1024KB: ####################   0.35s (2830.65 Mo/s)


Sandisk Ultra 1To sur lecteur USB
sur 4000MB:
disk_write    1KB: #################### 122.75s (32.59 Mo/s)
disk_read     1KB: ####################  12.52s (319.53 Mo/s)
disk_write 1024KB: #################### 127.24s (31.44 Mo/s)
disk_read  1024KB: ####################   1.45s (2749.29 Mo/s)
sur 4000MB (2nd run):
disk_write    1KB: #################### 125.20s (31.95 Mo/s)
disk_read     1KB: ####################  12.54s (319.09 Mo/s)
disk_write 1024KB: #################### 126.44s (31.64 Mo/s)
disk_read  1024KB: ####################   1.37s (2910.23 Mo/s)

Sandisk Ultra 1To lecteur USB dans slot microsd:
sur 4000MB:
disk_write    1KB: #################### 125.60s (31.85 Mo/s)
disk_read     1KB: ####################  12.51s (319.78 Mo/s)
disk_write 1024KB: #################### 125.24s (31.94 Mo/s)
disk_read  1024KB: ####################   1.36s (2938.42 Mo/s)
sur 4000MB (2nd run):
disk_write    1KB: #################### 126.72s (31.56 Mo/s)
disk_read     1KB: ####################  12.56s (318.41 Mo/s)
disk_write 1024KB: #################### 126.53s (31.61 Mo/s)
disk_read  1024KB: ####################   1.44s (2776.79 Mo/s)


new sandisk fit mini usb 128Go sur port usb:
disk_write    1KB: ####################  25.82s (38.73 Mo/s)
disk_read     1KB: ####################   2.86s (349.32 Mo/s)
disk_write 1024KB: ####################  24.92s (40.13 Mo/s)
disk_read  1024KB: ####################   0.30s (3281.97 Mo/s)

new sandisk ultra fit mini usb 128Go sur port usb usb 3.1 gen1:
disk_write    1KB: ####################  21.23s (47.10 Mo/s)
disk_read     1KB: ####################   3.04s (328.93 Mo/s)
disk_write 1024KB: ####################  21.22s (47.13 Mo/s)
disk_read  1024KB: ####################   0.46s (2181.99 Mo/s)

new SSD samung 1To sur Sabrent (usb):
disk_write    1KB: ####################  11.53s (86.76 Mo/s)
disk_read     1KB: ####################   5.57s (179.62 Mo/s)
disk_write 1024KB: ####################   4.08s (244.82 Mo/s)
disk_read  1024KB: ####################   0.34s (2911.05 Mo/s)

new SSD crucial 1To sur Sabrent (usb):
sur 4000MB:
disk_write    1KB: ####################  28.94s (138.20 Mo/s)
disk_read     1KB: ####################  12.55s (318.67 Mo/s)
disk_write 1024KB: ####################  17.25s (231.93 Mo/s)
disk_read  1024KB: ####################   1.39s (2879.66 Mo/s)
sur 4000MB (2nd run):
disk_write    1KB: ####################  33.55s (119.22 Mo/s)
disk_read     1KB: ####################  12.20s (327.94 Mo/s)
disk_write 1024KB: ####################  17.15s (233.25 Mo/s)
disk_read  1024KB: ####################   1.36s (2951.93 Mo/s)




*** Dell kakashi Corto/Elsa (si sur batterie, mettre sur mode perf elev�e):
windows disk size 5000
python version   : 3.10.4 (64bits) (16 core(s))
cpu              :  11th Gen Intel(R) Core(TM) i7-11800H CPU @ 2.30GHz
test_cpu_int2    : ####################   0.35s
test_cpu_float2  : ####################   0.06s
test_scipy_xxt   : ####################   0.64s (622x)
test_orb4.5.5    : ####################   0.13s (768.35fps)
test_orbcv imgs  : ####################   0.66s (151fps)
test_orbcv bis   : ####################   0.54s (183.35fps)
disk_write    1KB: ####################   19.43s (235 Mo/s)
disk_read     1KB: ####################   17.74s (281 Mo/s)
disk_write 1024KB: ####################   3.31s (1375 Mo/s)
disk_read  1024KB: ####################   1.23s (4078 Mo/s)


*** don de concept: gros
C:\dev\git\electronoos\scripts>python test_perf.py
python version   : 3.10.6 (64bits) (2 core(s))
cpu              : Intel(R) Pentium(R) CPU G4400 @ 3.30GHz
test_cpu_int2    : ####################   0.52s
test_cpu_float2  : ####################   0.08s
test_scipy_xxt   : ####################   2.17s (184.08x)
test_orb4.6.0    : ####################   0.29s (350.74fps)
test_orbcv imgs  : ####################   1.62s (61.63fps)
test_orbcv bis   : ####################   0.90s (110.84fps)
disk_write    1KB: ####################  39.08s (25.59 Mo/s)
disk_read     1KB: ####################   5.57s (179.69 Mo/s)
disk_write 1024KB: ####################  19.08s (52.41 Mo/s)
disk_read  1024KB: ####################   0.41s (2446.89 Mo/s)

*** don de concept: petit
python version   : 3.10.6 (64bits) (2 core(s))
cpu              : Intel(R) Pentium(R) CPU G4400 @ 3.30GHz
test_cpu_int2    : ####################   0.50s
test_cpu_float2  : ####################   0.09s
test_scipy_xxt   : ####################   1.58s (253.52x)
test_orb4.6.0    : ####################   0.23s (426.77fps)
test_orbcv imgs  : ####################   0.84s (118.55fps)
test_orbcv bis   : ####################   0.84s (118.55fps)
disk_write    1KB: ####################  24.98s (40.03 Mo/s)
disk_read     1KB: ####################   8.25s (121.24 Mo/s)
disk_write 1024KB: ####################  17.95s (55.71 Mo/s)
disk_read  1024KB: ####################   0.33s (3049.87 Mo/s)

*** don de la region petit ordi de Corto
python version   : 3.12.0 (64bits) (2 core(s))
cpu              : Intel(R) Celeron(R) N5100 @ 1.10GHz
test_cpu_int2    : ####################   0.71s
test_cpu_float2  : ####################   0.13s
test_cpu_ram 2G  : ####################   0.47s
test_cpu_ram 4G  : ####################   0.98s
test_cpu_ram 6G  : ####################   2.57s
test_cpu_ram 8G  : ####################   3.79s
test_cpu_ram10G  : ####################   5.35s
test_cpu_ram12G  : ####################   7.00s
test_cpu_ram14G  : ####################   10.51s
test_cpu_ram16G  : ####################   12.65s
disk_read     1KB: ####################   7.00s (142.92 Mo/s)
disk_read  1024KB: ####################   1.38s (726.17 Mo/s)




*** ExoScale instance Standard - Large

ubuntu@VM-ef8b3a4e-a4fe-4560-9021-74a52faa6357:~/dev/git/electronoos/scripts$ python3 test_perf.py
python version   : 3.10.12 (64bits) (4 core(s))
cpu              : Intel Xeon Processor (Skylake)
ram              : 7.24 / 7.75 GB
test_cpu_int2    : ####################   0.35s
test_cpu_float2  : ####################   0.08s
test_crypt       : ####################   5.26s
test_cpu_ram 2G  : ####################   1.20s
test_cpu_ram 4G  : ####################   2.21s
test_cpu_ram 6G  : ####################   3.65s
test_cpu_ram 8G  : ####################   4.88s
test_cpu_ram10G  : ####################   6.13s
test_cpu_ram12G  : ####################   7.44s
test_cpu_ram14G  : ####################   8.59s
test_cpu_ram16G  :  Memory Error...
test_scipy_xxt   : ####################   1.02s (393.63x)
test_orb4.6.0    : ####################   0.18s (566.20fps)
test_orbcv imgs  : ####################   0.66s (151.02fps)
test_orbcv bis   : ####################   0.61s (164.29fps)
multiprocess x1 :  0.39s /  0.12s /  5.26s /  1.13s /  0.01s /  0.01s /  0.01s =>    6.93s (per thread:6.93s)
multiprocess x4 :  0.40s /  0.12s /  5.30s /  1.34s /  0.02s /  0.02s /  0.01s =>   14.13s (per thread:3.53s)
multiprocess x8 :  0.76s /  0.29s / 10.56s /  2.59s /  0.02s /  0.02s /  0.02s =>   28.40s (per thread:3.55s)
multiprocess x32:  2.97s /  0.84s / 42.23s / 10.87s /  0.08s /  0.08s /  0.08s =>   85.55s (per thread:2.67s)
disk_write    1KB: ####################   5.11s (195.62 Mo/s)
disk_read     1KB: ####################   1.71s (585.41 Mo/s)
disk_write 1024KB: ####################   2.85s (350.36 Mo/s)
disk_read  1024KB: ####################   0.74s (1359.73 Mo/s)


*** Azure Server1 - "8 cores" 16 GB
na@Server1:~/dev/git/electronoos/scripts$ python3 test_perf.py
python version   : 3.12.3 (64bits) (4 core(s))
cpu              : Intel(R) Xeon(R) Platinum 8272CL CPU @ 2.60GHz
ram              : 12.34 / 15.57 GB
test_cpu_int2    : ####################   0.63s
test_cpu_float2  : ####################   0.08s
test_crypt       : ####################   5.36s
test_cpu_ram 2G  : ####################   0.32s
test_cpu_ram 4G  : ####################   0.64s
test_cpu_ram 6G  : ####################   0.96s
test_cpu_ram 8G  : ####################   1.28s
test_cpu_ram10G  : ####################   1.59s
test_cpu_ram12G  : ####################   1.91s
test_cpu_ram14G  : ####################   2.23s
test_cpu_ram16G  : ####################   2.55s
test_scipy_xxt   : ####################   1.00s (401.42x)
test_orb4.6.0    : ####################   0.17s (596.29fps)
test_orbcv imgs  : ####################   0.66s (152.03fps)
test_orbcv bis   : ####################   0.65s (152.85fps)
multiprocess x1 :  0.63s /  0.09s /  5.37s /  1.00s /  0.28s /  0.78s /  0.78s =>    8.92s (per thread:8.92s)
multiprocess x4 :  1.33s /  0.18s /  5.87s /  1.97s /  0.55s /  1.40s /  1.40s =>   21.61s (per thread:5.40s)
multiprocess x8 :  2.65s /  0.36s / 11.75s /  4.25s /  1.12s /  2.86s /  2.86s =>   47.46s (per thread:5.93s)
multiprocess x32: 10.62s /  1.42s / 47.16s / 16.83s /  4.44s / 11.59s / 11.56s =>  151.08s (per thread:4.72s)
disk_write    1KB: ####################   8.33s (120.02 Mo/s)
disk_read     1KB: ####################   4.66s (214.56 Mo/s)
disk_write 1024KB: ####################   7.39s (135.39 Mo/s)
disk_read  1024KB: ####################   3.79s (263.53 Mo/s)

*** Azure Server2cpu - Standard F4as v6 (4 vcpus, 16 GiB memory) - "8 cores" 16 GB
INF: Changing disk test size to 5000 MB
python version   : 3.12.3 (64bits) (4 core(s))
cpu              : AMD EPYC 9V74 80-Core Processor
ram              : 15.00 / 15.61 GB
test_cpu_int2    : ####################   0.30s
test_cpu_float2  : ####################   0.05s
test_crypt       : ####################   4.10s
test_cpu_ram 2G  : ####################   0.08s
test_cpu_ram 4G  : ####################   0.16s
test_cpu_ram 6G  : ####################   0.25s
test_cpu_ram 8G  : ####################   0.33s
test_cpu_ram10G  : ####################   0.41s
test_cpu_ram12G  : ####################   0.49s
test_cpu_ram14G  : ####################   0.56s
test_cpu_ram16G  : ####################   0.65s
test_scipy_xxt   : ####################   0.48s (825.25x)
test_orb4.6.0    : ####################   0.08s (1249.10fps)
test_orbcv imgs  : ####################   0.32s (313.66fps)
test_orbcv bis   : ####################   0.32s (315.63fps)
multiprocess x1 :  0.31s /  0.05s /  4.10s /  0.46s /  0.16s /  0.43s /  0.42s =>    5.93s (per thread:5.93s)
multiprocess x4 :  0.32s /  0.06s /  4.11s /  0.82s /  0.16s /  0.44s /  0.43s =>   12.27s (per thread:3.07s)
multiprocess x8 :  0.63s /  0.11s /  8.22s /  1.90s /  0.32s /  0.88s /  0.88s =>   25.21s (per thread:3.15s)
multiprocess x32:  2.52s /  0.44s / 32.92s /  7.29s /  1.30s /  3.62s /  3.61s =>   76.92s (per thread:2.40s)
disk_write    1KB: ####################  81.11s (61.65 Mo/s)
disk_read     1KB: ####################  20.04s (249.44 Mo/s)
disk_write 1024KB: ####################  49.19s (101.64 Mo/s)
disk_read  1024KB: ####################   0.80s (6252.09 Mo/s)




*** Ordi gabriel portable gamer
python version   : 3.13.1 (64bits) (8 core(s))
cpu              : AMD Ryzen 5 2500U with Radeon Vega Mobile Gfx
ram             : 11.94 / 14.90 GB
test_cpu_int2    : ####################   1.03s
test_cpu_float2  : ####################   0.16s
test_crypt            : ####################   11.56s
test_cpu_ram 2G  : ####################   0.67s
test_cpu_ram 4G  : ####################   1.33s
test_cpu_ram 6G  : ####################   2.12s
test_cpu_ram 8G  : ####################   3.13s
test_cpu_ram10G  : ####################   4.05s
test_cpu_ram12G  : ####################   6.97s
test_cpu_ram14G  : ####################   15.05s
test_cpu_ram16G  : ####################   19.40s
test_scipy_xxt   : ####################   2.23s (179.55x)
test_orb4.10.0    : ####################   0.57s (175.56fps)
test_orbcv imgs  : ####################   3.84s (26.06fps)
test_orbcv bis   : ####################   1.62s (61.55fps)
disk_write    1KB: ####################   22.69s (44 Mo/s)
disk_read     1KB: ####################   19.55s (51 Mo/s)
disk_write 1024KB: ####################   4.91s (203 Mo/s)
disk_read  1024KB: ####################   0.67s (1492 Mo/s)


"""