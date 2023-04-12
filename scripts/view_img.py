"""
Quick way to view an image

syntax: scriptname imagename [analyse]
- imagename: a name or a folder (finish with '/'), try to load folder
- analyse: analyse image (faces...)
"""

import cv2
import sys
import numpy as np
import time

#~ def _getBasePath( self ):
        #~ strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print( "DBG: loadModels: strLocalPath: %s" % strLocalPath )
        #~ if strLocalPath == "":
            #~ strLocalPath = "."
        #~ return strLocalPath


def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum( ((imageA.astype("int16") - imageB.astype("int16")) ** 2) ) # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return abs(err)
    
def getScreenWidth():
    import ctypes
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    print("screensize: %s" % str(screensize))
    return screensize[0]

def viewImg( strFilename, bAnalyse = False, bAnalyseAlt = False ):
    """
    Draw an image, the fastest possible, then launch some interactivity if asked...
    (good for remote ssh, xming or ...)
    """
    original = cv2.imread( strFilename )
    bNoImageSpecified = False
    if not original is None:
        while original.shape[0]>1080:
            original = cv2.resize( original, (original.shape[1]//2,original.shape[0]//2) )
        im = original.copy()
        cv2.namedWindow(strFilename,cv2.WINDOW_NORMAL)
        cv2.moveWindow( strFilename, 10, 50 )        
        cv2.imshow( strFilename, im )
        bMustRedraw = False
    else:
        bNoImageSpecified = True
        bMustRedraw = True
    
    idx = -1
    strFolder = ""
    listFiles = []
    bAutoZoom = 1
    rZoomFactor = 1.
    bFilenameIsShownInWindowsTitle = True
    bFilenameIsShownInWindowsTitle = False
    
    # do we extract interesting info like facereco num from filename ?
    bOutputOnScreenInfoFromFilename = True
    bOutputOnScreenInfoFromFilename = False

    fr = None
    maskDetector = None
    
    bInRenamming = False
    strRename = ""
    strPrevRename = ""
    imPrev = None
    strPrevIndexEnd = None
    
    astrListFocus = ["103"]
    
    
    while( True ):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
                
        #~ if key != 255: print(key)
        
        
        #~ if key == 20:
            #~ continue # after page up, we got a 20 ?!? (but stop the key repeat)
        
        if bInRenamming:
            if key != 13:
                if key > 30 and key < 128:
                    strRename += chr(key)
                    print("INF: renaming, current string: '%s'" % (strRename) )
                elif key == 8: # delete
                    strRename = strRename[:-1]
                    strPrevRename = "" # if you start to delete, then you perhaps hit a key by mistake
            else:
                bInRenamming = False
                if strRename == "":
                    strRename = strPrevRename
                if strRename != "":
                    print("INF: add '%s' to filename" % strRename )
                    import shutil
                    if 1:
                        # add postfix
                        strCurrentFilenameAbs = strFolder + os.sep + listFiles[idx]
                        newName = strCurrentFilenameAbs.replace('.', "__" + strRename + '.' )
                        print("INF: '%s' => '%s'" % (strCurrentFilenameAbs,newName) )
                        shutil.move(strCurrentFilenameAbs,newName)
                        if fr: facerecognition_dlib.storedFeatures.informFileRenamed( strCurrentFilenameAbs, newName )
                        listFiles[idx] = listFiles[idx].replace('.', "__" + strRename + '.' )
                    else:
                        # add prefix
                        strCurrentFilenameAbs = strFolder + os.sep + listFiles[idx]
                        newName = strFolder + os.sep + strRename + "__" + listFiles[idx]
                        print("INF: '%s' => '%s'" % (strCurrentFilenameAbs,newName) )
                        shutil.move(strCurrentFilenameAbs,newName)
                        if fr: facerecognition_dlib.storedFeatures.informFileRenamed( strCurrentFilenameAbs, newName )
                        listFiles[idx] = strRename + "__" + listFiles[idx]
                        
                    strPrevRename = strRename
                    strPrevIndexEnd = strRename
                    strRename = ""
                #continue # need to redraw!
                key = 255 # prevent next test key == 13
                bMustRedraw = True
            
            
        
        # navigate into files
        bImageChanged = False
        nChangeImageOffset = 0
        if key == 85 or ( ( key == 56 or key == ord('b') ) and not bInRenamming): # page up or keypad8
            nChangeImageOffset = -1
        elif key == 86 or ( ( key == 50 or key == ord('n') ) and not bInRenamming): # page up or keypad2
            nChangeImageOffset = +1
        elif key == 36: # $
            nChangeImageOffset = -10
        elif key == 42: # *
            nChangeImageOffset = +10            
        elif key == 61: # = # = because the circonflexe generate an assert in the
            nChangeImageOffset = -100
        elif key == 217: # u with accent
            nChangeImageOffset = +100
        elif (key == ord('l') and not bInRenamming):
            # goto last
            nChangeImageOffset = -999999999 # so it's less than 0 and it cycle to last
        elif (key == ord('f') and not bInRenamming):
            # goto first
            nChangeImageOffset = 999999999 # so it's more  than 0 and it cycle to first

            
        elif key == ord('s'):
            # render only file matching a string defined somewhere
            print("jump to next file matching: %s" % str(astrListFocus) )
            while(idx+1<len(listFiles)):
                idx += 1
                strIndexEnd = listFiles[idx].split("_")[-1].split('.')[0]
                if strIndexEnd in astrListFocus:
                    break                    
        elif key == ord('z'):
            # same but reverse
            print("jump to prev file matching: %s" % str(astrListFocus) )
            while(idx>0):
                idx -= 1
                strIndexEnd = listFiles[idx].split("_")[-1].split('.')[0]
                if strIndexEnd in astrListFocus:
                    break                    
            
        elif key == 80: # origin
            idx = 0
            bImageChanged = True
        elif key == 87: # end
            idx = len(listFiles)-1
            bImageChanged = True
        elif key == ord('p'):
            print('"%s"' % listFiles[idx] )
            
        if key == ord('a'):
            # toggle analyse face
            bAnalyse = not bAnalyse 

        if key == ord('m'):
            # toggle alternate face analyse
            bAnalyseAlt = not bAnalyseAlt
            
        if nChangeImageOffset != 0:
            bImageChanged = True
            
        if bImageChanged:
            bInRenamming = False
            strRename = ""
            bMustRedraw = True

        if key == 171 or key == 43: # '+' on num keyboard
            rZoomFactor *=2
            bMustRedraw = True
            print("zoom+")
        elif key == 173 or key == 45: # '-' on num keyboard
            rZoomFactor /=2.
            bMustRedraw = True
            print("zoom-")
            
        if key == 13:
            bInRenamming = True
            print( "INF: enter renamming, type new name then press enter to finish..." )
            
        if key != 255 or bMustRedraw:
            
            bMustRedraw = False
            
            if idx == -1:                
                # charge folder content
                import os
                strFolder = os.sep.join(strFilename.split(os.sep)[:-1])
                listFiles = sorted(os.listdir( strFolder ))
                # clean non images file
                i = 0
                while(i < len(listFiles) ):
                    if not( ".png" in listFiles[i].lower() or ".jpg" in listFiles[i].lower()):
                        del listFiles[i]
                    else:
                        i += 1
                    
                if bNoImageSpecified:
                    idx = 0
                else:
                    idx = listFiles.index(strFilename[len(strFolder)+1:])
                            
            idx += nChangeImageOffset
            if idx < 0:
                idx = len(listFiles) -1
            elif idx >= len(listFiles):
                idx = 0
            strFileToShow = strFolder + os.sep + listFiles[idx]
            print("INF: showing: %s (%d/%d)" % (strFileToShow,idx,len(listFiles)) )
            original = cv2.imread( strFileToShow )
            while original.shape[0]>1080:
                original = cv2.resize( original, (original.shape[1]//2,original.shape[0]//2) )
            im = original.copy()
            xPosIndex = 20
            yPosIndex = 100
            if im is None:
                import numpy as np
                im = np.zeros((300,300,3), np.uint8 )
                print("WRN: can't read image '%s'" % strFileToShow )
            else:
                if not imPrev is None and imPrev.shape == im.shape:
                    rDiff = mse( im, imPrev )
                    print( "rDiff: %5.2f" % rDiff )
                imPrev = im
                if bAnalyse:
                    if not fr:
                        import sys
                        import os
                        sys.path.append(os.path.expanduser("~/dev/git/face_tools/") )
                        import facerecognition_dlib
                        fr = facerecognition_dlib.FaceRecogniser()
                        fr.loadModels()        
                        fr.setVerbose(1)                          
                    rConf, feat, facepos, facelandmark = fr.extractFeaturesFromFile( strFileToShow )
                    if (idx % 100) == 0:
                        facerecognition_dlib.storedFeatures.save()

                    faceLandmarks = fr.shape_predictor(original, facerecognition_dlib.arrayToDlibRect(facepos))
                    
                    if 1:
                        # advanced rendering
                        fr._computeFaceQuality(original,faceLandmarks) # to print intermediate information                        
                        im = fr._renderFaceInfo( im, faceLandmarks )
                    else:
                        # just a rect                        
                        #~ r = facerecognition_dlib.dlibRectToArray(facepos)
                        r = facepos
                        #~ print("r: %s" % str(r) )
                        if r != []:
                            cv2.rectangle(im,(r[0],r[1]),(r[2],r[3]), (255,80,80), 2 )
                            xPosIndex = int((r[0]+r[2])/2)-15
                            yPosIndex = r[3]+40
                        
                    if 0:
                        # customTesting
                        im = facerecognition_dlib.addGlasses(im,facepos,faceLandmarks)
                        
                    if 1:
                        # add properties
                        extra_prop = fr.getProperties(feat)
                        print("extra_prop: %s" % str(extra_prop) )
                        nNbrProperties = len(extra_prop)
                        for i,p in enumerate(extra_prop):
                            strTxt = "%s: %s,%5.2f" % (p[0], str(p[1]),p[2])                            
                            cv2.putText( im, strTxt, (10,im.shape[0]-(24*nNbrProperties)+i*24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2 )
                
                if bAnalyseAlt:
                    if maskDetector == None:
                        import sys
                        import os
                        sys.path.append( os.path.expanduser("~/dev/git/electronoos/custom_from_ext/") )
                        import am_tensorflow_infer
                        maskDetector = am_tensorflow_infer.MaskDetector()
                        maskDetector.loadModels()
                        
                    timeBegin = time.time()
                    retVal = maskDetector.detectFromImage( original, bShowResults=False )
                    print("INF: MaskDetector: analyses takes %5.3fs" % (time.time()-timeBegin) )
                    for detected in retVal:
                        class_id, conf, xmin, ymin, xmax, ymax = detected
                        if class_id == 0:
                            color = (0, 255, 0)
                        else:
                            color = (255, 0, 0)
                        nThick = 2
                        if conf < 0.8:
                            nThick = 1
                        cv2.rectangle( im, (xmin, ymin), (xmax, ymax), color, nThick )
                        cv2.putText(im, "%s: %.2f" % ( maskDetector.classToStr(class_id), conf), (xmin + 2, ymin - 4),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, nThick )
                        
                        
                
                if bFilenameIsShownInWindowsTitle:
                    # recreate image each time, plus: title is the good one
                    # cons: blink
                    cv2.destroyAllWindows()
                    strWindowName = strFileToShow
                else:
                    if bOutputOnScreenInfoFromFilename:
                        strFilenameToDraw = listFiles[idx]                        
                        cv2.putText( im, strFilenameToDraw, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (0,0,0), 2 )
                        cv2.putText( im, strFilenameToDraw, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (255,0,0), 1 )
                        strIndexEnd = strFilenameToDraw.split("_")[-1].split('.')[0]
                        
                        cv2.putText( im, strIndexEnd, (xPosIndex,yPosIndex), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,0), 4 )
                        cv2.putText( im, strIndexEnd, (xPosIndex,yPosIndex), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,0,0), 2 )
                        
                        if fr:
                            # print also index below the face
                            xf = int(( facepos[0]+facepos[2] ) / 2 - 15)
                            yf = int( facepos[3] + 32 )

                            if 1:
                                # render also face size
                                strIndexEnd += "(%dx%d)" % (facepos[2]-facepos[0],facepos[3]-facepos[1])
                            
                            cv2.putText( im, strIndexEnd, (xf,yf), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 4 )
                            cv2.putText( im, strIndexEnd, (xf,yf), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,0), 2 )                        
                            
                        if strIndexEnd != strPrevIndexEnd:
                            strPrevIndexEnd = strIndexEnd
                            cv2.rectangle( im, (0,0), (im.shape[1]-1, im.shape[0]-1), (0,255,0), 16 )
                        
                    
                    
                    strWindowName = "view_img"
                    
            if bInRenamming:
                cv2.line( im, (xPosIndex-10,yPosIndex+50), (xPosIndex-10,yPosIndex+50-30), (0,255,0), 2 )
            if strRename != "":
                cv2.putText( im, strRename, (xPosIndex,yPosIndex+50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4 )
                            
            cv2.namedWindow(strWindowName,cv2.WINDOW_NORMAL)      

            windowPosX, windowPosY = 10+150, 50 # 10, 50 for top left corner, a bit more to be able to see person index in my file
            if bAutoZoom:
                rZoomToApply = 1
                while 1:
                    rIdealRatio = getScreenWidth()/(im.shape[1]*rZoomToApply)
                    if rIdealRatio < 1:
                        rZoomToApply /= 2
                    elif rIdealRatio >= 2:
                        rZoomToApply *= 2
                    else:
                        break
                im = cv2.resize(im,(0,0),fx=rZoomToApply,fy=rZoomToApply)
                rZoomFactor = rZoomFactor
                windowPosX, windowPosY = 0,0

            cv2.imshow( strWindowName, im )
            cv2.moveWindow( strWindowName, windowPosX, windowPosY )
            h,w,p = im.shape
            cv2.resizeWindow(strWindowName, int(rZoomFactor*w),int(rZoomFactor*h))            
    
        # key != 255 or bMustRedraw
    # while - end
    print("DBG: end of while")
    if fr: 
        print("DBG: avant store features")
        facerecognition_dlib.storedFeatures.save()
# viewImg - end        
        
strFilename = sys.argv[1]
bAnalyse = False
bAnalyseAlt = False
if len(sys.argv)>2: 
    bAnalyse = True
viewImg( strFilename, bAnalyse = bAnalyse, bAnalyseAlt = bAnalyseAlt )

print("DBG: ended...")

# j'en suis la:
# 1907