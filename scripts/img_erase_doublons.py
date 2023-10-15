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
    
def erase_doublons(strPath):
    listFile = sorted(os.listdir(strPath))
    imPrev = cv2.imread(strPath+listFile[0])
    nNbrErased = 0
    threshold = 0.01 # very fine difference
    threshold = 0.03 # someone move in the background, or face in the foreground move slightly
    for f in listFile[1:]:
        im = cv2.imread(strPath+f)
        if im.shape == imPrev.shape:
            diff = computeImageDifference(imPrev, im)
            print("%s: diff: %.3f" % (f,diff) )
            if diff < threshold:
                print("=> erasing: %s" % f)
                os.unlink(strPath+f)
                nNbrErased += 1
                continue
        
        imPrev = im
    print("INF: erase_doublons: erased %d file(s) on %d" % (nNbrErased,len(listFile) ) )
    return nNbrErased
# erase_doublons - end
            
    
    
    
strPath = "/tmp_img/"
strPath = "/img_lyon/"
erase_doublons(strPath)