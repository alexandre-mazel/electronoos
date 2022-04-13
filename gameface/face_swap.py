# -*- coding: cp1252 -*-

import cv2
import math
import os
import sys
import time

sys.path.append("../../electronoos/alex_pytools")
#~ import face_detector_cv3
import cv2_tools

sys.path.append("../../face_tools")
import facerecognition_dlib

def multiplyList(a,k):
    """
    multiply all element and subelement of a by k
    """
    if not isinstance(a,list):
        return a*k
        
    out = []
    for e in a:
        out.append(multiplyList(e,k))
    return out
    
def addToList(a,c):
    """
    add a constant c to all element and subelement of a
    """
    if not isinstance(a,list):
        return a+c
        
    out = []
    for e in a:
        out.append(addToList(e,c))
    return out

def analyseFolder(folder):
    """
    analyse a folder with a bunch of images
    """
    bSpeedTest = 1
    bSpeedTest = 0
    
    
    bRenderDebug = 1
    bRenderDebug = 0
    
    fdl = facerecognition_dlib.faceRecogniser
    
    
    
    timeBegin = time.time()
    
    listFiles = sorted(os.listdir(folder))
    
    bRender = 0
    
    idx_end = 0
    
    
    idx = 0
    
    while idx<len(listFiles):
        f = listFiles[idx]
        print("%4d/%4d: %s" % (idx,len(listFiles),f) )
        if not "jpg" in f:
            idx += 1
            continue
        absf = folder + f
        if 1:
            im = cv2.imread(absf)
        else:
            # when everything is precomputed
            im = None
        
        rConfidence, features, faceshape,facelandmark = fdl.extractFeaturesFromImg( im, absf, bForceRecompute = 0 )

        if bRender:
            cv2.imshow("FaceTracker",im)
            key=cv2.waitKey(5) # time for image to refresh even if continuously pressing a key
            #~ key=cv2.waitKey(0)
            if key == 27:
                break

        idx += 1
        
        if (idx %100) == 0:
            facerecognition_dlib.storedFeatures.save()

                
        if idx_end != 0 and idx>idx_end:
            break

    
    facerecognition_dlib.storedFeatures.save()
# analyseFolder - end

def getDiffFacePosture( s1,l1,s2,l2,bRemoveContour=0):
    """
    return diff of comparison of both faceshape, facelandmark for two faces
    """
    #~ print("DBG: getDiffFacePosture s1: %s" % str(s1))
    #~ print("DBG: getDiffFacePosture s2: %s" % str(s2))
    #~ print("DBG: getDiffFacePosture l1: %s" % str(l1))
    #~ print("DBG: getDiffFacePosture l2: %s" % str(l2))
    # project l2 in l1 space:
    offset_x = s2[0]-s1[0]
    offset_y = s2[0]-s1[0]
    rx = (s1[2]-s1[0]) / (s2[2]-s2[0])  # ratio_x
    ry = (s1[3]-s1[1]) / (s2[3]-s2[1])
    
    if bRemoveContour:
        l1 = l1[17:]
        l2 = l2[17:]

    
    rSumDiff = 0
    # first facelandmark element is faceshape !
    for i in range(1,len(l1)):
        p1 = l1[i]
        p2 = l2[i][:] # copy
        
        p2[0] = s1[0] + (p2[0]-s2[0])*rx
        p2[1] = s1[1] + (p2[1]-s2[1])*ry

        
        
        dist = math.sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))
        rSumDiff += dist
    #~ print("DBG: getDiffFacePosture: rSumDiff: %.3f" % rSumDiff )
        
    return rSumDiff

def faceSwap(folder1,folder2,folder3 = None):
    """
    for each face in folder1, find one in f2 (or f3) with the same angle and expressivity, then paste it
    """
    listFiles = sorted(os.listdir(folder1))
    listFiles2 = sorted(os.listdir(folder2))
    if folder3 != None:
        # ne marche pas car il faut alors aussi changer absf3
        listFiles3 = sorted(os.listdir(folder3))
        listFiles2.extend(listFiles3)
    
    idx = 100
    #~ idx = 900
    
    fdl = facerecognition_dlib.faceRecogniser
    
    while idx<len(listFiles):
        f = listFiles[idx]
        print("%4d/%4d: %s" % (idx,len(listFiles),f) )
        if not "jpg" in f:
            idx += 1
            continue
        absf = folder1 + f
        rConfidence, features, faceshape,facelandmark = fdl.extractFeaturesFromImg( None, absf )
        if faceshape == []:
            idx += 1
            continue
                
        rDiffMin = 99999999999
        fMin = ""
        numMin = -1
        for numf2,f2 in enumerate(listFiles2):
            #~ if numf2 % 100 == 0: print("%d/%d/%d" % (idx,numf2,len(listFiles2)))
            absf2 = folder2 + f2
            rConfidence2, features2, faceshape2,facelandmark2 = fdl.extractFeaturesFromImg( None, absf2, bVerbose = False )
            if faceshape2 == []:
                continue
            if 0:
                # test to check diff is 0
                faceshape2 = multiplyList(faceshape,2)
                faceshape2 = addToList(faceshape2,100)
                facelandmark2 = multiplyList(facelandmark,2)
                facelandmark2 = addToList(facelandmark2,100)
            rDiff = getDiffFacePosture(faceshape,facelandmark,faceshape2,facelandmark2)
            if rDiff < rDiffMin:
                fMin = f2
                rDiffMin = rDiff
                numMin = numf2
        
        print("rDiffMin: %.3f" % rDiffMin)
        im = cv2.imread(absf)
        absf2 = folder2+fMin
        im2 = cv2.imread(absf2)
        rConfidence2, features2, faceshape2,facelandmark2 = fdl.extractFeaturesFromImg( None, absf2 )
        
        im = fdl._renderFaceInfo(im,facelandmark,nAddOffset=120)
        im2 = fdl._renderFaceInfo(im2,facelandmark2,nAddOffset=-120)
        cv2.putText(im,str(idx),(640-60,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
        cv2.putText(im2,str(numMin),(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
        
        cv2.imshow("1",im)
        cv2.imshow("2",im2)
        key = cv2.waitKey(10)
        if key != 27:
            key = cv2.waitKey(0)
        if key == 27:
            break
                
        idx += 1
            
if os.name == "nt":
    if 0:
        strPath = "d:/face_swap_test/f6/"
        analyseFolder(strPath)
        exit(0)

    folder1 = "d:/face_swap_test/f1/"
    folder2 = "d:/face_swap_test/f2/"
    folder3 = "d:/face_swap_test/f1/"
    folder3 = None
    
    folder1 = "d:/face_swap_test/f3/"
    folder2 = "d:/face_swap_test/f4/"
    faceSwap(folder1,folder2,folder3)