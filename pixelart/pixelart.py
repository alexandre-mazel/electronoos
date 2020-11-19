# -*- coding: utf-8 -*-

#
# Pixel Art
# (c) 2016 A.Mazel
#

#
# Current way:
# toggle one big pixel
#
# 

import cv2

import math
import mutex #python2
import numpy
import sys
import time

sys.path.insert( 0, "../../protolab" )
import protolab.geometry as geo


class PixelArt:
    def __init__( self, nImgSizeW, nImgSizeH, nScreenSizeW, nScreenSizeH ):
        self.nImgSizeW = nImgSizeW # rendering resolution, could and will be different than window size
        self.nImgSizeH = nImgSizeH
        self.nScreenSizeW = nScreenSizeW # rendering resolution, could and will be different than window size
        self.nScreenSizeH = nScreenSizeH
        
        self.resetPixels()
                
        self.colors = []
        self.colors.append((0,0,0))
        self.colors.append((255,255,255))
        self.colors.append((127,127,127))
        self.colors.append((0,0,255))
        self.colors.append((0,255,0))
        self.colors.append((255,0,0))
        self.nExtraColorIndex = 2
        
        # test:
        self.pixels[0][0] = 0
        self.pixels[-1][-1] = 0
        self.bMouseDown = False
        
        self.lastDrawX = self.lastDrawY = -1
        self.currentColorIndex = -1
        self.bAlreadyToggled = False
        
        self.mutexMouse = mutex.mutex()


        self.strSaveFilename = "/tmp/fastscheme.dat"
        self.loadFromDisk()
        
        self.computeScreenLayout()
        
        self.timeBeginDraw = time.time()
        
    def resetPixels( self ):
        self.pixels = list()
        for j in range(self.nImgSizeH):
            self.pixels.append(list())
            for i in range(self.nImgSizeW):
                self.pixels[-1].append(1)        
        
    def __del__( self ):
        self.exit()
    
    def saveToDisk(self):
        file = open(self.strSaveFilename, "wt")
        file.write(str(self.pixels))
        file.close()
        
    def loadFromDisk(self):
        try:
            file = open( self.strSaveFilename, "rt" )
            aList = file.read()
            self.pixels = eval(aList)
            file.close()
        except:
            return 0
            
        print( "INF: PixelArt.loadFromDisk: loading from '%s'" % self.strSaveFilename );
        
        print( "INF: PixelArt.loadFromDisk: at end: %s" % self.__str__() )
        return 1
        
    def exit( self ):
        print( "INF: PixelArt.exit: exiting..." );
        self.saveToDisk()
        
    def __str__( self ):
        strOut = ""
        #~ strOut += "full figs: \n%s\n" % str(self.listFigures)
        return strOut
        
    def computeScreenLayout( self ):
        """
        based on image size and resolution screen size, compute where are the stuffs
        """
        
        self.nPixelSizeW = self.nScreenSizeW/self.nImgSizeW
        self.nPixelSizeH = self.nScreenSizeH/self.nImgSizeH

        self.nPixelSizeW = self.nPixelSizeH # we want a square draw
  
        # all in pixel in the rendering buffers
        self.nDrawAreaX = 0
        self.nDrawAreaY = 0
        self.nDrawAreaW = self.nPixelSizeW * self.nImgSizeW
        self.nDrawAreaH = self.nPixelSizeH * self.nImgSizeH
        
        self.nControlX = self.nDrawAreaX+self.nDrawAreaW
        self.nControlY = self.nDrawAreaY
        
        self.nChangeColorX = self.nControlX + 10
        self.nChangeColorY = self.nControlY + 0
        
        self.nEraseX = self.nControlX + 100
        self.nEraseY = self.nControlY + 100
        
    def mouseDown(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
        self.bMouseDown = True

        self._mouseMove( x, y )        

        self.mutexMouse.unlock()

    def mouseUp(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)        
        self._mouseMove( x, y )        

        self.bMouseDown = False
        self.lastDrawX = self.lastDrawY = -1
        self.currentColorIndex = -1
        self.bAlreadyToggled = False
        
        self.mutexMouse.unlock()
        
    def _mouseMove( self, x, y ):
        """
        unarmored moveMove version
        """
        if( self.bMouseDown ): 
            if x < self.nDrawAreaX+self.nDrawAreaW and y < self.nDrawAreaY+self.nDrawAreaH:
                xDraw = (x - self.nDrawAreaX)/self.nPixelSizeW
                yDraw = (y - self.nDrawAreaY)/self.nPixelSizeH
                if self.lastDrawX != xDraw or self.lastDrawY != yDraw:
                    col = self.pixels[yDraw][xDraw]
                    if self.currentColorIndex == -1:
                        if col == 0:
                            self.currentColorIndex = 1
                        elif col == 1:
                            self.currentColorIndex = self.nExtraColorIndex
                        else:
                            self.currentColorIndex = 0
                    self.pixels[yDraw][xDraw] = self.currentColorIndex
                    self.lastDrawX = xDraw
                    self.lastDrawY = yDraw
            else:
                # out of drawing area
                if x > self.nEraseX and x < self.nEraseX + 30 and y >self.nEraseY and y < self.nEraseY + 30:
                    self.resetPixels()
                elif x >= self.nChangeColorX and x < self.nChangeColorX+self.nPixelSizeW and y >= self.nChangeColorY and y < self.nChangeColorY+self.nPixelSizeH:
                    if not self.bAlreadyToggled:
                        self.bAlreadyToggled = True
                        self.nExtraColorIndex = ( self.nExtraColorIndex + 1 )
                        if self.nExtraColorIndex >= len(self.colors):
                            self.nExtraColorIndex = 2

                
    def mouseMove(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
        self._mouseMove(x, y)
        self.mutexMouse.unlock()
            
    def update( self ):
        pass
        
    def render( self, img ):
        """
        render in an image (already created)
        """
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
            
        self.renderSizeW = 320
        self.renderSizeH = 240
            
        img_h, img_w, nbrplane = img.shape
        img[::] = (255,255,255)
        bMouseDown = self.bMouseDown
        
        cv2.rectangle( img, (self.nDrawAreaX, self.nDrawAreaY),(self.nDrawAreaX+self.nDrawAreaW+1, self.nDrawAreaY+self.nDrawAreaH+1),0,1)

        for j in range(self.nImgSizeH):
            for i in range(self.nImgSizeW):
                cv2.rectangle(img, (i*self.nPixelSizeW,j*self.nPixelSizeH),((i+1)*self.nPixelSizeW,(j+1)*self.nPixelSizeH), self.colors[self.pixels[j][i]], -1, 0, 0)

        # draw control on right
        cv2.rectangle(img, (self.nChangeColorX,self.nChangeColorY),(self.nChangeColorX+self.nPixelSizeW,self.nChangeColorY+self.nPixelSizeH), self.colors[self.nExtraColorIndex], -1, 0, 0)
        
        cv2.rectangle(img, (self.nEraseX,self.nEraseY),(self.nEraseX+30,self.nEraseY+30), (127,45,245), -1, 0, 0)

        
        rDuration = time.time() - self.timeBeginDraw
        strTxt = str(int(rDuration)) + " sec"
        color = 255
        if rDuration > 300:
            color = (255,0,0)
        cv2.putText( img, strTxt, (self.nControlX+10, 400), 1, 2, color)
        
        self.mutexMouse.unlock()
    # render - end
    
    def handleSuppr( self ):
        pass
        
# class FastScheme - end

def runApp():
    """
    """
    nCptFrameFps = 0
    timeBeginFps = time.time()
    nNbrFrameToComputeFps = 100
    
    screenName = "PixelArt"
    nImgSizeX = 16;
    nImgSizeY = 16;
    
    nScreenSizeX = 1024;
    nScreenSizeY = 880;
        
    pa = PixelArt(nImgSizeX, nImgSizeY, nScreenSizeX, nScreenSizeY)


    def on_mouse_event(event, x, y, flags, param):
        #print (x, y)
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            pa.mouseUp( x, y )
        elif event == cv2.EVENT_LBUTTONDOWN:
            pa.mouseDown( x, y )
        elif event == cv2.EVENT_MOUSEMOVE: # and (flags & cv2.CV_EVENT_FLAG_LBUTTON) :
            pa.mouseMove( x, y )
    # on_mouse_event - end

    screen = numpy.zeros((nScreenSizeY,nScreenSizeX,3), numpy.uint8)
    cv2.namedWindow( screenName )
    cv2.moveWindow(screenName,0,0)
    cv2.setMouseCallback( screenName, on_mouse_event )
    while(True):
    
        # read user events (background)
        pa.render( screen )
        cv2.imshow( screenName, screen )
        nExtendedKey = cv2.waitKey(1)
        if( nExtendedKey != -1 ):
            print( "INF: nExtendedKey: %s" % nExtendedKey )
            nKey =  nExtendedKey & 0xFF;
            print( "INF: nKey: %s" % nKey )
            if( chr(nKey) == 'q' ):
                break;
            if( nKey == 255 ):
                # suppr
                pa.handleSuppr()

    
        time.sleep(0.03) # 0.03
        
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
    pa.exit()
    print( "INF: runApp: finished..." )
# runApp - end

runApp()
print( "finished..." )