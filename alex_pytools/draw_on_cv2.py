# -*- coding: utf-8 -*-
import cv2

class CV2_Drawer:
    """
    handle all mouse handling to draw on a cv2 drawed image.
    eg:
    im = cv2.imread("toto.jpg")
    drawer = CV2_Drawer( im)
    while 1:
        if drawer.isFinished():
            break
        
    
    """
    def __init__( self, image, strWindowName = "CV2 Draw" ):
        self.listSegment = [] # list of all mouse drawed segment
        self.strWindowName = strWindowName
        self.bQuit = False
        self.bMouseDown = False
        self.image = image
        
        winFlags = cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO | cv2.WINDOW_GUI_EXPANDED
        print("winFlags: %X" % winFlags )
        #~ winFlags = cv2.WINDOW_AUTOSIZE | cv2.WINDOW_FREERATIO | cv2.WINDOW_GUI_EXPANDED
        #~ print("winFlags: %X" % winFlags )
        #~ winFlags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_FULLSCREEN
        #~ print("winFlags: %X" % winFlags )
        
        cv2.namedWindow( self.strWindowName, winFlags )
        h,w,p = self.image.shape
        
        from win32api import GetSystemMetrics

        wScreen = GetSystemMetrics(0)
        hScreen = GetSystemMetrics(1)
        #~ wScreen *= 2
        #~ hScreen *= 2
        print("screen reso: %dx%d" % (wScreen, hScreen) )
        
        print("im reso: %dx%d" % (w, h) )

        self.rZoomFactor = 2.
        self.rZoomFactor = wScreen/w
        self.hSeen = int( hScreen / self.rZoomFactor )
        self.yOrig = 0
        self.yOrigMax = h - self.hSeen
        self._redraw()
        cv2.moveWindow( self.strWindowName, 10, 10 )       
        cv2.resizeWindow(self.strWindowName, int(self.rZoomFactor*w),int(self.rZoomFactor*h)) 
        #~ cv2.createTrackbar("tb", self.strWindowName, 0, 100, self.onTrackBarChange)
            
        cv2.setMouseCallback( self.strWindowName, self.on_mouse_event )
        cv2.waitKey(1)
        
    def onTrackBarChange( self, count ):
        print("tb: %d" % count )
        
    def on_mouse_event(self,event, x, y, flags, param):
        #~ print(x, y)
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            self._mouseUp( x, y )
        elif event == cv2.EVENT_LBUTTONDOWN:
            self._mouseDown( x, y )
        elif event == cv2.EVENT_MOUSEMOVE: # and (flags & cv2.CV_EVENT_FLAG_LBUTTON) :
            self._mouseMove( x, y )
    # on_mouse_event - end
    
    def _mouseDown( self, x, y ):
        self.bMouseDown = True
        self.lastPos = None
        self._mouseMove(x,y)
        
    def _mouseUp( self, x, y ):
        self.bMouseDown = False
        
    def _mouseMove( self, x, y ):
        if self.bMouseDown:
            if self.lastPos != None:
                cv2.line(self.screen, self.lastPos, (x,y), (0,0,0), 2 )
                cv2.imshow( self.strWindowName, self.screen )
            self.lastPos = (x,y)
            
        
        
    def _update( self ):
        bMustRedraw = False
        
        key = cv2.waitKey(1)
        if key != -1: print("key: %d" % key )
        if key == ord('q') or key == 27:
            self.bQuit = True
        
        if key == 171 or key == 43: # '+' on num keyboard
            self.rZoomFactor *=2
            bMustRedraw = True
            print("zoom+")
        elif key == 173 or key == 45: # '-' on num keyboard
            self.rZoomFactor /=2.
            bMustRedraw = True
            print("zoom-")
            
        if key == 36: # '$ or up
            self.yOrig -= 4
            if self.yOrig < 0:
                self.yOrig = 0
            bMustRedraw = True
        if key == 42: # '* or down
            self.yOrig += 4
            if self.yOrig > self.yOrigMax:
                self.yOrig = self.yOrigMax-1
            bMustRedraw = True

            
        if bMustRedraw:
            self._redraw()
            
    def _redraw( self ):
        self.screen = self.image[self.yOrig:self.yOrig+self.hSeen,:]
        h,w,p = self.screen.shape
        
        cv2.imshow( self.strWindowName, self.screen )
        cv2.resizeWindow(self.strWindowName, int(self.rZoomFactor*w),int(self.rZoomFactor*h)) 

    def isFinished( self ):
        self._update()
        return self.bQuit
        
# class Drawer - end

    #~ screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    #~ cv2.namedWindow( screenName )
    
    
"""
    On peut multiplier le numerateur et le denominateur par un meme nombre sans changer la valeur de la
    fraction, donc 3/5 = 3*2/5*2 =  6/10 soit 0.6
"""