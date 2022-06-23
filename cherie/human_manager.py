"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.

Launch server On AGX:
cd ~/dev/git/electronoos/scripts/versatile
nohup python3 run_cloud_server.py

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
import cloud_services

sys.path.append("../../electronoos/alex_pytools")
import face_detector_cv3
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
        
    def as_dict(self):
        #~ strOut = json.dumps((self.nUID,self.nTotalSeen,self.nSeenToday,self.nDayStreak),indent=2,ensure_ascii =False)
        #~ strOut = '{"HumanKnowledge": 1,"uid": %d, "totalseen": %d, "seentoday": %d, "daystreak": %d}' % (self.nUID,self.nTotalSeen,self.nSeenToday,self.nDayStreak)
        #~ strOut =  json.dumps(self.__dict__)
        #~ return strOut
        return self.__dict__

    def from_dict(self, dct: dict):
        #~ print("DBG: from_dict: %s" % dct )       
        self.nUID = dct['nUID']
        self.nTotalSeen = dct['nTotalSeen']
        self.nSeenToday = dct['nSeenToday']
        self.nDayStreak = dct['nDayStreak']
        self.strDayLastSeen = dct['strDayLastSeen']
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
        #~ self.cs = cloud_services.CloudServices( "robot-enhanced-education.org", 25340 )
        self.cs = cloud_services.CloudServices( "localhost", 13000 )
        self.cs.setVerbose( True )
        self.cs.setClientID( "test_on_the_fly" )
        self.fdcv3 = face_detector_cv3.facedetector
        self.strSaveFilename = misctools.getUserHome() + "save/"
        try:
            os.makedirs(self.strSaveFilename)
        except: pass
        self.strSaveFilename += "cherie_human_manager.dat"
        self.aHumanKnowledge = {} # uid => HumanKnowledge
        self.load()
        
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
        return False on server problem
        """
        #~ if not self.cs.isRunning():
            #~ return False
        resDetect = self.fdcv3.detect(img,bRenderBox=False,confidence_threshold=0.4) # ~0.06s on mstab7 on a VGA one face image
        if len(resDetect) > 0:
            if 0:
                # select only centered faces
                faces = [face_detector_cv3.selectFace(resDetect,img.shape)]
            else:
                # all faces
                faces = resDetect
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
                print( "reco ret: %s, duration: %.2fs\n" % (str(retVal), time.time()-timeBegin ))
                # avec un perso (moi), depuis mon ordi.
                # computation sur mstab7: 0.48s (locale)
                # sur agx (plus long car network): 0.20 (mais no extra info)
                if retVal != False:
                    nHumanID = retVal[1][0][1]
                    listExtras = retVal[1][0][2]
                    strTxt = "%d"%nHumanID
                    strTxt2 = ""
                    strTxt3 = ""
                    strTxt4 = ""
                    strTxt5 = ""
                    strTxt6 = ""
                    bLookAt = 0
                    bNear = 0
                    bInteract = 0
                    if nHumanID != -1:
                        hface = endY-startY
                        bNear = hface>60
                        if nHumanID not in self.aHumanKnowledge.keys():
                            self.aHumanKnowledge[nHumanID] = HumanKnowledge(nHumanID)
                        self.aHumanKnowledge[nHumanID].nTotalSeen += 1
                        strCurrentDay = misctools.getDayStamp()
                        if strCurrentDay != self.aHumanKnowledge[nHumanID].strDayLastSeen:
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
                            bLookAt = abs(yaw)<0.55 and abs(pitch)<0.2
                            if bLookAt: strTxt6 += " LOOKAT"
                    if bNear:
                        strTxt6 += " NEAR"
                    if bLookAt and bNear:
                        strTxt6 += " INTERACT"
                        bInteract = 1
                    y = endY+5
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
                    
                    if bLookAt:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,255,255))

                    if bInteract:
                        cv2.rectangle(img,(startX,startY),(endX, endY),(255,0,0))
                        
# class HumanManager - end



def realLifeTestWebcam():
    hm = HumanManager()
    cap = cv2.VideoCapture(0) #ouvre la webcam
    while 1:
        ret, img = cap.read() # lis et stocke l'image dans frame
        if img is None:
            continue
        print(img.shape)
        
        #~ img = cv2.resize(img, None, fx=0.5,fy=0.5)
        
        hm.updateImage(img)
        
        # Display the output
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break
    hm = None # call to del and save



if __name__ == "__main__":
    realLifeTestWebcam()