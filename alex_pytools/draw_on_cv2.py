# -*- coding: utf-8 -*-
import cv2
import time

def getScreenResolution():
    from win32api import GetSystemMetrics
    wScreen = GetSystemMetrics(0)
    hScreen = GetSystemMetrics(1)
    return wScreen, hScreen

class CV2_Drawable:
    """
    handle all mouse handling to draw on a cv2 drawed image.
    eg:
    im = cv2.imread("toto.jpg")
    drawer = CV2_Drawer( im)
    while 1:
        if drawer.isFinished():
            break
        
    
    """
    def __init__( self ):
        self.strWindowName = None
        self.reset()
        
    def reset( self ):
        if self.strWindowName != None:
            cv2.destroyWindow(self.strWindowName)
        self.listSegment = [] # list of all mouse drawed segment
        self.bQuit = False
        self.bMouseDown = False
        self.imageOriginal = None
        self.image = None
        self.screen = None
        self.bInScrollMode = False
        self.colorDraw = (0,0,0)
        
        
    def create(self, image, strWindowName = "Draw on img"):
        self.reset()
        
        self.strWindowName = strWindowName
        self.imageOriginal = image
        self.image = self.imageOriginal.copy()
        
        self.recordedMouseDraw = [] # record all position of drawing: a list of all position
        self.nIndexLastRecord = -1 # point the last recorded (will point the end unless during undo navigation)  

        wScreen, hScreen = getScreenResolution() 
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
        self._redraw()
        cv2.waitKey(1)
        
    def onTrackBarChange( self, count ):
        print("tb: %d" % count )
        
    def on_mouse_event(self,event, x, y, flags, param):
        print( "DBG: event: 0x%x, pos: (%d, %d), flags: %x, param: %s" % (event,x, y,flags, param) )
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            self._mouseUp( x, y )
        elif event == cv2.EVENT_LBUTTONDOWN:
            self._mouseDown( x, y )
        elif event == cv2.EVENT_MOUSEMOVE: # and (flags & cv2.CV_EVENT_FLAG_LBUTTON) :
            self._mouseMove( x, y, bErase = (flags==1) )
    # on_mouse_event - end
    
    def _mouseDown( self, x, y ):

        if x < 40:
            # control mode
            print("INF: _mouseDown: control down: y: %d, screen shape: %d" % (y,self.screen.shape[0]) )
            nSizeBorderUndo = 40
            if y < nSizeBorderUndo:
                self.undo()
            elif y > self.screen.shape[0] - nSizeBorderUndo:
                self.redo()
            self.nControlModeStartY = y
            self.bInScrollMode = True
            return
            
        while self.nIndexLastRecord != -1 and self.nIndexLastRecord < len(self.recordedMouseDraw):
            # after an undo
            del self.recordedMouseDraw[-1]
        self.recordedMouseDraw.append([])
        self.nIndexLastRecord = len(self.recordedMouseDraw)
        print( "DBG: self.nIndexLastRecord: %s" % self.nIndexLastRecord )
        self.writeStart(x,y+self.yOrig)
        self.bMouseDown = True
        self._mouseMove(x,y)
        
    def _mouseUp( self, x, y ):
        if self.bMouseDown:
            self._mouseMove(x, y)
            self.writeEnd(x,y+self.yOrig)
            self.bMouseDown = False
        self.bInScrollMode = False
        
    def _mouseMove( self, x, y, bErase = False ):
        if self.bMouseDown:
            self.recordedMouseDraw[-1].append((x,y+self.yOrig))
            self.writeContinue(x,y+self.yOrig, bErase)
            cv2.imshow( self.strWindowName, self.screen )
        else:
            if self.bInScrollMode:
                # control mode
                dyScroll = self.nControlModeStartY - y
                print( "dyScroll: %d" % dyScroll )
                self.yOrig += dyScroll
                if self.yOrig < 0:
                    self.yOrig = 0
                if self.yOrig > self.yOrigMax:
                    self.yOrig = self.yOrigMax-1
                self.nControlModeStartY = y
                self._redraw()
                
                
            
    def writeStart( self, x, y ):
        self.lenTrait = 0
        self.lastPos = None
        
    def writeContinue( self, x, y, bErase = False ):
        if self.lastPos != None:
            if bErase:
                col = (127,127,127)
            else:
                col= self.colorDraw
            cv2.line(self.image, self.lastPos, (x,y), col, 2, 0 )
        self.lenTrait += 1
        self.lastPos = (x,y)
        
    def writeEnd( self, x, y ):
        if self.lenTrait < 2:
            cv2.circle(self.image, (x,y), 2, self.colorDraw, 0 )
            cv2.imshow( self.strWindowName, self.screen )
        
    def _update( self ):
        bMustRedraw = False
        
        key = cv2.waitKey(1)
        if key != -1: print("key: %d" % key )
        if key == ord('q') or key == 27:
            cv2.destroyWindow(self.strWindowName)
            self.bQuit = True
            return
        
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
            self.undo()

        if key == ord('y'): # y: redo
            self.redo()
            
        if bMustRedraw:
            self._redraw()
            
            
    def undo( self ):
        print("undo")
        self.nIndexLastRecord -= 1
        self._redrawAllDrawing()
            
    def redo( self ):
        print("redo")
        if self.nIndexLastRecord < len(self.recordedMouseDraw):
            self.nIndexLastRecord += 1
            self._redrawAllDrawing()        
            
    def _redraw( self ):
        self.screen = self.image[self.yOrig:self.yOrig+self.hSeen,:]
        h,w,p = self.screen.shape
        
        cv2.imshow( self.strWindowName, self.screen )
        cv2.resizeWindow(self.strWindowName, int(self.rZoomFactor*w),int(self.rZoomFactor*h)) 

    def _redrawAllDrawing( self ):
        self.image = self.imageOriginal.copy()
        self._redraw()
        print("recordedMouseDraw: %s" % self.recordedMouseDraw )
        for draw in self.recordedMouseDraw[0:self.nIndexLastRecord]:
            self.writeStart(draw[0][0], draw[0][1])
            for pt in draw:
                self.writeContinue(pt[0],pt[1])
            self.writeEnd(draw[-1][0],draw[-1][1])
        self._redraw()
        
    def isFinished( self ):
        self._update()
        return self.bQuit
        
    def setDrawColor( self, color = (0,0,0) ):
        self.colorDraw = color
        
# class CV2_Drawable - end

def autoTest():
    import numpy
    nSizeX, nSizeY = (800, 600)
    screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    screen[:] = (255,255,255)
    drawable = CV2_Drawable()
    drawable.create(screen)
    
    while 1:
        if drawable.isFinished(): # if you don't wait for that, it will crash at exit ?!? (seen 05/2020: windows10 mstablet)
            break
            
if __name__ == "__main__":
    autoTest()
    
"""
    On peut multiplier le numerateur et le denominateur par un meme nombre sans changer la valeur de la
    fraction, donc 3/5 = 3*2/5*2 =  6/10 soit 0.6
"""