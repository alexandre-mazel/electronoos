import numpy as np
import cv2

def generate_random_img(w,h,nbrplane=3):
    #~ im = np.zeros((h,w,nbrplane), dtype=np.uint8)
    im = np.random.randint(255, size=[h, w, nbrplane])
    im = im.astype(dtype=np.uint8)
    print(im.shape)
    print(im[0,0])
    print(im[0,1])
    
    bShow = 1
    if bShow:
        cv2.imshow("random img", im)
        cv2.waitKey(0)
    
    return im
    
generate_random_img(640,480)