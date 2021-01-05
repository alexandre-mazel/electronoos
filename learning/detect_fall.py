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
import math

import numpy as np

def renderCenteredText( im, strText, pt, nFontFace, rScale, color, nFontThickness ):
    rcRendered, baseline = cv2.getTextSize( strText, nFontFace, rScale, nFontThickness )
    cv2.putText(im, strText, (pt[0]-rcRendered[0]//2,pt[1]), nFontFace, rScale, color, nFontThickness )


def div2(pt):
    for i in range(len(pt)):
        pt[i] /= 2

def div2tuple(pt):
    ptret = list(pt)
    for i in range(len(pt)):
        ptret[i] /= 2
    return tuple(ptret)

def mul2tuple(pt):
    ptret = list(pt)
    for i in range(len(pt)):
        ptret[i] *= 2
    return tuple(ptret)
    
def avg2(pt1,pt2):
    assert( len(pt1) == len(pt2) )
    a = []
    for i in range(len(pt1)):
        a.append( (pt1[i]+pt2[i])/2 )
    return a
    
def dist(p1,p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx*dx+dy*dy)
        
def isFullConf(triols, rThreshold = 0.2):
    """
    return True if all third values are > threshold
    """
    for i in range(2,len(triols),3):
        if triols[i] < rThreshold:
            return False
    return True
    
    
class WorldMemory:
    def __init__( self ):
        self.facts = [] # list of fact, a fact is a pos, a ttl and a fact (here, just True or False)
        
    def update( self ):
        """
        get everything older
        """
        i = 0
        while i < len(self.facts):
            self.facts[i][1] -= 1
            if self.facts[i][1] < 0:
                print("ING: WorldMemory.update: erasing %d: %s" % (i,str(self.facts[i]) ) )
                del self.facts[i]
                continue
            i += 1
            
                
    def get( self, pos, rRadius = 5 ):
        i = 0
        while i < len(self.facts):
            rDist = dist(self.facts[i][0],pos)
            if rDist < rRadius:
                self.facts[i][1] -= 1
                if self.facts[i][1] < 0:
                    print("ING: WorldMemory.get: erasing %d: %s" % (i,str(self.facts[i]) ) )
                    del self.facts[i]
                    continue
                print("ING: WorldMemory.get: returning %d: %s (dist:%5.1f)" % (i,str(self.facts[i]), rDist ) )
                return self.facts[i][2]
            i += 1
        return None
    
    
    def set( self, pos, fact, rRadius = 5, nTTL = 5 ):
        """
        - rRadius: radius to identify if a new plot is a new one
        """
        i = 0
        while i < len(self.facts):
            rDist = dist(self.facts[i][0],pos)
            if rDist < rRadius:
                self.facts[i][0] = pos
                self.facts[i][1] = nTTL
                self.facts[i][2] = fact
                print("ING: WorldMemory.set: updating %d to %s (dist:%5.1f)" % (i,str(self.facts[i]), rDist ) )
                return
            i += 1
        self.facts.append([pos,nTTL, fact])
        print("ING: WorldMemory.set: adding %d %s" % (len(self.facts)-1,str(self.facts[-1]) ) )
        return
# WorldMemory - end


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
                
               
def isDeboutHandCoded( sk, bOnlyTorso = False, bVerbose = False ):                
    """
    use a hand coded rules
    """
    
    neck = sk.listPoints[Skeleton.getNeckIndex()]
    
    if bVerbose: print("neck: %s" % str(neck))
    
    legsInfo = sk.getLegs()
    if bVerbose: print("legs: %s" % str(legsInfo))
    
    bb = sk.getBB_Size()
    sto = sk.getStomach()
    

    
    rh,rk,ra = legsInfo[0] # hip, knee, ankle
    lh,lk,la = legsInfo[1]
    
    avgFeets = [ ra[0]+la[0],ra[1]+la[1],ra[2]+la[2] ]
    div2(avgFeets)
    
    lal = sk.getArms()
    if bVerbose: print("arms: %s" % str(lal))
    rs,re,rw = lal[0] #shoulder, elbow, wrist
    ls,le,lw = lal[1]
    
    rThreshold = 0.2
    
    #~ # si les pieds sont plus bas que les hanches
    # a essayer: orientation cou/(estomac ou moyenne des hanches): vertical => debout; sinon couche
    # a essayer: quand les fesses sont sur le sol
    
    # NB: on n'arrivera jamais a voir que quelqu'un qui est assis ou couche' oriente' vers la camera est tombe'
    
    # si les mains ou a defaut les coudes sont plus hautes que les pieds ou a defaut les hanches
    bDeboutFromArmsLegsHeight = None
    
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
        if neck[2] > rThreshold:
            lHi = neck[:2]
        else:
            lHi = None
        
        if lHi != None or rHi != None:
            
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
                
            if lLo != None or rLo != None:

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

                
                bDeboutFromArmsLegsHeight = hi[1]+rMargin<lo[1] # WRN:  pixel Y are inverted (high pixel are smaller than lower)
        
                if bVerbose: print("rMargin:%5.2f, bDeboutFromArmsLegsHeight: %s"% (rMargin,bDeboutFromArmsLegsHeight) )

    bDeboutFromTorsoAngle = None
    if (rh[2] > rThreshold or lh[2] > rThreshold) and neck[2] > rThreshold:
        if (rh[2] > rThreshold and lh[2] > rThreshold):
            avg_hip = avg2(rh,lh)
        elif rh[2] > rThreshold:
            avg_hip = rh
        else:
            avg_hip = lh
        dx = avg_hip[0]-neck[0]
        dy = avg_hip[1]-neck[1]
        if abs(dx) < 0.1:
            coef = dy*10
        else:
            coef = dy/dx
        bDeboutFromTorsoAngle = abs(coef) > 1. # 1: diagonal
        if bVerbose: print("coef: %5.1f (dy:%3.1f,dx:%3.1f), bDeboutFromTorsoAngle: %s" % (coef,dy, dx, bDeboutFromTorsoAngle) )
    #~ else:
        #~ return None
        
    # fesses sur le sol
    bNotBumOnGround = None
    if rh[2] > rThreshold and lh[2] > rThreshold:
        avg_hip = avg2(rh,lh)
    elif rh[2] > rThreshold:
        avg_hip = rh
    elif lh[2] > rThreshold:
        avg_hip = lh
    else:
        avg_hip = None
    if avg_hip != None:
        # look for lower point in legs, but not hip:
        rLowest = -10000
        #~ for i in range(cv2_openpose.Skeleton.NBR_POINTS):
        for i in [cv2_openpose.Skeleton.RKNEE,cv2_openpose.Skeleton.LKNEE,cv2_openpose.Skeleton.RANKLE,cv2_openpose.Skeleton.LANKLE]:
            if i == cv2_openpose.Skeleton.RHIP or i == cv2_openpose.Skeleton.LHIP:
                continue
            if sk.listPoints[i][2] < rThreshold:
                continue
            if sk.listPoints[i][1] > rLowest:
                rLowest = sk.listPoints[i][1]
        if rLowest >= 0:
            #~ lenLimbs = sk.getLenLimbs()
            #~ if bVerbose: print("lenLimbs: %s" % str(lenLimbs) )
            #~ rLenLegs = (lenLimbs[0][0] +lenLimbs[1][0]) / 2
            rLenLegs = sk.getAvgLenLeg()
            if rLenLegs != None:
                bNotBumOnGround = (avg_hip[1] + (rLenLegs*0.75)) < rLowest
                if bVerbose: print("avg hip: %5.1f, lowest: %5.1f, rLenLegs: %5.1f, bNotBum: %s" % (avg_hip[1],rLowest,rLenLegs, bNotBumOnGround) )
                if legsInfo[0][2][2] < rThreshold and legsInfo[1][2][2] < rThreshold:
                    if bVerbose: print("INF: no foot seen, reseting bNotBumOnGround" )
                    # on ne voit aucun pied, soit ils ne sont pas a l'ecran soit il sont derriere, dans le doute, on prefere dire None
                    bNotBumOnGround = None
    #~ return bNotBumOnGround
        
    # on veut etre sur => si hesitation, ne se prononces pas
    if 0:
        if not bOnlyTorso:
            if bDeboutFromArmsLegsHeight != bDeboutFromTorsoAngle:
                return None

            
        #~ if bDeboutFromArmsLegsHeight:
        if bDeboutFromTorsoAngle == None and bNotBumOnGround:
            return 1
            
        if bDeboutFromTorsoAngle and bNotBumOnGround:
            return 1

            
        if bDeboutFromTorsoAngle == None and bNotBumOnGround == None and bDeboutFromArmsLegsHeight != None:
            return bDeboutFromArmsLegsHeight
            
        if bDeboutFromTorsoAngle != None and bNotBumOnGround == None:
            return bDeboutFromTorsoAngle
            
        return 0
        
        
    else:
        if bDeboutFromTorsoAngle == bNotBumOnGround and bDeboutFromTorsoAngle == bDeboutFromArmsLegsHeight:
            return bDeboutFromTorsoAngle
        if bNotBumOnGround != None:
            return bNotBumOnGround
        if bDeboutFromTorsoAngle != None:
            return bDeboutFromTorsoAngle        
        if bDeboutFromArmsLegsHeight != None:
            return bDeboutFromArmsLegsHeight
        return None
    
        
        
    
def predictHandCoded( listSkel ):
    ret = []
    for sk in listSkel:
        ret.append(isDeboutHandCoded(sk,bOnlyTorso=0))
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
        #~ print("predicted: %s" % pred)
        print("diff on learn: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) #1/80  sans avg hand/feet 3/158
        # test
        pred = classifier.predict(listDeboutFTotal[len(listCoucheF):] )
        #~ print("predicted: %s" % pred)
        print("diff on extra debout: %d/%d" % (len(pred)-sum(pred),len(pred)) ) # count zeroes # 2/114  9/111
        
        if 1:
            # hand coded test
            pred = predictHandCoded(listCouche+listDebout)
            classes = [0]*len(listCouche) + [1]*len(listDebout) 
            #~ print("predicted: %s" % pred)
            
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
            
            print("diff on LEARN folder Hand Coded: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) # 96/345 mix hauteur bras et jambe et angle torse: 59/297=0.272 (seul torso: 68/345=0.197) avec bum: 19/297 (only torso et bum: 28/345=0.081) avec new avg len on bum: 16/297 # avec nouvel regle utilisation angle si pas bum: 19/297
            # apres refactor: 37/366
        
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
        #~ print("predicted: %s" % pred)
        print("diff on test folder: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) #17/274  16/315
        
        # hand coded test
        pred = predictHandCoded(listCouche+listDebout)
        classes = [0]*len(listCouche) + [1]*len(listDebout) 
        #~ print("predicted: %s" % pred)
        
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
        
        print("diff on TEST folder Hand Coded: %d/%d" % (sum(abs(pred-classes)),len(pred) ) ) # 37/372 # 54/402 sans margin, 45/402 mix hauteur bras et jambe et angle torse:  11/361=0.030 (change seul torso: 16/402=0.039) avec bum: 19/361 (only torso et bum: 22/402=0.055) avec new avg len on bum: 14/364 # avec nouvel regle utilisation angle si pas bum: 9/364
        # apres refactor des conditions: 108/598
        # total: 145/964 (0.15)
        
    #~ from sklearn.externals import joblib        
    joblib.dump(classifier, 'detect_fall_classifier.pkl')

# learn - end

def analyseFilenameInPath( strPath, bForceRecompute = False, bRender=True, bForceAlternateAngles = False ):
    """
    Return False if user want to quit.
    
    Rappel: convert one video to png:
    ffmpeg -i in.mp4 -vsync 0 out%05d.png
    """
    bJustPrecompute = 0
    print("INF: analyseFilenameInPath: strPath: %s" % strPath )
    op = cv2_openpose.CVOpenPose()
    if 1:
        clf = joblib.load('detect_fall_classifier.pkl')
    #~ skel = op.analyseFromFile(strImageFilename)
    listFile = sorted(  os.listdir(strPath) )
    i = 0
    bContinue = True
    nCptGenerated = 0
    rThresholdAvg = 0.1
    wm = WorldMemory()
    while i < len(listFile) and bContinue:
        print("Analyse: %d/%d" % (i,len(listFile) ) )
        #~ if i < 2000:
            #~ i += 1
            #~ continue
        f = listFile[i]
        tf = strPath + f
        if os.path.isdir(tf):
            bRet = analyseFilenameInPath(tf + os.sep,bForceRecompute=bForceRecompute,bRender=bRender,bForceAlternateAngles=bForceAlternateAngles)
            if not bRet: return bRet
            i += 1
            continue
        
        filename, file_extension = os.path.splitext(f)
        if ".png" in file_extension.lower() or ".jpg" in file_extension.lower(): 
            skels = op.analyseFromFile(tf,bForceRecompute=bForceRecompute,bForceAlternateAngles=bForceAlternateAngles)
            if bJustPrecompute:
                i += 1
                continue
            im = cv2.imread(tf)
            for skel in skels:
                if 1:
                    rAvg = skel.computeAverageConfidence()
                    if rAvg < rThresholdAvg:
                        continue
                    
                feat = skelToFeatures(skel)
                colorText = (255,255,255)
                txt = ""
                if 0:
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
                        ret = isDeboutHandCoded(skel,bVerbose=1)
                        if ret == 0:
                            txt += "Fall"
                        elif ret == 1:
                            txt += "Stand"
                        else:
                            txt += "?"
                if 1:
                    txt += " / "
                    txt = "" #erase all other algorithms
                    ret = isDeboutHandCoded(skel,bVerbose=1,bOnlyTorso=True)
                    bFromCache = 0
                    if ret == None:
                        ret = wm.get(skel.getNeckPos(),rRadius=20)
                        if ret != None: bFromCache = 1
                    else:
                        wm.set(skel.getNeckPos(),ret,rRadius=20) # default is 5 ttl (1 in update and 1 in get)
                    if ret == 0:
                        txt += "Fall"
                        colorText = (80,80,255)
                    elif ret == 1:
                        txt += "Stand"
                        colorText = (255,80,80)
                    else:
                        txt += "?"
                        
                    if bFromCache: 
                        colorText = mul2tuple(colorText)
                        #~ txt = txt[0].lower() + txt[1:]

                #render skel with color
                skel.render(im, colorText,bRenderConfidenceValue=False)

                print(txt)
                bb = skel.getBB()
                renderCenteredText(im, txt, ( (bb[0]+bb[2]) // 2,bb[3]+18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3 )
                renderCenteredText(im, txt, ( (bb[0]+bb[2]) // 2,bb[3]+18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colorText, 1 )
            
            # skels.render(im, bRenderConfidenceValue=False)
            
            wm.update()
            if bRender: cv2.imshow("detected",im)
            
            if 0:
                # ffmpeg -r 10 -i %06d.png -vcodec libx264 -b:v 4M -b:a 1k test.mp4
                cv2.imwrite("d:/generated/%06d.png" % nCptGenerated, im)  # NB: won't work with sub folder (overwriting dest)
                nCptGenerated += 1
                
                # pour un petit gif anime de l'image de 823 a 992 # les de debut et fin ne fonctionnent pas => isoler dans un dossier
                # ffmpeg -r 10 -i %06d.png -start_number 823 -vframes 169 -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
                # => use of the "a (%d).png" techniques
            
            if bRender:
                key = cv2.waitKey(1)
                print(key)
                if key == ord('q') or key == 27:
                    bContinue = False
                    break
                if key == ord('p'):
                    i -= 5 # skip also some previous file not images, like skel... - crappy!
                    if i < 0:
                        i = -1
                
        i += 1
    # while - end
    
    return bContinue
        
#analyseFilenameInPath  - end

if __name__ == "__main__":
    pathData = "/home/am/"
    if os.name == "nt":  pathData = "d:/"
    
    #~ learn()
    #~ analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/test/couche/", bForceRecompute=True)
    #~ analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/demo/")
    #~ analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/test_frontal2/")
    #~ analyseFilenameInPath(cv2_openpose.strPathDeboutCouche+"fish/demo/")
    analyseFilenameInPath(pathData+"/exported/", bForceRecompute = 1, bForceAlternateAngles = 1)
    #~ analyseFilenameInPath(pathData+"/tmp2/")
    