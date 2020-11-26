# Encapsulation in a nett class of the opencv openpose pose estimation
# inspired from https://www.learnopencv.com/deep-learning-based-human-pose-estimation-using-opencv-cpp-python/
#

import cv2
import time
import numpy as np

class Skeleton:
    
    # internal ordering
    # "nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"
    NOSE = 0
    LEYE = 1
    REYE = 2
    LEAR = 3
    REAR = 4
    LSHOULDER= 5
    RSHOULDER= 6
    LELBOW = 7
    RELBOW = 8
    LWRIST = 9
    RWRIST = 10
    LHIP  = 11
    RHIP = 12
    LKNEE = 13
    RKNEE = 14
    LANKLE  = 15
    RANKLE = 16
    
    #~ Nose - 0, Neck - 1, Right Shoulder - 2, Right Elbow - 3, Right Wrist - 4,
#~ Left Shoulder - 5, Left Elbow - 6, Left Wrist - 7, Right Hip - 8,
#~ Right Knee - 9, Right Ankle - 10, Left Hip - 11, Left Knee - 12,
#~ LAnkle - 13, Right Eye - 14, Left Eye - 15, Right Ear - 16,
#~ Left Ear - 17, Background - 18
    
    POSE_PAIRS=[ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]] # COCO ORDERING
    
    def __init__( self ):
        self.listPoints = []
        
        
    def createFromCoco( self, cocoListPoints ):
        self.listPoints = cocoListPoints
        
    def save( self, filename, skel ):
        pass
        
    def load( self, filename ):   
        pass

    def render( self, im ):
        """
        """
        # Draw Skeleton
        print("render: pts: %s" % str(self.listPoints) )
        print("render: len: %s" % len(self.listPoints) )
        for pair in Skeleton.POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]
            #~ print(partA)
            #~ print(partB)

            if self.listPoints[partA] and self.listPoints[partB]:
                cv2.line(im, self.listPoints[partA], self.listPoints[partB], (0, 255, 255), 2)
                cv2.circle(im, self.listPoints[partA], 3, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)



class CVOpenPose:
    """
    op = CVOpenPose()
    ...
    im = imread()
    ...    
    skel = op.analyse(im)
    skel an ordered list of skeleton.
    cf analyse for output description
    """
    
    def __init__( self, strOptionnalModelPath = "../models/", strMode = "COCO" ):
        #~ strMode = "MPI"
        self.strModelPath = strOptionnalModelPath
        self.net = None
        self.strMode = strMode
        
        if strMode == "COCO":
            print("COCO")
            self.protoFile = "pose/coco/pose_deploy_linevec.prototxt"
            self.weightsFile = "pose/coco/pose_iter_440000.caffemodel"
            self.nPoints = 18
            self.PosePairs = [ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]]
        elif strMode == "MPI" :
            print("NDEV!")
            print("MPI")
            self.protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
            self.weightsFile = "pose/mpi/pose_iter_160000.caffemodel"
            self.nPoints = 15
            self.PosePairs = [[0,1], [1,2], [2,3], [3,4], [1,5], [5,6], [6,7], [1,14], [14,8], [8,9], [9,10], [14,11], [11,12], [12,13] ]            
        
    def _loadModels( self ):
        t = time.time()
        self.net = cv2.dnn.readNetFromCaffe(self.strModelPath + self.protoFile, self.strModelPath + self.weightsFile)
        if 0:
            print("INF: Using CPU device")
            self.net.setPreferableBackend(cv2.dnn.DNN_TARGET_CPU)
        else:
            print("INF: Using GPU device")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        print("INF: time taken by loading: {:.3f}".format(time.time() - t)) # biga-U18: 1.25

    def analyse( self, im ):
        if self.net == None:
            self._loadModels()
            
        print("Start")
        
        frameWidth = im.shape[1]
        frameHeight = im.shape[0]
        threshold = 0.1

        t = time.time()
        # input image dimensions for the network
        inWidth = 368
        inHeight = 368
        #~ inWidth //= 2
        #~ inHeight //= 2
        inpBlob = cv2.dnn.blobFromImage(im, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)
        self.net.setInput(inpBlob)        
        output = self.net.forward()
        print("INF: time taken by network: {:.3f}".format(time.time() - t)) # biga-U18: gpu: 0.40first, 0.11 next -- cpu: 5.5s ----MsTab4: 6.5s
        print("output: %s" % str(output) )
        print("output len: %s" % len(output) )
        print("output shape: %s" % str(output.shape) )
        
        skel = Skeleton()

        H = output.shape[2]
        W = output.shape[3]
        
        nPoints = 18        
        
        if 1:
            # render proba
            i = 0
            probMap = output[0, i, :, :]            
            for i in range(1,nPoints):
                probMap += output[0, i, :, :]
            probMap = cv2.resize(probMap, (frameWidth, frameHeight))
            cv2.imshow("prob_nose", probMap)

        # Empty list to store the detected keypoints
        points = []

        for i in range(nPoints):
            # confidence map of corresponding body's part.
            probMap = output[0, i, :, :]

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
            
            # Scale the point to fit on the original image
            x = (frameWidth * point[0]) / W
            y = (frameHeight * point[1]) / H

            if prob > threshold: 
                cv2.circle(im, (int(x), int(y)), 3, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.putText(im, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
                cv2.putText(im, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)

                # Add the point to the list if the probability is greater than the threshold
                points.append((int(x), int(y)))
            else :
                points.append(None)
                
        skel.createFromCoco(points)
            
        return skel
        
    # analyse - end



# class CVOpenPose - end




if __name__ == "__main__":
    image_file = "../data/alexandre.jpg"
    image_file = "../data/multiple_humans.jpg"
    
    im = cv2.imread(image_file)
    op = CVOpenPose()
    skel = op.analyse(im)
    skel = op.analyse(im)
    skel.render(im)
    
    zoom=1
    im = cv2.resize(im,None,fx=zoom,fy=zoom)
    cv2.imshow('Output-Skeleton', im)    
    
    cv2.waitKey(0)