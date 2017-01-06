# -*- coding: utf-8 -*-

import ctypes
import struct
import time

import cv2 # manually copied cv2.pyd to lib/site-packages
import numpy # pip install numpy

def getMousePosition():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]
        
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def moveMouseAndClick( x, y ):    
    setCursorPos = ctypes.windll.user32.SetCursorPos
    sendMouseEvent = ctypes.windll.user32.mouse_event

    setCursorPos(x,y)
    sendMouseEvent( 2,0,0,0,0)
    sendMouseEvent( 4,0,0,0,0)
    
def getForegroundWindow():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    #~ active_window_name = ctypes.windll.user32.GetWindowText(window)
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)        
    return buff.value


def captureScreen():
    """
    retrieve a numpy/cv2 buffer containing the whole screen pixels
    return: the numpy object
    """
    #Constants   
    SM_CXSCREEN = 0   
    SM_CYSCREEN = 1        
    SRCCOPY = 0xCC0020      
    DIB_RGB_COLORS = 0
    
    srcdc = ctypes.windll.user32.GetWindowDC(0)
    memdc = ctypes.windll.gdi32.CreateCompatibleDC(srcdc)
    
    #~ l,t,r,b=ctypes.windll.gdi32.GetWindowRect(0)
    #~ height=b-t
    #~ width=r-l
    width =  ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
    height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
    print( "captureScreen: screen res: %dx%d" % (width, height) )
    left = 0
    top = 0
    

    bmp = ctypes.windll.gdi32.CreateCompatibleBitmap(srcdc, width, height)
    ctypes.windll.gdi32.SelectObject(memdc, bmp)
    ctypes.windll.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, SRCCOPY)        
    bmp_header = struct.pack('LHHHH', struct.calcsize('LHHHH'), width, height, 1, 24)
    c_bmp_header = ctypes.c_buffer(bmp_header) 
    c_bits = ctypes.c_buffer(' ' * (height * ((width * 3 + 3) & -4)))
    got_bits = ctypes.windll.gdi32.GetDIBits(memdc, bmp, 0, height,c_bits, c_bmp_header, DIB_RGB_COLORS)
    print( "nbrline: %s" % got_bits )
    
    # c_bits contains now a ctpes.c_char_Array
    
    # convert to numpy and save
    #~ img = np.zeros([width, height,3],dtype=np.uint8)
    #~ for j in range(height):
        #~ for i in range(width):
    #~ img = numpy.array(c_bits)
    img = numpy.reshape( numpy.frombuffer( c_bits, numpy.uint8 )[:-1], (height,width , 3) )
    
    img = img[::-1] # mirror
    # revert b and r
    #~ r,g,b = cv2.split(img)
    #~ img = cv2.merge([b,g,r])

    print img.shape
    #~ cv2.imwrite( "/tmp/toto.png", img )
    return img
# captureScreen - end

#~ print getMousePosition()
#moveMouseAndClick(100,100)
#~ captureScreen()


def recordBook():
    imgprev = None
    numpage = 1
    while(1):
        focused = getForegroundWindow()
        if not "Reader for PC" in focused:
            print( "pas dans reader" )
            time.sleep(0.5)
            continue
        if "(ne " in focused:
            print( "ne r�pond pas..." )
            time.sleep(0.5)
            continue
        print( "capturing...")
        img = captureScreen()
        # book page numer is from 736,870 a 860,888
        #check this pas is unseen
        if numpy.all(img == imgprev):
            print( "next page...")
            moveMouseAndClick(874,867) # next page
            time.sleep(1.)
        else:
            print( "writing %d" % numpage )
            imgprev = img            
            cv2.imwrite( "/tmp/%08d.png" % numpage, img )
            numpage += 1
        

recordBook()
#~ print getForegroundWindow()
# j'ain installé tessract. a tester !
# j'ain installé tessract. a tester !