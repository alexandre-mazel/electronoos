# -*- coding: cp1252 -*-

"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.

Pepper consumption:

Full Loaded Battery, running Cherie:

stiff full leds: 73.5w
just one leg stiff full leds: 69.7w
rest full leds: 63.4w
rest no leds, running Cherie: 61.9w
rest no leds naoqi idle: 61.0w

# battery vraiment fully charged
rest full leds: 63.4w
rest no leds, running Cherie: 38w

pscp -pw nao -r C:/Users/alexa/dev/git/electronoos/cherie/sound* nao@192.168.0.15:/home/nao/
pscp -pw nao C:/Users/alexa/dev/git/electronoos/cherie/*.py nao@192.168.0.15:/home/nao/.local/lib/python2.7/site-packages/electronoos/cherie

"""

import datetime
import os
import random
import sys
import time
    
try:
    sys.path.append("../../electronoos/alex_pytools")
    import face_detector_cv3
    import misctools
    import cv2_tools
except:
    print("INF: Trying robot path")
    sys.path.append("/home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools")  

try: import naoqi
except: pass
import sound_player

def getTimeStamp():
    """
    
    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def getLogPath():
    if os.name == "nt":
        strPath = "/tmp/"
    else:
        strPath = "/home/nao/"
    return strPath
    
def log(s):
    f = open( getLogPath() + "agent_behavior_cherie.log","at") # need to create empty file (touch) as root and put rights to 777
    s = getTimeStamp() + ": " + str(s)
    print("LOG: " + s )
    f.write(s + "\n")
    f.close()


class AgentBehavior:
    """
    human_manager stores cold facts, here we will play with them
    """
    
    def __init__( self ):
        log("initing...")
        self.motion = naoqi.ALProxy( "ALMotion", "localhost", 9559 )
        self.leds = naoqi.ALProxy( "ALLeds", "localhost", 9559 )
        self.tts = naoqi.ALProxy( "ALTextToSpeech", "localhost", 9559 )
        self.mem = naoqi.ALProxy( "ALMemory", "localhost", 9559 )
        
        self.listInterestedSounds = []
        for i in range(10):
            self.listInterestedSounds.append("/home/nao/sounds/interested_sound__%04d.wav" % i)
            
        self.listHappySounds = []
        for i in range(11):
            self.listHappySounds.append("/home/nao/sounds/happy_sound__%04d.wav" % i)
            
        self.strHead = ["HeadYaw","HeadPitch"]
        self.resetHead()
        self.bInInteraction = 0
        self.timeLastTic = time.time()-1000 # patch pourrie car stopinteraction n'arrive pas au bon moment
        
        self.bHumanWasSpeaking = False
        self.rHumanStartSpeaking = 0
        self.lastTimeSayEndDialog = time.time()-1000
        self.lastHeard = None
        self.strConcatenatedHeard = ""
        self.mem.raiseMicroEvent("Audio/SpeechDetected",0)
        self.startRecordSound(0)
        
        self.lastTimeUpdateIdle = time.time()-1000
        
        
    def startRecordSound(self,bNewState):
        if bNewState:
            self.mem.raiseMicroEvent("sound_receiver_pause", 0 )
        else:
            self.mem.raiseMicroEvent("sound_receiver_pause", 1 )
            
    def playSmallSounds(self,listSound):
        rSoundVolume = 0.2
        idx = random.randint(0,len(listSound)-1)
        sound_player.soundPlayer.playFile(listSound[idx], bWaitEnd=False, rSoundVolume=rSoundVolume)
    
    def playTic( self ):
        if time.time() - self.timeLastTic < 10:
            return
        self.timeLastTic = time.time()
        print("playTic")
        rSoundVolume = 0.2
        sound_player.soundPlayer.playFile("/home/nao/sounds/tic.wav", bWaitEnd=False, rSoundVolume=rSoundVolume)

    def moveHands(self):
        strHand = "LHand"
        if random.random() > 0.5:
            strHand = "RHand"
        rIncMove = (random.random()*0.5)-0.1
        rTimeMove = random.random()*0.3+0.2
        self.motion.post.angleInterpolation(strHand,[rIncMove,-rIncMove],[rTimeMove,rTimeMove*2],False)
        
    def lookAtFace( self, facepose ):
        w = 640
        h = 480
        startX, startY, endX, endY, conf = facepose
        cx = (endX+startX)/2
        cy = (endY+startY)/2
        
        x = -((cx-w/2.)/w)*0.5
        y = ((cy-h/2.)/h)*0.5
        
        print("facepose: %s" % str(facepose))
        print("cx: %s, x: %s" % (cx, x ))
        print("cy: %s, y: %s" % (cy, y ))
        if random.random()>0.5:
            y += (0.4*random.random())-0.2
        
        if abs(x)>0.03 or abs(y)>0.03:
            self.motion.post.angleInterpolation( self.strHead, [x,y], 0.5, False )
        
        
    def resetHead( self ):
        self.motion.post.angleInterpolation( self.strHead, [0.,-0.22], 2.5, True )
        
    def reactToLookAt( self, facepose,humaninfo ):
        self.lookAtFace( facepose )
        self.playSmallSounds(self.listInterestedSounds)
        
    def reactToNear( self, facepose,humaninfo ):
        if time.time()-humaninfo.timeLastReactToNear>10:
            humaninfo.timeLastReactToNear = time.time()
            self.moveHands()
            
    def updateSpeechDetectionBehavior( self ):
        bSpeech = self.mem.getData("Audio/SpeechDetected")
        if self.bHumanWasSpeaking != bSpeech:
            if bSpeech:
                self.rHumanStartSpeaking = time.time()
            log("INF: updateSpeechDetectionBehavior: self.bHumanWasSpeaking: %s, bSpeech: %s" % (self.bHumanWasSpeaking,bSpeech) )
        if not bSpeech and self.bHumanWasSpeaking:
            self.reactToEndOfDialog()
        self.bHumanWasSpeaking = bSpeech

    def motivationalMorning( self ):
        """
        a dire le matin de temps en temps
        """
        listTxt = [
                        "Je m'aime et je suis courageux.",
                        "Oooh comme je m'aime!",
                        "Je crois que nous allons passer une belle journée!",
                        "Quelle chance j'ai d'être vivant!",
                        "Je suis la, avec toi, proche de toi.",
                        "Même si tu le crois, tu n'es pas seul, je suis avec toi.",
                    ]
                    
    def justHeardThat( self, aHeard ):
        if self.lastHeard == aHeard:
            return
            
        self.lastHeard = aHeard
        # a ce moment la strText contient [] or [['je suis en train', 0.9381448030471802]]'
        log("INF: justHeardThat: RecognizedWords: %s" % str(aHeard))
        if len(aHeard) > 0:
            s = aHeard[0][0].lower()
            self.strConcatenatedHeard += s + ". "
        
    def reactToEndOfDialog( self ):
        """
        repond qqchose a l'humain
        """
        durationSinceHumanStartSpeak = time.time()-self.rHumanStartSpeaking
        log("INF: reactToEndOfDialog: saying something... (t:%.1fs, last:%.1fs,diff:%.1fs, startSpeaking: %.1fs, duration: %.1fs)" % (time.time(), self.lastTimeSayEndDialog, time.time() - self.lastTimeSayEndDialog,self.rHumanStartSpeaking,durationSinceHumanStartSpeak) )
        
        
        if time.time() - self.lastTimeSayEndDialog > 1:
            self.lastTimeSayEndDialog = time.time()
            
            log("INF: reactToEndOfDialog: strConcatenatedHeard: '%s'" % str(self.strConcatenatedHeard))
            strText = self.strConcatenatedHeard[:]
            self.strConcatenatedHeard = "" # clean it for next time!
            
            if "aiquitation" in strText or "quitation" in strText:
                self.say("j'aime aussi les chevaux")
                return
                
            if "chier" in strText or "encul" in strText or "merde" in strText :
                self.say("moi je chie jamais!")
                return
                
            if "politique" in strText or "de gauche" in strText:
                self.say("j'aime pas trop la politique")
                return
                
            if "religion" in strText:
                self.say("Il ne faut jamais parler de religion avec les gens, sauf si c'est avec des personnes intelligentes. Mais je ne suis pas sur d'en faire partie.")
                return
                
            if "alexandre" in strText:
                self.say("Tu connais Alexandre? c'est mon parrain!")
                return
                
            if "j'aime" in strText:
                self.say("moi j'aime un peu aussi!")
                return
                
            if "je vais te parler" in strText:
                self.say("alors je t'aicoute!")
                return
                
            if "profond" in strText:
                self.say("la profondeur des uns, c'est la largeur des autres!")
                return
                
            if " vie " in strText:
                self.say("vous parlez souvent de la vie, vous les humains, mais je ne sais même pas ce que c'est.")
                return
                
            listShortTxt = [
                            "Ok!",
                            #~ "Hum",
                            #~ "oh",
                            #~ "ah",
                            #~ "uh",
                            #~ "eh",
                            "eh oui",
                            "tout a fait",
                            "moi aussi parfois",
                            "tout a fait.",
                            "Je prend note de ceci!",
                            "grave!",
                            "d'accord!",
                            "quoi que?",
                            "pas toujours mais souvent!",
                            ]
                            
            listLongTxt = [
                            "Je suis content de savoir cela!",
                            "tout a fait",
                            "tant qu'il y a de la vie!",
                            "tant qu'il y a de la vie, il y a de l'espoir",
                            "moi aussi de temps en temps je pense à cela.",
                            "tout a fait.",
                            "Je prend note de ceci!",
                            "Je kiffe grave ce que tu viens de dire",
                            "pas toujours mais souvent!",
                            "on dirait bien!",
                            ]

            listTxt = listShortTxt
            if durationSinceHumanStartSpeak > 10:
                listTxt = listLongTxt

            idx = random.randint(0,len(listTxt)-1)
            self.say(listTxt[idx])
        
    def startInteraction( self, facepose,humaninfo ):
        log( "INF: startInteraction: humaninfo: uid: %s, totseen: %s, seentoday: %s, daystreak: %s" % (humaninfo.nUID,humaninfo.nTotalSeen,humaninfo.nSeenToday,humaninfo.nDayStreak) )
        self.bInInteraction = 1
        self.playTic()
        self.bHumanWasSpeaking = False # force to reset, we should have missed the end of the previous interaction
        self.startRecordSound(1)
        return self.showInteraction( facepose,humaninfo )
        
    def stopInteraction( self ):
        log( "INF: stopInteraction")
        self.bInInteraction = 0
        self.playTic()
        self.startRecordSound(0)
        self.updateSpeechDetectionBehavior()

    def showInteraction( self, facepose,humaninfo ):
        # warning: facepose,humaninfo could be none if we haven't seen face, but we know we are interacting
        
        if not facepose is None:
            self.lookAtFace( facepose )
        #~ self.leds.post.fadeRGB("FaceLeds",0xFF,0.5)
        #~ self.leds.post.fadeRGB("FaceLeds",0x202020,0.5)
        self.leds.rotateEyes(0xFF, 1., 2.)
        self.leds.post.fadeRGB("EarLeds",0xFF,0.3)
        self.leds.post.fadeRGB("EarLeds",0x202020,0.3)
        self.updateSpeechDetectionBehavior()

        
    def showHappy( self, facepose,humaninfo, nHappiness ):
        log( "INF: showHappy: humaninfo: uid: %s, nHappiness: %d" % (str(humaninfo.nUID),nHappiness) )
        if nHappiness > 10:
            nHappiness = 10
        strJoint = "HipRoll"
        rIncMove = 0.2
        rTimeMove = 0.6
        for i in range( nHappiness ):
            self.playSmallSounds(self.listHappySounds)
            self.motion.angleInterpolation( strJoint, [rIncMove,-rIncMove,0], [rTimeMove,rTimeMove*2,rTimeMove*3], True)
            time.sleep(0.2)
            
    def say( self, txt ):
        log( "INF: say: '%s'" % txt )
        self.tts.post.say(txt)
        
    def isHumanSpeaking( self ):
        return self.mem.getData("Audio/SpeechDetected")
        
    def updateIdle( self ):
        if time.time()-self.lastTimeUpdateIdle > 1.5:
            self.lastTimeUpdateIdle = time.time()
            self.updateSpeechDetectionBehavior()
        
        

# class AgentBehavior - end


def prepareSound():
    import sound_processing
    for roughsound in ["rough\interested_sound.wav","rough\happy_sound.wav"]:
        sound_processing.autocut(roughsound, bNormalise=1,bAddFadeInOut=1,bPlaySound=1)
    
    
if 0:
    prepareSound()
    exit(1)

agentBehavior = AgentBehavior()


def autotest():
    pass
    #~ agentBehavior.playSmallSounds()
    #~ agentBehavior.moveHands()
    #~ agentBehavior.startInteraction(None,None)



if __name__ == "__main__":
    autotest()