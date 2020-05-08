# pip install pillow
from PIL import ImageGrab

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools


def continuousSave():
    print("INF: continuousSaveOfClipbBoardImage...")
    img_prev = None
    while 1:
        img = ImageGrab.grabclipboard()
        # or ImageGrab.grab() to grab the whole screen!
        if img != img_prev:
            img_prev = img
            name = "/tmp/" + misctools.getFilenameFromTime() + ".png"
            print( "INF: saving to '%s'" % name ) 
            img.save( name, 'PNG' )
# continuousSave - end


continuousSave()