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
    #~ print(tsx,tsy)
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
    #~ print("DBG: renderCross: x: %d, y: %d" % (x,y))
    if 1:
        # outliner
        c = (0,0,0)
        for i in range(nSize):
            im[y+i+1,x+1] = c
            im[y-i+1,x+1] = c
            im[y+1,x+i+1] = c
            im[y+1,x-i+1] = c
        
    im[y,x] = color
    for i in range(nSize):
        im[y+i,x+0] = color
        im[y-i,x+0] = color
        im[y+0,x+i] = color
        im[y+0,x-i] = color

def putTextAndCross( im, pos, color, strText, nSize = 2 ):
    putTextCentered( im, strText, (pos[0],pos[1]-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2 )
    renderCross(im, pos, color, nSize)
    
def tempFtoC(t):
    return (t-32)/1.8
    
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
    
    # from various website:
    # fpa_temp_kelvin*65.00/63535.00
    #  0.0465*SensorValue-349.44 
    # git lepton3:
    # ambientTemperature = 25.0;
	# slope = 0.0217;
	#T = slope*raw+ambientTemperature-177.77
    
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
    
    ramping computed from google spreadsheet "lepton3 - temperature ramping"
    """
    # regression estimation
    a = 0.0346090322
    b = -254.4290432
    rT = v*a+b
    
    return rT
    
    
def pix2TempAlt( v, nCameraTemperatureScale100 = 32500 ):
    nOffsetK = 273.15
    rVal = ( 0.0217 * (v - 8192) ) + (nCameraTemperatureScale100/100.) - nOffsetK
    return rVal

    
def pix2TempAlt2( v, nCameraTemperatureScale1000 = 32500 ):
    nCameraTemperatureScale1000 = 25000
    rVal = ( 0.0217 * v ) + (nCameraTemperatureScale1000/1000.) -177.77
    rVal = tempFtoC(rVal)
    return rVal
    
def visualiseData( frame ):
    """
    create an image visualisable from an image in uint16
    return the new created image
    """
    render = frame.copy()
    
    cv2.normalize(render, render, 0, 65535, cv2.NORM_MINMAX) # extend contrast
    #~ np.right_shift(render, 8, render) # fit data into 8 bits
    
    #~ cv2.normalize(render, render, 0, 255, cv2.NORM_MINMAX) # extend contrast
    
    #~ render = cv2.equalizeHist(render) #work only on 8bits
    
    
    
    nZoom = 1
    nZoom = 4 ; render = cv2.resize(render, None, fx=nZoom, fy=nZoom )
    render = (render/256).astype('uint8')
    render = cv2.applyColorMap(render, cv2.COLORMAP_JET) # only for 8bits
    
    return render
    
    
def renderTemperatureOnImage(render, frame,nCameraInternalTemp):
    """
    draw information into the render image buffer about data contains in frame
    """
    nZoom=render.shape[1]//frame.shape[1]
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
    
    txt = "%s/%5.1fC/%5.1fC/%5.1fC" % (t_min, pix2Temp(t_min), pix2TempAlt(t_min,nCameraInternalTemp), pix2TempAlt2(t_min,nCameraInternalTemp) )
    putTextAndCross( render, (x_min*nZoom, y_min*nZoom), (255,0,0), txt )
    txt = "%s/%5.1fC/%5.1fC/%5.1fC" % (t_max, pix2Temp(t_max), pix2TempAlt(t_max,nCameraInternalTemp), pix2TempAlt2(t_max,nCameraInternalTemp) )
    putTextAndCross( render, (x_max*nZoom, y_max*nZoom), (0,0,255), txt )
    txt = "%s/%5.1fC/%5.1fC/%5.1fC" % (t_center, pix2Temp(t_center), pix2TempAlt(t_center,nCameraInternalTemp), pix2TempAlt2(t_center,nCameraInternalTemp) )
    putTextAndCross( render, (x_center*nZoom, y_center*nZoom), (200,200,200), txt, nSize=4 )

def acquire():

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
    aPrevExtras = None
    
    # signification extra datas (mainly the changing one)
    dictExtraName = {
                # 0: 0x50 puis oxA apres un ffc
                 1: "time in millisec (low part)",
                 2: "time in millisec (hi part)",
                 # 3: 0X818 , ffc will occurs in 6 frames,  puis 2 puis 0X820
                 # 3-7: lie au ffc
               20: "frame number",                              # at 27 fps (hw return 1 one over 3)
               #~ 22:  "",
               #~ 23:  "",
               24: "camera temperature",
               #~ 25: "",
               29: "camera temperature avg",
             #~ 124: "",
    }
    
    """
    apres un ffc:
0: : 80  (0x50)
1: time in millisec (low part): 20480  (0x5000)
2: time in millisec (hi part): 31874  (0x7c82)
3: : 2  (0x2)
4: : 5736  (0x1668)
5: : 1755  (0x6db)
6: : 28040  (0x6d88)
7: : 193  (0xc1)
20: frame number            : 2669  (0xa6d)
23: : 7348  (0x1cb4)
24: camera temperature      : 31295  (0x7a3f)
25: : 8066  (0x1f82)
nCameraInternalTemp: 31039

puis

0: : 10  (0xa)
1: time in millisec (low part): 44298  (0xad0a)
2: time in millisec (hi part): 4  (0x4)
3: : 2080  (0x820)
4: : 0  (0x0)
5: : 0  (0x0)
6: : 0  (0x0)
7: : 0  (0x0)
20: frame number            : 2685  (0xa7d)
22: : 8179  (0x1ff3)
23: : 7334  (0x1ca6)
24: camera temperature      : 31305  (0x7a49)
25: : 8067  (0x1f83)
29: : 31301  (0x7a45)
30: : 43386  (0xa97a)
31: : 4  (0x4)
124: : 15047  (0x3ac7)
nCameraInternalTemp: 31301
"""
    
    timeLastFFC = time.time()
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        #~ print("ret: %s" % ret)
        #~ print("frame: %d 0x%X" %( frame[0,0],frame[0,0]) )
        #~ frame.tofile("/tmp/im.raw")
        if ret == False:
            time.sleep(0.3)
            continue

        if bFirstTime:
            bFirstTime = 0
            print("image properties: %s, type: %s" % (str(frame.shape), frame.dtype) )
            
        # Our operations on the frame come here
        #~ gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #~ frame = np.rot90(frame)
        
        #analyse extra datas
        aExtras = frame[-2:].copy()
        aExtras = aExtras.reshape((320))
        #~ print("aExtras: %s" % aExtras )
        
        if 1:
            print("-"*40)
            # render variations on extras
            for i in range(len(aExtras)): 
                if aExtras[i] > 0 or 1: 
                    if aPrevExtras is None or aExtras[i] != aPrevExtras[i]:
                        if i not in dictExtraName.keys():
                            label = ""
                        else:
                            label = "%-24s" % dictExtraName[i]
                        print("%3d: %s: %d  (0x%x)" % (i,label,aExtras[i],aExtras[i]) )
            aPrevExtras = aExtras[:]
        
        #~ nCameraInternalTemp = aExtras[24]
        nCameraInternalTemp = aExtras[29]
        nFFCFlag = aExtras[3]
        if nFFCFlag == 0X818:
            print("***FFC***: duration:%5.2fs" % (time.time()-timeLastFFC) ) # 286sec # 300sec # 300
            misctools.beep(600,100)
            timeLastFFC = time.time()
        
        print("nCameraInternalTemp: %s" % nCameraInternalTemp )
        
        # remove border
        frame = frame[:-2:]
        
        render = visualiseData(frame)


        if 0:
            fn = misctools.getFilenameFromTime() + ".jpg"
            fn = "c:/tmpi7/" + fn
            retVal = cv2.imwrite(fn, render )
            assert(retVal)
            print("INF: output to '%s'" % fn )
            
            
        if 1:
            renderTemperatureOnImage(render,frame,nCameraInternalTemp)


        # Display the resulting frame
        
        # add a blincking dot
        if not bBlinkIsLighten:
            cv2.circle( render, (40,20), 10,(255,0,0), -1 )
        bBlinkIsLighten = not bBlinkIsLighten
        
        cv2.imshow('render',render)
        #~ cv2.imshow('gray',gray)
        key = ( cv2.waitKey(1) & 0xFF )
        if key == ord('q') or key == 27:
            return False
            
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
# acquire - end

def analysePathFromRaw( strPath, w = 160, h=120 ):
    
    aPrevExtras = None

    for f in sorted( os.listdir(strPath) ):
        if ".raw" in f.lower():
            print("INF: loading %s" % f )
            tf = strPath + f
            im = np.fromfile(tf, dtype=np.uint16, count = w*(h+10)) # +10 for read extra parameters
            #~ im = im.byteswap() # little to big => no changes
            print("INF: loaded im shape: %s, type: %s" % (str(im.shape),im.dtype) )
            
            nExtraDatas = im.shape[0]-(w*h)
            aExtras = im[-nExtraDatas:]
            im = im[:-nExtraDatas]
            
            if 1:
                # render variations
                for i in range(len(aExtras)): 
                    if aExtras[i] > 0: 
                        if aPrevExtras is None or aExtras[i] != aPrevExtras[i]:
                            print("%d: %d 0x%x" % (i,aExtras[i],aExtras[i]) )
                aPrevExtras = aExtras[:]

            nCameraInternalTemp = aExtras[29]
            print("nCameraInternalTemp: %d" % nCameraInternalTemp )
            nCameraInternalTemp = 30760 # exactly [263]*10
            # on my example it sould be 31150, nearest are [29], then [24]
            # or 30820 then nearest are 29 82 or 24
            # another moment, good number was 30520, nearest: 82: 30000 puis 29: 31280
            #30760: exactly [263]*10
            # 
            # flat-field correction (FFC): seems not currently hiding the lens !!!
            #
        
            #~ print("DBG: im0: %d 0x%X" %( im[0],im[0]) )
            im = np.reshape(im,(h,w))
            #~ print("INF: loaded im shape: %s, type: %s" % (str(im.shape),im.dtype) )
            #~ print("DBG: im0: %d 0x%X" % (im[0,0],im[0,0]) )
            
            
            render = visualiseData(im)
            renderTemperatureOnImage(render,im,nCameraInternalTemp)
            cv2.imshow('render',render)
            key = ( cv2.waitKey(0) & 0xFF )
            if key == ord('q') or key == 27:
                return False

# analysePathFromRaw - end

if __name__ == "__main__":
    acquire()
    #~ analysePathFromRaw("c:/tmpi12/")
 
    # ma main: 36/36.5 #
    # radiateur du salon cote jardin: 40


"""
extra lines in images first line:
[[   10 41830     5  2096     0 24848 33288 59554  2178  1034  1280  9216   # a part 2ieme et 3ieme rien ne change. 2: des secondes et 3 inc a chaque overflow de 2
      0   307     3   307     3  1401     0     0  3226     0  8131  5948 # 9ieme semble etre counter de frame 11 et 12 varie autour de 8188 et 5718
  30952  7859     0     0     0 30828 45662     4     0     0     0     0 # 1er pourrait etre LA valeur
    159   119 19200   512     1   128    64     0     0     0     0     1
    128   100     0     0     0     0     0     0    30     0     1     1
    158   118     7    21     7   420    30    15    33     9     0     0
      7     0     3     0     0     0     0     0  8192  8192 30000  2437
      6 51744    21  1000     0 24928     2  2437     6 51744    21  1000
      0 24928     2     0     0     0     0     0     0     0     0     0
      0     0     0     0     0     0     0     0     0     0     0     0
      0     0     0     0 14446 33842 15433 14347 43008     0     0     0
      0     0     0     0     0     0     0     0     0     0     0     0
      0     0     0     0     0     0     0     0     0     0     0     0
      0     0     0     0]]
      """