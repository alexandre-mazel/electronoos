#################
#
# On the ground detector
#
# Use sklearn to differenciate a skeleton of a standing human from a crouching/lying people
#
#
#############

import sys
sys.path.append("../alex_pytools/" )

import cv2

import cv2_openpose
from cv2_openpose import Skeleton

import sklearn 
from sklearn import  svm
import joblib
import os

import numpy as np

def div2(pt):
    for i in range(len(pt)):
        pt[i] /= 2

def avg2(pt1,pt2):
    assert( len(pt1) == len(pt2) )
    a = []
    for i in range(len(pt1)):
        a.append( (pt1[i]+pt2[i])/2 )
    return a
        
def isFullConf(triols, rThreshold = 0.2):
    """
    return True if all third values are > threshold
    """
    for i in range(2,len(triols),3):
        if triols[i] < rThreshold:
            return False
    return True


def skelToFeatures(sk):
    lil = sk.getLegs()
    bb = sk.getBB_Size()
    sto = sk.getStomach()
    rh,rk,ra = lil[0] # hip, knee, ankle
    lh,lk,la = lil[1]
    
    avgFeets = [ ra[0]+la[0],ra[1]+la[1],ra[2]+la[2] ]
    div2(avgFeets)
    
    lal = sk.getArms()
    rs,re,rw = lal[0] #shoulder, elbow, wrist
    ls,le,lw = lal[1]
    
    avgHands = [ rw[0]+lw[0],rw[1]+lw[1],rw[2]+lw[2] ]
    div2(avgHands)
    
    return  Skeleton.getVector(sto,rh,bb) \
                + Skeleton.getVector(sto,lh,bb) \
                + Skeleton.getVector(rh,rk,bb) \
                + Skeleton.getVector(rk,ra,bb) \
                + Skeleton.getVector(lh,lk,bb) \
                + Skeleton.getVector(lk,la,bb) \
                #~ + Skeleton.getVector(avgHands,avgFeets,bb) \
                
               
def isDeboutHandCoded( sk ):                
    """
    use a hand coded rules
    """
    bVerbose = 0
    lil = sk.getLegs()
    if bVerbose: print("legs: %s" % str(lil))
    
    bb = sk.getBB_Size()
    sto = sk.getStomach()
    

    
    rh,rk,ra = lil[0] # hip, knee, ankle
    lh,lk,la = lil[1]
    
    avgFeets = [ ra[0]+la[0],ra[1]+la[1],ra[2]+la[2] ]
    div2(avgFeets)
    
    lal = sk.getArms()
    if bVerbose: print("arms: %s" % str(lal))
    rs,re,rw = lal[0] #shoulder, elbow, wrist
    ls,le,lw = lal[1]
    
    rThreshold = 0.2
    
    #~ # si les pieds sont plus bas que les hanches
    
    # si les mains ou a defaut les coudes sont plus hautes que les pieds ou a defaut les hanches
    if rw[2] > rThreshold:
        rHi = rw[:2]
    elif re[2] > rThreshold:
        rHi = re[:2]
    else:
        rHi = None

    if lw[2] > rThreshold:
        lHi = lw[:2]
    elif le[2] > rThreshold:
        lHi = le[:2]
    else:
        # check le neck
        neck = sk.listPoints[Skeleton.getNeckIndex()]
        if neck[2] > rThreshold:
            lHi = neck[:2]
        else:
            lHi = None
        
    if lHi == None and rHi == None:
        return None
        
    if lHi == None:
        hi = rHi
    elif rHi == None:
        hi = lHi
    else:
        hi = avg2(rHi,lHi)
        
        
        
    if ra[2] > rThreshold:
        rLo = ra[:2]
    elif rk[2] > rThreshold:
        rLo = rk[:2]
    else:
        rLo = None

    if la[2] > rThreshold:
        lLo = la[:2]
    elif lk[2] > rThreshold:
        lLo = lk[:2]
    else:
        lLo = None
        
    if lLo == None and rLo == None:
        return None
        
    if lLo == None:
        lo = rLo
    elif rLo == None:
        lo = lLo
    else:
        lo = avg2(rLo,lLo)
        
    if bVerbose: print("rLo:%s,lLo:%s" % (rLo,lLo) )
        
    if bVerbose: print("hi:%s,lo:%s" % (hi,lo) )
    
    #~ return hi[1]<lo[1] # add a margin ?
    
    bb = sk.getBB_Size()
    rMargin = bb[1]/4
    
    if bVerbose: print("rMargin:%5.2f"%rMargin)
    
    if hi[1]+rMargin<lo[1]: # WRN:  pixel Y are inverted (high pixel are smaller than lower)
        return 1
    return 0
        
        
    
        
        
    
def predictHandCoded( listSkel ):
    ret = []
    for sk in listSkel:
        ret.append(isDeboutHandCoded(sk))
    return np.array(ret)
                                

def learn():
    nFilterNbrPoint = 7
    listCouche = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/learn/couche/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: couche %d skels" % len(listCouche) )
    listDebout = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/learn/debout/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: debout %d skels" % len(listDebout) )
    
    #~ listCouche  = listCouche[:5]
    
    listDebout = listDebout[:len(listCouche)]
    print("INF: debout reduced to %d skels" % len(listDebout) )
    
    # transform to skeleton to features based on vector joint orientations

    listCoucheF = []
    for sk in listCouche:
        feat = skelToFeatures(sk)
        if isFullConf(feat):
            listCoucheF.append(feat)
        
    listDeboutFTotal = []
    for sk in listDebout:
        feat = skelToFeatures(sk)
        if isFullConf(feat):
            listDeboutFTotal.append(feat)

    
    #~ print("INF: couche: %s" % str(listCouche) )

    listDeboutF = listDeboutFTotal[:len(listCoucheF)]    
    print("INF: debout reduced to %d skels" % len(listDeboutF) )

        
    features = listCoucheF + listDeboutF
    
    print("INF: features repart: %s/%s/%s" % (len(listCoucheF),len(listDeboutF),len(features)) )
    print(features)
    
    # create classes
    classes = [0]*len(listCoucheF) + [1]*len(listDeboutF) 
    
    print("INF: classes: %d" % len(classes) )
    print(classes)
    
    classifier = svm.SVC()
    classifier.fit(features, classes)
    
    if 1:
        # test
        pred = classifier.predict(features)
        print("predicted: %s" % pred)
        print("diff on learn: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) #1/80
        # test
        pred = classifier.predict(listDeboutFTotal[len(listCoucheF):] )
        print("predicted: %s" % pred)
        print("diff on extra debout: %d/%d" % (len(pred)-sum(pred),len(pred)) ) # count zeroes # 2/114
        
        if 1:
            # hand coded test
            pred = predictHandCoded(listCouche+listDebout)
            classes = [0]*len(listCouche) + [1]*len(listDebout) 
            print("predicted: %s" % pred)
            
            # remove None case
            pred = pred.tolist()
            i = 0
            while i < len(pred):
                if pred[i] == None:
                    del pred[i]
                    del classes[i]
                else:
                    i += 1
            pred = np.array(pred)
            
            print("diff on learn folder hand coded: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) # 37/372 # 54/402 sans margin, 45/402
        
        
        # test on test folder
        listCouche = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/test/couche/",nFilterNbrPoint=nFilterNbrPoint)
        print("INF: couche %d skels" % len(listCouche) )
        listDebout = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/test/debout/",nFilterNbrPoint=nFilterNbrPoint)
        print("INF: debout %d skels" % len(listDebout) )
        listCoucheF = []
        for sk in listCouche:
            feat = skelToFeatures(sk)
            if isFullConf(feat):
                listCoucheF.append(feat)
            
        listDeboutF = []
        for sk in listDebout:
            feat = skelToFeatures(sk)
            if isFullConf(feat):
                listDeboutF.append(feat)
                
        features = listCoucheF + listDeboutF
        
        print("INF: features repart: %s/%s/%s" % (len(listCoucheF),len(listDeboutF),len(features)) )
        print(features)
        
        # create classes
        classes = [0]*len(listCoucheF) + [1]*len(listDeboutF) 
        pred = classifier.predict(features)
        print("predicted: %s" % pred)
        print("diff on test folder: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) #17/274
        
        # hand coded test
        pred = predictHandCoded(listCouche+listDebout)
        classes = [0]*len(listCouche) + [1]*len(listDebout) 
        print("predicted: %s" % pred)
        
        # remove None case
        pred = pred.tolist()
        i = 0
        while i < len(pred):
            if pred[i] == None:
                del pred[i]
                del classes[i]
            else:
                i += 1
        pred = np.array(pred)
        
        print("diff on test folder hand coded: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) # 37/372 # 54/402 sans margin, 45/402
        
    #~ from sklearn.externals import joblib        
    joblib.dump(classifier, 'detect_fall_classifier.pkl')

# learn - end

def analyseFilenameInPath( strPath ):
    op = cv2_openpose.CVOpenPose()
    clf = joblib.load('detect_fall_classifier.pkl')
    #~ skel = op.analyseFromFile(strImageFilename)
    listFile = sorted(  os.listdir(strPath) )
    i = 0
    while i < len(listFile):
        f = listFile[i]
        tf = strPath + f
        if os.path.isdir(tf):
            analyseFilenameInPath(tf + os.sep)
            continue
        filename, file_extension = os.path.splitext(f)
        if ".png" in file_extension.lower() or ".jpg" in file_extension.lower(): 
            skels = op.analyseFromFile(tf)
            im = cv2.imread(tf)
            for skel in skels:
                feat = skelToFeatures(skel)
                if isFullConf(feat):
                    pred = clf.predict([feat])[0]
                    if pred==0:
                        txt = "Fall"
                    else:
                        txt = "Stand"
                else:
                    txt = "?"
                    
                if 1:
                    txt += " / "
                ret = isDeboutHandCoded(skel)
                if ret == 0:
                    txt += "Fall"
                elif ret == 1:
                    txt += "Stand"
                else:
                    txt += "?"
                
                print(txt)
                bb = skel.getBB()
                cv2.putText(im, txt, ( (bb[0]+bb[2]-20) // 2,bb[3]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2 )
                cv2.putText(im, txt, ( (bb[0]+bb[2]-20) // 2,bb[3]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1 )
            skels.render(im)
            cv2.imshow("detected",im)
            key = cv2.waitKey(0)
            print(key)
            if key == ord('q') or key == 27:
                break
            if key == ord('p'):
                i -= 5 # skip also some prev not images like skel... - crappy!
                if i < 0:
                    i = -1
                
        i += 1
    # while - end
        
#analyseFilenameInPath  - end

if __name__ == "__main__":
    learn()
    #~ analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/test/debout/")
    analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/test/couche/")
    