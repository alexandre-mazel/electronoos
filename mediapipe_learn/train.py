import math
import os
import cv2

from sklearn import svm # pip install scikit-learn
import numpy as np
import pickle

from mediapipe_fx import computeBaryChest, landmarkToListPoints, computeSizeChest, vectNorm3D, anIdxWrists,sum3D,div3D

def myLandmarksDrawPt3D( img, skel ):
    img2 = img.copy()
    h,w = img.shape[:2]
    if 1:
        # draw line:
        pairPts = [(11,12),(11,13),(13,15),(12,14),(14,16),(12,24),(11,23)]
        for p1,p2 in pairPts:
            ptint1 = ( int(skel[p1][0]*w),int(skel[p1][1]*h))
            ptint2 = ( int(skel[p2][0]*w),int(skel[p2][1]*h))
            cv2.line(img2,ptint1,ptint2, (255,0,0),2)
            
    for num,pt in enumerate(skel):
        ptint = ( int(pt[0]*w),int(pt[1]*h))
        cv2.circle( img2,ptint, 3, (255,0,0))
        cv2.putText( img2, "%d"%num, ptint,  fontFace = cv2.FONT_HERSHEY_DUPLEX, fontScale = 1.0,color = (255,255,0), thickness = 1 )
    return img2

def computeFeaturesFromFile(strFilename, bDetect = False):
    """
    return a list of list of features
    """
    print("\nINF: loadFile '%s'" % strFilename )
    if bDetect: classifier = pickle.load(open("trained_clf_pickle.dat", 'rb'))
    
    f = open(strFilename,"rt")
    allImages = []
    nSizeAnalyse = 120
    listOfFeatures = []
    
    img = np.zeros((480,640,3))
    strLastAction = "???"
    while 1:
        buf = f.readline()
        if(len(buf)<2): break
        #print(buf)
        dataForOneImage = eval(buf)
        #print(dataForOneImage)
        #print(dataForOneImage[0])
        
        if bDetect:
            img[:] = (0,0,0)
            img = myLandmarksDrawPt3D(img,dataForOneImage)
            cv2.putText(
                  img, text = strLastAction, org = (20, 40), 
                  fontFace = cv2.FONT_HERSHEY_DUPLEX,
                  fontScale = 1.0, color = (255, 0, 0), thickness = 2
                )
            cv2.imshow( 'detected', img )
            key = cv2.waitKey(33/3) # real time is 33.3 (30 fps)
            if key == 27:
                break
        
        allImages.append(dataForOneImage)
        if len(allImages)==nSizeAnalyse:
            print("got %s images, computing..." % (len(allImages)))
            avgHandL = [0,0,0]
            avgHandR = [0,0,0]
            for i in range(nSizeAnalyse):
                bary = computeBaryChest(allImages[i])
                size = computeSizeChest(allImages[i])
                #~ print("bary: %s, size: %s" % (bary,size) )
                vHandL = vectNorm3D(allImages[i][anIdxWrists[0]],bary,size)
                vHandR = vectNorm3D(allImages[i][anIdxWrists[1]],bary,size)
                avgHandL = sum3D( avgHandL, vHandL )
                avgHandR = sum3D( avgHandR, vHandR )
            avgHandL = div3D( avgHandL, nSizeAnalyse )
            avgHandR = div3D( avgHandR, nSizeAnalyse )
            print("avgHandL: %s" % avgHandL )
            print("avgHandR: %s" % avgHandR )
            feats = []
            feats.extend(avgHandL)
            feats.extend(avgHandR)
            listOfFeatures.append(feats)
            if bDetect:
                predicted = classifier.predict([feats])
                detected_class = predicted[0]
                className = dictClassName[detected_class]
                print("detected: %s" % className )
                strLastAction = className
            allImages = []
    return listOfFeatures


def trainAll():
    # loop all folders
    aListClassName = []
    allFeatures = []
    allClasseRef = []
    for parentFolder in ["C:/seq_vid2/","D:/seq_vid/"]:
        for folder in os.listdir(parentFolder):
            if not os.path.isdir(parentFolder+folder):
                continue
                
            for f in os.listdir(parentFolder+folder):
                if not ".skl" in f:
                    continue
                listOfFeatures = computeFeaturesFromFile(parentFolder+folder+"/"+f)
                allFeatures.extend(listOfFeatures)
                for i in range(len(listOfFeatures)):
                    allClasseRef.append(len(aListClassName))
                    
            aListClassName.append(folder)
    
    print("allFeatures: %s" % allFeatures )            
    print("allClasseRef: %s" % allClasseRef )
    for nNumClass,strClassName in enumerate(aListClassName):
        print("numclass: %d: class: %s" % (nNumClass,strClassName) )
        
    classifier = svm.SVC()
    classifier.fit(allFeatures, allClasseRef)
    # Saving classifier using pickle 
    pickle.dump(classifier, open("trained_clf_pickle.dat", 'wb')) 
    
dictClassName = {
    0: "phone",
    1: "sms",
    2: "sleep",
    3: "eat",
    4: "fight",
    5: "stretch",
}
        
def detect():
    # load classifier using pickle 
    classifier = pickle.load(open("trained_clf_pickle.dat", 'rb'))
    file = "C:/seq_vid2/sms/sms_01.skl"
    file = "D:/seq_vid/eat/eat_01.skl"
    file = "D:/seq_vid/stretch/stretch_04.skl"
    file = "c:/seq_vid2/test.skl"
    listOfFeatures = computeFeaturesFromFile(file,bDetect=1)
    for f in listOfFeatures:
        predicted = classifier.predict([f])
        print(predicted)
        for pred in predicted:
            print("predicted: %s" % pred )
    
    
    
    
def test():
    strPath = "C:/seq_vid2/sms/"
    strPathD = "D:/seq_vid/eat/"
    strFile = strPath + "sms_01.skl"
    loadFile(strFile)
    strFile = strPath + "sms_02.skl"
    loadFile(strFile)

    strFile = strPathD + "eat_01.skl"
    computeFeaturesFromFile(strFile)
    
#~ trainAll()
detect()