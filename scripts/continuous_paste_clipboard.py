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
    frequency = 200 # Set Frequency To 2500 Hertz
    duration = 250  # Set Duration To 1000 ms == 1 second
    misctools.beep(frequency, duration)

def beepEveryHalf():
    if misctools.isQuarterHour():
        if misctools.isHalfHour():
            h,m,s = misctools.getTime()
            if m == 30:
                # demi
                #~ misctools.beep(440, 100)
                misctools.deepbell()
            else:
                # count the hour
                for i in range(h):
                    #~ misctools.beep(440, 100)
                    #~ time.sleep(0.1)
                    misctools.ringTheBell(h)
        else:
            #~ misctools.beep(880, 100)
            misctools.ting()
    if misctools.isHalfHour(nOffsetMin=5):
        # fin du pomodoro
        for i in range(3):
            misctools.ting()
            time.sleep(0.1)
    
    

def continuousSave():
    print("INF: continuousSaveOfClipbBoardImage...")
    img_prev = None
    nFrameWithoutSave = 0
    while 1:
        beepEveryHalf()
        img = ImageGrab.grabclipboard()
        # or ImageGrab.grab() to grab the whole screen!
        if img == None:
            time.sleep(0.5)
            continue
        if not isPilImgEqual( img, img_prev ):
            img_prev = img
            name = "/tmp_scr/" + misctools.getFilenameFromTime() + ".png"
            print( "INF: saving to '%s'" % name ) 
            img.save( name, 'PNG' )
            bipInform()
            nFrameWithoutSave = 0
        else:
            if nFrameWithoutSave > 20:
                time.sleep(0.4)
            else:
                time.sleep(0.05)
            nFrameWithoutSave += 1
# continuousSave - end

if __name__ == "__main__":
    continuousSave()