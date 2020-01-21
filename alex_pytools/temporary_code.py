# in this file, let's put some source file to be put somewhere else.
# NB it will comitted so changes can be tracked even if the location of the code is temporary

import cv2
import numpy as np
import time

def mseFloat(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum( ((imageA.astype("float") - imageB.astype("float")) ** 2) )
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def computeFeatures(im):
    return [im.mean()]
    
def diffFeatures(v1,v2):
    return abs(v1[0]-v2[0])

def generateHeatMask( im ):
    """
    Take an image containing a face and generate the dlib heatmap (how each pixel will change the dlib face match result
    """
    featref = computeFeatures(im)
    h,w,nbp = im.shape
    print("w:%d,h:%d"%(w,h))
    heatMap = np.zeros((h,w,1), dtype=np.int8)
    black = [0,0,0]
    white = [255,255,255]
    rMaxDiff = 0
    for j in range(h):
        print("j:%d" % j )
        for i in range(w):
            #~ print("i:%d" % i )
            arDiff = []
            for color in [black,white]:
                #~ print("color:%s" % color)
                imt = np.copy(im)
                
                # quite same time on my tablet !!! 
                # (would have think the [] would be far fastest!)
                if 0:
                    cv2.circle(imt, (i,j), 1, color )
                else:
                    imt[j,i]=color
                if 0:
                    cv2.imshow("imt",imt)
                    cv2.waitKey(1)
                #~ feat = computeFeatures(imt)
                #~ rDiff = diffFeatures(featref,feat)
                rDiff = mseFloat(im,imt)
                arDiff.append(rDiff)
                #~ print(rDiff)
            rDiff = max(arDiff)
            if rDiff > rMaxDiff:
                rMaxDiff = rDiff
            heatMap[j,i] = rDiff*10
    print("rMaxDiff: %5.3f" % rMaxDiff )
    #~ print(dir(cv2))
    #~ heatMap = cv2.resize(heatMap,(w*2,h*2))
    cv2.namedWindow("heat",cv2.CV_WINDOW_AUTOSIZE|cv2.WINDOW_NORMAL)
    cv2.imshow("heat",heatMap)
    cv2.resizeWindow("heat",600,480)
    cv2.waitKey(0)
            
im = cv2.imread("/tmp/a.jpg")
# crop to face a bit more
timeBegin = time.time()
xl = 50
xr = 200
yt=30
yb = 150
im = im[yt:yb,xl:xr]
generateHeatMask(im)
print("duration: %5.2fs" % (time.time()-timeBegin))