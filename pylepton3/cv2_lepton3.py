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
    renderCross(im, pos, color, nSize)
    putTextCentered( im, strText, (pos[0],pos[1]-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2 )
    
    
def pix2Temp( v ):
    """
    Convert pixel data to temp in Celsius
    """
    #~ rT =  ( 0.0217 * (v - 8192) )
    
    # with TLinear mode enabled
    #~ rT = v / 100. - 273.15
    #~ rT = v / 100.
    
    #~ nOffsetK = 273.15
    #~ nCameraTemperatureScale100 = 30400+780 # + 390 pour le mode maison ou 

    #~ rT = ( 0.0217 * (v - 8192) ) + (nCameraTemperatureScale100/100.) - nOffsetK
    
    """
    mesure:
    mode maison / humain
    9447: 71.4
    9326: 64
    7882: 23.6
    7733:   15.4
    7200: -18
    7430: 8
    8530: 41.8
    8105: 27.7
    
    8237: 33.5 / 36.4
    """
    # regression estimation
    a = 0.0346090322
    b = -254.4290432
    rT = v*a+b
    return rT


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
    
    
    
    nZoom = 1
    nZoom = 4 ; render = cv2.resize(render, None, fx=nZoom, fy=nZoom )
    render = (render/256).astype('uint8')
    render = cv2.applyColorMap(render, cv2.COLORMAP_JET) # only for 8bits

    if 0:
        fn = misctools.getFilenameFromTime() + ".jpg"
        fn = "c:/tmpi7/" + fn
        retVal = cv2.imwrite(fn, render )
        assert(retVal)
        print("INF: output to '%s'" % fn )
        
        
    if 1:
        # print temperature on screen:
        a = frame
        h,w = a.shape[:2]
        #~ mint = int(a.min()) # use int to copy the variable instead of pointing in the array
        #~ maxt = int(a.max())
        idx_max = np.argmax(a)
        x_max, y_max = idx_max%w,idx_max//w
        idx_min = np.argmin(a)
        x_min, y_min = idx_min%w,idx_min//w
        t_min = int(a[y_min,x_min])
        t_max = int(a[y_max,x_max])
        x_center, y_center = w//2,h//2
        t_center = int(a[y_center,x_center])
        txt = "%5.1fC" % pix2Temp(t_min)
        putTextAndCross( render, (x_min*nZoom, y_min*nZoom), (255,0,0), txt )
        txt = "%s/%5.1fC" % (t_max, pix2Temp(t_max) )
        putTextAndCross( render, (x_max*nZoom, y_max*nZoom), (0,0,255), txt )
        txt = "%s/%5.1fC" % (t_center, pix2Temp(t_center) )
        putTextAndCross( render, (x_center*nZoom, y_center*nZoom), (200,200,200), txt, nSize=4 )


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