"""
some classic handy classes
(c) 2010-2022 A. Mazel
"""    

import math
import numpy as np
import random
import time

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

def getSimplexNoise(t,y=0):
    """
    return a nicely moving noise in [-1 /+1].
    - t: a running time or simulated one, same t return same value. called with passing second should give a nice result.
    - y: optionnal offset to give another type of value
    the sum of all noise tend to zero
    """
    # min and max seems to be limited from -0.864 to 0.864
    maxval = 0.865
    import opensimplex # pip install opensimplex
    #~ gen = opensimplex.OpenSimplex(sizegrid=sizegrid)
    global global_gen
    if global_gen == None: global_gen = opensimplex.OpenSimplex()
    gen = global_gen
    v = gen.noise2d(x=t,y=y,bUseCache=False)
    #~ v = abs(v*255)
    v = v/maxval
    return v

def generateImageSimplex(w,h,rZoom=1,sizegrid=256,offsetx=0,offsety=0):
    """
    sizegrid: change in the library to get more details (but not concluant)
    nice with a zoom around 200
    """
    # min and max seems to be limited from -0.864 to 0.864
    maxval = 0.865
    import opensimplex # from electronoos
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
    # but need to generate for each zoom the good detail unlimitedly
    # 
    rZoom = 1.
    im1 = generateImageSimplex(w,h,rZoom=rZoom*64,offsetx=0,offsety=0)
    im2 = generateImageSimplex(w,h,rZoom=rZoom*16,offsetx=0,offsety=0)
    im3 = generateImageSimplex(w,h,rZoom=rZoom*4,offsetx=0,offsety=0)
    im4 = generateImageSimplex(w,h,rZoom=rZoom*1,offsetx=0,offsety=0)
    
    #~ im = im1*0.5 + im2*0.25 + im3*0.125 + im4 * 0.0625  # 1 + 2 + 4 + 8 = 15
    
    if 0:
        c1 = 0.5
        c2 = 0.25
        c3 = 0.125
        c4 = 0.09
    else:
        c1 = 0.4
        c2 = 0.3
        c3 = 0.2
        c4 = 0.1
    
    if 0:
        im = im1*c1
        im += im2*c2
        im += im3*c3
        im += im4*c4
    else:
        im = im1*c4
        im += im2*c3
        im += im3*c2
        im += im4*c1        

    im = im.astype(np.uint8)
    #~ print(im)
    return im
    
def animateLandscape():
    import cv2
    inc = 1
    zoom = 1
    while zoom < 1000:
        im = generateLandscape(480,300,zoom,offsetx=int(math.sin(inc)*10),offsety=int(math.sin(inc)*10))
        im = cv2.resize(im,None,fx=2,fy=2)
        cv2.imshow("OpenSimplex grey", im)
        key = cv2.waitKey(0)
        if key == ord('q') or key == 27:
            break
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

def testGetSimplexNoise():
    while(1):
        print("%5.2f" % getSimplexNoise(time.time()))
        time.sleep(0.5)
    
            
if __name__ == "__main__":
    #~ exploreMethod()
    #~ animateLandscape()
    # for robot animation, juste generate in 1D with a transition of movement from the value of the pixel
    testGetSimplexNoise()
    