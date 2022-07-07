"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.

Launch server On AGX:
cd ~/dev/git/electronoos/scripts/versatile
nohup python3 run_cloud_server.py &

# ou en local windows:
cd C:\\Users\\alexa\\\dev\\git\\electronoos\\scripts\\versatile
python run_cloud_server.py

# in case of problem:
# taskkill /F /im python.exe

"""
import cv2
import json
import os
import sys
import time


sys.path.append("../scripts/versatile")
try:
    import cloud_services
except:
    print("INF: Trying robot path")
    sys.path.append("/home/nao/.local/lib/python2.7/site-packages/electronoos/scripts/versatile/")    
    import cloud_services

try:
    sys.path.append("../../electronoos/alex_pytools")
    import face_detector_cv3
    import misctools
    import cv2_tools
except:
    print("INF: Trying robot path")
    sys.path.append("/home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools")    
    import misctools
    import cv2_tools


from json import JSONEncoder
from json import JSONDecoder

def _defaultEncoder(self, obj):
    return getattr(obj.__class__, "as_dict", _defaultEncoder.default)(obj)

_defaultEncoder.default = JSONEncoder().default
JSONEncoder.default = _defaultEncoder


def _defaultDecoder(self, obj):
    return getattr(obj.__class__, "from_dict", _defaultDecoder.default)(obj)

print(dir(JSONDecoder()))
_defaultDecoder.default = JSONDecoder().raw_decode
JSONDecoder.default = _defaultDecoder



class HumanKnowledge:
    def __init__( self, nUID = -1):
        self.nUID = nUID
        self.nTotalSeen = 0
        self.nSeenToday = 0
        self.nDayStreak = 0
        self.strDayLastSeen = "1974_08_19" # string representing the last time seen
        # compute duration of current interaction (we just note time of last, if it's recent, we are still in interaction
        self.rTimeLastInteraction = 0 # as time.time() info
        self.rDurationInteraction = 0 # in sec
        self.rTotalInteraction = 0 # in sec
        
        self.timeLastReactToFace = 0 # as time.time() info
        self.timeLastReactToLook = 0
        self.timeLastReactToNear = 0
        self.timeLastReactToInteract = 0

        
    def as_dict(self):
        #~ strOut = json.dumps((self.nUID,self.nTotalSeen,self.nSeenToday,self.nDayStreak),indent=2,ensure_ascii =False)
        #~ strOut = '{"HumanKnowledge": 1,"uid": %d, "totalseen": %d, "seentoday": %d, "daystreak": %d}' % (self.nUID,self.nTotalSeen,self.nSeenToday,self.nDayStreak)
        #~ strOut =  json.dumps(self.__dict__)
        #~ return strOut
        return self.__dict__

    def from_dict(self, dct):
        #~ print("DBG: from_dict: %s" % dct )       
        try:
            # when adding a new variable, add it at the end, so the data will be loaded 
            # and new one will raise exceptions, but will be ok next time
            self.nUID = dct['nUID']
            self.nTotalSeen = dct['nTotalSeen']
            self.nSeenToday = dct['nSeenToday']
            self.nDayStreak = dct['nDayStreak']
            self.strDayLastSeen = dct['strDayLastSeen']
            
            self.rTimeLastInteraction = dct['rTimeLastInteraction']
            self.rDurationInteraction = dct['rDurationInteraction']
            self.rTotalInteraction = dct['rTotalInteraction']
            
            self.timeLastReactToFace = dct['timeLastReactToFace']
            self.timeLastReactToLook = dct['timeLastReactToLook']
            self.timeLastReactToNear = dct['timeLastReactToNear']
            self.timeLastReactToInteract = dct['timeLastReactToInteract']
            
        except KeyError as err:
            print("WRN: HumanKnowledge.from_dict: first time exception after adding new attributes? : can't find %s" % err )
            # the object will be partially inited, but it's ok
            
        return self
        

def decode_custom(dct):
    #~ print("DBG: decode_custom: %s" % dct )
    if "HumanKnowledge" in dct or "nTotalSeen" in dct.keys():
        hk = HumanKnowledge().from_dict(dct)
        return hk
    if isinstance(dct, dict): # key as string => int
        dictKeyAsInt = dict()
        for k,v in dct.items():
            if misctools.is_string_as_integer(k):
                dictKeyAsInt[int(k)] = v
        return dictKeyAsInt
    return dct
    
    

class HumanManager:
    def __init__( self ):
        
        self.bPepper = os.name != "nt"
        
        if self.bPepper:
            self.cs = cloud_services.CloudServices( "robot-enhanced-education.org", 25340 )
        else:
            self.cs = cloud_services.CloudServices( "localhost", 13000 )
            
        self.cs.setVerbose( True )
        strClientName = "test_on_the_fly" 
        try:
            import abcdk.system
            if abcdk.system.isOnRobot():
                strClientName = abcdk.system.getNickName()
        except BaseException as err:
            print("WRN: HumanManager.init: while getting client name err: %s" % str(err) )
            
        print("INF: HumanManager.init: using client name '%s'" % strClientName  )
        self.cs.setClientID( strClientName )
        try:
            self.fdcv3 = face_detector_cv3.facedetector
        except:
            print("WRN: face_detector_cv3: won't present")
            
        self.strSaveFilename = misctools.getUserHome() + "save/"
        try:
            os.makedirs(self.strSaveFilename)
        except: pass
        
        self.strSaveFilename += "cherie_human_manager.dat"
        self.aHumanKnowledge = {} # uid => HumanKnowledge
        self.load()
        
        if self.bPepper:
            import naoqi
            self.mem = naoqi.ALProxy( "ALMemory",  "localhost", 9559 );
            import abcdk.extractortools
            afd = naoqi.ALProxy("ALFaceDetection", "localhost", 9559)
            afd.post._run() # explicit start (instead of registering to event)
            import agent_behavior
            reload(agent_behavior)
            self.ab = agent_behavior.agentBehavior
        else:
            self.ab = None
            
        # state info
        self.rTimeGlobalLastInteraction = time.time()-1000
        self.bWasInteracting = 0
        self.timeNoFace = time.time()
        
    def __del__(self):
        self.save()
        
    def load( self ):
        try:
            f = open(self.strSaveFilename,"rt")
        except misctools.FileNotFoundError:
            print("WRN: HumanManager.load: file not found: '%s'" % self.strSaveFilename)
            return 0
        try:
            self.aHumanKnowledge = json.load(f,object_hook=decode_custom)
        except BaseException as err:
            print("INF: HumanManager.load: potential error (or file empty): %s" % str(err) )
            self.__del__ = lambda do_nothing: None
            exit(1) # don't continue, as all historic will be erased #not working
        print("INF: HumanManager.load: loaded: %d humans" % ( len(self.aHumanKnowledge) ) )
        f.close()
        print(repr(self.aHumanKnowledge))
        return 1
        
    def save( self ):
        print("DBG: HumanManager.save: saving to '%s'" % str(self.strSaveFilename))
        f = open(self.strSaveFilename,"wt")
        ret = json.dump((self.aHumanKnowledge),f,indent=2,ensure_ascii =False)
        f.close()
        


    def updateImage( self, img, bAddDebug = False ):
        """
        return face detected, lookat, near, interact or None on image or server problem
        """
        #~ if not self.cs.isRunning():
            #~ return None
            
        if img is None:
            return None
            
        bSeenFaces = 0
        bSomeoneLook = 0
        bSomeoneNear = 0
        bSomeoneInteract = 0
        rTimeSinceLastInteraction = time.time()-1000
        
        # ~0.06s on mstab7 on a VGA one face image
        if not self.bPepper:
            faces = self.fdcv3.detect(img,bRenderBox=False,confidence_threshold=0.4)
        else:
            # pepper
            import abcdk.extractortools
            faces = []
            datas = self.mem.getData("FaceDetection/FaceDetected")
            print("datas: %s" % datas)
            #~ datas = mem.getData("FaceDetected")
            #~ print("datas: %s" % datas)
            faceinfo = abcdk.extractortools.FaceDetectionNew_decodeInfos(datas)
            if len(faceinfo.objects) > 0:
                for face in faceinfo.objects:
                    print("DBG: face: %s" % face )
                    vertices = face.faceInfo.vertices
                    coef = 2 # face detect return in QVGA and here were are in VGA
                    margin = 50
                    posface = [vertices[0][0]*coef,vertices[0][1]*coef,vertices[1][0]*coef,vertices[2][1]*coef,face.faceInfo.rConfidence]
                    
                    # cause we could have a time decay between analyse and grab
                    posface[0] = max(0,posface[0]-margin)
                    posface[1] = max(0,posface[1]-margin)
                    posface[2] += margin
                    posface[3] += margin
                    
                    #~ posface = [0,0,img.shape[1],img.shape[0],1] # send entire image containing faces
                    faces.append(posface)
            print("DBG: pepper, final faces: %s" % str(faces))
            
        if len(faces) < 1:
            if time.time() - self.timeNoFace > 10.:
                self.timeNoFace = time.time()
                if self.ab: self.ab.resetHead()
                

            rTimeSinceGlobalLastInteraction = time.time() - self.rTimeGlobalLastInteraction
            print("rTimeSinceGlobalLastInteraction: %s" % rTimeSinceGlobalLastInteraction )
            if rTimeSinceGlobalLastInteraction < 5:
                if self.ab: self.ab.showInteraction( None,None )
                self.bWasInteracting = 1
            else:
                if self.bWasInteracting:
                    self.bWasInteracting = 0
                    if self.ab: self.ab.stopInteraction()
                        
            return 0,0,0,0
        
        bSomeFace = 1
        self.timeNoFace = time.time()
        if 0:
            # select only centered faces
            faces = [face_detector_cv3.selectFace(faces,img.shape)]
        else:
            # all faces
            pass
        for face in faces:
            print("DBG: updateImage: face: %s" % str(face) )
            startX, startY, endX, endY, confidence = face
            # ajoute un peu autour du visage
            nAddedOffsetY = int((endY-startY)*0.25)
            nAddedOffsetX = int(nAddedOffsetY*0.6)
            x1,y1,x2,y2=startX, startY, endX, endY
            x1 = max(x1-nAddedOffsetX,0)
            y1 = max(y1-nAddedOffsetY,0)
            x2 = min(x2+nAddedOffsetX,img.shape[1])
            y2 = min(y2+nAddedOffsetY,img.shape[0])
            
            imgFace = img[y1:y2,x1:x2]
            timeBegin = time.time()
            retVal = self.cs.imageReco_continuousLearn(imgFace)
            print( "INF: reco ret: %s, duration: %.2fs\n" % (str(retVal), time.time()-timeBegin ))
            # avec un perso (moi), depuis mon ordi.
            # computation time:
            # - sur mstab7: 0.48s (locale) / 0.55s / 0.58s avec tout -  (extras takes 0.03s, angle, smile and mood takes 0.07s)
            #    apres optim avec angle smile mood: 0.45s
            # - sur agx (plus long car network): 0.20 (mais no extra info); avec extra: 0.72 
            #    apres optim avec angle smile mood: 0.37s (mode1) 
            #    apres optim avec angle smile mood: 0.19s (mode0)
            
            if retVal != False and retVal[0] != -1:
                nHumanID = retVal[1][0][1]
                faceposrelativeaucrop = retVal[1][0][2]  # attention: la pos du  visage  est dans l'image croppe donc pas la bonne position !
                listExtras = retVal[1][0][3]
                strTxt = "%d"%nHumanID
                strTxt2 = ""
                strTxt3 = ""
                strTxt4 = ""
                strTxt5 = ""
                strTxt6 = ""
                strTxt7 = ""
                bLookAt = 0
                bNear = 0
                bInteract = 0
                if nHumanID != -1:
                    hface = endY-startY
                    bNear = hface>150 # was 60
                    print("hface: %s" % hface )
                    if nHumanID not in self.aHumanKnowledge.keys():
                        self.aHumanKnowledge[nHumanID] = HumanKnowledge(nHumanID)
                    self.aHumanKnowledge[nHumanID].nTotalSeen += 1
                    strCurrentDay = misctools.getDayStamp()
                    if strCurrentDay != self.aHumanKnowledge[nHumanID].strDayLastSeen:
                        # premiere fois du jour
                        if self.aHumanKnowledge[nHumanID].nTotalSeen>100:
                            if self.ab: self.ab.showHappy( face,self.aHumanKnowledge[nHumanID],self.aHumanKnowledge[nHumanID].nTotalSeen/100 )
                        
                        self.aHumanKnowledge[nHumanID].nSeenToday = 1
                        if misctools.getDiffTwoDateStamp(self.aHumanKnowledge[nHumanID].strDayLastSeen,strCurrentDay ) > 1:
                            self.aHumanKnowledge[nHumanID].nDayStreak = 0
                        else:
                            self.aHumanKnowledge[nHumanID].nDayStreak = 0
                        self.aHumanKnowledge[nHumanID].strDayLastSeen = strCurrentDay
                    else:
                        self.aHumanKnowledge[nHumanID].nSeenToday += 1
                    strTxt2 += "TotalSeen: %d" % (self.aHumanKnowledge[nHumanID].nTotalSeen)
                    strTxt3 += "nSeenToday: %d" % (self.aHumanKnowledge[nHumanID].nSeenToday)
                    strTxt4 += "nDayStreak: %d" % (self.aHumanKnowledge[nHumanID].nDayStreak)
                    emo = misctools.findInNammedList(listExtras,"emotion")
                    if emo != None:
                        strTxt5 = str(emo)
                    ori = misctools.findInNammedList(listExtras,"orientation")
                    if ori != None:
                        yaw,pitch,roll = ori[1]
                        strTxt6 = "orient: %.2f,%.2f,%.2f"%(yaw,pitch,roll)
                        bLookAt = abs(yaw)<0.1 and abs(pitch)<0.5 # le pitch n'est pas si important que ca!
                        if bLookAt: 
                            strTxt6 += " LOOKAT"
                        bSomeoneLook = 1
                    rTimeSinceLastInteraction = time.time() - self.aHumanKnowledge[nHumanID].rTimeLastInteraction
                if bNear:
                    strTxt6 += " NEAR"
                    bSomeoneNear = 1
                if bLookAt and bNear:
                    strTxt6 += " INTERACT"
                    bInteract = 1
                    bSomeoneInteract = 1

                print("rTimeSinceLastInteraction: %s" % rTimeSinceLastInteraction )                    
                if bInteract:
                    self.rTimeGlobalLastInteraction = time.time()
                    self.bWasInteracting = bInteract

                    if rTimeSinceLastInteraction < 5:
                        # we were in interaction
                        self.aHumanKnowledge[nHumanID].rDurationInteraction += rTimeSinceLastInteraction
                        self.aHumanKnowledge[nHumanID].rTotalInteraction += rTimeSinceLastInteraction
                        if self.ab: self.ab.showInteraction( face,self.aHumanKnowledge[nHumanID] )
                    else:
                        # it's a new interaction
                        self.aHumanKnowledge[nHumanID].rDurationInteraction = 0
                        if self.ab: self.ab.startInteraction( face,self.aHumanKnowledge[nHumanID] )
                        print("start interaction")
                    self.aHumanKnowledge[nHumanID].rTimeLastInteraction = time.time()
                    strTxt7 += "time interact: %.2f" % self.aHumanKnowledge[nHumanID].rDurationInteraction
                
                if not bInteract:
                    if rTimeSinceLastInteraction >= 5:
                        if self.bWasInteracting:
                            self.bWasInteracting = False
                            if self.ab: self.ab.stopInteraction()
                    if bLookAt:
                        if self.ab: self.ab.reactToLookAt(face,self.aHumanKnowledge[nHumanID])
                    if bNear:
                        if self.ab: self.ab.reactToNear(face,self.aHumanKnowledge[nHumanID])
                        
                if bAddDebug:
                    y = endY-10
                    dy = 22
                    nFontId = cv2.FONT_HERSHEY_SIMPLEX
                    rFontSize = 0.8
                    nFontThick = 2
                    colFont = (255,255,255)
                    cv2.putText(img,strTxt,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    
                    rFontSize /= 2
                    dy //= 2
                    nFontThick //= 2
                    cv2_tools.putTextCentered(img,strTxt2,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    cv2_tools.putTextCentered(img,strTxt3,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    cv2_tools.putTextCentered(img,strTxt4,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    cv2_tools.putTextCentered(img,strTxt5,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    cv2_tools.putTextCentered(img,strTxt6,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    cv2_tools.putTextCentered(img,strTxt7,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    
                    if bLookAt:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,255,255))

                    if bInteract:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,0,0))
            # for face

        return bSomeFace, bSomeoneLook, bSomeoneNear, bSomeoneInteract
                        
# class HumanManager - end
humanManager = HumanManager()


def realLifeTestWebcam():
    hm = humanManager
    cap = cv2.VideoCapture(0) #ouvre la webcam
    while 1:
        ret, img = cap.read() # lis et stocke l'image dans frame
        if img is None:
            continue
        print(img.shape)
        
        #~ img = cv2.resize(img, None, fx=0.5,fy=0.5)
        
        bAddDebug = 0
        bAddDebug = os.name == "nt"
        
        hm.updateImage(img, bAddDebug=bAddDebug)
        
        # Display the output
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break
    hm = None # call to del and save
    humanManager.save() # now hm is the global object, it not saved anymore when Noning it!
    
# realLifeTestWebcam - end


if __name__ == "__main__":
    realLifeTestWebcam()