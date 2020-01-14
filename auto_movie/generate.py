
import cv2
import numpy as np
import os
import time

#~ import abcdk.image # for getExifInfo, need PIL

def generate(strPath):
    wrender=320
    hrender=320
    s = np.zeros((hrender,wrender,3), dtype=np.int8)
    listImg = sorted(os.listdir(strPath))
    nCpt = 0
    for f in listImg[3:]:
        print("t:%5.2f, f:%s" % (time.time(),f ) )
        filename = strPath+f
        im = cv2.imread(filename)
        #~ print abcdk.image.getExifInfo( filename, ["Model", "DateTime"] );
        h,w,nplane=im.shape
        xlo,xro = 1000,2000
        yto,ybo = 800,800+( (xro-xlo)*h/w )
        nSpeedX = 0
        nSpeedY = 0
        rZoomX = 0.4
        rZoomY = 0.4
        for inc in range(200):
            i = inc
            j = inc
            xl= int(xlo+rZoomX*inc)
            xr = int(xro-rZoomX*inc)
            yt = int(yto+rZoomY*inc)
            yb = int(ybo-rZoomY*inc)
            s = im[yt+j*nSpeedY:yb+j*nSpeedY,xl+i*nSpeedX:xr+i*nSpeedX]
            s = cv2.resize(s,(wrender,hrender))
            cv2.imshow("f",s)
            key = cv2.waitKey(4) # ~25fps
            if key == 27:
                return
        nCpt += 1
        if nCpt > 2:
            break
    
    
generate("D:/temp_photo_pour_auto_montage/")