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
                #~ os.fsync( win32file._get_osfhandle(self.handle) )
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
    print( "python version : %d.%d.%d (%dbits) (%d core(s))" % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro,8 * struct.calcsize("P"),multiprocessing.cpu_count()) )
    
def test_cpu_int( bPrint = True ):
    if bPrint: sys.stdout.write( "test_cpu_int2  : " )
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
    if bPrint: sys.stdout.write( "test_cpu_float2: " )
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
        if bPrint: print( "numpy: not found")
        return 0

    try:
        import scipy.fftpack
    except:
        if bPrint: print( "scipy.fftpack: not found")
        return 0
        
    
    if bPrint: sys.stdout.write( "test_scipy_xxt : " )
    timeBegin = time.time();
    nLengthSec = 10
    for i in range(20):
        nSizeArray = nLengthSec*48000*2
        n = numpy.random.random_integers( -32000,32000,nSizeArray)
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
        if bPrint: print( "opencv: not found")
        return 0
        
    import math
    import numpy
    
    if bPrint: sys.stdout.write( "test_orb%-7s: " % cv2.__version__ )
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
        if bPrint: sys.stdout.write( "test_orbcv imgs: " )
    else:
        if bPrint: sys.stdout.write( "test_orbcv bis : " )
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

        

def test_disk_write( nMB=200 ):
    sys.stdout.write( "test_disk_write: " )
    timeBegin = time.time();
    file = FlushableFile( "temp.tmp", "w" );
    nTimePerLoop = int(100000*nMB / 200);
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            file.write( "A"*100 );
        sys.stdout.write( "#" );
        sys.stdout.flush();
    file.flush();
    file.close();
    rDuration = time.time() - timeBegin;
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*100/(rDuration*1024*1024)));
    return rDuration;
#test_disk_write - end
        
        
        
def test_disk_read( nMB=200 ):
    sys.stdout.write( "test_disk_read : " )
    clear_caches()
    timeBegin = time.time();
    file = FlushableFile( "temp.tmp", "r" );
    nTimePerLoop = int(100000*nMB / 200);
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            dummy = file.read(1*100);
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
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*100/(rDuration*1024*1024)));
    if( strMsg != "" ):
        print( strMsg )
    return rDuration;
#test_disk_read - end

def simple_test(bToto):
    print("test!!!")

def test_multithreading():
    # It shows us that
    import platform
    if platform.system() == 'Windows':
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
            
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB);
    os.unlink( "temp.tmp" );
# test_perf - end
    
nDiskTestSizeMB = 200;    
if( len(sys.argv)> 1 ):
    nDiskTestSizeMB=int(sys.argv[1]);
    print( "Changing disk test size to %d MB" % nDiskTestSizeMB );
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



"""