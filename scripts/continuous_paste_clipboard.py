# pip install pillow
from PIL import ImageGrab

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

import time

def isPilImgEqual(im1, im2):
    if im1 == None or im2 == None:
        return False
        
    from PIL import ImageChops
    return ImageChops.difference(im1, im2).getbbox() is None
    
    #~ return im1.getdata() == im2.getdata() # compare just adress?
# isPilImgEqual - end

def bipInform():
    import winsound
    frequency = 500 # Set Frequency To 2500 Hertz
    duration = 50  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

def continuousSave():
    print("INF: continuousSaveOfClipbBoardImage...")
    img_prev = None
    while 1:
        img = ImageGrab.grabclipboard()
        # or ImageGrab.grab() to grab the whole screen!
        if img == None:
            time.sleep(0.2)
            continue
        if not isPilImgEqual( img, img_prev ):
            img_prev = img
            name = "/tmp/" + misctools.getFilenameFromTime() + ".png"
            print( "INF: saving to '%s'" % name ) 
            img.save( name, 'PNG' )
            bipInform()
        else:
            time.sleep(0.2)
# continuousSave - end


continuousSave()