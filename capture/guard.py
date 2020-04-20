import sys
sys.path.append("../alex_pytools/")
import misctools
import webcam

import cv2 # made with cv 3.2.0-dev
import numpy as np
import os
import select
import time
import sys
import v4l2capture  # can be found here : https://github.com/gebart/python-v4l2capture/blob/master/capture_picture.py


def guard(nNumCamera):
    if 1:
        from signal import signal, SIGPIPE, SIG_DFL
        signal(SIGPIPE,SIG_DFL)     

            
    webcam.list_video_device()
    wcam = webcam.WebCam(strDeviceName = "/dev/video%d" % nNumCamera )
    
    #~ print("resolution: " + str(webcam.get_webcam_available_resolution(wcam)) ) # not the good object
    
    im = wcam.getImageRetry()

    strWindowName = "camera %d" % nNumCamera
    
    nCptFrame = 0
    begin = time.time()
    
    aLastTimeAndName = []

    strPrevName = ""
    imPrev = im[:]
    im[:]=(255,255,255) # first one => refresh at first!
    timeLastOutputtedHtml = time.time()
    strCurrentImageInHtml = ""
    strPrevImageInHtml = ""
    bPreviousWasDifferent = False # you need to update once more, as the image in the html is always the previews one (for refresh blinking avoidance)
    # center of image
    xc1 = int(im.shape[1]*1/4)
    xc2 = int(im.shape[1]*3/4)
    yc1 = int(im.shape[0]*1/4)
    yc2 = int(im.shape[0]*3/4)
    nCptMoveSeq = 0 # nbr of continuous moving (and writed images)
    while( 1 ):
        im = wcam.getImage(bVerbose=False)
        if im is None:
            print("DBG: wait for camera ready...")
            time.sleep(3.)
        else:
            if 0:
                cv2.imshow(strWindowName,im)
                key = cv2.waitKey(1)
                #~ print key
                if key == 27: break
            nCptFrame += 1
            if nCptFrame > 100:
                duration = time.time() - begin
                print( "fps: %5.3f" % (float(nCptFrame)/duration) )
                nCptFrame = 0
                begin = time.time()
            if 1:
                rDiff = misctools.mse(im,imPrev, bDenoise=True)
                rDiffCenter = misctools.mse(im[yc1:yc2,xc1:xc2],imPrev[yc1:yc2,xc1:xc2], bDenoise=True)
                rAvgColor = im.mean()
                imPrev = im
                print("DBG: rDiff: %5.2f, rDiffCenter: %5.2f, color: %5.2f" % (rDiff,rDiffCenter, rAvgColor) )
                livedataFilename = "/var/www/html/view/data/liveData"
                #~ livedataFilename = "/var/www/html/data/notify.asp"
                bRewriteHtml = False
                
                # 4 types de lumiere, regit la couleur: 
                # - nuit avec juste tele: 4
                # - juste sam: 14
                # - sombre avec juste salon: 35
                # - en journee: ??
                
                # avec bDenoise=True
                # rDiff: 70/ 60/ 130/ 700
                # rDiffCenter: 70/ 105/ 130/ 700
                
                # 180deg (nuit / jour)
                bMovement = (rAvgColor < 40 and (rDiff > 250 or rDiffCenter > 150) ) \
                    or  (rAvgColor > 40 and (rDiff > 300 or rDiffCenter > 200) )
                    
                # PsEye (nuit / jour)   (salon eclaire: avg98) 
                bMovement = (rAvgColor < 40 and (rDiff > 250 or rDiffCenter > 150) ) \
                    or  (rAvgColor > 90 and (rDiff > 350 or rDiffCenter > 300) )                
                if  bMovement:
                    if bPreviousWasDifferent: nCptMoveSeq += 1
                    else: nCptMoveSeq = 0
                    bPreviousWasDifferent = True
                    print("DBG: writing image... (nCptMoveSeq: %d)" % nCptMoveSeq )
                    # write image and update liveData for html server
                    # write image and update liveData for html server
                    strImageName = "%s.jpg" % misctools.getFilenameFromTime() #time.time()
                    strDate = misctools.getDateStamp()
                    strTotalImageName = "/var/www/html/view/data/" + strDate
                    misctools.makeDirsQuiet(strTotalImageName)
                    strTotalImageName += os.sep + strImageName
                    cv2.imwrite( strTotalImageName, im,[int(cv2.IMWRITE_JPEG_QUALITY), 80] )
                    strCurrentTime = misctools.getTimeStamp()
                    aLastTimeAndName.append([strCurrentTime, strDate + os.sep + strImageName])
                    aLastTimeAndName = aLastTimeAndName[-9:] # nbr image per pages
                    
                    bRewriteHtml = True
                    if nCptMoveSeq > 4:
                        time.sleep(0.5) # don't refresh too often !
                    else:
                        time.sleep(0.1)
                else:
                    bPreviousWasDifferent = False
                    time.sleep(0.2)
                    if time.time() - timeLastOutputtedHtml > 120.:
                        bRewriteHtml = True
                    
                if bRewriteHtml or bPreviousWasDifferent:
                    print("DBG: generating webpage...")
                    #~ generateHtml(aLastName, bReverse)
                    file = open(livedataFilename, "wt")
                    #file.write("<IMG SRC=./data/%s></IMG>" % strImageName )
                    file.write("<table><tr>")
                    nCpt = 0
                    print("aLastTimeAndName:%s"%aLastTimeAndName)
                    for s,f in aLastTimeAndName:
                        file.write("<td><IMG SRC=./data/%s width=640></IMG><br><center>%s</td>" % (f, s) )
                        if (nCpt % 3) == 2:
                            file.write("</tr><tr>")
                        nCpt += 1
                    file.write("</tr></table><font size=-10>last computed: %s</font>" % misctools.getTimeStamp() )
                    file.write("<!--end-->" )
                    file.close()
                    timeLastOutputtedHtml = time.time()

# guard - end

if __name__ == "__main__":
    nNumCamera = 0
    if len(sys.argv) > 1:
        if sys.argv[1][0] == '-':
            print( "syntax: %s <camera_num (default: %s)>" % (sys.argv[0] ),nNumCamera)
            exit(-1)
        else:
            nNumCamera = int(sys.argv[1])
    guard( nNumCamera )