#
# Mega fast and chool schema editor
# (c) 2016 A.Mazel
#

import cv2
imoport cv2.cv

import numpy
import time


nCptFrameFps = 0
timeBeginFps = time.time()
nNbrFrameToComputeFps = 1000


screenName = "fast_scheme"
bSmallScreen = 1
nSizeX = 2960;
nSizeY = 2100;
if( bSmallScreen ):    
    nSizeX /=2
    nSizeY /=2

        cv.SetMouseCallback(self.windowname, self.on_mouse)

    def on_mouse(self, event, x, y, flags, param):
        pt = (x, y)
        if event == cv.CV_EVENT_LBUTTONUP or not (flags & cv.CV_EVENT_FLAG_LBUTTON):
            self.prev_pt = None
        elif event == cv.CV_EVENT_LBUTTONDOWN:
            self.prev_pt = pt
        elif event == cv.CV_EVENT_MOUSEMOVE and (flags & cv.CV_EVENT_FLAG_LBUTTON) :
            if self.prev_pt:
                for dst in self.dests:
                    cv.Line(dst, self.prev_pt, pt, cv.ScalarAll(255), 5, 8, 0)
            self.prev_pt = pt
            cv.ShowImage(self.windowname, img)

screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
while(True):
    
    # read user events
    
    cv2.imshow( screenName, screen ) 
    
    nKey =  cv2.waitKey(1) & 0xFF;

    
    
    
    time.sleep(0.02) # 0.03
    
    # print fps
    nCptFrameFps += 1
    if( nCptFrameFps > nNbrFrameToComputeFps ):
        duration = time.time()-timeBeginFps
        rFps = 1./(duration/nCptFrameFps)
        print( "fps: %5.1f" % rFps )
        nCptFrameFps = 0
        timeBeginFps = time.time()
        break;
        
# while(True) - end