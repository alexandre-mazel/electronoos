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

#~ import sklearn 
from sklearn import  svm


def learn():
    nFilterNbrPoint = 7
    listCouche = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/couche/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: couche %d skels" % len(listCouche) )
    listDebout = cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/debout/",nFilterNbrPoint=nFilterNbrPoint)
    print("INF: debout %d skels" % len(listDebout) )
    
    listCouche  = listCouche[:4]
    
    listDebout = listDebout[:len(listCouche)]
    print("INF: debout reduced %d skels" % len(listDebout) )
    
    features = listCouche + listDebout
    
    print("INF: features: %s" % len(features) )
    print(features)

    
    classes = [0]*len(listCouche) + [1]*len(listDebout) 
    
    print("INF: classes: %d" % len(classes) )
    print(classes)
    
    classifier = svm.SVC(gamma=0.001)
    classifier.fit(features, classes)
    
if __name__ == "__main__":
    learn()