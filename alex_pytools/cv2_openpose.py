# Encapsulation in a nett class of the opencv openpose pose estimation
# inspired from https://www.learnopencv.com/deep-learning-based-human-pose-estimation-using-opencv-cpp-python/
#
# manual library link:
# on my biga: 
# export PYTHONPATH=/usr/local/lib/python3.6/dist-packages/cv2/python-3.6:$PYTHONPATH
# on champion:
# export PYTHONPATH=/usr/local/lib/python3.8/site-packages/cv2/python-3.8/:$PYTHONPATH


import cv2
import math
import os
import time
import numpy as np

import cv2_openpose_pairing

def lenPts(pt1,pt2):
    return math.sqrt( (pt1[0]-pt2[0])*(pt1[0]-pt2[0]) + (pt1[1]-pt2[1])*(pt1[1]-pt2[1]) )


class Skeleton:
    
    # internal ordering
    # "nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"
    #~ NOSE = 0
    #~ LEYE = 1
    #~ REYE = 2
    #~ LEAR = 3
    #~ REAR = 4
    #~ LSHOULDER= 5
    #~ RSHOULDER= 6
    #~ LELBOW = 7
    #~ RELBOW = 8
    #~ LWRIST = 9
    #~ RWRIST = 10
    #~ LHIP  = 11
    #~ RHIP = 12
    #~ LKNEE = 13
    #~ RKNEE = 14
    #~ LANKLE  = 15
    #~ RANKLE = 16
    
    #~ Nose - 0, Neck - 1, Right Shoulder - 2, Right Elbow - 3, Right Wrist - 4,
#~ Left Shoulder - 5, Left Elbow - 6, Left Wrist - 7, Right Hip - 8,
#~ Right Knee - 9, Right Ankle - 10, Left Hip - 11, Left Knee - 12,
#~ LAnkle - 13, Right Eye - 14, Left Eye - 15, Right Ear - 16,
#~ Left Ear - 17, Background - 18

    NOSE = 0
    NECK = 1
    RSHOULDER=2
    RELBOW=3
    RWRIST=4
    LSHOULDER=5
    LELBOW=6
    LWRIST=7
    RHIP=8
    RKNEE=9
    RANKLE=10
    LHIP=11
    LKNEE=12
    LANKLE=13
    REYE=14
    LEYE=15
    REAR=16
    LEAR=17
    NBR_POINTS=18
    
#~ Neck - 1, Right Shoulder - 2, Right Elbow - 3, Right Wrist - 4,
#~ Left Shoulder - 5, Left Elbow - 6, Left Wrist - 7, Right Hip - 8,
#~ Right Knee - 9, Right Ankle - 10, Left Hip - 11, Left Knee - 12,
#~ LAnkle - 13, Right Eye - 14, Left Eye - 15, Right Ear - 16,
#~ Left Ear - 17, Background - 18


        
    POSE_PAIRS=[ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]] # COCO ORDERING
    
    # all indexes are returned right then left
    
    def getLegsIndex():
        return [
                        [8,9,10],
                        [11,12,13],
                    ]
                    

    def getArmsIndex():
        return [
                        [2,3,4],
                        [5,6,7],
                    ]
                    
    def getWristsIndex():
        return [4,7]    

    def getAnklesIndex():
        return [10,13]
        
    def getNeckIndex():
        return 1

    def getNeckPos(self):
        return [self.listPoints[1][0],self.listPoints[1][1]]
        
    def getLegs(self):
        legs = Skeleton.getLegsIndex()
        
        return [
                        [self.listPoints[legs[0][0]],self.listPoints[legs[0][1]],self.listPoints[legs[0][2]] ],
                        [self.listPoints[legs[1][0]],self.listPoints[legs[1][1]],self.listPoints[legs[1][2]] ],
                    ]

    def getArms(self):
        arms = Skeleton.getArmsIndex()
        
        return [
                        [self.listPoints[arms[0][0]],self.listPoints[arms[0][1]],self.listPoints[arms[0][2]] ],
                        [self.listPoints[arms[1][0]],self.listPoints[arms[1][1]],self.listPoints[arms[1][2]] ],
                    ]
                    
    def getBB(self,rThreshold = 0.2):
        """
        get BB of all points in the skeleton
        """
        xmin = ymin = 9999999
        xmax = ymax= -1
        for pt in self.listPoints:
            if pt[2] > rThreshold:
                if pt[0] < xmin:
                    xmin = pt[0]
                if pt[0] > xmax:
                    xmax = pt[0]  
                if pt[1] < ymin:
                    ymin = pt[1]
                if pt[1] > ymax:
                    ymax = pt[1]

        return[xmin, ymin, xmax, ymax]
        
    def getBB_Size(self,rThreshold = 0.2):
        """
        get BB of all points in the skeleton
        """
        xmin, ymin, xmax, ymax = self.getBB(rThreshold=rThreshold)
        return[ max(xmax-xmin,1), max(ymax-ymin,1) ] # BB will be always > 0
        
    def getAvgLenLeg( self,rThreshold = 0.2 ):
        """
        return the average length of a complete leg
        """
        #~ todo si pas de chevilles prends la cuisse x 2 ou l'inverse, ou l'autre jambe...
        #~ se debrouille quoi !
        #~ a tester sur 86/1212
        
        legs = self.getLegs()
        lenlegs = []
        
        for i in range(2):
            if legs[i][0][2] > rThreshold and legs[i][1][2] > rThreshold and legs[i][2][2] > rThreshold:
                l = lenPts(legs[i][0],legs[i][1])+lenPts(legs[i][1],legs[i][2])
            elif legs[i][0][2] > rThreshold and legs[i][1][2] > rThreshold:
                l = lenPts(legs[i][0],legs[i][1]) * 2
            elif legs[i][1][2] > rThreshold and legs[i][2][2] > rThreshold:
                l = lenPts(legs[i][1],legs[i][2]) * 2
            else:
                l = None
            if l != None:
                lenlegs.append(l)
        if len(lenlegs) == 0:
            return None
        if len(lenlegs) == 1:
            return lenlegs[0]
        return (lenlegs[0]+lenlegs[1]) / 2
                
                
        
    def getLenLimbs(self,rThreshold = 0.2):
        """
        return len and min confidence of each limbs, arms then legs
        """
        legs = self.getLegs()
        arms = self.getLegs()
        rleg =  lenPts(legs[0][0],legs[0][1])+lenPts(legs[0][1],legs[0][2]), (legs[0][0][2] + legs[0][1][2] + legs[0][2][2]) /3
        lleg =  lenPts(legs[1][0],legs[1][1])+lenPts(legs[1][1],legs[1][2]), (legs[1][0][2] + legs[1][1][2] + legs[1][2][2]) /3

        rarm =  lenPts(arms[0][0],arms[0][1])+lenPts(arms[0][1],arms[0][2]), (arms[0][0][2] + arms[0][1][2] + arms[0][2][2]) /3
        larm =  lenPts(arms[1][0],arms[1][1])+lenPts(arms[1][1],arms[1][2]), (arms[1][0][2] + arms[1][1][2] + arms[1][2][2]) /3
        
        return rleg, lleg, rarm, larm
        
    def getStomach(self):
        """
        return approximation of stomach point
        """
        neck = self.listPoints[Skeleton.getNeckIndex()]
        hips = Skeleton.getLegsIndex()
        rhip = self.listPoints[hips[0][0]]
        lhip = self.listPoints[hips[1][0]]
        yhip = (rhip[1] + lhip[1])//2
        return [neck[0], yhip, min(neck[2],rhip[2],lhip[2]) ] # conf should be the average or the min
        
    def __init__( self ):
        self.listPoints = []
        
        
    def createFromCoco( self, cocoListPoints ):
        self.listPoints = cocoListPoints
        
    def computeAverageConfidence( self ):
        """
        compute average and not just average on detected point
        """
        
        rSum = 0.
        for pt in self.listPoints:
            rSum += pt[2]
        avgC = rSum / len(self.listPoints)
        return avgC

    def render( self, im, color = (0,255,255), bRenderConfidenceValue = True ):
        """
        """
        # compute average
        
        # avgX = sum([pt[2] for pt in self.listPoints])                
        avgX = avgY = avgC = 0
        nbrPoints = 0
        for pt in self.listPoints:
            if pt[2] > 0.1:
                avgX += pt[0]
                avgY += pt[1]
                nbrPoints += 1
            avgC += pt[2]
        
        avgX = avgX/nbrPoints
        avgY = avgY/nbrPoints
        avgC = avgC/len(self.listPoints)
        
        nThick = 1
        if avgC > 0.3:
            nThick = 2
        if avgC > 0.5:
            nThick = 4
        
        # Draw Skeleton
        #~ print("render: pts: %s" % str(self.listPoints) )
        #~ print("render: len: %s" % len(self.listPoints) )
        for pair in Skeleton.POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]
            #~ print(partA)
            #~ print(partB)
            #~ if partA >= 17 or partB>= 17:
                #~ print("out")
                #~ continue
                
            threshold = 0.2
            if self.listPoints[partA][2] < threshold or self.listPoints[partB][2] < threshold:
                continue
                
            if 1:
                confJoint = (self.listPoints[partA][2] + self.listPoints[partB][2] ) /2
                nThickPerJoint = 1
                if confJoint > 0.3:
                    nThickPerJoint = 2
                if confJoint > 0.5:
                    nThickPerJoint = 4
                nThick = nThickPerJoint

            if self.listPoints[partA] and self.listPoints[partB]:
                cv2.line(im, self.listPoints[partA][:2], self.listPoints[partB][:2], color, nThick)
                if partA == Skeleton.NOSE:
                    pointColor = (255, 255, 255)
                else:
                    pointColor = (180, 180, 180)
                cv2.circle(im, self.listPoints[partA][:2], 3, pointColor, thickness=-1, lineType=cv2.FILLED)
        

        
        if bRenderConfidenceValue:
            txt = "%3.2f" % avgC
            cv2.putText(im, txt, (int(avgX),int(avgY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
            cv2.putText(im, txt, (int(avgX),int(avgY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                
                
    def __str__( self ):
        return str(self.listPoints)
    
    def getVector(p1,p2,bb=[1,1]):
        """
        return a vector normalised or not between two points.
        if bb is given it will be an approximation of the skeleton size
        """
        return [ (p2[0]-p1[0])/bb[0], (p2[1]-p1[1])/bb[1], min(p1[2],p2[2]) ]
    

# class Skeleton - end

class Skeletons:
    NBR_POINTS = 18
    
    def __init__(self):
        self.aSkels = []
        
    def append( self, skel ):
        self.aSkels.append(skel)
        
    def filter( self, rThresholdConfidence = 0.2, nThresholdNbrPoints = 0 ):
        """
        remove all uninteresting skeletons
        """
        i = 0
        nCptInterestingPoint = 0
        while i<len(self.aSkels):
            sk = self.aSkels[i]
            for pt in sk.listPoints:
                if pt[2] >=rThresholdConfidence:
                    nCptInterestingPoint += 1
                    if nCptInterestingPoint > nThresholdNbrPoints:
                        break
            else:
                # no pt found greater than threshold
                del self.aSkels[i]
                continue
            i += 1
            
    def computeMaxAverageConfidence( self ):
        """
        return confidence of the skeleton with maximum confidence
        """
        rMax = 0.
        for sk in self.aSkels:
            rVal = sk.computeAverageConfidence()
            if rVal > rMax:
                rMax = rVal
        return rMax
            
    def save( self, filename ):
        print("INF: Skeletons, saving %s skeleton(s) to '%s'" % (len(self.aSkels),filename) )
        f = open(filename,"wb")
        if len(self.aSkels) > 0:
            #~ ln = np.ndarray(len(self.aSkels,len(self.aSkels[0])),np.float32)
            ln = np.array([np.array(x.listPoints) for x in self.aSkels],dtype=np.float32)
            print("DBG: %s, dtype: %s" % (type(ln),ln.dtype) )
            ln.tofile(f)
        # else we write an empty file, and that's great
        f.close()
        
        if 0:
            # check saving (for debug or test purpose)
            skels2 = Skeletons()                
            skels2.load(filename)
            print("skels2: %s" % skels2)
            assert(len(self.aSkels)==len(skels2.aSkels))
            print("self  : %s" % self )
            print("skels2: %s" % skels2 )
            assert(self==skels2)        

        
    def load( self, filename, bVerbose = True ):   
        f = open(filename,"rb")
        ln = np.fromfile(f,dtype=np.float32)
        nbrskel = len(ln)//Skeletons.NBR_POINTS//3
        ln = np.reshape(ln,(nbrskel,Skeletons.NBR_POINTS,3))
        f.close()
        if 0:
            print("DBG: type: %s" % str(type(ln)) )
            print("DBG: len: %s" % str(len(ln)) )
            print("DBG: shape: %s" % str(ln.shape) )
            print("DBG: dtype: %s" % str(ln.dtype) )
            print("DBG: ln: %s" % str(ln) )

        self.aSkels = []        
        for k in range(ln.shape[0]):
            sk = Skeleton()            
            for j in range(ln.shape[1]):
                sk.listPoints.append( (int(ln[k,j,0]),int(ln[k,j,1]),ln[k,j,2]) )
            self.aSkels.append(sk)
            
        if bVerbose: print("INF: Skeletons, %s loaded skeleton(s) from '%s'" % (len(self.aSkels),filename) )
        
        
    def __str__(self):
        txt = "%d skeleton(s):\n" % len(self.aSkels)
        for sk in self.aSkels:
            txt += str(sk) + "\n"
        return txt
        
    def __eq__(self, other): 
        if not isinstance(other, Skeletons):
            # don't attempt to compare against unrelated types
            return NotImplemented
            
        if len(self.aSkels) != len(other.aSkels):
            return False
            
        for j in range(len(self.aSkels)):
            if len(self.aSkels[j].listPoints) != len(other.aSkels[j].listPoints):
                return False            
            for i in range(len(self.aSkels[j].listPoints)):
                if self.aSkels[j].listPoints[i][0] != other.aSkels[j].listPoints[i][0] or self.aSkels[j].listPoints[i][1] != other.aSkels[j].listPoints[i][1]:
                    return False
                diff = self.aSkels[j].listPoints[i][2]-other.aSkels[j].listPoints[i][2]
                if diff > 0.01:
                    return False
                    
        return True
        
    def render( self, im, bRenderConfidenceValue = True ):
        aColors = [(0,255,255),(255,0,255),(255,255,0),(127,255,255),(255,127,255),(255,255,127)]
        for i, sk in enumerate(self.aSkels):
            sk.render(im,aColors[i%len(aColors)],bRenderConfidenceValue=bRenderConfidenceValue)
            
            
    def getAsLists(self):
        """
        return the all points in each skeleton as a list of trouple
        """
        listSkel = []
        for sk in self.aSkels:
                listSkel.append(sk.listPoints)
        return listSkel
        
    
    # iterator for handy access to aSkels
    def __iter__(self):
        self.iter_idx = -1 #will store previously returned
        return self
        
    def __next__(self): # Python 2: def next(self)
        self.iter_idx += 1
        if self.iter_idx >= len(self.aSkels):
            raise StopIteration
        return self.aSkels[self.iter_idx]
        
    
    # some other nice sugars for indexing
    def __len__(self):
        return len(self.aSkels)
    def __getitem__(self,key):
        return self.aSkels[key]
    def __delitem__(self,key):
        del self.aSkels[key]
        
# class Skeletons - end

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
    
    def __init__( self, strOptionnalModelPath = "../models/", strMode = "COCO", bStressTest = False ):
        #~ strMode = "MPI"
        self.strModelPath = strOptionnalModelPath
        self.net = None
        self.strMode = strMode
        self.timeTakenByNetworkTotal = 0
        self.nbrAnalyse = 0
        self.timeFirstAnalyse = 0 # first one is often slower
        self.bStressTest = bStressTest
        
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
            print("INF: Using GPU device") # biga-U18 export PYTHONPATH=/usr/local/lib/python3.6/dist-packages/cv2/python-3.6:$PYTHONPATH
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        print("INF: time taken by loading: {:.3f}".format(time.time() - t)) # biga-U18: 1.25

    def analyse( self, im ):
        """
        return a list of skel as an object Skeletons
        """
        
        bDebug = 1
        bDebug = False
        
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
        if self.bStressTest:
            print("INF: stress test net..." )
            for i in range(1000):
                inpBlob = cv2.dnn.blobFromImage(im, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)
                self.net.setInput(inpBlob) 
                output = self.net.forward()
        if self.timeFirstAnalyse == 0:
            self.timeFirstAnalyse = time.time() - t
        else:
            self.timeTakenByNetworkTotal += time.time() - t
            self.nbrAnalyse += 1
        print("INF: time taken by network: {:.3f}".format(time.time() - t)) # biga-U18: gpu: 0.40 first, 0.11 next -- cpu: 5.5s ----MsTab4: 6.5s        
        #~ print("output: %s" % str(output) )
        print("output len: %s" % len(output) )
        print("output shape: %s" % str(output.shape) )
        
        skel = Skeleton()

        H = output.shape[2]
        W = output.shape[3]
        
        nPoints = 18            
        
        if 1:
            # multi person to integrate!
            t = time.time()
            detected_keypoints = []
            keypoints_list = np.zeros((0,3))
            keypoint_id = 0
            threshold = 0.1

            for part in range(nPoints):
                probMap = output[0,part,:,:]
                probMap = cv2.resize(probMap, (im.shape[1], im.shape[0]))
                keypoints = cv2_openpose_pairing.getKeypoints(probMap, threshold)
                #~ print("Keypoints - {} : {}".format(cv2_openpose_pairing.keypointsMapping[part], keypoints))
                keypoints_with_id = []

                for i in range(len(keypoints)):
                    keypoints_with_id.append(keypoints[i] + (keypoint_id,))
                    keypoints_list = np.vstack([keypoints_list, keypoints[i]])
                    keypoint_id += 1

                detected_keypoints.append(keypoints_with_id)


            if bDebug:
                frameClone = im.copy()
                for i in range(nPoints):
                    for j in range(len(detected_keypoints[i])):
                        cv2.circle(frameClone, detected_keypoints[i][j][0:2], 5, cv2_openpose_pairing.colors[i], -1, cv2.LINE_AA)
                        txt = "%3.2f" % detected_keypoints[i][j][2] # draw confidence
                        txt = "%d" % detected_keypoints[i][j][3] # draw index
                        cv2.putText(frameClone, txt, detected_keypoints[i][j][0:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
                        cv2.putText(frameClone, txt, detected_keypoints[i][j][0:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.imshow("Keypoints",frameClone)

            valid_pairs, invalid_pairs = cv2_openpose_pairing.getValidPairs(output,frameWidth,frameHeight,detected_keypoints)
            personwiseKeypoints = cv2_openpose_pairing.getPersonwiseKeypoints(valid_pairs, invalid_pairs,keypoints_list)

            print("INF: time taken by people appariement: {:.3f}".format(time.time() - t)) # biga-U18: gpu: 1s for 4 people 0.1 for 1(alex)
            print("personwiseKeypoints: %s\n" % personwiseKeypoints )
            print("detected_keypoints: %s\n" % detected_keypoints )
            
            detected_keypoints_flat = [item for sublist in detected_keypoints for item in sublist]
            print("detected_keypoints_flat: %s\n" % detected_keypoints_flat )
            
            skels = Skeletons()
            for person in personwiseKeypoints:
                # 19 float: 18 index + a confidence
                skel = []
                for i in range(18):
                    index = int(person[i])
                    #~ print("DBG: person pt index: %s" % index )                    
                    if index == -1:                        
                        pt = (0,0,0.)
                    else:
                        pt = detected_keypoints_flat[index][:3]
                    skel.append(pt)
                s = Skeleton()
                s.createFromCoco(skel)
                skels.append(s)
            print("skel_list: %s" % skels)

            if bDebug:
                frameClone = im.copy()
                for i in range(17):
                    for n in range(len(personwiseKeypoints)):
                        index = personwiseKeypoints[n][np.array(cv2_openpose_pairing.POSE_PAIRS[i])]
                        if -1 in index:
                            continue
                        B = np.int32(keypoints_list[index.astype(int), 0])
                        A = np.int32(keypoints_list[index.astype(int), 1])
                        cv2.line(frameClone, (B[0], A[0]), (B[1], A[1]), cv2_openpose_pairing.colors[i], 3, cv2.LINE_AA)
                cv2.imshow("Detected Pose" , frameClone)
                cv2.moveWindow("Detected Pose",640,0)
                cv2.waitKey(0)
            
            
            return skels
        
        
            
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
                txt = "%d (%3.1f)" % (i,prob)
                cv2.putText(im, txt, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
                cv2.putText(im, txt, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)

                # Add the point to the list if the probability is greater than the threshold
                points.append((int(x), int(y)))
            else :
                points.append(None)
                
        skel.createFromCoco(points)
            
        return skel
        
    # analyse - end
    
    def analyseFromFile( self, strImageFile, bForceRecompute=False, bForceAlternateAngles = False ):
        """
        Analyse a file, and cache results in a file with same name.skl
        """
        filename, file_extension = os.path.splitext(strImageFile)
        strSkelFilename = filename + ".skl"
        if os.path.exists(strSkelFilename) and not bForceRecompute:
            skels = Skeletons()
            skels.load(strSkelFilename)
            return skels
        im = cv2.imread(strImageFile)
        skels = self.analyse(im)
        if len(skels.aSkels) == 0 or skels.computeMaxAverageConfidence() < 0.3 or bForceAlternateAngles:
            # try inverted (no need to test each angles)
            print("INF: analyseFromFile: trying reverted for '%s' ..." % strImageFile )
            im2 = np.flipud(im)
            skels2 = self.analyse(im2)
            for sk in skels2:
                if sk.computeAverageConfidence() > 0.3:
                    # invert all points upsidedown
                    for i in range(len(sk.listPoints)):
                        sk.listPoints[i] = sk.listPoints[i][0], im.shape[0] - sk.listPoints[i][1], sk.listPoints[i][2]
                    skels.aSkels.append(sk)
            if bForceAlternateAngles:
                # add the two 90 rotations
                print("INF: analyseFromFile: trying rotated for '%s' ..." % strImageFile )
                im2 = np.rot90(im)
                skels2 = self.analyse(im2)
                for sk in skels2:
                    if sk.computeAverageConfidence() > 0.3:
                        # invert all points upsidedown
                        for i in range(len(sk.listPoints)):
                            sk.listPoints[i] = (im.shape[1]-sk.listPoints[i][1]), sk.listPoints[i][0], sk.listPoints[i][2]
                        skels.aSkels.append(sk)
                im2 = np.rot90(im,3) # ccw
                skels2 = self.analyse(im2)
                for sk in skels2:
                    if sk.computeAverageConfidence() > 0.3:
                        # invert all points upsidedown
                        for i in range(len(sk.listPoints)):
                            sk.listPoints[i] = sk.listPoints[i][1], im.shape[0] - sk.listPoints[i][0], sk.listPoints[i][2]
                        skels.aSkels.append(sk)
                
                # filter redundant skels
                i = 0
                while i < len(skels):
                    n1 = skels[i].getNeckPos()
                    j = i + 1
                    while j < len(skels):
                        n2 = skels[j].getNeckPos()
                        if lenPts(n1,n2) < 10:
                            c1 = skels[i].computeAverageConfidence()
                            c2 = skels[j].computeAverageConfidence()
                            bb1=skels[i].getBB()
                            bb2=skels[j].getBB()
                            bQuiteSameBB = lenPts(bb1,bb2)<20 and lenPts(bb1[2:],bb2[2:])<20 
                            if c1 < 0.4 and c2 > 0.7 or (c1 > 0.7 and c2 > 0.7 and bQuiteSameBB and c1 < c2):
                                del skels[i]
                                break
                            if c1 > c2:
                                del skels[j]
                                continue # continue on next j, without changing j
                        j += 1
                    else:
                        # not out from the break in the while
                        i += 1
                        
            
                        
        skels.save(strSkelFilename)
        return skels
    # analyseFromFile - end

    def getFirstTimeTakenByNetwork(self):
        return self.timeFirstAnalyse
        
    def getAverageTimeTakenByNetwork(self):
        """
        Not counting the first one !!!
        """
        return self.timeTakenByNetworkTotal / self.nbrAnalyse



# class CVOpenPose - end

def analyseOneFile( strFilename, bForceRecompute=False, bForceAlternateAngles = False, bRender = True ):
    
    op = CVOpenPose()
    if 0:
        # previous method
        im = cv2.imread(strFilename)
        skels= op.analyse(im)
        #~ skel = op.analyse(im) # to test time taken
    else:
        skels = op.analyseFromFile(strFilename,bForceRecompute=bForceRecompute,bForceAlternateAngles=bForceAlternateAngles)
        im = cv2.imread(strFilename)
    skels.render(im)
    
    if bRender:
        zoom=1
        im = cv2.resize(im,None,fx=zoom,fy=zoom)
        cv2.imshow('Output-Skeleton', im)
        cv2.waitKey(0)    
    
    #~ skels.save("/tmp/test.skl") # test saving
    

def extractFromPath( strPath ):
    bOverwrite = False
    print("INF: extractFromPath: analysing folder: %s (overwrite:%s)" % (strPath,bOverwrite) )
    op = CVOpenPose()
    for f in sorted(  os.listdir(strPath) ):
        tf = strPath + f
        if os.path.isdir(tf):
            extractFromPath(tf + os.sep)
            continue
        filename, file_extension = os.path.splitext(f)
        if ".png" in file_extension.lower() or ".jpg" in file_extension.lower():            
            print("INF: analysing '%s'" % tf )
            im = cv2.imread(tf)
            if im.shape[0]<130:
                # thermal image!
                print("INF: too low resolution => skip")
                continue
            outname = strPath + filename + ".skl"
            if not bOverwrite and os.path.exists(outname):
                print("INF: already done => skip")
                continue
            skels = op.analyse(im)
            skels.render(im)
            print("skels: %s" % skels )
            cv2.imshow('skels', im)
            key = cv2.waitKey(1)
            skels.filter(0.2)
            skels.save(outname)
                
            if key == ord('q') or key == 27:
                print("INTERRUPTED")
                exit(-1)
            #~ exit(1) # debugging
            
            
def loadSkeletonsFromOneFolder(strPath, nFilterNbrPoint = 6):
    """
    nFilterNbrPoint: remove all skeletons with less than x detected point
    """
    listSkels = []
    for f in sorted(  os.listdir(strPath) ):
        tf = strPath + f
        filename, file_extension = os.path.splitext(f)
        if ".skl" in file_extension.lower():
            #~ print("INF: analysing '%s'" % f )
            skels = Skeletons()
            skels.load(tf,bVerbose=False)
            skels.filter(nThresholdNbrPoints=nFilterNbrPoint)
            
            # return Skeletons or list of Points ?
            listSkels.extend(skels.aSkels)
            #~ listSkels.extend(skels.getAsLists())
            
    #~ print(listSkels)
            
    return listSkels
            
            
            
#~ C:\Users\amazel\dev\git\electronoos>scp -r model* am@192.168.0.40:/home/am/dev/git/electronoos/

strPathDeboutCouche = "/home/am/images_salon_debout_couche/"
if os.name == "nt": strPathDeboutCouche = "D:/images_salon_debout_couche/"

if __name__ == "__main__":
    strFilename = "../data/alexandre.jpg"
    strFilename = "../data/multiple_humans.jpg"
    strFilename = "../data/human_upsidedown.png"
    strFilename = "../data/alexandre_rot1.jpg"
    #~ strFilename = "../data/alexandre_rot2.jpg"
    #~ strFilename = "../data/alexandre_rot3.jpg"
    
    bTestPerf = 1
    bStressTest = 0
    if bTestPerf or bStressTest:
        while 1:
            timeBegin = time.time()
            op = CVOpenPose(bStressTest=bStressTest)
            op._loadModels()
            durationLoadModels = time.time()-timeBegin
            timeBegin = time.time()
            listFile = ["alexandre.jpg","multiple_humans.jpg","human_upsidedown.png","alexandre_rot1.jpg","alexandre_rot2.jpg","alexandre_rot3.jpg"]
            for f in listFile:
                filename = "../data/" + f
                op.analyseFromFile(filename,bForceRecompute=True,bForceAlternateAngles=False)
            duration = time.time()-timeBegin
            print("    duration: load models: %.2fs" % durationLoadModels) 
            print("    fst net : %.2fs"% op.getFirstTimeTakenByNetwork() )
            print("    avg net : %.2fs"% op.getAverageTimeTakenByNetwork() )
            print("    duration: %.1fs (%.2fs per im)" % (duration,duration/len(listFile)) )
            if not bStressTest: exit(0)
            
    """
    CV2_OpenCV:
    mstab7:
        cpu mode:
            duration: load models: 0.36s
            fst net : 1.15s
            avg net : 1.08s
            duration: 10.1s (1.69s per im)
        gpu mode:
            (la lib opencv n'a pas ete recompile non plus pour utilise le gpu)
         
    Big A (linux):
        cpu mode:
            duration: load models: 0.24s
            fst net : 6.43s
            avg net : 6.43s
            duration: 53.0s (8.83s per im)
        gpu mode:
            duration: load models: 1.47s
            fst net : 0.41s
            avg net : 0.10s
            duration: 2.6s (0.43s per im)

            
    Champion1:
        cpu mode:
            duration: load models: 0.13s
            fst net : 0.43s
            avg net : 0.42s
            duration: 3.9s (0.66s per im)
            
            after reboot and removing gpu board:
            duration: load models: 0.12s
            fst net : 0.37s
            avg net : 0.37s
            duration: 3.5s (0.58s per im)


        gpu mode:
            # check with nvtop that something is loading !!!
            # need to recompile opencv with cuda support !!!
            duration: load models: 0.13s
            fst net : 1.42s
            avg net : 0.04s
            duration: 2.3s (0.38s per im)


            

    
    
    """
    
        
    if 1:
        analyseOneFile(strFilename,bForceRecompute=True,bForceAlternateAngles=True)
    elif 0:
        # recherche multi angle
        op = CVOpenPose()
        im = cv2.imread(strFilename)
        skels= op.analyse(im)
        skels.render(im)
        print("skels: %s" % skels )
        cv2.imshow('skels', im)
        key = cv2.waitKey(0)
    elif 1:
        extractFromPath(strPathDeboutCouche+"/fish/test/")
    else:
        loadSkeletonsFromOneFolder(strPathDeboutCouche+"fish/couche/")