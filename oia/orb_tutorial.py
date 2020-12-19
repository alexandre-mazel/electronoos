import numpy as np
import cv2
from matplotlib import pyplot as plt

# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html

def concatenateImages(listImages):
    """
    take n filenames and concatenate all images in one big image.
    return the big image and a list of all loaded images
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
        
    return ret, ims
        
        
        
    

#~ cv2.ocl.setUseOpenCL(False) # prevent a crash in orb.detect (not working for me) # OpenCL should not be used when using non-UMat args.

#~ img = cv2.imread(,0)

listImgs = ['decor1.jpg','decor2.jpg','decor3.jpg']
imgTotal, imgs = concatenateImages(listImgs)

#~ img=cv2.UMat(img)

#~ orb = cv2.ORB() #gener
orb = cv2.ORB_create(scoreType=cv2.ORB_HARRIS_SCORE,nfeatures=500)

kps = []
descs = []
for img in imgs:
    # find the keypoints with ORB
    kp = orb.detect(img,None)
    print("kp len: %s" % len(kp) )

    # compute the descriptors with ORB
    kp, desc = orb.compute(img, kp)

    print("kp len: %s" % len(kp) )
    print("desc len: %s" % len(desc) )
    
    kps.append(kp)
    descs.append(desc)

# link all keypoints from image 2 to 1 and to 3
    
if 0:
    # didactif a la main tutorial
    arSumDistTotal = []
    for idxmatch in [0,2]:
        rSumDist = 0
        nCptMatch = 0
        nOffsetOrigin = imgs[0].shape[1]
        nOffsetOther = 0
        if idxmatch == 2:
            nOffsetOther = nOffsetOrigin + imgs[1].shape[1]
        for i in range(len(kp)):
            rDistMin = float('inf')
            jMin = -1
            for j in range(len(kp)):
                rDist = sum(descs[1][i]-descs[idxmatch][j])
                if rDist < rDistMin:
                    rDistMin = rDist
                    jMin = j
            
            if rDistMin < 2000:
                #~ print("min: %d => %d (%s),(%s), (%5.1f)" % (i, jMin, str(kp[i].pt), str(kp[jMin].pt), rDistMin) )
                cv2.line(imgTotal,(int(kps[1][i].pt[0])+nOffsetOrigin,int(kps[1][i].pt[1])), (int(kps[idxmatch][jMin].pt[0])+nOffsetOther,int(kps[idxmatch][jMin].pt[1])),(255,0,0),2)
                nCptMatch += 1
            rSumDist += rDistMin
        arSumDistTotal.append(rSumDist)
        print("nCptMatch: %d, rSumDist: %5.2f" % (nCptMatch,rSumDist))
else:
    #~ kps[1] = kps[1][:10]
    #~ descs[1] = descs[1][:10]
    # Create a Brute Force Matcher object.
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
    for idxmatch in [0,2]:        
        
        nOffsetOrigin = imgs[0].shape[1]
        nOffsetOther = 0
        if idxmatch == 2:
            nOffsetOther = nOffsetOrigin + imgs[1].shape[1]
            
        nCptMatch = 0
        rSumDist = 0
        rSumDistSmall = 0
        
        matches = bf.match(descs[1], descs[idxmatch])
        matches = sorted(matches, key = lambda x : x.distance)
        for match in matches:
            rDist = match.distance
            idx1 = match.queryIdx #queryIdx is the first of match and not the second !!!
            idx2 = match.trainIdx
            #~ print(rDist)
            if rDist < 60:
                #~ print("%d,%d" % (idx1,idx2))
                cv2.line(imgTotal,(int(kps[1][idx1].pt[0])+nOffsetOrigin,int(kps[1][idx1].pt[1])), (int(kps[idxmatch][idx2].pt[0])+nOffsetOther,int(kps[idxmatch][idx2].pt[1])),(255,0,0),max(1,int(60-rDist)))
                nCptMatch += 1
                rSumDistSmall += rDist
            rSumDist += rDist
        print("nCptMatch: %d, rSumDist: %5.2f, rSumDistSmall: %5.2d" % (nCptMatch,rSumDist,rSumDistSmall))
        
        # count the sum of the 20 smaller:
        matches = matches[:20]
        rSumDist = 0
        for match in matches:
            rSumDist += match.distance
        print("rSumDist: %f" % rSumDist)

    


imgTotal = cv2.resize(imgTotal,None,fx=0.15,fy=0.15)
cv2.imshow("orb match",imgTotal)
cv2.waitKey(0)