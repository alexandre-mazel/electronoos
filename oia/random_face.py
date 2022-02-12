import numpy as np
import cv2
import time

def generate_random_img(w, h, nbrplane=3, nbrColor = 256, bShow = 1):
    #~ im = np.zeros((h,w,nbrplane), dtype=np.uint8)
    im = np.random.randint(nbrColor, size=[h, w, nbrplane])
    if nbrColor<256:
        im *= int(255/(nbrColor-1))
    im = im.astype(dtype=np.uint8)
    #~ print(im.shape)
    #~ print(im[0,0])
    #~ print(im[0,1])
    
    bShow = 1
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
        detected_objects = self.cascade_classifier.detectMultiScale(image_grey, minSize=(20, 30),maxSize=(100,120),minNeighbors = 13)
        return detected_objects
        
    def renderFaces(self,image,faces,color = (0, 255, 0)):
        img2 = np.copy(image)
        img2=np.ascontiguousarray(img2, dtype=np.uint8) # copy, just to prevent some rectangle sometimes throwing: "TypeError: Layout of the output array img is incompatible with cv::Mat"
        for (x,y,w,h) in faces:        
            cv2.rectangle( img2, (x, y), (x+w, y+h), color, 2)
        return img2

#~ class FaceDetector - end


fd =FaceDetector()
cpt = 0
cpt_found = 0
time_begin = time.time()
while 1:
    if 0:
        #~ im = generate_random_img(640,480)
        im = generate_random_img(60,120,1) # 120,000 images => rien (61.6fps)
    else:
        im = generate_random_img(10,16,1,4)
        im = cv2.resize(im,(0,0),fx=10,fy=10,interpolation = cv2.INTER_CUBIC ) # INTER_CUBIC, INTER_NEAREST
    
    #~ im = cv2.imread("../data/multiple_humans.jpg")
    faces = fd.detect(im)
    if len(faces)>0:
        print("Found Face(s)")
        im_to_render = fd.renderFaces(im,faces)
        window_name = "faces %d!" % cpt
        cv2.imshow(window_name,im_to_render)
        cv2.moveWindow(window_name,128*(cpt_found%8),200)
        cv2.waitKey(10)
        cpt_found += 1
    cpt += 1
    if (cpt%100)==0:
        print("frame: %d, %.1fps" % (cpt,cpt/(time.time()-time_begin)))