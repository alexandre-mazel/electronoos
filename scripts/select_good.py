import cv2
import numpy as np
import os
import sys
import time

sys.path.append("../../face_tools/" )
import face_detector

sys.path.append("../alex_pytools/" )
import face_detector_cv3


# use the abcdk from git folder!
sys.path.insert(0,"../../abcdk/sdk" )
sys.path.insert(0,"c:/Users/alexa/dev/git/abcdk" )
sys.path.insert(0,"c:/Users/alexa/dev/git/abcdk/sdk" )
sys.path.insert(0,"c:/Users/alexa/dev/git/abcdk/sdk/abcdk" )
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
    IMG_7334_r.JPG or _r1 or _r2 or r3 ... (each a rot of 90deg)
    or
    IMG_7334_r_pm.JPG
    or
    IMG_7334_pm.JPG
    # quality range from [(nothing), _pm, _good, _perfect]
    """
    files = sorted( os.listdir(strPath) )
    files = filterOnExts( files, ["jpg"] )
        
    fd = face_detector.FaceDetectOpenCV()
    fdcv3 = face_detector_cv3.facedetector
    nNumPhoto = 0 # -1 # -4
    bReload = True
    bShowFace = True
    bShowOnlyGood = False
    im = None

    renderSizeX = 2736
    renderSizeY = 1824
    while 1:
        if bReload:
            bReload = False
            bToDel = False
            if not im is None:
                # draw a computing sign
                cv2.circle( im, (30,30),20, (255,0,0), -1 )
                cv2.imshow("im", im )
                cv2.waitKey(100)
            if nNumPhoto < 0:
                nNumPhoto = len(files)+nNumPhoto
            if nNumPhoto >= len(files):
                nNumPhoto = nNumPhoto - len(files)
            fname = strPath + files[nNumPhoto]
            if bShowOnlyGood:
                bLoop = 0
                while not "_good" in fname and not "__perfect" in fname:
                    nNumPhoto += 1
                    if nNumPhoto >= len(files):
                        nNumPhoto = nNumPhoto - len(files)
                        if bLoop:
                            break # on a fait le tour, on arrete
                        bLoop = 1
                    fname = strPath + files[nNumPhoto]
                    
                
            print("\n\nINF: loading %s" % files[nNumPhoto] )
            timeBegin = time.time()
            photo = cv2.imread( fname ) # IM_READ_IGNORE_ORIENTATION
            print("DBG: loading takes: %5.3fs (%dx%d)" % ((time.time()-timeBegin),photo.shape[1], photo.shape[0]) )
            while photo.shape[0] > renderSizeY:
                print("INF: This is a big photo, resizing it" )
                photo = cv2.resize(photo,(photo.shape[1]//2,photo.shape[0]//2))
                print("INF: newshape: %s" % str(photo.shape))
                
            nRotate = 0
            if "_r1" in files[nNumPhoto]:
                nRotate = 1
            elif "_r2" in files[nNumPhoto]:
                nRotate = 2
            elif "_r3" in files[nNumPhoto]:
                nRotate = 3
                
            nQuality = 0
            if "_pm" in files[nNumPhoto]:
                nQuality = 1
            elif "_good" in files[nNumPhoto]:
                nQuality = 2
            elif "_perfect" in files[nNumPhoto]:
                nQuality = 3
                
            for i in range(nRotate):
                photo = np.rot90(photo,axes=(0, 1))

            minFaceSize = 100
            #~ faces = fd.detect_face( photo, bCompleteSearch= True )
            faces = fdcv3.detect(photo,bRenderBox=False,confidence_threshold=0.3)
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
                    nRotate += 1
            
            if 0:
                photo = face_detector.drawRectForFaces( photo, faces )
            
            im = np.zeros( (renderSizeY,renderSizeX,3), np.uint8 )
            
            ratioPhoto = photo.shape[1]/float(photo.shape[0])
            if ratioPhoto < 1:
                # photo has been rotated!
                photosizeY = renderSizeY
                photosizeX = int(photosizeY * ratioPhoto)
            else:
                photosizeX = renderSizeX
                photosizeY = int(photosizeX/ratioPhoto)
                if photosizeY > renderSizeY:
                    photosizeY = renderSizeY
                    photosizeX = int(renderSizeY*ratioPhoto)
                
            print("photosizeX: %d, photosizeY: %d" % (photosizeX,photosizeY))
            print("renderSizeX: %d, renderSizeY: %d" % (renderSizeX,renderSizeY))
            assert(photosizeY<=renderSizeY)
            im[0:photosizeY,0:photosizeX] = cv2.resize(photo,(photosizeX,photosizeY))
            
            print("nbr faces found: %d" % (len(faces)))
            headOffsetX = photosizeX
            headOffsetY = 0
            headSizeX = (renderSizeX-photosizeX)
            if len(faces)>2:
                headSizeX //= len(faces)
            print("headSizeX: %d" % headSizeX )
            if headSizeX == 0:
                headSizeX = int(renderSizeX*1/3)
                headOffsetX = renderSizeX - headSizeX

            
            if bShowFace:
                for (x,y,w,h) in faces:
                    w = w-x
                    h = int((h-y)*1.) # new face detect doesn't return same rect
                    face = photo[y:y+h,x:x+w]
                    headSizeY = int((headSizeX*w)/h)
                    #~ headSizeY/=2
                    headSizeY = int(headSizeY*1.7)
      
                    face = cv2.resize( face, (headSizeX, headSizeY) )
                    rFaceSizeYInScreen = headSizeY
                    if headOffsetY+headSizeY > renderSizeY:
                        rFaceSizeYInScreen = renderSizeY-headOffsetY
                    print("headOffsetX: %d, headOffsetY: %d" % (headOffsetX,headOffsetY))
                    im[headOffsetY:headOffsetY+headSizeY,headOffsetX:headOffsetX+headSizeX] = face[0:rFaceSizeYInScreen,]
                    if 1:
                        colorText = (255,255,255)
                        rSharp,rLum = abcdk.image.getImageSharpness( photo[y:y+h,x:x+w] )
                        minColor = photo[y:y+h,x:x+w].min()
                        maxColor = photo[y:y+h,x:x+w].max()
                        strText = "sh/lum:%d/%d, r:%s/%s"%(int(rSharp), int(rLum),minColor,maxColor)
                        cv2.putText( im, strText, (headOffsetX+40, headOffsetY+50), cv2.FONT_HERSHEY_SIMPLEX, 2, colorText, 4 )
                    headOffsetY += headSizeY

            print("DBG: analysing takes: %5.3fs" % (time.time()-timeBegin))

        
        if nQuality > 0 or 1:
            for i in range(nQuality):
                cv2.circle( im, (30+i*80,30),30, (0,255,0), -1 )
                
        if bToDel:
                xc = 300
                yc = 300
                sizec=100
                cv2.circle( im, (xc,yc),sizec, (0,0,255), -1 )
                cv2.putText(im, "y?",(xc-sizec//2,yc),0,4,(255,255,255),4)
                
        #~ cv2.rectangle( im, (0, 0), (1000, 1000), (255, 255, 255), 3 ) 
        #~ print(dir(cv2.cv))
        cv2.namedWindow( "im", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty( "im", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        #~ return
        cv2.imshow("im", im )
        cv2.moveWindow( "im", 0,0 )

        key = cv2.waitKey(0)
        print( "key: %d" % key )
        if key == 3014656 or key == ord('d'):
            bToDel = True # ask to del, must press y to validate
        if key == ord('y'):
            if bToDel:
                os.unlink(strPath + files[nNumPhoto])
                del files[nNumPhoto]
                bReload = True
                continue
        if key == 2424832  or key == ord('b'):
            # fleche gauche: prev
            nNumPhoto -= 1
            bReload = True
            continue
        if key == 2555904 or key == ord('n'):
            # fleche gauche: next
            nNumPhoto += 1
            bReload = True
            continue
        if key == 27 or key == ord('q'):
            break
        if key == ord('r'):
            nRotate += 1
            nRotate %= 4
            astrRot = ["","_r1", "_r2", "_r3"]
            newname = files[nNumPhoto]
            for sr in astrRot:
                newname = newname.replace(sr, "")
            newname = newname.replace(".", astrRot[nRotate]+'.')
            print("INF: renaming '%s' to '%s'"%(files[nNumPhoto],newname) )
            os.rename(strPath + files[nNumPhoto],strPath + newname)
            files[nNumPhoto]=newname
            bReload = True
        
        if key == 32:
            # space: change quality
            nQuality += 1
            if nQuality > 3:
                nQuality = 0
                cv2.rectangle( im, (0+0*80,0),(30+3*80,60), (0,0,0), -1 )
            astrQuality = ["","_pm", "_good", "_perfect"]
            newname = files[nNumPhoto]
            for sq in astrQuality:
                newname = newname.replace(sq, "")
            newname = newname.replace(".", astrQuality[nQuality]+'.')
            print("INF: renaming '%s' to '%s'"%(files[nNumPhoto],newname) )
            os.rename(strPath + files[nNumPhoto],strPath + newname)
            files[nNumPhoto]=newname
            
        if key == ord('f'):
            bShowFace = not bShowFace
            print("DBG: bShowFace: %d" % bShowFace )
            bReload = True

        if key == ord('g'):
            bShowOnlyGood = not bShowOnlyGood
            print("DBG: bShowOnlyGood: %d" % bShowOnlyGood )
            bReload = True            
            
            
    
#~ strPath = "C:/Users/amazel/perso/photo18b/2018-07-01_-_CelineStGermain/"
#~ strPath = "D:/temp_photo_pour_auto_montage/"
strPath = "c:/photos22/2022-07-03_-_BookAwa/"

selectInFolder( strPath )