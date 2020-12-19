import numpy as np
import cv2
from matplotlib import pyplot as plt

def concatenateImages(listImages):
    """
    take n filenames and concatenate all images in one big image
    """
    ims = []
    sumW = 0
    maxH = 0
    for f in listImages:
        im = cv2.imread(f,cv2.IMREAD_GRAYSCALE)
        ims.append(im)
        h,w = im.shape
        sumW += w
        if h > maxH:
            maxH = h
        
        
    ret = np.zeros((maxH,sumW),np.uint8)
    
    x = 0
    for im in ims:
        h,w = im.shape
        ret[0:h,x:x+w]=im
        x += w
        
    return ret
        
        
        
    

#~ cv2.ocl.setUseOpenCL(False) # prevent a crash in orb.detect (not working for me) # OpenCL should not be used when using non-UMat args.

#~ img = cv2.imread(,0)

listImgs = ['decor1.jpg','decor2.jpg','decor3.jpg']
img = concatenateImages(listImgs)

#~ img=cv2.UMat(img)

#~ orb = cv2.ORB() #gener
orb = cv2.ORB_create(nfeatures=1000)

# find the keypoints with ORB
cv2.ocl.setUseOpenCL(False) # prevent a crash in orb.detect (not working for me)
kp = orb.detect(img,None)

# compute the descriptors with ORB

kp, desc = orb.compute(img, kp)

print("kp len: %s" % len(kp) )
print("desc len: %s" % len(desc) )

# draw only keypoints location,not size and orientation
img2=img.copy()
img2 = cv2.drawKeypoints(img,kp,img2,color=(0,255,0), flags=0 ) #cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
#~ plt.imshow(img2),plt.show()

# link all keypoints using same descriptions
nCptMatch = 0
for i in range(len(kp)):
    rDistMin = float('inf')
    jMin = -1
    for j in range(len(kp)):
        if i == j:
            continue # no comparison with same
        #~ print(len(desc[i]))
        rDist = sum(desc[i]-desc[j])
        #~ print("rDist: %s" % rDist)
        if rDist < rDistMin:
            rDistMin = rDist
            jMin = j
    
    if rDistMin < 2000 or 1:
        print("min: %d => %d (%s),(%s), (%5.1f)" % (i, jMin, str(kp[i].pt), str(kp[jMin].pt), rDistMin) )
        cv2.line(img2,(int(kp[i].pt[0]),int(kp[i].pt[1])), (int(kp[jMin].pt[0]),int(kp[jMin].pt[1])),(255,0,0),2)
        nCptMatch += 1
print("nCptMatch: %d" % nCptMatch)
    
    


img2 = cv2.resize(img2,None,fx=0.15,fy=0.15)
cv2.imshow("orb",img2)
cv2.waitKey(0)