# -*- coding: utf-8 -*-

#
# Mega fast and chool schema editor
# (c) 2016 A.Mazel
#

import cv2

import mutex
import numpy
import sys
import time

sys.path.append( "../../protolab" )
import protolab.geometry as geo

def computePerimeter(shape):
    rDist = 0
    for i in range(len(shape)-1): # we don't add the distance between last and first
        rDist += geo.distance( shape[i], shape[(i+1)%len(shape)] ) # modulo in the case of we want the distance to first and last
    return rDist

class FastScheme:
    def __init__( self, nResolutionW, nResolutionH ):
        self.nResolutionW = nResolutionW # rendeing resolution, could and will be different than window size
        self.nResolutionH = nResolutionH
        # but for the moment, they are of the same size
        self.listPts = [] # a list of list of coord (one for each trace)
        self.listObject = [] # a list of object to render
        self.listClosedFigures = [] # list of closed figures (square, circle, ...)
        self.nGridSize = 20
        self.bMouseDown = False
        self.mutexMouse = mutex.mutex()
        
    def __del__( self ):
        self.exit()
        
    def exit( self ):
        print( "INF: FastScheme: exiting..." );
        file = open( "/tmp/fast" + str(time.time()) + ".dat", "wt" )
        file.write( str(self.listPts) )
        file.close()
        
    def computeShapeBuffer( self ):
        pass
        
    def analyseShape( self, shape ):
        """
        analyse a new shape
        """
        rPerimeter = computePerimeter( shape )
        print( "rPerimeter: %s" % rPerimeter )        
        rLastFirstDist = geo.distance( shape[0], shape[-1] )
        print( "rLastFirstDist: %s" % rLastFirstDist )
        if( rLastFirstDist * 6 < rPerimeter ): # 8
            # nearly bClosedFigure
            shape.append( shape[0] )
            self.listClosedFigures.append(shape[:])
            
            

    def mouseDown(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
        self.listPts.append([])
        self.bMouseDown = True
        self._mouseMove( x, y )
        self.mutexMouse.unlock()

    def mouseUp(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)        
        self._mouseMove( x, y )
        self.bMouseDown = False
        self.analyseShape( self.listPts[-1] )
        self.mutexMouse.unlock()
        
    def _mouseMove( self, x, y ):
        """
        unarmored moveMove version
        """
        if( self.bMouseDown ):
            self.listPts[-1].append([x,y])
        
    def mouseMove(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)        
        self._mouseMove(x, y)
        self.mutexMouse.unlock()
            
    def gridify( self, pt ):
        pt[0] = ((pt[0]+(self.nGridSize/2))/self.nGridSize)*self.nGridSize
        pt[1] = ((pt[1]+(self.nGridSize/2))/self.nGridSize)*self.nGridSize                
        
        
    def update( self ):
        pass
        
    def render( self, img ):
        """
        render in an image (already created)
        """
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
            
        img_h, img_w, nbrplane = img.shape
        img[::] = (255,255,255)
        bMouseDown = self.bMouseDown
        for i in range(len(self.listPts)):
            shape = self.listPts[i]
            if( bMouseDown and i == len(self.listPts)-1 ):
                bLastOne = 1
            else:
                bLastOne = 0
            pt1 = shape[0]
            if( not bLastOne ):
                self.gridify(pt1)
            
            for pt2 in shape[1:]:
                if( not bLastOne ):
                    self.gridify(pt2)
                cv2.line( img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), (255,0,0) )
                pt1 = pt2
        # for listPts - end
        
        for fig in self.listClosedFigures:
            for pt in fig:
                pt1 = fig[0]
                for pt2 in shape[1:]:
                    cv2.line( img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), (255,0,0), 2 )
                    pt1 = pt2

        
        self.mutexMouse.unlock()
    # render - end
        
# class FastScheme - end

def runApp():
    nCptFrameFps = 0
    timeBeginFps = time.time()
    nNbrFrameToComputeFps = 100
    
    screenName = "fast_scheme"
    bSmallScreen = 1
    nSizeX = 2960;
    nSizeY = 2100;
    if( bSmallScreen ):    
        nSizeX /=2
        nSizeY /=2
        
    fast = FastScheme(nSizeX, nSizeY)


    def on_mouse_event(event, x, y, flags, param):
        #print (x, y)
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            fast.mouseUp( x, y )
        elif event == cv2.EVENT_LBUTTONDOWN:
            fast.mouseDown( x, y )
        elif event == cv2.EVENT_MOUSEMOVE: # and (flags & cv2.CV_EVENT_FLAG_LBUTTON) :
            fast.mouseMove( x, y )
    # on_mouse_event - end

    screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    cv2.namedWindow( screenName )
    cv2.setMouseCallback( screenName, on_mouse_event )
    while(True):
    
        # read user events (background)
        fast.render( screen )
        cv2.imshow( screenName, screen )
        nKey =  cv2.waitKey(1) & 0xFF;
        if( chr(nKey) == 'q' ):
            break;

    
        time.sleep(0.02) # 0.03
        
        # print fps
        nCptFrameFps += 1
        if( nCptFrameFps > nNbrFrameToComputeFps ):
            duration = time.time()-timeBeginFps
            rFps = 1./(duration/nCptFrameFps)
            print( "fps: %5.1f" % rFps )
            nCptFrameFps = 0
            timeBeginFps = time.time()       
    # while(True) - end
    # fast = None; # call del, why it doesn't call it automatically !?! (rtfm)
    fast.exit()
    print( "INF: runApp: finished..." )
# runApp - end

runApp()
print( "finished..." )