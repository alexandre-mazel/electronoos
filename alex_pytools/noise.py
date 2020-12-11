"""
some classic handy classes
(c) 2010-2022 A. Mazel
"""    

import math
import numpy as np
import random

global_gen = None

"""
Pour avoir plus de details, on mixe plusieurs grille a differente resolution

noise1 = PerlinNoise(octaves=3)
noise2 = PerlinNoise(octaves=6)
noise3 = PerlinNoise(octaves=12)
noise4 = PerlinNoise(octaves=24)

xpix, ypix = 100, 100
pic = []
for i in range(xpix):
    row = []
    for j in range(ypix):
        noise_val =         noise1([i/xpix, j/ypix])
        noise_val += 0.5  * noise2([i/xpix, j/ypix])
        noise_val += 0.25 * noise3([i/xpix, j/ypix])
        noise_val += 0.125* noise4([i/xpix, j/ypix])
"""
def generateImageSimplex(w,h,rZoom=1,sizegrid=256,offsetx=0,offsety=0):
    """
    sizegrid: change in the library to get more details (but not concluant)
    nice with a zoom around 200
    """
    # min and max seems to be limited from -0.864 to 0.864
    maxval = 0.865
    import opensimplex
    #~ gen = opensimplex.OpenSimplex(sizegrid=sizegrid)
    global global_gen
    if global_gen == None: global_gen = opensimplex.OpenSimplex()
    gen = global_gen
    
    
    
    #~ for i in range(3):
        #~ print(gen.noise2d(10,10))

    
    min = +100000
    max = -100000
    
    random.seed(0) # for the random case
    im = np.zeros((h,w),dtype=np.uint8)
    for j in range(h):
        for i in range(w):
            if 1:
                v = gen.noise2d(x=(i-w/2+offsetx)/rZoom, y=(j-h/2+offsety)/rZoom,bUseCache=True)
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
    print("zoom: %s, min: %5.3f, max: %5.3f" % (rZoom, min,max) )
    return im
    
def generateImagePerlin(w,h,rZoom=1,sizegrid=256,offsetx=0,offsety=0):
    """
    at 12 octaves, nice around a 1.5 zoom
    """
    
    import perlin_noise
    
    # min and max seems to be limited from -0.864 to 0.864
    maxval = 0.63

    min = +100000
    max = -100000
    
    im = np.zeros((h,w),dtype=np.uint8)
    noise = perlin_noise.PerlinNoise(octaves=12, seed=1)
    for j in range(h):
        for i in range(w):
            if 1:
                x=(i-w/2+offsetx)/rZoom
                y=(j-h/2+offsety)/rZoom
                x /= w
                y /= h
                v = noise([x,y])
                v = int( ( (v+maxval)/(2*maxval) )* 255 )
            im[j,i] = v
            if v > max:
                max = v
            if v < min:
                min = v

    print("zoom: %s, min: %5.3f, max: %5.3f" % (rZoom, min,max) )
    return im
    
    
def generateLandscape(w,h,rZoom=1,offsetx=0,offsety=0):
    
    # use of 4 simplex at different scale
    # nice zoom are around 1 for noisy to 64 for nice detail
    im1 = generateImageSimplex(w,h,rZoom=rZoom*1,offsetx=0,offsety=0)
    im2 = generateImageSimplex(w,h,rZoom=rZoom*4,offsetx=0,offsety=0)
    im3 = generateImageSimplex(w,h,rZoom=rZoom*16,offsetx=0,offsety=0)
    im4 = generateImageSimplex(w,h,rZoom=rZoom*64,offsetx=0,offsety=0)
    
    im = im1*0.0625 + im2*0.125 + im3*0.25 + im4 * 0.5

    im = im.astype(np.uint8)
    #~ print(im)
    return im
    
def animateLandscape():
    import cv2
    inc = 1
    zoom = 1
    while zoom < 1000:
        im = generateLandscape(160,120,zoom,offsetx=int(math.sin(inc)*10),offsety=int(math.sin(inc)*10))
        im = cv2.resize(im,None,fx=2,fy=2)
        cv2.imshow("OpenSimplex grey", im)
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27:
            break
        zoom *= 1.1
    
    
            
def exploreMethod():
    import cv2
    import time
    timeBegin = time.time()
    if 0:
        inc = 1
        zoom = 0.1
        while zoom < 1000:
            im = generateImageSimplex(160,120,zoom,offsetx=int(math.sin(inc)*10),offsety=int(math.sin(inc)*10))
            im = cv2.resize(im,None,fx=2,fy=2)
            cv2.imshow("OpenSimplex grey", im)
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                break
            zoom *= 1.1
            #~ inc += 1
    elif 0:
        zoom = 50
        for sizegrid in [64,256,1024,1024*1024]:
            im = generateImageSimplex(160,120,zoom,sizegrid)
            im = cv2.resize(im,None,fx=2,fy=2)
            cv2.imshow("OpenSimplex grey " + str(sizegrid), im)
            cv2.waitKey(10)
        key = cv2.waitKey(0)    
    elif 0:
        inc = 1
        zoom = 0.6
        while zoom < 2:
            im = generateImagePerlin(160,120,zoom,offsetx=int(math.sin(inc)*10),offsety=int(math.sin(inc)*10))
            im = cv2.resize(im,None,fx=2,fy=2)
            cv2.imshow("Perlin grey", im)
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                break
            zoom *= 1.1
            inc += 1 
    elif 1:
        w = 320
        h = 240
        # time comparison
        for i in range(10):
            generateImageSimplex(w,h) # ms tab4: 6.5s (3.5s using cached data)
            #~ generateImagePerlin(w,h)# ms tab4: 208s
        
        
    print( "duration: %5.2fs" % (time.time()-timeBegin) )

    
    
            
if __name__ == "__main__":
    #~ exploreMethod()
    animateLandscape()