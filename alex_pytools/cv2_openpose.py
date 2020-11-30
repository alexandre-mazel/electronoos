# Encapsulation in a nett class of the opencv openpose pose estimation
# inspired from https://www.learnopencv.com/deep-learning-based-human-pose-estimation-using-opencv-cpp-python/
#
# on my biga: export PYTHONPATH=/usr/local/lib/python3.6/dist-packages/cv2/python-3.6:$PYTHONPATH

import cv2
import os
import time
import numpy as np

keypointsMapping = ['Nose', 'Neck', 'R-Sho', 'R-Elb', 'R-Wr', 'L-Sho', 'L-Elb', 'L-Wr', 'R-Hip', 'R-Knee', 'R-Ank', 'L-Hip', 'L-Knee', 'L-Ank', 'R-Eye', 'L-Eye', 'R-Ear', 'L-Ear']

POSE_PAIRS = [[1,2], [1,5], [2,3], [3,4], [5,6], [6,7],
              [1,8], [8,9], [9,10], [1,11], [11,12], [12,13],
              [1,0], [0,14], [14,16], [0,15], [15,17],
              [2,17], [5,16] ]

# index of pafs correspoding to the POSE_PAIRS
# e.g for POSE_PAIR(1,2), the PAFs are located at indices (31,32) of output, Similarly, (1,5) -> (39,40) and so on.
mapIdx = [[31,32], [39,40], [33,34], [35,36], [41,42], [43,44],
          [19,20], [21,22], [23,24], [25,26], [27,28], [29,30],
          [47,48], [49,50], [53,54], [51,52], [55,56],
          [37,38], [45,46]]

colors = [ [0,100,255], [0,100,255], [0,255,255], [0,100,255], [0,255,255], [0,100,255],
         [0,255,0], [255,200,100], [255,0,255], [0,255,0], [255,200,100], [255,0,255],
         [0,0,255], [255,0,0], [200,200,0], [255,0,0], [200,200,0], [0,0,0]]


def getKeypoints(probMap, threshold=0.1):

    mapSmooth = cv2.GaussianBlur(probMap,(3,3),0,0)

    mapMask = np.uint8(mapSmooth>threshold)
    keypoints = []

    #find the blobs
    contours, _ = cv2.findContours(mapMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #for each blob find the maxima
    for cnt in contours:
        blobMask = np.zeros(mapMask.shape)
        blobMask = cv2.fillConvexPoly(blobMask, cnt, 1)
        maskedProbMap = mapSmooth * blobMask
        _, maxVal, _, maxLoc = cv2.minMaxLoc(maskedProbMap)
        keypoints.append(maxLoc + (probMap[maxLoc[1], maxLoc[0]],))

    return keypoints


# Find valid connections between the different joints of a all persons present
def getValidPairs(output,frameWidth, frameHeight,detected_keypoints):
    valid_pairs = []
    invalid_pairs = []
    n_interp_samples = 10
    paf_score_th = 0.1
    conf_th = 0.7
    # loop for every POSE_PAIR
    for k in range(len(mapIdx)):
        # A->B constitute a limb
        pafA = output[0, mapIdx[k][0], :, :]
        pafB = output[0, mapIdx[k][1], :, :]
        pafA = cv2.resize(pafA, (frameWidth, frameHeight))
        pafB = cv2.resize(pafB, (frameWidth, frameHeight))

        # Find the keypoints for the first and second limb
        candA = detected_keypoints[POSE_PAIRS[k][0]]
        candB = detected_keypoints[POSE_PAIRS[k][1]]
        nA = len(candA)
        nB = len(candB)

        # If keypoints for the joint-pair is detected
        # check every joint in candA with every joint in candB
        # Calculate the distance vector between the two joints
        # Find the PAF values at a set of interpolated points between the joints
        # Use the above formula to compute a score to mark the connection valid

        if( nA != 0 and nB != 0):
            valid_pair = np.zeros((0,3))
            for i in range(nA):
                max_j=-1
                maxScore = -1
                found = 0
                for j in range(nB):
                    # Find d_ij
                    d_ij = np.subtract(candB[j][:2], candA[i][:2])
                    norm = np.linalg.norm(d_ij)
                    if norm:
                        d_ij = d_ij / norm
                    else:
                        continue
                    # Find p(u)
                    interp_coord = list(zip(np.linspace(candA[i][0], candB[j][0], num=n_interp_samples),
                                            np.linspace(candA[i][1], candB[j][1], num=n_interp_samples)))
                    # Find L(p(u))
                    paf_interp = []
                    for k in range(len(interp_coord)):
                        paf_interp.append([pafA[int(round(interp_coord[k][1])), int(round(interp_coord[k][0]))],
                                           pafB[int(round(interp_coord[k][1])), int(round(interp_coord[k][0]))] ])
                    # Find E
                    paf_scores = np.dot(paf_interp, d_ij)
                    avg_paf_score = sum(paf_scores)/len(paf_scores)

                    # Check if the connection is valid
                    # If the fraction of interpolated vectors aligned with PAF is higher then threshold -> Valid Pair
                    if ( len(np.where(paf_scores > paf_score_th)[0]) / n_interp_samples ) > conf_th :
                        if avg_paf_score > maxScore:
                            max_j = j
                            maxScore = avg_paf_score
                            found = 1
                # Append the connection to the list
                if found:
                    valid_pair = np.append(valid_pair, [[candA[i][3], candB[max_j][3], maxScore]], axis=0)

            # Append the detected connections to the global list
            valid_pairs.append(valid_pair)
        else: # If no keypoints are detected
            print("No Connection : k = {}".format(k))
            invalid_pairs.append(k)
            valid_pairs.append([])
    return valid_pairs, invalid_pairs



# This function creates a list of keypoints belonging to each person
# For each detected valid pair, it assigns the joint(s) to a person
def getPersonwiseKeypoints(valid_pairs, invalid_pairs,keypoints_list):
    # the last number in each row is the overall score
    personwiseKeypoints = -1 * np.ones((0, 19))

    for k in range(len(mapIdx)):
        if k not in invalid_pairs:
            partAs = valid_pairs[k][:,0]
            partBs = valid_pairs[k][:,1]
            indexA, indexB = np.array(POSE_PAIRS[k])

            for i in range(len(valid_pairs[k])):
                found = 0
                person_idx = -1
                for j in range(len(personwiseKeypoints)):
                    if personwiseKeypoints[j][indexA] == partAs[i]:
                        person_idx = j
                        found = 1
                        break

                if found:
                    personwiseKeypoints[person_idx][indexB] = partBs[i]
                    personwiseKeypoints[person_idx][-1] += keypoints_list[partBs[i].astype(int), 2] + valid_pairs[k][i][2]

                # if find no partA in the subset, create a new subset
                elif not found and k < 17:
                    row = -1 * np.ones(19)
                    row[indexA] = partAs[i]
                    row[indexB] = partBs[i]
                    # add the keypoint_scores for the two keypoints and the paf_score
                    row[-1] = sum(keypoints_list[valid_pairs[k][i,:2].astype(int), 2]) + valid_pairs[k][i][2]
                    personwiseKeypoints = np.vstack([personwiseKeypoints, row])
    return personwiseKeypoints

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

    def render( self, im, color = (0,255,255) ):
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

            if self.listPoints[partA] and self.listPoints[partB]:
                cv2.line(im, self.listPoints[partA][:2], self.listPoints[partB][:2], color, nThick)
                cv2.circle(im, self.listPoints[partA][:2], 3, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
        

        
        txt = "%3.2f" % avgC
        cv2.putText(im, txt, (int(avgX),int(avgY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
        cv2.putText(im, txt, (int(avgX),int(avgY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, lineType=cv2.LINE_AA)
            
                
    def __str__( self ):
        return str(self.listPoints) 

# class Skeleton - end

class Skeletons:
    NBR_POINTS = 18
    
    def __init__(self):
        self.aSkels = []
        
    def append( self, skel ):
        self.aSkels.append(skel)
        
    def filter( self, rThreshold = 0.2):
        """
        remove all uninteresting skeletons
        """
        i = 0
        while i<len(self.aSkels):
            sk = self.aSkels[i]
            for pt in sk.listPoints:
                if pt[2] >=rThreshold:
                    break
            else:
                # no pt found greater than threshold
                del self.aSkels[i]
                continue
            i += 1
        
        
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

        
    def load( self, filename ):   
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
            
        print("INF: Skeletons, %s loaded skeleton(s) from '%s'" % (len(self.aSkels),filename) )
        
        
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
        
    def render( self, im ):
        aColors = [(0,255,255),(255,0,255),(255,255,0),(127,255,255),(255,127,255),(255,255,127)]
        for i, sk in enumerate(self.aSkels):
            sk.render(im,aColors[i%len(aColors)])
            
            
    def getAsLists(self):
        """
        return the all points in each skeleton as a list of trouple
        """
        listSkel = []
        for sk in self.aSkels:
                listSkel.append(sk.listPoints)
        return listSkel
        
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
        print("INF: time taken by network: {:.3f}".format(time.time() - t)) # biga-U18: gpu: 0.40 first, 0.11 next -- cpu: 5.5s ----MsTab4: 6.5s        
        print("output: %s" % str(output) )
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
                keypoints = getKeypoints(probMap, threshold)
                print("Keypoints - {} : {}".format(keypointsMapping[part], keypoints))
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
                        cv2.circle(frameClone, detected_keypoints[i][j][0:2], 5, colors[i], -1, cv2.LINE_AA)
                        txt = "%3.2f" % detected_keypoints[i][j][2] # draw confidence
                        txt = "%d" % detected_keypoints[i][j][3] # draw index
                        cv2.putText(frameClone, txt, detected_keypoints[i][j][0:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, lineType=cv2.LINE_AA)
                        cv2.putText(frameClone, txt, detected_keypoints[i][j][0:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.imshow("Keypoints",frameClone)

            valid_pairs, invalid_pairs = getValidPairs(output,frameWidth,frameHeight,detected_keypoints)
            personwiseKeypoints = getPersonwiseKeypoints(valid_pairs, invalid_pairs,keypoints_list)

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
                        index = personwiseKeypoints[n][np.array(POSE_PAIRS[i])]
                        if -1 in index:
                            continue
                        B = np.int32(keypoints_list[index.astype(int), 0])
                        A = np.int32(keypoints_list[index.astype(int), 1])
                        cv2.line(frameClone, (B[0], A[0]), (B[1], A[1]), colors[i], 3, cv2.LINE_AA)
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



# class CVOpenPose - end

def analyseOneFile( strFilename ):
    im = cv2.imread(image_file)
    op = CVOpenPose()
    skels= op.analyse(im)
    #~ skel = op.analyse(im)
    skels.render(im)
    
    zoom=1
    im = cv2.resize(im,None,fx=zoom,fy=zoom)
    cv2.imshow('Output-Skeleton', im)
    cv2.waitKey(0)    
    
    skels.save("/tmp/test.skl") # test saving
    

def extractFromPath( strPath ):
    print("INF: extractFromPath: analysing folder: %s" % strPath )
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
            skels = op.analyse(im)
            skels.render(im)
            print("skels: %s" % skels )
            cv2.imshow('skels', im)
            key = cv2.waitKey(1)
            skels.filter(0.2)
            outname = strPath + filename + ".skl"
            skels.save(outname)
                
            if key == ord('q') or key == 27:
                print("INTERRUPTED")
                exit(-1)
            #~ exit(1) # debugging
            
            
def loadSkeletonsFromOneFolder(strPath):
    listSkels = []
    for f in sorted(  os.listdir(strPath) ):
        tf = strPath + f
        filename, file_extension = os.path.splitext(f)
        if ".skl" in file_extension.lower():
            print("INF: analysing '%s'" % f )
            skels = Skeletons()
            skels.load(tf)
            listSkels.extend(skels.getAsLists())
            #~ print(listSkels)
            
    return listSkels
            
            
            


strPathDeboutCouche = "/home/am/images_salon_debout_couche/"
if os.name == "nt": strPathDeboutCouche = "c:/images_salon_debout_couche/"

if __name__ == "__main__":
    if 0:
        image_file = "../data/alexandre.jpg"
        image_file = "../data/multiple_humans.jpg"    
        analyseOneFile(image_file)
    elif 0:
        extractFromPath(strPathDeboutCouche)
    else:
        loadSkeletonsFromOneFolder(strPathDeboutCouche+"fish/couche/")