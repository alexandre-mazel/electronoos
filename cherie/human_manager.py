# -*- coding: cp1252 -*-

"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.

Launch server On AGX:
cd ~/dev/git/electronoos/scripts/versatile
nohup python3 run_cloud_server.py &

# bug a voir:
ader.cc:48] Successfully opened dynamic library libnvinfer_plugin.so.7
am@am-desktop:~/dev/git/electronoos/scripts/versatile$ tail nohup.out
DBG: detectEmotion: ssd detect takes 0.000s
DBG: detectEmotion: preprocess takes 0.000s
DBG: detectEmotion: net takes 0.150s
INF: detectEmotion: detected:
[[(110, 96, 129, 129), 0, 0.9584208130836487, 'Neutral']]
INF: detectEmotion total processing: 0.151s
DBG: continuousLearnFrom: detectedEmotions: [[(110, 96, 129, 129), 0, 0.9584208130836487, 'Neutral']]
DBG: continuousLearnFromImg: angle, smile and mood takes 0.17s
DBG: continuous_learn: retVal: (1, 2, [110, 96, 239, 225], (('orientation', [0.0, -0.13906162699743954, -0.010869137177270227], 666), ('smile', -0.49528985507246376, 0.4166666666666667), ('emotion', 'Neutral', 0.9584208130836487), ('gender', 0, 0.6), ('age', 58, 0.6))) (db has 0 peoples)
WRN/ERR: continuous_learn: users all disappeared !?! (if first time then ok)am@am-desktop:~/dev/git/electronoos/scripts/versatile$


# ou en local windows:
cd C:\\Users\\alexa\\\dev\\git\\electronoos\\scripts\\versatile
python run_cloud_server.py

# mettre a jour le robot:
pscp -pw nao -P 55022 C:/Users/alexa/dev/git/electronoos/cherie/*.py nao@engrenage.studio:/home/nao/.local/lib/python2.7/site-packages/electronoos/cherie

# NB: le misctools.py a utiliser est celui de /home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools

# lancer le soundrecorder sur le robot (maintenant lancer automatiquement depuis /home/nao/run_cherie.sh, call depuis /etc/profile)
killall python2.7; nohup python -c "import abcdk.sound_analyser; abcdk.sound_analyser.launchSoundReceiverFromShell('localhost',False)"&
# launching two of them will fail "already registered", that's fine !
# voir si il est lancé (devrait etre 2)
ps eax | grep sound_analyser | wc


# mise a jour du robot chez brice:
pscp -pw naonao C:/Users/alexa/dev/git/electronoos/cherie/*.py nao@87.90.82.139:/home/nao/.local/lib/python2.7/site-packages/electronoos/cherie & pscp -pw naonao C:/Users/alexa/dev/git/abcdk/sdk/abcdk/sound_a*.py nao@87.90.82.139:/home/nao/.local/lib/python2.7/site-packages/abcdk/ & pscp -pw naonao C:/Users/alexa/dev/git/electronoos/alex_pytools/misc*.py nao@87.90.82.139:/home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools/ &

# tout abcdk:
pscp -r -pw naonao C:/Users/alexa/dev/git/electronoos/* nao@87.90.82.139:/home/nao/.local/lib/python2.7/site-packages/electronoos/
# que alextools
pscp -r -pw naonao C:/Users/alexa/dev/git/electronoos/alex_pytools/* nao@87.90.82.139:/home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools/

# voir des stats:
sur agx:
df . -h
/dev/mmcblk0p1   28G   22G  5,0G  81% /
ls /home/am/imgs/Jarc/* | wc
  24568   24568 1350378
  
# monitor sur le robot:
cd ./.local/lib/python2.7/site-packages/electronoos/cherie/
python monitor_pepper.py

# voir sur les images sur le serveur
./dev/git/electronoos/scripts/view_img.py ~/imgs/Jarc/

# log interessant:
cat /home/nao/agent_behavior_cherie.log



# in case of problem:
# taskkill /F /im python.exe

# continuer a tester la speech reco speech_reco_test dans le dossier scripts

# copier les sons depuis le robot:
pscp -pw naonao nao@87.90.82.139:/home/nao/recorded/rawWavs/* d:\cherie_sound_record\

# rsync -rv --size-only nao@87.90.82.139:/home/nao/recorded/rawWavs/ /mnt/d/cherie_sound_record/ # d n'est pas monté!



"""

import cv2
import json
import os
import sys
import random
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

def getTitleFromGenderAge(listExtras):
    astr = [
                    ["jeune homme", "Monsieur"],
                    ["jeune femme", "Madame"],
                    ["jeune humain", "Humain"],
    ]
    gender = misctools.findInNammedListAndGetFirst(listExtras,"gender",2) # no value => 2
    age = misctools.findInNammedListAndGetFirst(listExtras,"age",100)
    idxAge = 0
    if age >= 20:
        idxAge = 1
    return astr[gender][idxAge]
    
def computerSay( txt ):
    import tts
    tts.tts.load()
    tts.tts.say(txt)

class HumanKnowledge:
    def __init__( self, nUID = -1):
        self.nUID = nUID
        self.strFirstName = ""
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
            self.strFirstName = dct['strFirstName']
            
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
        
        if self.bPepper or 1:
            self.cs = cloud_services.CloudServices( "robot-enhanced-education.org", 25340 )
        else:
            computerSay("demarrage")
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
        
        self.lastTimeSaySomething = time.time()-1000
        
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
        print(str(self.aHumanKnowledge))
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
            
            
        # reglage selon la machine:
        if os.name == "nt":
            hFaceTreshold = 74
        else:
            hFaceTreshold = 130
        
        if self.bPepper:
            try:
                aHeard = self.mem.getData("Audio/RecognizedWords")
                if aHeard != []:
                    if self.ab: self.ab.justHeardThat(aHeard)
            except BaseException as err:
                print("ERR: retrieve Audio/RecognizedWords: %s" % str(err))
            
        
            
        wImg = img.shape[1]
            
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
            if self.ab: self.ab.updateIdle()
                

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
            try:
                retVal = self.cs.imageReco_continuousLearn(imgFace)
            except BaseException as err:
                print("ERR: updateImage: while imagereco: %s" % (str(err)))
                break # quit faces analyse
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
                strTxt = "%d" % nHumanID
                strTxt2 = ""
                strTxt3 = ""
                strTxt4 = ""
                strTxt5 = ""
                strTxt6 = ""
                strTxt7 = ""
                strTxtInfo = ""
                strSay = ""
                bLookAt = 0
                bNear = 0
                bInteract = 0
                if nHumanID != -1:
                    hface = endY-startY
                    bNear = hface>hFaceTreshold # was 60
                    print("hface: %s" % hface )
                    if nHumanID not in self.aHumanKnowledge.keys():
                        self.aHumanKnowledge[nHumanID] = HumanKnowledge(nHumanID)
                    self.aHumanKnowledge[nHumanID].nTotalSeen += 1
                    strCurrentDay = misctools.getDayStamp()
                    if strCurrentDay != self.aHumanKnowledge[nHumanID].strDayLastSeen:
                        # premiere fois du jour
                        # TODO: décorreller le comptage de la reaction qui dit bonjour: dire que si seentoday < petit il faut parler actuellement si = 0
                        if self.aHumanKnowledge[nHumanID].nTotalSeen>10:
                            if self.aHumanKnowledge[nHumanID].nTotalSeen>1000:
                                strSay = "Bonjour %s !" % self.aHumanKnowledge[nHumanID].strFirstName
                            else:
                                strSay = "Bonjour %s !" % getTitleFromGenderAge(listExtras)
                            if self.ab: self.ab.showHappy( face,self.aHumanKnowledge[nHumanID],self.aHumanKnowledge[nHumanID].nTotalSeen/100 )
                        
                        self.aHumanKnowledge[nHumanID].nSeenToday = 1
                        if misctools.getDiffTwoDateStamp(self.aHumanKnowledge[nHumanID].strDayLastSeen,strCurrentDay ) > 1:
                            self.aHumanKnowledge[nHumanID].nDayStreak = 0
                        else:
                            self.aHumanKnowledge[nHumanID].nDayStreak = 0
                        self.aHumanKnowledge[nHumanID].strDayLastSeen = strCurrentDay
                        self.save()
                    else:
                        self.aHumanKnowledge[nHumanID].nSeenToday += 1
                        if self.aHumanKnowledge[nHumanID].nSeenToday % 200 == 0:
                            self.save()
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
                        bLookAt = abs(yaw)<0.25 and abs(pitch)<0.5 # le pitch n'est pas si important que ca!,  yaw was 0.18
                        if bLookAt: 
                            strTxt6 += " LOOKAT"
                        bSomeoneLook = 1

                    rTimeSinceLastInteraction = time.time() - self.aHumanKnowledge[nHumanID].rTimeLastInteraction
                
                    if bAddDebug:
                        nGender = misctools.findInNammedList(listExtras,"gender")
                        if nGender != None:
                            strTxtInfo += "gender: %s, "%(nGender[1])
                        nAge = misctools.findInNammedList(listExtras,"age")
                        if nAge != None:
                            strTxtInfo += "age: %s, "%(nAge[1])
                # end user == -1
                
                if bNear:
                    strTxt6 += " NEAR"
                    bSomeoneNear = 1
                if bLookAt and bNear:
                    strTxt6 += " INTERACT"
                    bInteract = 1
                    bSomeoneInteract = 1

                print("rTimeSinceLastInteraction: %s, strTxt6: %s\n" % (rTimeSinceLastInteraction,strTxt6) )                    
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
                        self.saySomething()
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
                    cv2_tools.putTextCentered(img,strTxtInfo,(int((startX+endX)/2)-10, y),nFontId, rFontSize, colFont, thickness = nFontThick );y+=dy
                    
                    if strSay != "":
                        cv2_tools.putTextCentered(img,strSay,(wImg//2, 100),nFontId, rFontSize*2, colFont, thickness = nFontThick );y+=dy
                        self.say(strSay)
                    
                    if bLookAt:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,255,255))

                    if bInteract:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,0,0))
            # for face

        return bSomeFace, bSomeoneLook, bSomeoneNear, bSomeoneInteract
                        
                        
    def say(self, txt):
        print('#'*40 + " SAY " + '#'*40)
        print("DBG: Saying: '%s'" % txt )
        if self.ab: 
            self.ab.say(txt)
        else: 
            computerSay(txt)
            
    def saySomething( self ):
        """
        ici il faudrait trouver un truc a dire.
        """
        print("DBG: saySomething: ICI il faudrait dire un truc si l'humain ne parle pas.")
        
        if time.time() - self.lastTimeSaySomething > 5*60:
            if self.ab and self.ab.isHumanSpeaking():
                return
            self.lastTimeSaySomething = time.time()
            listTxt = [
                            "Ca va ?",
                            "Tu fais quoi ?",
                            "Que va tu faire maintenant?",
                            "C'est le bon moment pour une pause!",
                            "C'est le bon moment pour une sieste!",
                            "C'est le bon moment pour appeller un ami!",
                            "C'est le bon moment pour souffler!",
                            "C'est le bon moment pour boire un verre d'eau!",
                            'Et au faite aime tu les haricots verts ?',
                            "Tu es vraiment super!",
                            "Je t'adore en tant qu'humain",
                            "Heureusement que tu es la!",
                            "Quand tu n'es pas la, je m'ennuie.",
                            "Penses a te reposer!",
                            "Tu devrais faire une pause!",
                            "Une journée sans rire, c'est une journée ou on ne rigole pas!",
                            "Aujourd'hui c'est un bon jour pour prendre une bonne raisolution de vie.",
                            ]

            idx = random.randint(0,len(listTxt)-1)
            self.say(listTxt[idx])
        
        
# class HumanManager - end
humanManager = HumanManager()


def realLifeTestWebcam():
    hm = humanManager
    cap = cv2.VideoCapture(0) #ouvre la webcam (0 for front or 1 for back)
    while 1:
        ret, img = cap.read() # lis et stocke l'image dans frame
        if img is None:
            continue
        print(img.shape)
        
        #~ img = cv2.resize(img, None, fx=0.5,fy=0.5)
        
        bAddDebug = 1
        bAddDebug = 0
        bAddDebug = os.name == "nt"
        bAddDebug = 1
        
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