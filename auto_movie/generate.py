
import cv2
import numpy as np
import os
import sys
import time
sys.path.append("/Users/amazel/dev/git/protolab_group/face_tools/" )
import face_detector

#~ import abcdk.image # for getExifInfo, need PIL

def generate(strPath):
    wrender=320
    hrender=240
    s = np.zeros((hrender,wrender,3), dtype=np.int8)
    listImg = sorted(os.listdir(strPath))
    nCpt = 0
    fd = face_detector.FaceDetectOpenCV()
    for f in listImg[:]:
        print("t:%5.2f, f:%s" % (time.time(),f ) )
        filename = strPath+f
        im = cv2.imread(filename)
        h,w,nplane=im.shape
        print("image size: %dx%d" % (w,h) )
        imreduced = cv2.resize(im,(w/8,h/8))
        minFaceSize = 100
        faces = fd.detect_face( im, bCompleteSearch = True )
        print("faces: %s" % str(faces) )
        faces = face_detector.filterFaces(faces, (minFaceSize,minFaceSize))

        #~ print abcdk.image.getExifInfo( filename, ["Model", "DateTime"] );

        # respect original ratio
        rOrigRatio = float(w)/h
        rRenderRatio = float(wrender)/hrender
        ratioOrigRender = rOrigRatio/rRenderRatio
        rRatioToApply = rOrigRatio/ratioOrigRender
        print("ratio: orig: %5.3f, render: %5.3f, ratio: %5.3f, rRatioToApply:%5.3f" % (rOrigRatio,rRenderRatio,ratioOrigRender,rRatioToApply) )
        
        
        

        
        nSpeedX = 0
        nSpeedY = 0
        rZoomX = 0
        rZoomY = 0
        
        # compute start of crop
        if len(faces)>0:
            face = faces[0]
            xf,yf,wf,hf = face
            margin = 0.5
            while 1:
                x1o = max(xf-int(wf*margin),0)
                x2o = min(xf+wf+int(wf*margin),w)
                y1o = max(yf-int(hf*margin),0)
                y2o = min(yf+hf+int(hf*margin),h)

                hr = y2o-y1o
                wr = hr * rRatioToApply
                x1o = ((x1o+x2o)/2)-(wr/2)
                x2o = x1o + wr
        
                print("start of crop: %d:%d %d:%d" % (x1o,x2o,y1o,y2o) )
                
                if x1o < 0:
                    x2o += -x1o
                    x1o = 0

                if y1o < 0:
                    y2o += -y1o
                    y1o = 0
                    
                print("start of crop: %d:%d %d:%d" % (x1o,x2o,y1o,y2o) )
                
                if x2o < w and y2o < h:
                    break
                margin -= 0.1
                
            rZoomX = 0.5
            rZoomY = 0.5
                
        else:
            assert(wrender>=hrender)
            # center picture in rendering in x, and start from bottom of image
            x1o,x2o = 0,w
            y1o,y2o = h-(w/rRatioToApply),h
            if w<h:
                nSpeedY = -4
            
        print("start of crop: %d:%d %d:%d" % (x1o,x2o,y1o,y2o) )

        for inc in range(200):
            i = inc
            j = inc
            x1= int(x1o+rZoomX*inc)
            x2 = int(x2o-rZoomX*inc)
            y1 = int(y1o+rZoomY*inc)
            y2 = int(y2o-rZoomY*inc)
            s = im[y1+j*nSpeedY:y2+j*nSpeedY,x1+i*nSpeedX:x2+i*nSpeedX]
            s = cv2.resize(s,(wrender,hrender))
            cv2.imshow("result",s)
            cv2.moveWindow("result", 0,0)
            cv2.imshow("orig",imreduced)
            cv2.moveWindow("orig", wrender+10,0)
            key = cv2.waitKey(4) # ~25fps
            if key == 27:
                return
        nCpt += 1
        
        #~ if nCpt > 4:
            #~ break
    
    
generate("D:/temp_photo_pour_auto_montage/")