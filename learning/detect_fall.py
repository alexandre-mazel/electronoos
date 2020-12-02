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



def skelToFeatures(sk):
    lil = sk.getLegs()
    bb = sk.getBB()
    sto = sk.getStomach()
    rh,rk,ra = lil[0]
    lh,lk,la = lil[1]
    
    return [
                                    Skeleton.getVector(sto,rh,bb),
                                    Skeleton.getVector(sto,lh,bb),
                                    Skeleton.getVector(rh,rk,bb),
                                    Skeleton.getVector(rk,ra,bb),
                                    Skeleton.getVector(lh,lk,bb),
                                    Skeleton.getVector(lk,la,bb),
                                ]
    
def learn():
    nFilterNbrPoint = 7
    listCouche = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/couche/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: couche %d skels" % len(listCouche) )
    listDebout = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/debout/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: debout %d skels" % len(listDebout) )
    
    listCouche  = listCouche[:4]
    
    listDebout = listDebout[:len(listCouche)]
    print("INF: debout reduced %d skels" % len(listDebout) )
    
    # transform to skeleton to features based on vector joint orientations

    for i in range(len(listCouche)):
        sk = listCouche[i]
        listCouche[i] = skelToFeatures(sk)
        
    for i in range(len(listDebout)):
        sk = listDebout[i]
        listDebout[i] = skelToFeatures(sk)
        
    features = listCouche + listDebout
    
    print("INF: features: %s" % len(features) )
    print(features)
    
    

    
    # create classes
    classes = [0]*len(listCouche) + [1]*len(listDebout) 
    
    print("INF: classes: %d" % len(classes) )
    print(classes)
    
    classifier = svm.SVC(gamma=0.001)
    classifier.fit(features, classes)
    
if __name__ == "__main__":
    learn()