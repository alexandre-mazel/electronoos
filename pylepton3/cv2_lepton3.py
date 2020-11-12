import numpy as np
import cv2
import os
import sys
import time

import threading

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

def putTextCentered( image, text, bottomCenteredPosition, fontFace, fontScale, color, thickness ):
    """
    Find a location in image to render a text from it's bottom centered position.
    handle out of image case.
    render it and return the location
    """
    tsx,tsy = cv2.getTextSize( text, fontFace, fontScale, thickness )[0]
    print(tsx,tsy)
    h,w = image.shape[:2]
    
    xd = bottomCenteredPosition[0]-(tsx//2)
    yd = bottomCenteredPosition[1]
    
    if xd < 0:
        xd = 0
    if xd+tsx > w:
        xd = w - tsx
        
    if yd-tsy < 0:
        yd = tsy
        
    if yd > h:
        yd = h
    
    cv2.putText( image, text, (xd,yd), fontFace, fontScale, (0,0,0), thickness+1 ) # black outline        
    cv2.putText( image, text, (xd,yd), fontFace, fontScale, color, thickness )
        
    return xd,yd
    
def renderCross(im, pos, color, nSize = 2 ):
    x,y=pos
    im[y,x] = color
    for i in range(nSize):
        im[y+i,x+0] = color
        im[y-i,x+0] = color
        im[y+0,x+i] = color
        im[y+0,x-i] = color
        
def putTextAndCross( im, pos, color, strText, nSize = 2 ):
    renderCross(im, pos, color, rTemp, nSize)
    putTextCentered( im, strText, (pos[0],pos[1]-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2 )


cap = cv2.VideoCapture(2) #or 0 + cv2.CAP_DSHOW
cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','1','6',' '))
cap.set(cv2.CAP_PROP_CONVERT_RGB, False)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

nCptFrame = 0
timeBegin = time.time()
bFirstTime = 1
bBlinkIsLighten = False
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    #~ print("ret: %s" % ret)
    if ret == False:
        time.sleep(0.3)
        continue

    if bFirstTime:
        bFirstTime = 0
        print("image properties: %s, type: %s" % (str(frame.shape), frame.dtype) )
        
    # Our operations on the frame come here
    #~ gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #~ frame = np.rot90(frame)
    
    # remove border
    frame = frame[:-2,:]
    
    render = frame.copy()
    
    cv2.normalize(render, render, 0, 65535, cv2.NORM_MINMAX) # extend contrast
    #~ np.right_shift(render, 8, render) # fit data into 8 bits
    
    #~ cv2.normalize(render, render, 0, 255, cv2.NORM_MINMAX) # extend contrast
    
    #~ render = cv2.equalizeHist(render) #work only on 8bits
    
    #~ render = cv2.applyColorMap(render, cv2.COLORMAP_JET) # only for 8bits
    
    render = cv2.resize(render, None, fx=4, fy=4 )

    if 0:
        fn = misctools.getFilenameFromTime() + ".jpg"
        fn = "c:/tmpi7/" + fn
        retVal = cv2.imwrite(fn, render )
        assert(retVal)
        print("INF: output to '%s'" % fn )
        
        
    if 0:
        # print temperature on screen:
        a = frame
        h,w,n = a.shape
        #~ mint = int(a.min()) # use int to copy the variable instead of pointing in the array
        #~ maxt = int(a.max())
        idx_max = np.argmax(a)
        x_max, y_max = idx_max%w,idx_max/w
        idx_min = np.argmin(a)
        x_min, y_min = idx_min%w,idx_min/w
        mint = int(a[y_min,x_min])
        maxt = int(a[y_max,x_max])
        centert = int(a[h/2,w/2])
        txt = str(a[y_min,x_min])
        putTextAndCross( a, (x_min, y_min), (255,0,0), txt )


    # Display the resulting frame
    if not bBlinkIsLighten:
        cv2.circle( render, (40,20), 10,(255,0,0), -1 )
    bBlinkIsLighten = not bBlinkIsLighten
    
    cv2.imshow('render',render)
    #~ cv2.imshow('gray',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    nCptFrame += 1
    if nCptFrame > 10:
        t = time.time() - timeBegin
        print("fps: %5.2f" % (nCptFrame / t) )
        nCptFrame = 0
        timeBegin = time.time()
        
        
    # D415: 60fps up to 1280x720 RGB
    # Fish Eye: 15 fps at 640x480
    time.sleep(0.3)
    


        


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()