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
import cv2_openpose
from cv2_openpose import Skeleton

#~ import sklearn 
from sklearn import  svm

def div2(pt):
    for i in range(len(pt)):
        pt[i] /= 2


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
    bb = sk.getBB()
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
                + Skeleton.getVector(avgHands,avgFeets,bb) \
                                

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
        print("diff on learn: %d/%d" % (sum(pred-classes),len(pred) ) ) #1/80
        # test
        pred = classifier.predict(listDeboutFTotal[len(listCoucheF):] )
        print("predicted: %s" % pred)
        print("diff on extra debout: %d/%d" % (len(pred)-sum(pred),len(pred)) ) # count zeroes # 2/114
        
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
        print("diff on test folder: %d/%d" % (sum(pred-classes),len(pred) ) ) #0/46
        
        
if __name__ == "__main__":
    learn()