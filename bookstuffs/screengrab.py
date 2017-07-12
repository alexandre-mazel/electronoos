# -*- coding: utf-8 -*-

import os
import sys
print sys.version

import ctypes
import struct
import time

import cv2 # manually copied cv2.pyd to lib/site-packages
import numpy # pip install numpy # pip: python get-pip.py

import PIL # pip install pillow
import pytesseract

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
    # surface: 2736x1824
    width = 2736
    height = 1824
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

def getChangeDifference( im1, im2 ):
	"""
	compute number of different pixels in two open cv2/np images
	return a ratio of different pixel [0..1] 1: all pixels are different
	"""
	diff = im1-im2
	ret,diff = cv2.threshold(diff, 32,1,cv2.THRESH_BINARY)
	#~ print(diff)
	avgDiff = diff.sum()/float(im1.shape[0]*im1.shape[1])
	print( "avg(diff): %s" % avgDiff )
	return avgDiff


def recordBook():
	imgprev = None
	numpage = 1
	while(1):
		focused = getForegroundWindow()
		#print( "current app: %s" % str(focused) )
		if not "Reader for PC" in focused:
		    print( "pas dans reader" )
		    time.sleep(0.5)
		    continue
		if "(ne " in focused.lower():
		    print( "ne répond pas..." )
		    time.sleep(0.5)
		    continue
		print( "capturing...")
		img = captureScreen()
		# book page numer is from 736,870 a 860,888
		#check this pas is unseen
		bPageEqual = imgprev == None or numpy.all(img == imgprev)
		bPageEqual = imgprev == None or getChangeDifference(img,imgprev) < 0.1
		if bPageEqual:
			print( "next page...")
			coord = (874, 876) #vaioCoord			
			#coord = (724, 900)# surface
			coord = (580, 720)# surface
			
			moveMouseAndClick(coord[0], coord[1]) # next page
			time.sleep(1.)
		else:
		    print( "writing %d" % numpage )
		    imgprev = img            
		    cv2.imwrite( "/tmp/%08d.png" % numpage, img )
		    numpage += 1

def cleanText( txt ):
	txt = txt.replace( " Ll", " d" )
	txt = txt.replace( " muf ", " oeuf " )
	txt = txt.replace( "'muf ", "'oeuf " )
	txt = txt.replace( " ccm", " com" )
	txt = txt.replace( " ccn", " con" )
	txt = txt.replace( "jcn ", "ion " )
	txt = txt.replace( "mem ", "ment " )
	txt = txt.replace( " mc", " mo" )
	return txt

def analysePage( openImage ):
	"""
	Analyse one page (already well cropped)
	"""
	timeBegin = time.time()
	res = pytesseract.image_to_string(openImage)
	
	duration = time.time() - timeBegin
	print( "Duration: %fs" % duration )
	#~ res = res.split()
	#~ res = " ".join(res)
	res = cleanText(res)
	print res
	return res

def analyseImage( strImg ):
	if not os.path.exists( strImg ):
		print( "ERR: file '%s' not found" % strImg )
		return -1
	print dir(pytesseract)
	 
	im = PIL.Image.open(strImg)
	top = 80
	bottom = 800
	imPage = im.crop( ( 120, top, 750, bottom ) )
	imPage.save("/tmp/tmp1.jpg" )
	txt1 = analysePage( imPage )

	imPage = im.crop( ( 840, top, 1520, bottom ) )
	imPage.save("/tmp/tmp2.jpg" )
	txt2 = analysePage( imPage )
	
	return txt1+txt2
# analyseImage - end

def testGetChangeDifference(fn1,fn2):
	im1 = cv2.imread(fn1)
	im2=cv2.imread(fn2)
	print getChangeDifference(im1,im2)


#~ print getForegroundWindow()
recordBook()
#~ testGetChangeDifference("/tmp/00000001.png","/tmp/00000002.png")
#~ analyseImage("/datas/00000001.png")
#~ analyseImage("/tmp/00000001.png")