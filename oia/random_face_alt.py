import numpy as np
import cv2
import math
import time

import sys
sys.path.append("../../electronoos/alex_pytools")
try: import face_detector_cv3
except: pass

def generate_raindrop(w, h, nbrplane=1, nbrColor = 256):
    im = np.zeros((h,w,nbrplane), dtype=np.uint8)
    imt = im.copy()
    
    nbr_circle = np.random.randint(0,w/3)
    for i in range(nbr_circle*4):
        x = np.random.randint(0,w)
        y = np.random.randint(0,h)
        r = np.random.randint(0,w/10)
        if 0:
            # no alpha
            cv2.circle(im,(x,y),r,(255,255,255),-1)
        else:
            # alpha
            imt[::] = 0
            if 0:
                cv2.circle(imt,(x,y),r,(255,255,255),-1)
            else:
                for j in range(r):
                    cv2.circle(imt,(x,y),r-j,(j*16,j*16,j*16),-1)
            alpha = 0.4
            im = cv2.addWeighted(imt, alpha, im, 1., 0)
    
    if 1:
        # threshold
        ret,im = cv2.threshold(im,100,255,cv2.THRESH_BINARY)
        
    im = 255-im
    return im
    
def generate_inkdrop(w, h, nbrplane=3, nbrColor = 256, bMirror = 0):
    im = np.zeros((h,w,nbrplane), dtype=np.uint8)
    im[:] = 255
    
    nbr_circle = np.random.randint(w/20)
    nbr_circle = np.random.randint(40)
    #~ nbr_circle = 20
    listTaches = [] # x,y,r,col
    for i in range(nbr_circle):
        x = np.random.randint(w)
        y = np.random.randint(h)
        r = np.random.randint(w/16)
        color = (0,0,0)
        if nbrplane>1 and 1:
            color_r,g,b=0,0,0
            if np.random.random()>0.5:color_r=255
            if np.random.random()>0.5:g=255
            if np.random.random()>0.5:b=255
            color = (color_r,g,b)
            #~ color = (0,0,0)
        listTaches.append((x,y,r,color))
        cv2.circle(im,(x,y),r,color,-1)
        if 1:
            # deforme le rond
            dx = x + np.random.randint(11)-5
            dy = y + np.random.randint(11)-5
            cv2.circle(im,(dx,dy),r,color,-1)
        len_radiance = int(r/(np.random.randint(3)+np.random.randint(2)+1))
        len_radiance = 30
        nbr_radiance = np.random.randint(4)+12
        rr = int(r/20)
        if rr > 0:
            for j in range(nbr_radiance):
                angle = j*2*math.pi/nbr_radiance
                rrt = rr
                for k in range(len_radiance+1):

                    angle += (np.random.random()-0.5)/20.
                    xr = x + int( (k+r) * math.cos(angle) )
                    yr = y + int( (k+r) * math.sin(angle) )
                    #~ rrt = rr
                    #~ if k == len_radiance and 0:
                        #~ rrt = int(rrt*1.3)
                    #~ else:
                        #~ rrt = rr+np.random.randint(4)
                    rrt += np.random.randint(4) - 2 # decrease little by little
                    if rrt< 1:
                        continue
                    cv2.circle(im,(xr,yr),rrt,color,-1)
                    # 
                if 0:
                    # lissage des 2 cercles
                    for angle_offset in [-0.2,+0.2]:
                        anglel = angle+angle_offset
                        xrl = x + int( (len_radiance+r-rr*0.) * math.cos(anglel) )
                        yrl = y + int( (len_radiance+r-rr*0.) * math.sin(anglel) )
                        cv2.circle(im,(xrl,yrl),int(rr/2),color,-1)
                        

    if 1:
        im = 255-im
        kernel = np.ones((5, 5), 'uint8')
        im = cv2.dilate(im, kernel, iterations=1)
        im = 255-im
        
    # apres le dilate on ajoute des projections
    for (x,y,r,color) in listTaches:
        if 1:
            # fines projections autour de la tache
            if r>10:
                for j in range(np.random.randint(8)+2):
                    angle = np.random.randint(360)
                    lent = np.random.randint(40)
                    offset = r+np.random.randint(8)
                    rrt = np.random.randint(2)+1
                    rrt_inc = (np.random.randint(11)-5)/10
                    #~ rrt_inc = 0
                    for k in range(lent):
                        if k%3==0:
                            rrt += rrt_inc
                        if rrt < 1:
                            break
                        xt = x + int( (k+offset+r) * math.cos(angle) )
                        yt = y + int( (k+offset+r) * math.sin(angle) )
                        cv2.circle(im,(xt,yt),int(rrt),color,-1)
                
    
    if bMirror:
        # mirror vertic
        im[:,w//2:w] = im[:,w//2:0:-1]
    return im

def generate_random_img(w, h, nbrplane=3, nbrColor = 256, bShow = 1):
    #~ im = np.zeros((h,w,nbrplane), dtype=np.uint8)
    im = np.random.randint(nbrColor, size=[h, w, nbrplane])
    if nbrColor<256:
        im *= int(255/(nbrColor-1))
    im = im.astype(dtype=np.uint8)
    #~ print(im.shape)
    #~ print(im[0,0])
    #~ print(im[0,1])
    
    if bShow:
        cv2.imshow("random img", im)
        key = cv2.waitKey(1)
        if key == 27:
            exit(0)
    
    return im
    
class FaceDetector:
    def __init__( self ):
        self.cascade_classifier = cv2.CascadeClassifier( "haarcascade_frontalface_default.xml")
        
    def detect( self, image ):
        """
        is there a face in image ?
        return [face1,face2,...] with each face a list of face coord [x,y,w,h]
        """
        if len(image.shape)>2 and image.shape[2] > 1:
            image_grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            image_grey = image
        detected_objects = self.cascade_classifier.detectMultiScale(image_grey, minSize=(20, 30),maxSize=(100,120),minNeighbors = 11)
        return detected_objects
        
    def renderFaces(self,image,faces,color = (0, 255, 0)):
        img2 = np.copy(image)
        img2=np.ascontiguousarray(img2, dtype=np.uint8) # copy, just to prevent some rectangle sometimes throwing: "TypeError: Layout of the output array img is incompatible with cv::Mat"
        for (x,y,w,h) in faces:        
            cv2.rectangle( img2, (x, y), (x+w, y+h), color, 2)
        return img2

#~ class FaceDetector - end


fd =FaceDetector()
fdcv3 = face_detector_cv3.facedetector
        
cpt = 0
cpt_found = 0
time_begin = time.time()
while 1:
    if 0:
        #~ im = generate_random_img(640,480)
        im = generate_random_img(60,120,1) # 120,000 images => rien (61.6fps)
    elif 1:
        #~ im = generate_raindrop(320,480)
        im = generate_inkdrop(1280,900)
        #~ im = generate_inkdrop(320,480,bMirror=1)
        #~ im = cv2.resize(im,(0,0),fx=2,fy=2)
        
        cv2.imshow("random img", im)
        if 0:
            key = cv2.waitKey(1)
        else:
            key = cv2.waitKey(0)
        if key == 27:
            exit(0)
    else:
        im = generate_random_img(10,16,1,4,bShow=1)
        im = cv2.resize(im,(0,0),fx=10,fy=10,interpolation = cv2.INTER_CUBIC ) # INTER_CUBIC, 
    
    #~ im = cv2.imread("../data/multiple_humans.jpg")
    if 1:
        # haarcascade
        faces = fd.detect(im)
        if len(faces)>0:
            print("Found Face(s)")
            im_to_render = fd.renderFaces(im,faces)
            window_name = "faces %d!" % cpt
            cv2.imshow(window_name,im_to_render)
            cv2.moveWindow(window_name,im.shape[1]*(cpt_found%8),200)
            cv2.waitKey(10)
            cpt_found += 1
    else:
        faces = fdcv3.detect(im,bRenderBox=False,confidence_threshold=.95)
        if len(faces)>0:
            print("Found Face(s)")
            im_to_render = im.copy()
            fdcv3.render_res(im_to_render, faces)
            window_name = "faces %d!" % cpt
            cv2.imshow(window_name,im_to_render)
            cv2.moveWindow(window_name,128*(cpt_found%8),200)
            cv2.waitKey(10)
            cpt_found += 1
    cpt += 1
    if (cpt%100)==0:
        print("frame: %d, %.1fps" % (cpt,cpt/(time.time()-time_begin)))