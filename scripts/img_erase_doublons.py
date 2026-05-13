import cv2
import math
import numpy as np
import os

def computeImageDifference( im1, im2 ):
    """
    return difference between two images expressed in a [0..1] coefficient
    """
    err = np.sum( ( im1.astype("uint16") - im2.astype("uint16") ) ** 2 ) # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s
    #~ print("err1:%s"%err)
    err /= float(im1.shape[0] * im1.shape[1])
    err=math.sqrt(err)/512.
    #~ print("err2:%s"%err)
    return err
    
def test():
    # weird: those 2 images are quite different (people at first plane is moving)
    # but the diff is quite identical <0.009
    # is it because it's the same object that moved and nothing else change?
    strPath = "c:/img_tech_and_fest/"
    im1 = cv2.imread(strPath+"2024_02_01-11h41m59s390212ms.jpg")
    im2 = cv2.imread(strPath+"2024_02_01-11h41m59s621931ms.jpg")
    print(computeImageDifference(im1,im2))
    print(computeImageDifference(im2,im1))
    
test()
exit(0)
    
def erase_doublons(strPath):
    """
    interesting: more images are detected same than in human_detection, 
    is it because the jpg compress datas and so, the images are sllightly change and become closer ?
    but we find difference as small as 0.016 on a recording threshold of > 0.03 and even once 0.009 !
    """
    bReallyErase = 0
    #~ bReallyErase = 1 # comment this line for testing purpose
    
    bFindDoublonsEveryWhere = 1 # find two identical image even not following
    
    if bFindDoublonsEveryWhere:
        import sys
        sys.path.append("../alex_pytools/")
        import image_tools
    
    listFile = sorted(os.listdir(strPath))
    imPrev = cv2.imread(strPath+listFile[0])
    nNbrErased = 0
    threshold = 0.01 # very fine difference
    threshold = 0.03 # someone move in the background, or face in the foreground move slightly
    
    dHash = {} # hash => filename
    for f in listFile[1:]:
        im = cv2.imread(strPath+f)
        if im.shape == imPrev.shape:
            diff = computeImageDifference(imPrev, im)
            print("DBG: %s: diff: %.3f" % (f,diff) )
            if diff < threshold:
                print("=> erasing: %s" % f)
                if bReallyErase:
                    os.unlink(strPath+f)
                nNbrErased += 1
                continue
                
            if bFindDoublonsEveryWhere:
                hash = image_tools.computeImageHash(im)
                if not hash in dHash:
                    dHash[hash] = f
                else:
                    print("INF: DictHash: duplicated image from hash: %s and %s ?" % (dHash[hash],f))
                    imOther = cv2.imread(strPath+dHash[hash])
                    diff = computeImageDifference(imOther, im)
                    print("DBG: diff: %f" % diff)
                    if diff < threshold/2:
                        print("=> erasing uncontinuous: %s" % f)
                        if bReallyErase:
                            os.unlink(strPath+f)
                        nNbrErased += 1
                
        
        imPrev = im
    print("\nINF: erase_doublons: erased %d file(s) on %d" % (nNbrErased,len(listFile) ) )
    return nNbrErased
# erase_doublons - end
            
    
    
    
strPath = "/tmp_img/"
strPath = "/img_lyon/"
strPath = "/tmp_dup/"
erase_doublons(strPath)