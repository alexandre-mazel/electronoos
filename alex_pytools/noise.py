"""
some classic handy classes
(c) 2010-2022 A. Mazel
"""    

import numpy as np
import random

def generateImageSimplex(w,h,rZoom=1):
    # min and max seems to be limited from -0.864 to 0.864
    maxval = 0.865
    import opensimplex
    gen = opensimplex.OpenSimplex()
    
    #~ for i in range(3):
        #~ print(gen.noise2d(10,10))

    
    min = +100000
    max = -100000
    
    random.seed(0)
    im = np.zeros((h,w),dtype=np.uint8)
    for j in range(h):
        for i in range(w):
            if 0:
                v = gen.noise2d(x=(i-w/2)/rZoom, y=(j-h/2)/rZoom)
                #~ v = abs(v*255)
                v = int( ( (v+maxval)/(2*maxval) )* 255 )
            else:
                v = int(random.random()* 255)
            im[j,i] = v
            #~ print("%5.1f => %s" % (v, im[j,i]) )
            if v > max:
                max = v
            if v < min:
                min = v
    print("min: %5.3f, max: %5.3f" % (min,max) )
    return im
    
            
def autoTest():
    import cv2
    zoom = 0.1
    while zoom < 10000:
        im = generateImageSimplex(160,120,zoom)
        im = cv2.resize(im,None,fx=3,fy=3)
        cv2.imshow("OpenSimpley grey", im)
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27:
            break
        zoom *= 1.1
            
if __name__ == "__main__":
    autoTest()