# -*- coding: utf-8 -*-

#
# Sound Acceptance test
# v0.81: add core handling
#
# Author: A. Mazel & L. George

import sys
import os
import struct
import time
import multiprocessing

def getFreeDiskSpace():
    """
    return current disk space in bytes
    """
    if os.name == 'posix':
        s = os.statvfs('/')
        nSize = (s.f_bavail * s.f_frsize)
        return nSize
    import psutil # pip install psutil
    usa = psutil.disk_usage('/')
    return usa.free

class FlushableFile:
    """
    A flushable multi os multi python version file encapsulation
    """
    def __init__( self, strFilename, strMode ):
        import platform
        self.bWindows = "windows" in platform.system().lower()
        if self.bWindows:
            import win32file
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
        n = numpy.zeros(nSizeArray, dtype=numpy.float)
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
        if bPrint: print( "opencv  : not found")
        return 0
        
    import math
    import numpy
    
    if bPrint: sys.stdout.write( "test_orb%-9s: " % cv2.__version__ )
    h = 640
    w = 480    
    img = numpy.zeros((h,w,1), numpy.uint8)
    for j in range(h):
        for i in range(w):
            img[j,i,0] = math.sin(w*h)*1000
    
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
        if bPrint: print( "opencv: not found")
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
            img[j,i,0] = math.sin(w*h)*1000
    
    try:
        img1 = cv2.imread( "test_perf_vga_01.png" )
        img2 = cv2.imread( "test_perf_vga_02.png" )
        if img1 is None or img2 is None:
            raise BaseException("")
    except:
        print( "test_perf_vga_*.png: not found")
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
    if platform.system() == 'Windows' or 1:
        return 0

    rTotalDuration = 0
    for nNbrProcessInParalell in [4,8,32]:
        sys.stdout.write( "multiprocess x%-2d:" % nNbrProcessInParalell  )    
        bFirstInLine = True
        all_process = []
        for func_to_test in (test_cpu_int,test_cpu_float,test_numpy,test_opencv_orb,test_opencv_orb_realcase,test_opencv_orb_realcase):
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
        print(" => %7.2fs" % rTotalDuration )
    return rTotalDuration
    

def test_perf(nDiskTestSizeMB=200):
    print_version()
    rTotalTime = 0;
    rTotalTime += test_cpu_int();
    rTotalTime += test_cpu_float();
    rTotalTime += test_numpy();
    rTotalTime += test_opencv_orb();
    rTotalTime += test_opencv_orb_realcase();
    rTotalTime += test_opencv_orb_realcase(); # because on some computer the previous one takes time initialise stuffs
    if 1:
        # multithreading
        rTotalTime += test_multithreading();
            
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB, nPacketSize=1024);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB, nPacketSize=1024);
    
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB, nPacketSize=1024*1024);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB, nPacketSize=1024*1024);
    
    os.unlink( "temp.tmp" );
# test_perf - end
    
nDiskTestSizeMB = 1000;    
if( len(sys.argv)> 1 ):
    nDiskTestSizeMB=int(sys.argv[1]);
    print( "INF: Changing disk test size to %d MB" % nDiskTestSizeMB );
    
if getFreeDiskSpace() /(1024*1024) < nDiskTestSizeMB:
    nDiskTestSizeMB = int( (getFreeDiskSpace()*0.9)/(1024*1024) )
    print( "INF: Due to low empty disk space, reducing disk test size to %d MB" % nDiskTestSizeMB );
    
test_perf(nDiskTestSizeMB=nDiskTestSizeMB);

#####################################
"""
Some results sur la Surface Pro 4:

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


D:\>python c:test_perf.py
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


*** Raspberry4-therm ***

pi@raspberrypi:~/dev/git/electronoos/scripts $ python test_perf.py
python version   : 2.7.16 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.28s
test_scipy_xxt   : ####################   6.99s (57.19x)
test_orb3.2.0    : ####################   1.34s (74.62fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  83.26s (12.01 Mo/s)
disk_read     1KB: ####################  24.85s (40.24 Mo/s)
disk_write 1024KB: ####################  78.17s (12.79 Mo/s)
disk_read  1024KB: ####################  22.93s (43.62 Mo/s)

pi@raspberrypi:~/dev/git/electronoos/scripts $ LD_PRELOAD=/usr/lib/gcc/arm-linux-gnueabihf/8/libatomic.so python3 test_perf.py
python version   : 3.7.3 (32bits) (4 core(s))
test_cpu_int2    : ####################   1.72s
test_cpu_float2  : ####################   0.26s
test_scipy_xxt   : ####################   8.82s (45.35x)
test_orb4.1.1    : ####################   1.12s (88.94fps)
test_orbcv imgs  : test_perf_vga_*.png: not found
test_orbcv bis   : test_perf_vga_*.png: not found
disk_write    1KB: ####################  79.69s (12.55 Mo/s)
disk_read     1KB: ####################  24.57s (40.71 Mo/s)
disk_write 1024KB: ####################  78.36s (12.76 Mo/s)
disk_read  1024KB: ####################  22.93s (43.61 Mo/s)


"""