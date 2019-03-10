import cv2
import numpy as np
import os
import sys
import time

sys.path.append("/Users/amazel/dev/git/protolab_group/face_tools/" )
import face_detector

# use the abcdk from git folder!
sys.path.insert(0,"/Users/amazel/dev/git/protolab_group/abcdk/sdk" )
import abcdk.image

def filterOnExts( aFiles, astrExts = ["jpg"] ):
    """
    keep in aFiles only filenames (actually string) containing extensions in astrExts
    """
    for i in range(len(astrExts)):
        astrExts[i] = astrExts[i].lower()
        if astrExts[i][0] != '.':
            astrExts[i] = '.' + astrExts[i]
            
    i = 0
    while 1:
        for strExt in astrExts:
            if strExt not in aFiles[i].lower():
                del aFiles[i]
            else:
                i += 1
        if i >= len(aFiles):
            break
    return aFiles
    
    
def filterFacesOnQuality( im, faces ):
    f = []
    for (x,y,w,h) in faces:   
        #getImageSharpness_Face # should be nice but only cv1
        res = abcdk.image.getImageSharpness( im[y:y+h,x:x+w] )
        print( "filterFacesOnQuality: %s => res: %s" % (str((x,y,w,h)),res) )
        if res[0] > 30: # on faces, good have 330/500/838
            f.append((x,y,w,h))
    return f

def selectInFolder( strPath ):
    """
    filename will be changed in:
    IMG_7334_r.JPG
    or
    IMG_7334_r_pm.JPG
    or
    IMG_7334_pm.JPG
    # quality range from [(nothing), _pm, _good, _perfect]
    """
    files = sorted( os.listdir(strPath) )
    files = filterOnExts( files, ["jpg"] )
        
    fd = face_detector.FaceDetectOpenCV()
    nNumPhoto = -1 # -1 # -4
    bReload = True
    nRotate = 0
    im = None
    while 1:
        if bReload:
            bReload = False
            bToDel = False
            if im != None:
                # draw a computing sign
                cv2.circle( im, (30,30),20, (255,0,0), -1 )
                cv2.imshow("im", im )
                cv2.waitKey(100)
            if nNumPhoto < 0:
                nNumPhoto = len(files)+nNumPhoto
            if nNumPhoto >= len(files):
                nNumPhoto = nNumPhoto - len(files)
            fname = strPath + files[nNumPhoto]
            print("INF: loading %s" % files[nNumPhoto] )
            timeBegin = time.time()
            photo = cv2.imread( fname ) # IM_READ_IGNORE_ORIENTATION
            print("DBG: loading takes: %5.3fs (%dx%d)" % ((time.time()-timeBegin),photo.shape[1], photo.shape[0]) )
            if "_r" in files[nNumPhoto]:
                photo = np.rot90(photo,axes=(0, 1))
                
            nQuality = 0
            if "_pm" in files[nNumPhoto]:
                nQuality += 1
            if "_good" in files[nNumPhoto]:
                nQuality += 1
            if "_perfect" in files[nNumPhoto]:
                nQuality += 1
                
            for i in range(nRotate):
                photo = np.rot90(photo,axes=(0, 1))
            minFaceSize = 100
            faces = fd.detect_face( photo, bCompleteSearch= True )
            print("faces: %s" % str(faces) )
            faces = face_detector.filterFaces(faces, (minFaceSize,minFaceSize))
            faces = filterFacesOnQuality( photo, faces )
            print("faces_filtered: %s" % str(faces) )
            if len(faces) < 1 and nRotate == 0:
                photorot = np.rot90(photo,axes=(0, 1))
                #~ photorot = cv2.resize(photorot, (1280,960))
                #~ photorot = cv2.resize(photorot, (640,480))
                faces = fd.detect_face( photorot, bCompleteSearch= True )
                print("faces (2): %s" % str(faces) )
                faces = face_detector.filterFaces(faces, (minFaceSize,minFaceSize))
                faces = filterFacesOnQuality( photorot, faces )
                print("faces_filtered (2): %s" % str(faces) )
                if len(faces) > 0 or 0:
                    print("INF: Rotating!" )
                    photo = photorot
                    nRotate = 1
            
            if 1:
                photo = face_detector.drawRectForFaces( photo, faces )
            
            renderSizeX = 2736
            renderSizeY = 1824
            im = np.zeros( (renderSizeY,renderSizeX,3), np.uint8 )
            
            ratioPhoto = photo.shape[1]/float(photo.shape[0])
            if ratioPhoto < 1:
                # photo has been rotated!
                photosizeY = renderSizeY
                photosizeX = int(photosizeY * ratioPhoto)
            else:
                photosizeX = renderSizeX
                photosizeY = int(photosizeX/ratioPhoto)
                
            im[0:photosizeY,0:photosizeX] = cv2.resize(photo,(photosizeX,photosizeY))
            
            headOffsetX = photosizeX
            headOffsetY = 0
            headSizeX = renderSizeX-photosizeX
            print("headSizeX: %d" % headSizeX )
            if headSizeX == 0:
                headSizeX = renderSizeX*1/3
                headOffsetX = renderSizeX - headSizeX
            for (x,y,w,h) in faces:
                face = photo[y:y+h,x:x+w]
                headSizeY = (headSizeX*w)/h
                #~ headSizeY/=2
                face = cv2.resize( face, (headSizeX, headSizeY) )
                rFaceSizeYInScreen = headSizeY
                if headOffsetY+headSizeY > renderSizeY:
                    rFaceSizeYInScreen = renderSizeY-headOffsetY
                im[headOffsetY:headOffsetY+headSizeY,headOffsetX:headOffsetX+headSizeX] = face[0:rFaceSizeYInScreen,]
                if 1:
                    colorText = (255,255,255)
                    rSharp,rLum = abcdk.image.getImageSharpness( photo[y:y+h,x:x+w] )
                    minColor = photo[y:y+h,x:x+w].min()
                    maxColor = photo[y:y+h,x:x+w].max()
                    strText = "%d/%d, r:%s/%s"%(int(rSharp), int(rLum),minColor,maxColor)
                    cv2.putText( im, strText, (headOffsetX+40, headOffsetY+50), cv2.FONT_HERSHEY_SIMPLEX, 2, colorText, 4 )
                headOffsetY += headSizeY
            print("DBG: analysing takes: %5.3fs" % (time.time()-timeBegin))

        
        if nQuality > 0 or 1:
            for i in range(nQuality):
                cv2.circle( im, (30+i*80,30),30, (0,255,0), -1 )
                
        if bToDel:
                cv2.circle( im, (100,100),100, (0,0,255), -1 )
                
        #~ cv2.rectangle( im, (0, 0), (1000, 1000), (255, 255, 255), 3 ) 
        #~ print(dir(cv2.cv))
        cv2.namedWindow( "im", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty( "im", cv2.WND_PROP_FULLSCREEN,cv2.cv.CV_WINDOW_FULLSCREEN)
        #~ return
        cv2.imshow("im", im )
        cv2.moveWindow( "im", 0,0 )

        key = cv2.waitKey(0)
        print( "key: %d" % key )
        if key == 3014656:
            bToDel = True
        if key == 2424832:
            nNumPhoto -= 1
            bReload = True
            nRotate=0
        if key == 2555904:
            nNumPhoto += 1
            bReload = True
            nRotate=0
        if key == 27 or key == ord('q'):
            break
        if key == ord('r'):
            nRotate += 1
            bReload = True
        if key == 32:
            nQuality += 1
            if nQuality > 3:
                nQuality = 0
                cv2.rectangle( im, (0+0*80,0),(30+3*80,60), (0,0,0), -1 )
            astrQuality = ["","_pm", "_good", "_perfect"]
            newname = files[nNumPhoto]
            for sq in astrQuality:
                newname = newname.replace(sq, "")
            newname = newname.replace(".", astrQuality[nQuality]+'.')
            print("INF: renaming '%s' in '%s'"%(files[nNumPhoto],newname) )
            os.rename(strPath + files[nNumPhoto],strPath + newname)
            files[nNumPhoto]=newname
            
    
strPath = "C:/Users/amazel/perso/photo18b/2018-07-01_-_CelineStGermain/"
selectInFolder( strPath )