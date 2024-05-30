# -*- coding: cp1252 -*-

# sympathic stuffs for cv2

import cv2
#~ print("INF: cv2_tools: using CV2 version: %s" % cv2. __version__ )
import math
import numpy as np
import os

def drawHighligthedText(im,txt, position, fontface=cv2.FONT_HERSHEY_SIMPLEX, fontscale = 1,color = (255,255,255), thickness = 1, color_back=(127,127,127)):
    """
    render a text with a painted bounding box (highlighted)
    """
    
    textsize, baseline = cv2.getTextSize(txt, fontface, fontscale, thickness)
    #~ print("textsize: %s, baseline: %s" % (textsize, baseline) )
    # on ajoute des +1 et +2 pour aerer
    nExtraLeft = thickness//2+1
    nExtraBottom = thickness//2+2
    if "q" in txt or 'g' in txt or 'p' in txt:
        nExtraBottom = int(baseline*4/5)+2+1
    cv2.rectangle( im, (position[0]-nExtraLeft,position[1]+nExtraBottom), (position[0]+textsize[0],position[1]-textsize[1]-1-2),color_back,-1)
    cv2.putText(im,txt, position, fontface, fontscale,color,thickness)
    

def putTextCentered( image, text, bottomCenteredPosition, fontface=cv2.FONT_HERSHEY_SIMPLEX, fontscale = 1, color = (255,255,255), thickness = 1, bOutline=1):
    """
    Find a location in image to render a text from it's bottom centered position.
    handle out of image case.
    render it and return the location
    """
    tsx,tsy = cv2.getTextSize( text, fontface, fontscale, thickness )[0]
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
    
    if bOutline: cv2.putText( image, text, (xd,yd), fontface, fontscale, (0,0,0), thickness+1, cv2.LINE_AA ) # black outline        
    cv2.putText( image, text, (xd,yd), fontface, fontscale, color, thickness, cv2.LINE_AA )
        
    return xd,yd
    
def putTextRA( image, text, bottomRightPosition, fontface=cv2.FONT_HERSHEY_SIMPLEX, fontscale = 1, color = (255,255,255), thickness = 1, bOutline=1):
    """
    putTextRightAlign
    Find a location in image to render a text from it's bottom right position.
    Adjust to fit image (if too big)
    render it and return the location
    """
    tsx,tsy = cv2.getTextSize( text, fontface, fontscale, thickness )[0]
    #~ print(tsx,tsy)
    h,w = image.shape[:2]
    
    xd = bottomRightPosition[0]-(tsx)
    yd = bottomRightPosition[1]
    
    if xd < 0:
        xd = 0
    if xd+tsx > w:
        xd = w - tsx
        
    if yd-tsy < 0:
        yd = tsy
        
    if yd > h:
        yd = h
    
    if bOutline: cv2.putText( image, text, (xd,yd), fontface, fontscale, (0,0,0), thickness+1, cv2.LINE_AA ) # black outline        
    cv2.putText( image, text, (xd,yd), fontface, fontscale, color, thickness, cv2.LINE_AA )
        
    return xd,yd
    
def putTextBox( image, text, box, fontface=cv2.FONT_HERSHEY_SIMPLEX, color = (255,255,255), thickness = 1, bOutline = 1, bRenderBox = 0 ):
    """
    putTextBoxed
    Center a text in a box, adjust to fit size box (if too small or too big)
    render it and return the location and size
    - box: a xleft,ytop,xright,ybottom in image where to draw
    """
    fontscale = 10;
    wb = box[2]-box[0]
    hb = box[3]-box[1]
    while 1:
        (tsx,tsy),baseline = cv2.getTextSize( text, fontface, fontscale, thickness )
        print( "DBG: putTextBox: tsx: %s,tsy: %s, baseline: %s" % (tsx,tsy,baseline) )
        tsy += baseline
        if ( tsx < wb or tsx < 6 ) and ( tsy < hb or tsy < 5):
            break
        fontscale *= 0.8
        
    print( "DBG: putTextBox: fontscale: %s" % fontscale )
    if fontscale < 0.6 and thickness > 1:
        thickness = 1
        
    #~ if fontscale < 0.5 and thickness > 0.7:
        #~ thickness = 0.7 # thickness is an int!
        
    h,w = image.shape[:2]
    
    xd = box[0]+wb//2-tsx//2
    yd = box[1]+hb//2+tsy//2
        
    if bRenderBox:
        cv2.line( image, (box[0],box[1]), (box[2],box[1]), color, 1 )
        cv2.line( image, (box[0],box[3]), (box[2],box[3]), color, 1 )
        cv2.line( image, (box[0],box[1]), (box[0],box[3]), color, 1 )
        cv2.line( image, (box[2],box[1]), (box[2],box[3]), color, 1 )
    
    if bOutline: cv2.putText( image, text, (xd,yd-baseline+2), fontface, fontscale, (0,0,0), thickness+1, cv2.LINE_AA ) # black outline        
    cv2.putText( image, text, (xd,yd-baseline+2), fontface, fontscale, color, thickness, cv2.LINE_AA )
        
    return xd,yd
    
def saveImage_JpgWithSpecificSize( filename, img, nSizeMaxKo, nSizeMinKo = 0, nQualityStart = 80 ): 
    """
    return -1 if on error, or size in ko of saved file
    """
    print("DBG: saveImage_JpgWithSpecificSize: saving to '%s'" % filename)
    nQuality = nQualityStart
    while 1:
        print("DBG: saveImage_JpgWithSpecificSize: trying with quality: %s" % nQuality)
        bRet = cv2.imwrite(filename,img,[int(cv2.IMWRITE_JPEG_QUALITY), nQuality])
        if not bRet:
            print("ERR: can't write to file '%s" % filename )
            return -1
        nSize = os.path.getsize(filename) // 1024
        print("DBG: saveImage_JpgWithSpecificSize: nSize: %dkB" % nSize )
        if nSize > nSizeMaxKo:
            if nQuality <= 10:
                return nSize # don't want to do worse
            nQuality -= 5
        elif nSize < nSizeMinKo:
            nQuality += 2
        else:
            # it's ok
            return nSize
# saveImage_JpgWithSpecificSize - end

def drawRoundCorner(im, center, radius, color, nAngleStart=0, bDrawOuter=0):
    """
    draw a round corner (an half plain circle)
    - rAngleStart: which quarter? 0, 90, 180 or 270 (0 is the top left part, 90 is the next Counterclock Wise)
    - bDrawOuter: if set, instead of drawing the inside of the circle, draw the outside
    """
    for j in range(radius):
        for i in range(radius):
            if      (not bDrawOuter and math.sqrt(i*i+j*j) <= radius) \
                or (bDrawOuter and math.sqrt(i*i+j*j) >= radius) \
                :
                if nAngleStart == 0:
                    im[center[1]-j,center[0]-i] = color
                elif nAngleStart == 90:
                    im[center[1]-j,center[0]+i] = color
                elif nAngleStart == 180:
                    im[center[1]+j,center[0]+i] = color    
                else: # nAngleStart == 180:
                    im[center[1]+j,center[0]-i] = color    
                    
def hisEqualColor(img):
    """
    histogram equalization while maintaining (as much as possible) colors
    """
    ycrcb = cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(ycrcb)
    #~ print(len(channels))
    cv2.equalizeHist(channels[0],channels[0])
    cv2.merge(channels,ycrcb)
    cv2.cvtColor(ycrcb,cv2.COLOR_YCR_CB2BGR,img)
    return img
                    
def listCameras( bShowImages = True, bLiveFeed = False ):
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    - bShowImages: render one image for each found devices
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    xpos = 0
    ypos = 0
    ymax = 0
    listWorkingCameraObj = []
    while len(non_working_ports) < 6: # if there are more than 5 non working ports stop the testing. 
        camera = cv2.VideoCapture( dev_port, cv2.CAP_DSHOW ) # cv.CAP_DSHOW: to remove the warning
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." %dev_port)
        else:
            w = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if 1:
                if w == 1920 and h == 1080:
                    print("WRN: skipping read gopro pourri driver")
                    dev_port +=1
                    continue
            is_reading, img = camera.read()
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,w,h))
                working_ports.append(dev_port)
                if bLiveFeed: listWorkingCameraObj.append(camera)
                if bShowImages:
                    strWinName = "port %d" % dev_port
                    while img.shape[0]>500:
                        img = cv2.resize(img,(0,0),fx=0.5,fy=0.5)
                    cv2.imshow(strWinName,img)
                    #~ print("DBG: list_ports: move windows: %d, %d" % (xpos,ypos))
                    cv2.moveWindow(strWinName,xpos,ypos)
                    xpos += img.shape[1]+2
                    ymax = max(ymax,img.shape[0])
                    if xpos > 1300:
                        xpos = 0
                        ypos += ymax+24
                        ymax = 0
                    cv2.waitKey(100)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
                
        if not bLiveFeed: camera.release()
        
        dev_port +=1
        
    if bLiveFeed:
        print("INF: live feeding...")
        while 1:
            for i,cam in enumerate(listWorkingCameraObj):
                #~ print("DBG: retrieve image from numcamera: %d" % numcamera )
                numcam = working_ports[i]
                strWinName = "port %d" % numcam
                is_reading, img = cam.read()
                if is_reading:
                    img = hisEqulColor(img)
                    cv2.imshow(strWinName,img)
                else:
                    print("ERR: image not ready for camera port %d" % numcam)
            k = cv2.waitKey(100)
            if k == 27:
                break
        for cam in listWorkingCameraObj:
            cam.release()
            
        
    return available_ports,working_ports,non_working_ports
    
def computeImageDifference( im1, im2):
    import image_tools
    return image_tools.computeImageDifference(im1,im2)
    
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img
    
def autoCrop(im_param, bDebug=False ):
    import numpy
    dividerSize = 8
    im = cv2.resize(im_param,(0,0),fx=1/dividerSize,fy=1/dividerSize) # scale down (giving a simplified aspect)
    im = increase_brightness(im,40) # great when coming from scanner, when the background are often "not so white"
    h,w = im.shape[:2]
    print("DBG: autoCrop: work w: %s, h: %s " % (w,h) )
    if 0:
        corners = im[0,0],im[0,w-1],im[h-1,0],im[h-1,w-1]
        print("DBG: autoCrop: corners: %s" % str(corners))
        i = 1
        # find bottom interesting first line
        
        so = cv2.Sobel(im,cv2.CV_8U,1,0,ksize=5)
        soline = cv2.Sobel(im[h-i:h-i+1,],cv2.CV_64F,1,0,ksize=15)
        
        cv2.imshow("sobel",so)
        cv2.imshow("sobel_line",soline)
        cv2.waitKey(0)
        while 1:
            sobelx64f = cv2.Sobel(im[h-i:h-i+1,],cv2.CV_64F,1,0,ksize=5)
            maxdiff = np.max(sobelx64f)
            print("DBG: autoCrop: %d: %s" % (i,maxdiff))
            i += 1
            if i > h:
                break
    if 1:
        imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        imgray = cv2.blur(imgray,(31,31))
        ret,thresh = cv2.threshold(imgray,math.floor(numpy.average(imgray)*0.99),255,cv2.THRESH_BINARY_INV) # 0.99: essaye de garder moins de blanc autour, mais ca n'a pas fonctionné... (sur le cv d'elsa du moins)
        dilated=cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20)))
        contours,hierarchy = cv2.findContours(dilated,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        
        print("DBG: autoCrop: contours: %s" % str(contours) )
        new_contours=[]
        for c in contours:
            if cv2.contourArea(c) < h*w: # h*w: approx of image total size
                new_contours.append(c)
                
        print("DBG: autoCrop: new_contours: %s" % str(new_contours) )
                
        best_box=[-1,-1,-1,-1]
        for c in new_contours:
           x,y,w,h = cv2.boundingRect(c)
           if best_box[0] < 0:
               best_box=[x,y,x+w,y+h]
           else:
               if x<best_box[0]:
                   best_box[0]=x
               if y<best_box[1]:
                   best_box[1]=y
               if x+w>best_box[2]:
                   best_box[2]=x+w
               if y+h>best_box[3]:
                   best_box[3]=y+h
                   
        print("DBG: autoCrop: best_box: %s (dividerSize:%s)" % (str(best_box),dividerSize) )
        if bDebug:
            imDebug = im[:]
            cv2.rectangle(imDebug,(best_box[0],best_box[1]),(best_box[2],best_box[3]),(255,0,0),4)
            cv2.imshow("best_box",imDebug)
            cv2.waitKey(0)
            
    k = dividerSize
    return im_param[best_box[1]*k:best_box[3]*k+k,best_box[0]*k:best_box[2]*k+k] # +k//2 or +k (for rounding error)
        
        
    
def autoTest():
    im = np.zeros((600,800,3),dtype=np.uint8)
    drawHighligthedText( im, "drawHighligthedText", (50,50))
    drawHighligthedText( im, "aa", (50,100))
    drawHighligthedText( im, "MM", (50,150))
    drawHighligthedText( im, "MM", (50,400),fontscale=4, thickness=12)
    drawHighligthedText( im, "tglq", (300,400),fontscale=4, thickness=12)
    drawHighligthedText( im, "tglq", (300,100),fontscale=1, thickness=20)
    drawHighligthedText( im, "tglq", (300,250),fontscale=4, thickness=1)
    drawHighligthedText( im, "M", (400,100),fontscale=4, thickness=1)
    drawHighligthedText( im, "Le petit chaperon rouge!", (20,500),fontscale=1, thickness=1)
    drawHighligthedText( im, "Toto est cool.", (400,550),fontscale=1, thickness=1)
    putTextCentered( im, "Toto de centre.", (400,580),fontscale=1, thickness=1)
    putTextCentered( im, "Toto de gauche.", (00,580),fontscale=1, thickness=1)
    putTextCentered( im, "Toto de droite.", (1000,580),fontscale=1, thickness=1)
    

    centerCorner = (150,150)
    drawRoundCorner( im, centerCorner,30, (0,255,0),0)
    drawRoundCorner( im, centerCorner,30, (0,255,0),90)
    drawRoundCorner( im, centerCorner,30, (0,255,0),180)
    drawRoundCorner( im, centerCorner,30, (0,255,0),270)
    
    centerCorner = (220,150)
    drawRoundCorner( im, centerCorner,30, (0,255,0),0,bDrawOuter=1)
    drawRoundCorner( im, centerCorner,30, (0,255,0),90,bDrawOuter=1)
    drawRoundCorner( im, centerCorner,30, (0,255,0),180,bDrawOuter=1)
    drawRoundCorner( im, centerCorner,30, (0,255,0),270,bDrawOuter=1)
    
    cv2.imshow("cv2_tools",im)
    key=cv2.waitKey(1) # time for image to refresh even if continuously pressing a key
    key=cv2.waitKey(0)


if __name__ == "__main__":
    pass
    #~ autoTest()
    #~ listCameras(bLiveFeed=1)