# pip install pillow
from PIL import ImageGrab # pip install pillow

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
                print("bim 30")
                misctools.deepbell()
            else:
                # count the hour
                #~ for i in range(h):
                    #~ misctools.beep(440, 100)
                    #~ time.sleep(0.1)
                print("ring the bell")
                times = h
                if times > 12:
                    times = times-12
                if times == 0:
                    # NB: midnight => 12 coups
                    times = 12
                misctools.ringTheBell(times) # h de 0 a 24 => de 0 a 12 puis de 1 a 11
        else:
            #~ misctools.beep(880, 100)
            print("bim 15")
            misctools.ting()
    if misctools.isHalfHour(nOffsetMin=5):
        # fin du pomodoro
        print("bim pomodoro")
        for i in range(3):
            misctools.ting()
            time.sleep(0.1)
    
    

def continuousSave():
    print("INF: continuousSaveOfClipbBoardImage...")
    img_prev = None
    nFrameWithoutSave = 0
    while 1:
        beepEveryHalf()
        try:
            img = ImageGrab.grabclipboard()
        except OSError as err:
            print( "WRN: OSError in ImageGrab.grabclipboard: err: %s" % str(err))
            
        # or ImageGrab.grab() to grab the whole screen!
        if img == None:
            time.sleep(0.5)
            continue
        bIsImageEqual = True
        try:
            bIsImageEqual = isPilImgEqual( img, img_prev )
        except AttributeError as err:
            print( "WRN: isPilImgEqual: error: %s" % str(err))
            
        if not bIsImageEqual:
            img_prev = img
            name = "/scr/" + misctools.getFilenameFromTime() + ".png"
            print( "INF: saving to '%s'" % name ) 
            try:
                img.save( name, 'PNG' )
                bipInform()
            except AttributeError as err:
                print( "WRN: img.save: error: %s" % str(err))
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