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
        self.imageOriginal = image
        self.image = self.imageOriginal.copy()
        
        self.recordedMouseDraw = [] # record all position of drawing: a list of all position
        self.nIndexLastRecord = -1 # point the last recorded (will point the end unless during undo navigation)  

        
        from win32api import GetSystemMetrics
        wScreen = GetSystemMetrics(0)
        hScreen = GetSystemMetrics(1)
        #~ wScreen *= 2
        #~ hScreen *= 2
        print("screen reso: %dx%d" % (wScreen, hScreen) )
        if wScreen > 2*self.image.shape[1]:
            self.image = cv2.resize( self.image, (-1,-1), fx=2,fy=2)
        
        winFlags = cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO | cv2.WINDOW_GUI_EXPANDED
        print("winFlags: %X" % winFlags )
        #~ winFlags = cv2.WINDOW_AUTOSIZE | cv2.WINDOW_FREERATIO | cv2.WINDOW_GUI_EXPANDED
        #~ print("winFlags: %X" % winFlags )
        #~ winFlags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_FULLSCREEN
        #~ print("winFlags: %X" % winFlags )
        
        cv2.namedWindow( self.strWindowName, winFlags )
        h,w,p = self.image.shape

        
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
        self.recordedMouseDraw.append([])
        self.nIndexLastRecord = len(self.recordedMouseDraw)
        self.writeStart(x,y)
        self._mouseMove(x,y)
        
    def _mouseUp( self, x, y ):
        if self.bMouseDown:
            self._mouseMove(x, y)
            self.writeEnd(x,y)
            self.bMouseDown = False
        
    def _mouseMove( self, x, y ):
        if self.bMouseDown:
            self.recordedMouseDraw[-1].append((x,y))
            self.writeContinue(x,y)
            cv2.imshow( self.strWindowName, self.screen )
            
    def writeStart( self, x, y ):
        self.lenTrait = 0
        self.lastPos = None
        
    def writeContinue( self, x, y ):
        if self.lastPos != None:
            cv2.line(self.screen, self.lastPos, (x,y), (0,0,0), 2, 0 )
        self.lenTrait += 1
        self.lastPos = (x,y)
        
    def writeEnd( self, x, y ):
        if self.lenTrait < 2:
            cv2.circle(self.screen, (x,y), 2, (0,0,0), 0 )
            cv2.imshow( self.strWindowName, self.screen )
        
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
            self.yOrig -= 10
            if self.yOrig < 0:
                self.yOrig = 0
            bMustRedraw = True
        if key == 42: # '* or down
            self.yOrig += 10
            if self.yOrig > self.yOrigMax:
                self.yOrig = self.yOrigMax-1
            bMustRedraw = True

        if key == ord('z'): # z: undo
            self.nIndexLastRecord -= 1
            self._redrawAllDrawing()

            
        if bMustRedraw:
            self._redraw()
            
    def _redraw( self ):
        self.screen = self.image[self.yOrig:self.yOrig+self.hSeen,:]
        h,w,p = self.screen.shape
        
        cv2.imshow( self.strWindowName, self.screen )
        cv2.resizeWindow(self.strWindowName, int(self.rZoomFactor*w),int(self.rZoomFactor*h)) 

    def _redrawAllDrawing( self ):
        self.image = self.imageOriginal.copy()
        for draw in self.recordedMouseDraw[0:self.nIndexLastRecord]:
            self.writeStart(draw[0][0], draw[0][1])
            for pt in draw:
                self.writeContinue(pt[0],pt[1])
            self.writeEnd(draw[-1][0],draw[-1][1])
        self._redraw()
        
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