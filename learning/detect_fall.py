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


def learn():
    cv2_openpose.loadSkeletonsFromOneFolder(cv2_openpose.strPathDeboutCouche+"fish/couche/")
    
    
if __name__ == "__main__":
    learn()