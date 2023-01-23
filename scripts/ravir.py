# coding: cp1252

"""
Sophie et Marie-Cécile.

Breath engine for RAVIR project
# copy manually all breathing to Pepper:
scp -r C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/breath* nao@192.168.0.:/home/nao/
scp -r C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/cut* nao@192.168.0.:/home/nao/
scp C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/t*.wav nao@192.168.0.:/home/nao/noises/ # need to create folder before
scp d:/Python38-32/Lib/site-packages/opensimplex/*.py nao@192.168.0.:/home/nao/.local/lib/python2.7/site-packages/
or
scp D:\Python38-32_dont_use\Lib/site-packages/opensimplex/*.py nao@192.168.0.:/home/nao/.local/lib/python2.7/site-packages/


# update la demo
scp C:/Users/alexa/dev/git/electronoos/scripts/rav*.py nao@192.168.1.211:/home/nao/dev/git/electronoos/scripts/

Currently I'm inserting a silence at the beginning of each breath:
sound_processing:
        rTimeAdded = 0.1
        strPath = "/tmp2/brea/selected_intake/"
        strPath = "/home/nao/breath/selected_intake/"
        insertSilenceInFolder(strPath, rTimeAdded)
        insertSilenceInFolder("/home/nao/breath/selected_outtake/", rTimeAdded)

So we wait a bit for the body motion reaction.

* About voice generation:
# original in
C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/cut/

- recorded in the studio
- autocut and rename from sound_processing.py
- Dans audacity:
-    Rovee plugins, presets pepper_ravir (20/2/100)
-    Noise reduction
-    (shift+ctrl+R fait les 2 actions et ferme le fichier)
- sound_processing.changeVolumeInFolder(,2) # pour arriver a un son qui se tient d'un jour d'enregistrement a l'autre

# Record images during experience:
cd ~/dev/git/protolab_group/scripts
nohup python nao_camera_viewer.py

# copy le script depuis l'ordi:
scp C:\Users\alexa\dev\git\electronoos\demos_nao_and_pepper\nao_camera_viewer_for_ravir_new.py nao@192.168.1.211:/home/nao/dev/git/protolab_group/scripts/nao_camera_viewer.py

# backup le script nao_camera_viewer sur mon ordi:
scp nao@192.168.1.211:/home/nao/dev/git/protolab_group/scripts/nao_camera_viewer.py C:\Users\alexa\dev\git\electronoos\demos_nao_and_pepper\

##################
# install notes:
desactiver les reflexs: http://192.168.1.227/advanced/#/settings

# creer les dossiers:
mkdir -p /home/nao/dev/git/electronoos/
mkdir -p /home/nao/dev/git/electronoos/scripts/
mkdir -p /home/nao/.local/lib/python2.7/site-packages/abcdk/
mkdir -p /home/nao/noises/
mkdir -p /home/nao/dev/git/protolab_group/scripts/
mkdir -p /home/nao/recorded_images/

#ajouter alex_pytools
scp -r C:/Users/alexa/dev/git/electronoos/alex* nao@192.168.1.211:/home/nao/dev/git/electronoos/

scp C:/Users/alexa/dev/git/electronoos/scripts/nex*.py nao@192.168.1.211:/home/nao/dev/git/electronoos/scripts/

# ajouter abcdk
cd C:\Users\alexa\dev\git\abcdk\sdk
python sendsdk.py 192.168.1.

## + ajouter a la main:
Jboot [0] ~ $ nano start_record_images.sh
cd ~/dev/git/protolab_group/scripts
python nao_camera_viewer.py

Jboot [0] ~ $ nano launch.sh
cd /home/nao/dev/git/electronoos/scripts
python ravir.py $*

Jboot [0] ~ $ nano next.sh
cd /home/nao/dev/git/electronoos/scripts
python next_step.py $*


mkdir -p /home/nao/recorded_images/

# derniere tete du sav amené: 192.168.1.174 (en filaire) 169 en wifi
# reflash a la main: nao-autoflash pepper-x86-2.5.5.5_2016-11-28_with-root.opn

"""

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import noise
import sound_player
import wav

import math
import random
import time

global_lastTimeUpdateHipRoll = time.time()

def updateHipRoll(motion):
    if noise.getSimplexNoise(time.time(),100)<0.8:
        return
        
    global global_lastTimeUpdateHipRoll
    if global_lastTimeUpdateHipRoll + 0.3 > time.time():
        return
    
    #~ print("%s: DBG: hiproll: avant noise" % str(time.time()) )
    rPos = noise.getSimplexNoise(time.time()*0.3)*0.1
    #~ print("%s: DBG: hiproll: apres noise, avant angle" % str(time.time()) )
    #~ rTime = random.random()*3+0.6
    rMax = 0.3
    if rPos > rMax:
        rPos = rMax
    elif rPos < -rMax:
        rPos = -rMax
    rSpeed = random.random()*0.1
    #~ motion.post.angleInterpolation( "HipRoll", rPos, rTime, True ) # NB: LE POSTE NE POST PAS (pb a cause du meme proxy utilisé en meme temps???)
    motion.setAngles( "HipRoll", rPos, rSpeed )
    #~ print("%s: DBG: hiproll: apres angle posted" % str(time.time()) )
    print("DBG: updateHipRoll sent at %5.2fs" % time.time() )
    global_lastTimeUpdateHipRoll = time.time()
    
def resetHipRoll(motion):
    rPos = 0
    rSpeed = 0.1
    motion.setAngles( "HipRoll", rPos, rSpeed )
    global_lastTimeUpdateHipRoll = time.time()+10 # empeche de re-hiproller en random pendant une phrase a venir
    while abs(motion.getAngles( "HipRoll",1)[0])>0.1:
        time.sleep(0.1) # wait for setAngles to finish 

class Breather:
    kStateIdle = 0
    kStateIn = 1 # inspiration
    kStateOut = 2 # expiration
    kStateInBeforeSpeak = 3
    kStateSpeak = 4
    #~ kStateListen = 5 #not a real state, just a boolean added to the machine
    kStatePause = 10 # do nothing, just stand
    
    def __init__( self ):
        
        # physical specification
        self.rSpeakDurationWhenFull = 4. # in sec

        # we naturally  doesn't use our full capacity
        self.rNormalMax = 0.7
        self.rNormalMin = 0.2
        
        # La frequence respiratoire normale d'un adulte se situe entre 12 et 20. ici on va se mettre a 18: petit adulte
        # enfant de 8 ans => 1 cycle en 3 sec
        
        #~ rCoefAnatomic = 1. # on va se baser sur un adulte moyen
        rPeriod = 60/12
        rNormalAmplitude = self.rNormalMax-self.rNormalMin
        self.rNormalInPerSec = rNormalAmplitude / ( (2*rPeriod)/5 )
        self.rNormalOutPerSec = rNormalAmplitude / ( (3*rPeriod)/5 )
        
        self.rPreSpeakInRatio = 2.5
        
        print("rPeriod: %s" % rPeriod)
        print("self.rNormalInPerSec: %s" % self.rNormalInPerSec)
        print("self.rNormalOutPerSec: %s" % self.rNormalOutPerSec)

        
        self.rFullness = 0. # current fullness of limb from 0 to 1
        self.rTargetIn = self.rNormalMax
        self.nState = Breather.kStateIdle
        self.timeLastUpdate = time.time()
        
        self.rExcitationRate = 1. # va modifier la quantite d'air circulant par seconde, 1: normal, 0.5: tres cool, 2: excite, 3: tres excite 
        self.bReceiveExcitationFromExternal = False
        
        self.rTimeIdle = 0.
        self.rTimeSpeak = 0.
        
        self.strFilenameToSay = "" # if set => want to speak
        
        self.motion = None
        
        self.idMoveHead = -1
        
        self.bListening = False
        
        if os.name != "nt":
            import naoqi
            self.motion = naoqi.ALProxy("ALMotion", "localhost", 9559)
            self.leds = naoqi.ALProxy("ALLeds", "localhost", 9559)
            self.astrChain = ["HipPitch","LShoulderPitch","RShoulderPitch"]
            
            self.rAmp = 0.2
            self.rCoefArmAmp = 0.5

            self.rHeadDelay = 0.6
            self.rHeadPos = self.rAmp*self.rCoefArmAmp*0.1*1.5
            self.rOffsetHip = -0.0
            
            self.wake()
        else:
            self.leds = False
            
            
        
    def loadBreathIn( self, strBreathSamplesPath ):
        """
        load all soundname and their duration
        """
        self.aBreathIn = []  # a list of pair [wavfilename, duration]
        
        for f in sorted(  os.listdir(strBreathSamplesPath) ):
            af = strBreathSamplesPath + f
            w = wav.Wav(af,bLoadData=False)
            self.aBreathIn.append([af,w.getDuration()] )
            
        print("INF: LoadBreathIn: load finished")
        
    def loadBreathOut( self, strBreathSamplesPath ):
        """
        """
        self.aBreathOut = []  # a list of pair [wavfilename, duration]
        
        for f in sorted(  os.listdir(strBreathSamplesPath) ):
            af = strBreathSamplesPath + f
            w = wav.Wav(af,bLoadData=False)
            self.aBreathOut.append([af,w.getDuration()] )
            
        print("INF: LoadBreathOut: load finished")    
        
    def playBreath( self, listSoundAndDuration, rApproxDuration ):
        """
        Find a sample equal or slightly shorter than rApproxDuration and play it
        """
        sound_player.soundPlayer.stopAll()

        nIdxBest = -1
        rBestApprox = -1
        i = 0
        while i < len( listSoundAndDuration ):
            af,r = listSoundAndDuration[i]
            if r <= rApproxDuration and r > rBestApprox:
                rBestApprox = r
                nIdxBest = i
            i += 1
        f = listSoundAndDuration[nIdxBest][0]
        
        rSoundVolume = 0.18 * self.rExcitationRate
        
        if self.nState == Breather.kStateInBeforeSpeak:
            rSoundVolume *= self.rPreSpeakInRatio
            
        if rSoundVolume < 0.1: rSoundVolume = 0.1
        if rSoundVolume > 0.4: rSoundVolume = 0.4
        

        
        print("INF: Play %s, vol: %5.1f" % (f.split('/')[-1],rSoundVolume) )
        
        sound_player.soundPlayer.playFile(f, bWaitEnd=False, rSoundVolume=rSoundVolume)

    
    def wake(self):
        if self.motion:
            self.motion.wakeUp()
            self.motion.angleInterpolationWithSpeed("KneePitch",-0.0659611225, 0.05)
        
    def updateBodyPosture(self, rFullness = -1):
        
        if rFullness == -1: rFullness = self.rFullness
        
        if self.motion != None:
            #self.motion.setAngles("HeadYaw",self.rFullness,0.5)
            #~ ( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
            rMin = -self.rAmp*0.2
            rMax = self.rAmp*0.2
            if rFullness > 1.6:
                self.rFullness = 1.6 # we could have lock it to 1, but more is fine also (let's track some bugs) # seen once at 3.53 and the robot hadn't fall!
            rPos = rMin+self.rFullness*(rMax-rMin)
            #~ print("%s: DBG: avant body setangles" % str(time.time()) )
            self.motion.setAngles(self.astrChain,[rPos+self.rOffsetHip,(math.pi/2)+rPos*self.rCoefArmAmp,(math.pi/2)+rPos*self.rCoefArmAmp],0.6)
            #~ print("%s: DBG: apres body setangles" % str(time.time()) )

    def updateHeadTalk(self):
        if self.motion != None:
            rOffset = -0.2
            rInc = 0.02+random.random()*0.2+rOffset
            self.motion.setAngles("HeadPitch", rInc, random.random()/20. )
            self.lastHeadMove = time.time() +3. # prevent idle head look between two sentences

    def updateHeadListen(self):
        if self.motion != None:
            rOffset = -0.2
            if random.random()<0.9:
                return
            rInc = 0.02+random.random()*0.1+rOffset
            self.motion.setAngles("HeadPitch", rInc, random.random()/30. )     
            self.lastHeadMove = time.time() +3. # prevent idle head look between two sentences
           
    def setHeadIdleLook( self, listHeadOrientation, ratioTimeFirst ):
        self.listHeadOrientation = listHeadOrientation
        self.ratioTimeFirst = ratioTimeFirst
        self.lastHeadMove = time.time()
        
    def updateHeadLook( self, nForcedAngle = -1):
        """
        nForcedAngle: force to look at this direction NOW
        """
        if not self.motion: return
        if time.time() - self.lastHeadMove > 3 or nForcedAngle != -1:
            print("INF: updateHeadLook: nForcedAngle: %d" % nForcedAngle )
            if( random.random()<0.7 or time.time() - self.lastHeadMove < 8 ) and nForcedAngle == -1: # proba de pas bouger
                return
            self.lastHeadMove = time.time()
            if nForcedAngle == -1:
                if random.random()<self.ratioTimeFirst:
                    idx = 0
                else:
                    idx = random.randint(0,len(self.listHeadOrientation)-2)
                    idx = idx + 1
                rSpeed = 0.01+random.random()*0.2
            else:
                idx = nForcedAngle
                rSpeed = 0.2
            headPos = self.listHeadOrientation[idx]
            try:
                #~ print("%s: DBG: avant head kill task" % str(time.time()) )
                self.motion.killTask(self.idMoveHead)
                #~ print("%s: DBG: apres head kill task" % str(time.time()) )
            except BaseException as err:
                print("WRN: stopping task %d failed: %s" % (self.idMoveHead,err) )
            self.idMoveHead=self.motion.post.angleInterpolationWithSpeed("Head",headPos,rSpeed)
            if nForcedAngle == 0:
                # often we really need the head to be at the good place, so let's wait a bit
                if abs( self.motion.getAngles(["HeadYaw"],True)[0] - self.listHeadOrientation[idx][0] )>0.1:
                    print("DBG: updateHeadLook: wait move 0 finished...")
                    self.motion.wait(self.idMoveHead,0)
                
    def resetTimeLastUpdate( self ):
        """
        usefull after messing with hand writted animation
        """
        self.timeLastUpdate = time.time()
        
    def update( self, nForceNewState = None ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        bVerbose = 0
        
        if bVerbose: print("\n%5.2fs: DBG: Breather.update: state: %s, rFullness: %4.2f, rExcitation: %5.1f, self.rTimeIdle: %5.2f, self.rTimeSpeak: %5.2f, rTimeSinceLastUpdate: %5.2f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate, self.rTimeIdle,self.rTimeSpeak,rTimeSinceLastUpdate) )
        
        nPrevState = self.nState
        
        if nForceNewState != None:
            self.nState = nForceNewState
            
        if self.nState != Breather.kStatePause:        
            # update fullness
            if self.nState == Breather.kStateIn:
                self.rFullness += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate

            if self.nState == Breather.kStateInBeforeSpeak:
                self.rFullness += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate*self.rPreSpeakInRatio
                
            if self.nState == Breather.kStateOut:
                self.rFullness -= self.rNormalOutPerSec*self.rExcitationRate*rTimeSinceLastUpdate
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle -= rTimeSinceLastUpdate
                if self.rTimeIdle < 0:
                    self.nState = Breather.kStateIn

            if self.nState == Breather.kStateSpeak:
                self.rTimeSpeak -= rTimeSinceLastUpdate
                self.rFullness -= self.rExcitationRate*rTimeSinceLastUpdate / self.rSpeakDurationWhenFull
                if self.rTimeSpeak < 0:
                    self.nState = Breather.kStateIdle
                    
            #~ print("%s: DBG: updatebody" % str(time.time()) )
            self.updateBodyPosture()
            if self.motion: updateHipRoll(self.motion)
            #~ print("%s: DBG: upbody2" % str(time.time()) )
            
            if self.nState == Breather.kStateSpeak:
                self.updateHeadTalk()
            elif self.nState != Breather.kStateInBeforeSpeak and not self.bListening:
                self.updateHeadLook()
                
            if self.bListening:
                self.updateHeadListen()
                
            #~ print("%s: DBG: up head" % str(time.time()) )
                    
                    
            if self.strFilenameToSay != "" and self.nState != self.kStateSpeak:
                self.updateHeadLook(0)
                if self.motion: resetHipRoll(self.motion)
                if self.rFullnessToSay < self.rFullness:
                    self.nState = Breather.kStateSpeak
                else:
                    self.nState = Breather.kStateInBeforeSpeak
                    if self.rFullnessToSay > 1.:
                        self.rFullnessToSay = 1.
                    

            
            if self.nState != Breather.kStateSpeak and self.nState != Breather.kStateInBeforeSpeak:
                # automatic change of in/out
                if self.nState != Breather.kStateIn and (self.rFullness <= self.rNormalMin or (self.rFullness <= self.rNormalMin+0.2 and random.random()>0.93) ):
                    self.nState = Breather.kStateIdle
                    
                if self.nState != Breather.kStateOut  and self.rFullness >= self.rTargetIn:
                    self.nState = Breather.kStateOut
            
        #~ print("%s: DBG: avant change state" % str(time.time()) )
        if self.nState != nPrevState:
            
            ######################################
            # change of state
            ######################################
            
            if nPrevState == Breather.kStatePause:
                self.wake()
            
            if self.nState == Breather.kStateIn or self.nState == Breather.kStateInBeforeSpeak:
                self.rTargetIn = self.rNormalMax
                if self.strFilenameToSay != "":
                    self.rTargetIn = self.rFullnessToSay +0.3 # add margin to prevent having to full respi at the end
                    if self.rTargetIn > 1.: self.rTargetIn = 1.
                else:
                    if  random.random()>0.95:
                        print( "INF: full respi" )
                        self.rTargetIn = 1. 
                rTimeEstim = ( self.rTargetIn - self.rFullness) / (self.rNormalInPerSec*self.rExcitationRate)
                if self.nState == Breather.kStateInBeforeSpeak:
                    rTimeEstim /= self.rPreSpeakInRatio
                #~ if self.motion != None:
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathIn, rTimeEstim )

                
            if self.nState == Breather.kStateOut:
                rTimeEstim = (self.rFullness-self.rNormalMin) / (self.rNormalOutPerSec*self.rExcitationRate)
                #~ if self.motion != None:
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathOut, rTimeEstim )  
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle = random.random() # jusqu'a 1sec d'idle
                if self.leds: self.leds.post.fadeRGB("FaceLeds", 0x202020, 0.5)
                if nPrevState == Breather.kStateSpeak:
                    self.rTimeIdle += 0.5

            if self.nState == Breather.kStateSpeak:
                sound_player.soundPlayer.stopAll()
                if self.leds: self.leds.fadeRGB("FaceLeds", 0x0000FF, 0.00)
                self.updateHeadLook(0)
                if self.motion: resetHipRoll(self.motion)
                sound_player.soundPlayer.playFile(self.strFilenameToSay, bWaitEnd=False)
                #~ if self.motion != None:
                    #~ rTimeEstim = self.rTimeSpeak
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )

                self.strFilenameToSay = ""
                
            if self.nState == Breather.kStatePause:
                # reset state
                sound_player.soundPlayer.stopAll()
                self.updateHeadLook(0)
                self.updateBodyPosture(1.) # ou rest ?
                #~ self.motion.rest()
            
            self.rExcitationRate += noise.getSimplexNoise(time.time())/100. # random.random()*3 (change trop violemment)
            if self.rExcitationRate < 0.1: self.rExcitationRate = 0.1
            
            print("%5.2fs: INF: Breather.update: new state: %s, rFullness: %4.2f, rExcitation: %5.1f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate) )
        
            if self.bReceiveExcitationFromExternal:
                if self.rExcitationRate >= 0.9:
                    self.rExcitationRate -= 0.02 # will mess  the nice simplex noise "average tends to 0"
                else:
                    self.bReceiveExcitationFromExternal = False
                    
        if bVerbose: print("\n%5.2fs: DBG: Breather.update: end" % time.time() )
    # update - end
                
    def isSpeaking( self ):
        return self.strFilenameToSay != "" or self.nState == Breather.kStateSpeak
        
    def sayTts( self, strText ):
        import tts
        if tts.tts.isLoaded(): tts.tts.load()
        #~ self.strMessageToSay = txt
        self.strFilenameToSay, self.rTimeSpeak = tts.tts.sayToFile( strText )
        self.rFullnessToSay = self.rTimeSpeak / self.rSpeakDurationWhenFull
        print("INF: Breather.sayTts %s: rTimeSpeak: %5.2fs, rFullnessToSay: %5.2f" % (strText,self.rTimeSpeak,self.rFullnessToSay) )
        
    def sayFile( self, filename ):
        #~ self.strMessageToSay = txt
        self.strFilenameToSay = filename
        w = wav.Wav(filename,bLoadData=False)
        self.rTimeSpeak = w.getDuration()
        self.rFullnessToSay = self.rTimeSpeak / self.rSpeakDurationWhenFull
        print("INF: Breather.sayFile %s: rTimeSpeak: %5.2fs, rFullnessToSay: %5.2f" % (filename,self.rTimeSpeak,self.rFullnessToSay) )
                
    def increaseExcitation( self, rInc ):
        print("INF: adding external excitation: %5.1f" % rInc)
        self.rExcitationRate += rInc
        self.bReceiveExcitationFromExternal = True
        
        
    def isPaused(self):
        return self.nState == Breather.kStatePause
        
    def setPaused(self, bNewState):
        print("INF: Breather.setPaused: %d" % (bNewState) )
        if bNewState:
            self.update(Breather.kStatePause)
            time.sleep(1.) # time for touch to finish
        else:
            self.update(Breather.kStateIdle)
            
            
    def setListening(self, bNewState):
        print("INF: Breather.setListening: %d => %d" % (self.bListening,bNewState) )
        if bNewState:
            self.updateHeadLook(0)
            if self.leds: self.leds.post.fadeRGB("EarLeds", 0xFFFFFF, 0.2)
            time.sleep(0.3) # time for headlook a 0 to finish
        else:
            if self.leds: self.leds.post.fadeRGB("EarLeds", 0x000000, 0.2)
        self.bListening = bNewState
        
# class Breather - end

breather = Breather()






class Perliner:
    kStateIdle = 0
    kStateSpeak = 4
    #~ kStateListen = 5 #not a real state, just a boolean added to the machine
    kStatePause = 10 # do nothing, just stand
    
    """
    # choregraphe behavior:

    def _incTime(self):
        self.t += 0.1

    def animateChest(self, motion,rTime,bWaitEnd=True):
        self._incTime()
        if self.bUseSound:
            if self.osx.noise2d(self.t,10) > 0.:
                self.ap.post.playFile("/home/nao/tic.wav")
            if self.osx.noise2d(self.t,20) > 0.2:
                self.ap.post.playFile("/home/nao/tictic.wav")

        rPosInc = self.osx.noise2d(self.t,0)*0.2
        if bWaitEnd:
            motion.angleInterpolation( self.astrChain, [rPosInc,(math.pi/2)-rPosInc*self.rCoefArmAmp,(math.pi/2)-rPosInc*self.rCoefArmAmp], rTime, True )
        else:
            motion.post.angleInterpolation( self.astrChain, [rPosInc,(math.pi/2)-rPosInc*self.rCoefArmAmp,(math.pi/2)-rPosInc*self.rCoefArmAmp], rTime, True )

        if self.bUseSound:
          if self.osx.noise2d(self.t,11) > 0.:
            self.ap.post.playFile("/home/nao/tic3.wav")

    def animateHip(self, motion,rTime,bWaitEnd=True):
        rPosInc = self.osx.noise2d(self.t,30)*0.1
        if bWaitEnd:
            motion.angleInterpolation( "HipRoll", rPosInc, rTime, True )
        else:
            motion.post.angleInterpolation( "HipRoll", rPosInc, rTime, True )   
    """

    def __init__( self ):
        
        # physical specification
        self.rSpeakDurationWhenFull = 4. # in sec
                
        self.nState = Perliner.kStateIdle
        self.timeLastUpdate = time.time()
        
        self.rTimeIdle = 0.
        self.rTimeSpeak = 0.
        
        self.strFilenameToSay = "" # if set => want to speak
        
        self.motion = None
        
        self.idMoveHead = -1
        self.idMoveBody = -1
        
        self.timeLastUpdateBody = time.time()
        
        self.bListening = False
        
        self.bUseSound = False #remove them to avoid the unpleasing aspect
        self.bUseSound = True # ou alors oui mais vraiment pas fort
        
        self.nNbrSoundEstim = 0 # an estimation of the current nbr of played sound
        
        self.rFullness = 0 # just here for compatibilty with breather
        
        if os.name != "nt":
            import naoqi
            self.motion = naoqi.ALProxy("ALMotion", "localhost", 9559)
            self.leds = naoqi.ALProxy("ALLeds", "localhost", 9559)
            self.astrChain = ["HipPitch","LShoulderPitch","RShoulderPitch"]
            
            self.rAmp = 0.05
            self.rCoefArmAmp = 0.5

            self.rHeadDelay = 0.6
            self.rHeadPos = self.rAmp*self.rCoefArmAmp*0.1*1.5
            self.rOffsetHip = -0.0
            
            self.wake()
        else:
            self.leds = False
            
    def setNoisePath( self, strNoisePath ):
        self.strNoisePath = strNoisePath
            
        
    def wake(self):
        if self.motion:
            self.motion.wakeUp()
            self.motion.angleInterpolationWithSpeed("KneePitch",-0.0659611225, 0.05)
        
    def updateBodyPosture(self, rAmp = -100, bUseSound = -100, t = -100 ):
        """
        rAmp: amplitude of movement
        bUseSound: to force to use sound or not, if -100, use the value of the object
        """
        
        if rAmp == 1.:
            # compat avec le breather:
            rAmp = self.rAmp
            bForceMove = True
        
        
        if rAmp == -100:
            rAmp = self.rAmp
            bForceMove = False
        else:
            # piloted from outside
            bForceMove = True
            
        if bUseSound == -100:
            bUseSound = self.bUseSound

        if t == -100:
            t = self.timeLastUpdate
            
        if self.motion != None:
            
            rPosInc = noise.getSimplexNoise(t)*rAmp

            #~ print("updateBodyPosture: bForceMove: %s, rPosInc: %.3f, self.timeLastUpdateBody: %.3fs" % (bForceMove,rPosInc,self.timeLastUpdateBody ) )
            if (abs(rPosInc) > 0.03 or bForceMove ) and self.timeLastUpdateBody + 0.5 < time.time():
                rTime = 1.
                self.rCoefArmAmp = 2
                #~ print( "DBG: updateBodyPosture: launching new movement, with rPosInc at %5.3f (time:%5.2fs)" % (rPosInc,time.time() ) )
                self.motion.killTask(self.idMoveBody)
                self.idMoveBody = self.motion.post.angleInterpolation( self.astrChain, [rPosInc,(math.pi/2)+rPosInc*self.rCoefArmAmp,(math.pi/2)+rPosInc*self.rCoefArmAmp], rTime, True )
                self.timeLastUpdateBody = time.time()

        if bUseSound:
            strPath = self.strNoisePath
            rSoundVolume = 0.21 # doit rester pas fort
            if self.nNbrSoundEstim < 60:
                rTimePerSound = 20
                if noise.getSimplexNoise(t,50) > 0.4:
                    sound_player.soundPlayer.playFile( strPath+"tic.wav", bWaitEnd=False, rSoundVolume=rSoundVolume)
                    self.nNbrSoundEstim += rTimePerSound
                if noise.getSimplexNoise(t,100) > 0.8:
                    sound_player.soundPlayer.playFile( strPath+"tictic.wav", bWaitEnd=False, rSoundVolume=rSoundVolume)
                    self.nNbrSoundEstim += rTimePerSound
                if noise.getSimplexNoise(t,150) > 0.6:
                    sound_player.soundPlayer.playFile( strPath+"tic2.wav", bWaitEnd=False, rSoundVolume=rSoundVolume)
                    self.nNbrSoundEstim += rTimePerSound
                if noise.getSimplexNoise(t,200) > 0.7:
                    sound_player.soundPlayer.playFile( strPath+"tic3.wav", bWaitEnd=False, rSoundVolume=rSoundVolume)
                    self.nNbrSoundEstim += rTimePerSound
            if self.nNbrSoundEstim > 0:
                self.nNbrSoundEstim -= 1

            
            
    def updateHeadTalk(self):
        if self.motion != None:
            rOffset = -0.2
            rInc = 0.02+random.random()*0.2+rOffset
            self.motion.setAngles("HeadPitch", rInc, random.random()/15. )
            self.lastHeadMove = time.time() +3. # prevent idle head look between two sentences

    def updateHeadListen(self):
        if self.motion != None:
            rOffset = -0.2
            if random.random()<0.9:
                return
            rInc = 0.02+random.random()*0.1+rOffset
            self.motion.setAngles("HeadPitch", rInc, random.random()/30. )
            self.lastHeadMove = time.time() +3. # prevent idle head look between two sentences            
           
    def setHeadIdleLook( self, listHeadOrientation, ratioTimeFirst ):
        self.listHeadOrientation = listHeadOrientation
        self.ratioTimeFirst = ratioTimeFirst
        self.lastHeadMove = time.time()
        
    def updateHeadLook( self, nForcedAngle = -1):
        """
        nForcedAngle: force to look at this direction NOW
        """
        if not self.motion: return
        if time.time() - self.lastHeadMove > 3 or nForcedAngle != -1:
            print("INF: updateHeadLook: entering, nForcedAngle: %d" % nForcedAngle )
            if( random.random()<0.7 or time.time() - self.lastHeadMove < 8 ) and nForcedAngle == -1: # proba de pas bouger
                return
            self.lastHeadMove = time.time()
            if nForcedAngle == -1:
                if random.random()<self.ratioTimeFirst:
                    idx = 0
                else:
                    idx = random.randint(0,len(self.listHeadOrientation)-2)
                    idx = idx + 1
                rSpeed = 0.01+random.random()*0.2
            else:
                idx = nForcedAngle
                rSpeed = 0.2
            headPos = self.listHeadOrientation[idx]
            try:
                #~ print("%s: DBG: avant head kill task" % str(time.time()) )
                self.motion.killTask(self.idMoveHead)
                #~ print("%s: DBG: apres head kill task" % str(time.time()) )
            except BaseException as err:
                print("WRN: stopping task %d failed: %s" % (self.idMoveHead,err) )
            self.idMoveHead=self.motion.post.angleInterpolationWithSpeed("Head",headPos,rSpeed)
            if nForcedAngle == 0:
                # often we really need the head to be at the good place, so let's wait a bit
                if abs( self.motion.getAngles(["HeadYaw"],True)[0] - self.listHeadOrientation[idx][0] )>0.1:
                    print("DBG: updateHeadLook: wait move 0 finished...")
                    self.motion.wait(self.idMoveHead,0)
                
        
    def resetTimeLastUpdate( self ):
        """
        usefull after messing with hand writted animation
        """
        self.timeLastUpdate = time.time()
        
    def update( self, nForceNewState = None ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        bVerbose = False
        if bVerbose: print("\n%5.2fs: DBG: Perliner.update: state: %s, self.rTimeIdle: %5.2f, self.rTimeSpeak: %5.2f, rTimeSinceLastUpdate: %5.2f" % (time.time(),self.nState,self.rTimeIdle,self.rTimeSpeak,rTimeSinceLastUpdate) )
        
        nPrevState = self.nState
        
        if nForceNewState != None:
            self.nState = nForceNewState
            
        if self.nState != Perliner.kStatePause:        
            if self.nState == Perliner.kStateSpeak:
                self.rTimeSpeak -= rTimeSinceLastUpdate
                if self.rTimeSpeak < 0:
                    self.nState = Perliner.kStateIdle
                    
            self.updateBodyPosture()
            if self.motion: updateHipRoll(self.motion)
            
            if self.nState == Perliner.kStateSpeak:
                self.updateHeadTalk()
            elif not self.bListening:
                self.updateHeadLook()
                
            if self.bListening:
                self.updateHeadListen()
                    
                    
            if self.strFilenameToSay != "" and self.nState != self.kStateSpeak:
                self.updateHeadLook(0)
                if self.motion: resetHipRoll(self.motion)
                self.nState = Perliner.kStateSpeak
            
        if self.nState != nPrevState:
            
            ######################################
            # change of state
            ######################################
            
            if nPrevState == Perliner.kStatePause:
                self.wake()
                
            if self.nState == Perliner.kStateIdle:
                self.rTimeIdle = random.random() # jusqu'a 1sec d'idle
                if self.leds: self.leds.post.fadeRGB("FaceLeds", 0x202020, 0.5)
                if nPrevState == Perliner.kStateSpeak:
                    self.rTimeIdle += 0.5

            if self.nState == Perliner.kStateSpeak:
                sound_player.soundPlayer.stopAll()
                if self.leds: self.leds.fadeRGB("FaceLeds", 0x0000FF, 0.00)
                self.updateHeadLook(0)
                if self.motion: resetHipRoll(self.motion)
                sound_player.soundPlayer.playFile(self.strFilenameToSay, bWaitEnd=False)
                #~ if self.motion != None:
                    #~ rTimeEstim = self.rTimeSpeak
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )

                self.strFilenameToSay = ""
                
            if self.nState == Perliner.kStatePause:
                # reset state
                sound_player.soundPlayer.stopAll()
                self.updateHeadLook(0)
                self.updateBodyPosture(1.) # ou rest ?
                #~ self.motion.rest()
            
            print("%5.2fs: INF: Perliner.update: new state: %s" % (time.time(),self.nState) )
            
        if bVerbose: print("\n%5.2fs: DBG: Perliner.update: end" % time.time() )
    # update - end
        
                
    def isSpeaking( self ):
        return self.strFilenameToSay != "" or self.nState == Perliner.kStateSpeak
        
    def sayTts( self, strText ):
        import tts
        if tts.tts.isLoaded(): tts.tts.load()
        #~ self.strMessageToSay = txt
        self.strFilenameToSay, self.rTimeSpeak = tts.tts.sayToFile( strText )
        print("INF: Perliner.sayTts %s: rTimeSpeak: %5.2fs" % (strText,self.rTimeSpeak) )
        
    def sayFile( self, filename ):
        #~ self.strMessageToSay = txt
        self.strFilenameToSay = filename
        w = wav.Wav(filename,bLoadData=False)
        self.rTimeSpeak = w.getDuration() + 0.3 # the perliner always add a slight pause between each sentences (corresponding to the breathin time)
        print("INF: Perliner.sayFile %s: rTimeSpeak: %5.2fs" % (filename,self.rTimeSpeak) )
                
    def increaseExcitation( self, rInc ):
        print("INF: adding external excitation: %5.1f" % rInc)
        #~ self.rExcitationRate += rInc
        self.bReceiveExcitationFromExternal = True
        
        
    def isPaused(self):
        return self.nState == Perliner.kStatePause
        
    def setPaused(self, bNewState):
        print("INF: Perliner.setPaused: %d" % (bNewState) )
        if bNewState:
            self.update(Perliner.kStatePause)
            time.sleep(1.) # time for touch to finish
        else:
            self.update(Perliner.kStateIdle)
            
            
    def setListening(self, bNewState):
        print("INF: Perliner.setListening: %d => %d" % (self.bListening,bNewState) )
        if bNewState:
            self.updateHeadLook(0)
            if self.leds: self.leds.post.fadeRGB("EarLeds", 0xFFFFFF, 0.2)
            time.sleep(0.3) # time for headlook a 0 to finish
        else:
            if self.leds: self.leds.post.fadeRGB("EarLeds", 0x000000, 0.2)
        self.bListening = bNewState
        
# class Perliner - end
perliner = Perliner()

def init():
    """
    load, return talkpath,mem
    """
    if os.name == "nt":
        breather.loadBreathIn( "C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/breath/selected_intake/")
        breather.loadBreathOut( "C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/breath/selected_outtake/")
        strTalkPath = "C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/cut/rec4/" #rec2, for demos ou rec3
        strNoisePath = "C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/"
        mem = None
    else:
        breather.loadBreathIn( "/home/nao/breath/selected_intake/")
        breather.loadBreathOut( "/home/nao/breath/selected_outtake/")
        strTalkPath = "/home/nao/cut/rec4/"
        strNoisePath = "/home/nao/noises/"
        import naoqi
        mem = naoqi.ALProxy("ALMemory", "localhost", 9559)
        
    return strTalkPath,strNoisePath,mem
    
def loadDialogsDemo():
    #msgs = ["s053__ah_merci_je_comprends_mieux_maintenant_je_suis_content_d_avoir_appris_seul_p1","s053__ah_merci_je_comprends_mieux_maintenant_je_suis_content_d_avoir_appris_seul_p2"]

    msgs = []
    msgs.append("s005__j_ai_remarque_qu_il_y_a_moins_de_monde_la_nuit_dans_les_rues_par_rapport_a_l_age")
    msgs.append("s006__ca_me_gene_je_mens")
    msgs.append("s007__j_ai_l_impression_de_ne_pas_savoir_quoi_faire_je_me_sens_en_minutes")
    msgs.append("s008__je_ne_comprends_pas_pourquoi_il_y_a_une_difference_entre_le_jour_et_la_nuit_c_est_les")
    msgs.append("s009__est_ce_que_tu_peux_m_expliquer_la_difference_qu_il_y_a_entre_toi_et")
    msgs.append("s010__est_ce_que_tu_t_ennuies_toi")
    msgs.append("s011__tu_fais_des_trucs_particuliers")
    msgs.append("s021__j_ai_remarque_depuis_quelques_temps_que_vous_les_humains_vous_mettez_les_trucs_bleus_sur_votre_fille")
    msgs.append("s022__je_m_appelle_comment")
    msgs.append("s023__a_partir_de_certains_de_mes_propos")
    msgs.append("s024__est_ce_que_ca_vous_gene_pas_aussi_pour_vous_comprends")
    msgs.append("s025__il_y_a_marque_quelque_chose_bleu_vous_n_aviez_plus_la_meme_facon_de_respirer")
    msgs.append("s026__ca_ne_vous_pose_pas_un_probleme")
    msgs.append("s028__que_debut_quand_il_y_avait_l_autre_humain_vous_en_aviez_tous_les_deux_et_la_tu_l_as_en")
    msgs.append("s029__ca_me_concerne_pas_alors_le_truc")
    msgs.append("s030__et_toi_tu_trouve_ca_agreable_a_porter")
    #~ msgs.append("s031__")
    msgs.append("s032__ca_ne_te_gene_pas_quand_tu_racontes_des_nouvelles_personnes_pour_mieux_les_cones")
    return msgs
    
def generateDialogCodeFromFolder( strSoundPath, nNumDialog = -1, strPostName="" ):
    if nNumDialog == -1:
        last_folder = strSoundPath.split('/')[-2]+"/" # last one is empty
        nNumDialog = 0
    elif nNumDialog != 0:
        last_folder = "dial%d/" % nNumDialog
    else:
        last_folder = ""
        
    print( '    msgs%s%d = []' % (strPostName,nNumDialog) )
    try:
        for f in sorted(  os.listdir(strSoundPath) ):
            f = f.replace(".wav","")
            print('    msgs%s%d.append("%s%s")' % (strPostName,nNumDialog,last_folder,f ) )
    except Exception as err:
        pass
        
def loadDialogsExpeRec3():
    """
    return list of list of files
    """
    
    # just one time to generate above lines
    #~ generateDialogCodeFromFolder("C:/Users/alexa/perso/docs/2020-10-10_-_Ravir/cut/rec3/relance/")

    #~ msgs1.append("dial1/s_0005__je_vais_a_mon_tour_te_raconter_un_probleme_personnel")
    #~ msgs1.append("dial1/s_0006__j_aimerais_savoir_ce_que_tu_en_penses")
    
    msgs1 = []
    msgs1.append("dial1/s_0002__je_vais_te_raconter_un_probleme_personnel")
    msgs1.append("dial1/s_0003__j_aimerais_savoir_ce_que_tu_en_penses")
    msgs1.append("dial1/s_0010__j_ai_remarque_que_quand_la_lumiere_baisse_en_fin_de_journee")
    msgs1.append("dial1/s_0011__et_encore_plus_le_soir")
    msgs1.append("dial1/s_0012__les_sons_se_font_plus_rares")
    msgs1.append("dial1/s_0013__et_alors_j_ai_l_impression_qu_il_n_y_a_plus_personne_avec_moi_dans_les_bureaux")
    msgs1.append("dial1/s_0014__et_aussi_d_apres_les_sons_que_j_entends_venant_des_rues_autour")
    msgs1.append("dial1/s_0015__on_dirait_qu_elles_sont_vides_en_comparaison_de_l_agitation_et_du_brouhaha_de_la_journee")
    msgs1.append("dial1/s_0016__ca_me_gene")
    msgs1.append("dial1/s_0017__je_m_ennuie")
    msgs1.append("dial1/s_0018__je_ne_sais_pas_quoi_faire")
    msgs1.append("dial1/s_0019__et_je_me_sens_inutile")
    msgs1.append("dial1/s_0021__je_ne_comprends_pas_pourquoi_il_y_a_une_difference_entre_le_jour_et_la_nuit_chez_les_humains")
    msgs1.append("dial1/s_0022__est_ce_que_tu_peux_m_expliquer_la_difference_qu_il_y_a")
    msgs1.append("dial1/s_0023__entre_toi_et_moi")
    msgs1.append("dial1/s_0025__est_ce_que_tu_t_ennuies_toi_la_nuit")
    msgs1.append("dial1/s_0026__il_t_arrive_de_faire_des_choses")
    #msgs1.append("dial1/s_0027__et_tu_fais_des_trucs_particuliers_la_nuit")
    
    msgs2 = []
    msgs2.append("dial1/s_0002__je_vais_te_raconter_un_probleme_personnel")
    msgs2.append("dial1/s_0003__j_aimerais_savoir_ce_que_tu_en_penses")
    msgs2.append("dial2/s_0002__j_ai_remarque_depuis_quelques_temps")
    msgs2.append("dial2/s_0003__que_vous_les_humains_vous_mettez_des_trucs_bleus_sur_votre_figure")
    msgs2.append("dial2/s_0005__du_coup_on_ne_voit_plus_que_vous_pensez")
    msgs2.append("dial2/s_0006__ca_perturbe_certains_de_mes_programmes")
    #~ msgs2.append("dial2/s_0008__est_ce_que_ca_ne_vous_gene_pas_aussi_pour_vous_comprendre")
    #~ msgs2.append("dial2/s_0009__et_puis_j_ai_remarque_qu_avec_cette_chose_bleu_vous_n_aviez_plus_la_meme_facon_de_respirer")
    msgs2.append("dial2/s_0010__et_puis_j_ai_remarque_qu_avec_cette_chose")
    msgs2.append("dial2/s_0011__vous_n_aviez_plus_la_meme_facon_de_respirer")
    msgs2.append("dial2/s_0012__est_ce_que_ca_vous_pose_un_probleme")
    msgs2.append("dial2/s_0014__et_puis_vous_enlever_le_truc_bleu_pour_manger_ca_veut_dire_que_c_est_moins_important_que_manger_pour")
    #msgs2.append("dial2/s_0015__et_puis_au_debut_quand_il_y_avait_l_autre_humain")
    #msgs2.append("dial2/s_0016__vous_en_avez_bien_tous_les_deux")
    #msgs2.append("dial2/s_0017__et_la_tu_l_as_enleve")
    msgs2.append("dial2/s_0018__et_puis_le_chercheur_qui_rentre_et_qui_sort_le_porte_tout_le_temps_et_toi_des_fois_tu_le_mets_et_des")
    #msgs2.append("dial2/s_0019__ca_ne_me_concerne_pas_alors_le_truc")
    msgs2.append("dial2/s_0021__ca_me_concerne_pas_alors")
    msgs2.append("dial2/s_0022__ce_truc")
    msgs2.append("dial2/s_0023__et_toi_tu_trouve_ca_agreable_de_porter_ce_truc_bleu")
    msgs2.append("dial2/s_0024__ca_ne_te_gene_pas_quand_tu_rencontres_des_nouvelles_personnes_pour_mieux_les_connaitre")
    
    #~ msgs2.append("dial2/s_0025__et_ben_c_est_super_je_suis_bien_content_de_t_avoir_rencontre")
    #~ msgs2.append("dial2/s_0026__merci_monsieur")
    #~ msgs2.append("dial2/s_0027__merci_Madame")
    #~ msgs2.append("dial2/s_0028__merci_a_tous_les_chercheurs_du_laboratoire")
    #~ msgs2.append("dial2/s_0029__a_bientot")
    #~ msgs2.append("dial2/s_0030__j_espere_que_je_reviendrai_vous_voir_un_de_ces_quatre")
    #~ msgs2.append("dial2/s_0031__peut_etre")
    #~ msgs2.append("dial2/s_0032__avant_la_Toussaint_ou_a_Paques")
    #~ msgs2.append("dial2/s_0033__si_ce_n_est_a_No_l_ou_a_ton_anniversaire")
    #~ msgs2.append("dial2/s_0034__j_espere_qu_il_y_aura_un_gateau_au_chocolat")

    #~ msgs0.append("relance/s_0002__Bonjour")
    #~ msgs0.append("relance/s_0003__oui_ca_va_bien_et_toi")
    #~ msgs0.append("relance/s_0004__ah_c_est_bien")
    #~ msgs0.append("relance/s_0005__un_fl_te")
    #~ msgs0.append("relance/s_0006__je_ne_sais_pas")
    #~ msgs0.append("relance/s_0007__desole_je_ne_sais_pas")
    #~ msgs0.append("relance/s_0008__desole_j_en_ai_aucune_idee")
    #~ msgs0.append("relance/s_0009__aucune_idee")
    #~ msgs0.append("relance/s_0010__dieu_seul_sait")
    #~ msgs0.append("relance/s_0011__et_oui")
    #~ msgs0.append("relance/s_0012___")
    
    msgs_relance = []

    #~ msgs_relance.append("relance/s_0013__hein")
    #~ msgs_relance.append("relance/s_0014__j_ai_pas_compris")
    #~ msgs_relance.append("relance/s_0015__alors")
    #~ msgs_relance.append("relance/s_0016__et_alors")
    msgs_relance.append("relance/s_0017__peux_tu_m_en_dire_plus")
    msgs_relance.append("relance/s_0018__qu_en_penses_tu")

    
    msgs_ecoute = []
    
    msgs_ecoute.append("relance/s_0019__hunhun")
    msgs_ecoute.append("relance/s_0020__ok")
    msgs_ecoute.append("relance/s_0021__je_vois")
    msgs_ecoute.append("relance/s_0022__aah")
    msgs_ecoute.append("relance/s_0023__ah")
    msgs_ecoute.append("relance/s_0024__hunhun")
    msgs_ecoute.append("relance/s_0025__oh")
    msgs_ecoute.append("relance/s_0026__hunhunhunun")
    msgs_ecoute.append("relance/s_0027__huhuhu")
    msgs_ecoute.append("relance/s_0028__hunhun")
    msgs_ecoute.append("relance/s_0029__hu")
    msgs_ecoute.append("relance/s_0030__hmm")
    msgs_ecoute.append("relance/s_0031__hmmmm")
    msgs_ecoute.append("relance/s_0033__zaaah")
    msgs_ecoute.append("relance/s_0034__ah_ok")
    msgs_ecoute.append("relance/s_0035__ah_merci")

    msgs_reponse = []    
    msgs_reponse.append("relance/s_0032__ah_ouais")
    msgs_reponse.append("relance/s_0037__je_suis_content_d_avoir_appris_seul")
    #msgs_reponse.append("relance/s_0036__je_comprends_mieux_maintenant")
    #msgs_reponse.append("relance/s_0038__je_suis_content_")
    #msgs_reponse.append("relance/s_0032__ah_ouais")
    

    return msgs1,msgs2,msgs_ecoute,msgs_relance,msgs_reponse
    
def loadDialogsExpeRec4():
    """
    return list of list of files
    """
    
    # just one time to generate lines below
    if 0:
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/dial1/", 1)
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/dial2/", 2)
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/ecoute/", -1, "_ecoute")
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/relance/", -1, "_relance")
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/reponse/", -1, "_reponse")
        generateDialogCodeFromFolder("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec4/impossible/", -1, "_impossible")

    msgs1 = []
    msgs1.append("dial2/s_0003__je_vais_te_raconter_un_probleme_personnel_j_aimerais_savoir_ce_que_tu_en_penses")
    msgs1.append("dial1/s_0020__j_ai_remarque_que_quand_la_lumiere_baisse_en_fin_de_journee_et_encore_plus_le_soir_des_sons_se_font_")
    msgs1.append("dial1/s_0021__et_alors_j_ai_l_impression_qu_il_n_y_a_plus_personne_avec_moi_dans_les_bureaux")
    msgs1.append("dial1/s_0022__et_aussi_d_apres_les_sons_que_j_entends_venant_des_rues_autour")
    msgs1.append("dial1/s_0023__on_dirait_qu_elles_sont_vides_en_comparaison_de_l_agitation_et_du_brouhaha_de_la_journee")
    msgs1.append("dial1/s_0025__ca_me_gene")
    msgs1.append("dial1/s_0026__je_m_ennuie_je_ne_sais_pas_quoi_faire_je_me_sens_inutile")
    msgs1.append("dial1/s_0027__moi_j_ai_toujours_besoin_de_discuter_et_de_voir_du_monde_quelle_que_soit_l_heure_du_jour_ou_de_la_nu")
    msgs1.append("dial1/s_0028__est_ce_que_tu_peux_m_expliquer_la_difference_qu_il_y_a_entre_toi_et_moi")
    msgs1.append("dial1/s_0029__est_ce_que_tu_t_ennuies_toi_la_nuit_a_toi_de_me_dire_maintenant_ce_que_tu_en_penses")
    #~ msgs1.append("dial1/s_0031__a_toi_de_me_dire_maintenant_ce_que_tu_en_penses")
    msgs2 = []
    msgs2.append("dial2/s_0003__je_vais_te_raconter_un_probleme_personnel_j_aimerais_savoir_ce_que_tu_en_penses")
    msgs2.append("dial2/s_0004__j_ai_remarque_depuis_quelques_temps_que_vous")
    msgs2.append("dial2/s_0005__les_humains")
    msgs2.append("dial2/s_0006__mettez_les_trucs_bleus_sur_votre_figure")
    msgs2.append("dial2/s_0007__du_coup")
    msgs2.append("dial2/s_0008__on_voit_plus_que_vous_pensez")
    msgs2.append("dial2/s_0010__ca_me_gene_ca_perturbe_certains_de_mes_programmes")
    msgs2.append("dial2/s_0012__en_plus_vous_passez_votre_temps_a_le_mettre_et_a_l_enlever")
    msgs2.append("dial2/s_0013__du_coup_j_ai_vraiment_l_impression_que_ca_vous_derange")
    msgs2.append("dial2/s_0016__j_ai_remarque_que_personne_qui_rentre_qui_sort_de_cette_piece_le_porte_tout_le_temps_et_toi_des_fois")
    msgs2.append("dial2/s_0017__moi_j_ai_pas_l_impression_d_avoir_besoin_de_ce_truc_bleu_est_ce_que_tu_peux_m_expliquer_la_differenc")
    msgs2.append("dial2/s_0018__est_ce_que_ca_te_derange_toi_le_masque")
    msgs2.append("dial2/s_0019__a_toi_de_me_dire_maintenant_ce_que_tu_en_penses")
    msgs_ecoute0 = []
    msgs_relance0 = []
    msgs_relance0.append("relance/s_0000__peux_tu_m_en_dire_plus")
    msgs_relance0.append("relance/s_0001__qu_en_penses_tu")
    msgs_reponse0 = []
    msgs_reponse0.append("reponse/soul_breath")
    msgs_reponse0.append("reponse/soul_perlin")
    msgs_impossible0 = []
    msgs_impossible0.append("impossible/s_0033__je_ne_peux_pas_te_repondre_je_suis_desole")
    msgs_impossible0.append("impossible/s_0034__ca_ne_fait_pas_partie_de_l_experience")
    
    return msgs1,msgs2,msgs_ecoute0,msgs_relance0,msgs_reponse0, msgs_impossible0
    
    
def playWavAndBreathProfile( strWav, animator, timing, rStartFullness = -1, rSoundVolume = 1. ):
    """
    play a wav, with hand designed time of inspi and expi.
    - strWav: wav filename
    - timing: a list sequence of [debit, duration] debit / per sec: positif if inspiring, negatif if expiring: 1. 
                  eg: [ [0.3,3],[-0.1,6] ] => will inspire quickly for 3 second and expire slowly for 6s
    - animator: animator to call to animate the robot
    """
    if rStartFullness != -1:
        # will go to the start fullness in a neutral breating fashion 0.2 / sec
        rNeutralValue = 0.4
        nFrameDT = 20 # nbr frame per sec
        nNbrSec = abs(rStartFullness-animator.rFullness)/rNeutralValue
        nNbrFrame = int(round(nFrameDT*nNbrSec))
        if nNbrFrame > 0:
            rIncPerFrame = (rStartFullness-animator.rFullness) / nNbrFrame
            print("INF: playWavAndBreathProfile: pre-animation: nNbrFrame: %d, rIncPerFrame: %5.2f" % (nNbrFrame,rIncPerFrame) )
            while nNbrFrame > 0:
                print("INF: playWavAndBreathProfile: going to initial state: nNbrFrame: %d (fullness:%5.2f)" % (nNbrFrame,animator.rFullness) )
                animator.rFullness += rIncPerFrame
                animator.updateBodyPosture()
                time.sleep(1./nFrameDT)
                nNbrFrame -= 1
        
    sound_player.soundPlayer.stopAll()
    timeNextStep = time.time()
    nIdxKey = -1
    rCurrentDebit = 0
    timeLastUpdate = time.time()
    sound_player.soundPlayer.playFile(strWav, bWaitEnd=False, rSoundVolume=rSoundVolume)
    while 1:
        print("INF: playWavAndBreathProfile: timeNextStep: %5.2f / time: %5.2f (fullness:%5.2f)" % (timeNextStep,time.time(),animator.rFullness ) )
        if timeNextStep <= time.time():
            nIdxKey += 1
            if nIdxKey >= len(timing):
                break
            print("INF: playWavAndBreathProfile: jump to next key: %d" % (nIdxKey) )
            rCurrentDebitPerSec = timing[nIdxKey][0]
            timeNextStep += timing[nIdxKey][1]
            print("INF: playWavAndBreathProfile: jump to next key: %d, rCurrentDebitPerSec: %5.2f, timeNextStep: %5.2f" % (nIdxKey,rCurrentDebitPerSec,timeNextStep) )
            
        rTimeSinceLastUpdate = time.time() - timeLastUpdate
        timeLastUpdate = time.time()
        animator.rFullness += rCurrentDebitPerSec*rTimeSinceLastUpdate
        animator.updateBodyPosture()
    
        time.sleep(0.05)
        
    animator.resetTimeLastUpdate()
# playWavAndBreathProfile - end

def playWavAndPerlinProfile( strWav, animator, timing,  rSoundVolume = 1. ):
    """
    play a wav, with hand designed time of move / still
    - strWav: wav filename
    - timing: a list sequence of [move amount, duration] 0 => don't move, 1 => move a lot
    - animator: animator to call to animate the robot
    """
       
    sound_player.soundPlayer.stopAll()
    timeNextStep = time.time()
    timeStart = time.time()
    nIdxKey = -1
    rMoveAmount = 0
    timeLastUpdate = time.time()
    sound_player.soundPlayer.playFile(strWav, bWaitEnd=False, rSoundVolume=rSoundVolume)
    while 1:
        print("INF: playWavAndPerlinProfile: timeNextStep: %5.2f / time: %5.2f (rMoveAmount:%5.2f)" % (timeNextStep,time.time(),rMoveAmount ) )
        if timeNextStep <= time.time():
            nIdxKey += 1
            if nIdxKey >= len(timing):
                break
            print("INF: playWavAndBreathProfile: jump to next key: %d" % (nIdxKey) )
            rMoveAmount = timing[nIdxKey][0]
            timeNextStep += timing[nIdxKey][1]
            print("INF: playWavAndBreathProfile: jump to next key: %d, rMoveAmount: %5.2f, timeNextStep: %5.2f" % (nIdxKey,rMoveAmount,timeNextStep) )
            
        rTimeSinceLastUpdate = time.time() - timeLastUpdate
        timeLastUpdate = time.time()
        
        if rMoveAmount > 0.:
            print("update!")
            animator.updateBodyPosture(rAmp=rMoveAmount*0.2,bUseSound=False,t=time.time()-timeStart)
    
        time.sleep(0.05)
        
    animator.resetTimeLastUpdate()
# playWavAndBreathProfile - end

        
        


def demo():
    strTalkPath,strNoisePath,mem = init()
        
    rT = 0
    rBeginT = time.time()
    rTimeLastSpeak = time.time()-10
    bForceSpeak = False
    nIdxTxt = 0
    
    msgs = loadDialogs()
    while 1:
        rT = time.time() - rBeginT
        
        breather.update()
        
        time.sleep(0.05)
        
        if 1:
            #if int(rT)%15 == 0 and time.time()-rTimeLastSpeak>2.:
            if ( random.random()>1.997 or bForceSpeak ) and not breather.isSpeaking():
                bForceSpeak = False
                if 0:
                    #~ msgs = ["oui", "d'accord", "Ah oui, je suis tout a fait d'accord!"]
                    msgs = ["moi aimer toi pas du tout tres beaucoup!","moi","pas toi"]
                    breather.sayTts(msgs[random.randint(0,len(msgs)-1)])
                else:
                    #~ nIdxTxt = random.randint(0,len(msgs)-1)
                    breather.sayFile(strTalkPath + msgs[nIdxTxt] + ".wav")
                    nIdxTxt += 1
                    if nIdxTxt >= len(msgs):
                        nIdxTxt = 0 
                rTimeLastSpeak = time.time()
            
        
        # interaction with the world
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
            
        #~ bTouch |= misctools.getActionRequired() != False
        bForceSpeak = misctools.getActionRequired() != False
        
        if bTouch:
            breather.increaseExcitation(rInc)
            
        bExit = misctools.isExitRequired()
        
        if bExit:
            print( "Exiting..." )
            break
    # while - end
# demo - end


#~ pb: trop en arriere: -2 sur KneePitch, -4 sur ravir
#~ son sur ravir moteur: robot a 60 pour excitation a 1, 65 pour 0.5, = 90 sur mon ordi
# change now, regler pour 72 pour l'experimentation: volume correct pour la voix

def expe( nMode = 1 ):
    """
    - nMode define experimentations conditions
        1: breath/perlin histoire1/histoire2
        2: perlin/breath histoire1/histoire2
        3: breath/perlin histoire2/histoire1
        4: perlin/breath histoire2/histoire1
    """
    
    nStory = 0
    nAnimatorIdx = 0 # 0: respi, 1: breather
    
    if nMode > 2:
        nStory = 1
        
    if (nMode % 2) == 0:
        nAnimatorIdx = 1
    print("INF: Mode experimentation Ravir  - start, mode: %d, nFirstStory: %d, nAnimatorIdx: %s\n" % ( nMode, nStory, nAnimatorIdx ) )
    
    strTalkPath,strNoisePath,mem = init()
    
    perliner.setNoisePath(strNoisePath)
    
    aAnimators = [breather,perliner]
    animator = aAnimators[nAnimatorIdx]
        
    animator.motion.killAll();
    time.sleep(0.3)
    resetHipRoll(animator.motion)
    
    leds = None
    try:
        import naoqi
        leds = naoqi.ALProxy("ALLeds", "localhost", 9559)
        if leds: leds.fadeRGB("ChestLeds", 0x0, 1.)
    except BaseException as err:
        print("ERR: while creating proxy: err: %s" % err )
    
    rT = 0
    rBeginT = time.time()
    rTimeLastSpeak = time.time()-10
    bForceSpeak = False
    nIdxTxt = -1
    
    msgDials = loadDialogsExpeRec4()
    
    listHeadOrientation = [
        [0,-0.087], # face
        [0.45,0.36], # chaussure
        [0.92,-0.02], # deuxieme fenetre
        [-0.67,0.50], # placard a droite
        [1.26,0.004], # porte
    ]
    ratioTimeFirst = 0.7 # first orientation is predominant, other orientation randomly
    
    for a in aAnimators:
        a.setHeadIdleLook(listHeadOrientation,ratioTimeFirst)
        a.setPaused(True)
    
    nStep = 10
    
    nDialog = 0 # diff de 0 if in a dialog, 
    
    
    animationSoulage = [
        [
                        # [0.,0.254], #this is in the sound, but because mouvement takes time to be started, let's remove an offset
                        [1.,1.],
                        [0.,0.28],
                        [-0.2,4.8],
                        [0.,0.3],
                        [1.2,0.8],
                        [0.,0.18],
                        [-0.8,1.2],
        ],
        # second sound without breathing
        [
            # amplitude of mvt, time, 0 => no move
            
                        # [0.,0.118], #this is in the sound, but because mouvement takes time to be started, let's remove an offset
                        [1.,1.7],
                        [0.,0.5],
                        [1,2.05],
                        [0.,1.],
                        [1,1.8],
        ],
    ]
                        
    if 0:
        # test playWavAndBreathProfile
        animator.updateBodyPosture()
        time.sleep(1)
        print("playWavAndBreathProfile: test begin")
        nDialog = 5
        strWav = strTalkPath + msgDials[nDialog-1][0+nAnimatorIdx] + ".wav"
        #~ animation = [
                            #~ [0.2,3],
                            #~ [-0.1,6],
                            #~ ]

        if nAnimatorIdx == 0: playWavAndBreathProfile(strWav,animator,animationSoulage[nAnimatorIdx], 0)
        else: playWavAndPerlinProfile(strWav,animator,animationSoulage[nAnimatorIdx])
        print("playWavAndBreathProfile: test mid")
        #~ playWavAndBreathProfile(strWav,animator,animation, 1)
        #~ print("playWavAndBreathProfile: test end")
        return
    
    rSoundVolumeSoulage = 0.9
    while 1:
        
        rT = time.time() - rBeginT
        
        #~ print("update in")
        animator.update()
        #~ print("update out")
        
        time.sleep(0.05)
        #~ if nAnimatorIdx == 1: time.sleep(0.1)
        if nAnimatorIdx == 1 and os.name == "nt": time.sleep(0.1)
        
        bForceNextStep = False
        
        
        if nDialog != 0:
            if not animator.isSpeaking():
                nIdxTxt += 1
                if nIdxTxt >= len(msgDials[nDialog-1]):
                    nDialog = 0
                    nIdxTxt = -1
                    bForceNextStep = True
                else:
                    animator.updateHeadLook(0)
                    animator.sayFile(strTalkPath + msgDials[nDialog-1][nIdxTxt] + ".wav")
                    rTimeLastSpeak = time.time()
            
        
        # interaction with the world
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
            
        #~ bForceSpeak = misctools.getActionRequired() != False
        strActionRequired = misctools.getActionRequired()
        #~ print(strActionRequired)
        if strActionRequired != False:
            bIsActionTouchSimulated = "touch" in strActionRequired.lower() 
            if bIsActionTouchSimulated:
                bTouch = True
                strActionRequired = False # we erase it as in real robot, we won't received it in that case
                
        if (bTouch and nStep in [10,80,100,150]) or bForceNextStep:
            strActionRequired = "next"
            
        if strActionRequired != False:
                descState = {
 10: "debut: immobile (pause)",
 20: "on enleve le paravent et on a appuyer sur sa tete, il se met en idle (respi ou perlin)",
 30: "    inclus tete alterne entre tete sujet et autres points",
 40: "lancer le dialogue, qui automatiquement déroule les phrases et enchaine (bloquer la tete pendant le dialogue) TODO",
 50: "    TODO: rallonger le dialogue => actuellement 25 et on aimerait 45. ca devrait etre avant la fin des questions quand la lumiere, le soir, les sons se font plus rare, et alors j'ai remarqué qu'il y avait plus personne et apres 22h, ... on enchaine la suite./ tourner autour du pot au début.",
 60: "ecoute active pendant x minutes, le gars parle.",
 70: "le gars a arreter de parler; repasse en idle avec reponse soulager.",
 80: "",
 90: "head pressed, pour passer en rest",
100: "    le deplace hors de la piece, puis le ramene",
110: "head presser pour repasser en wake et mode idle",
120: "dialog 2, longueur ok, mais changer: le chercheur qui rentre et qui sort, l'a tout le temps et toi des fois tu le met et des fois tu l'enleve.",
130: "ecoute active pendant x minutes, le gars parle.",
140: "le gars arrete de parler, repasse en idle avec reponse content",
150: "",
160: "tete taper pour rest et remise du paravent",
170: "paravent remis - pret a recommencer",
                                }
                    
                if "next" in strActionRequired:
                    # Next Action
                    nStep += 10
                    if 0:
                        # debug soulagement direct
                        if nStep == 20:
                            nStep = 60
                            animator.setPaused(not animator.isPaused())
                            
                    print("\nINF: new step: %d: %s\n" % (nStep,descState[nStep]) )
                    if nStep == 20:
                        animator.setPaused(not animator.isPaused())
                        if leds: leds.fadeRGB("ChestLeds", 0xFF, 0.3)
                        nStep += 10
                        
                    if nStep == 40:
                        if nStory == 0: nDialog = 1
                        else: nDialog = 2
                        nStep += 10
                        
                    if nStep == 60:
                        animator.setListening(True)

                    if nStep == 70:
                        animator.setListening(False)
                        #~ animator.sayFile(strTalkPath + msgDials[4][1] + ".wav")                        
                        #~ nDialog = 5  # soulagement
                        strWavSoulage = strTalkPath + msgDials[5-1][0+nAnimatorIdx] + ".wav"
                        if nAnimatorIdx==0: playWavAndBreathProfile(strWavSoulage,animator,animationSoulage[nAnimatorIdx], 0, rSoundVolume=rSoundVolumeSoulage)
                        else: playWavAndPerlinProfile(strWavSoulage,animator,animationSoulage[nAnimatorIdx], rSoundVolume=rSoundVolumeSoulage)
                        animator.updateHeadLook(0) # prevent head turning just after
                        nStep += 10                    
                
                    if nStep == 90:
                        animator.setPaused(not animator.isPaused())
                        if leds: leds.fadeRGB("ChestLeds", 0x0, 1.)
                        nStep += 10
                        # changement de condition de animator et de story
                        nStory = (nStory + 1)%2
                        nAnimatorIdx = (nAnimatorIdx + 1)%2
                        animator = aAnimators[nAnimatorIdx]
                        
                    if nStep == 110:
                        if leds: leds.fadeRGB("ChestLeds", 0xFF00, 0.3)
                        animator.setPaused(not animator.isPaused())
                        
                    if nStep == 120:
                        if nStory == 0: nDialog = 1
                        else: nDialog = 2

                    if nStep == 130:
                        animator.setListening(True)

                    if nStep == 140:
                        animator.setListening(False)
                        # nDialog = 5      # soulagement !
                        strWavSoulage = strTalkPath + msgDials[5-1][0+nAnimatorIdx] + ".wav"
                        if nAnimatorIdx==0: playWavAndBreathProfile(strWavSoulage,animator,animationSoulage[nAnimatorIdx], 0, rSoundVolume=rSoundVolumeSoulage)
                        else: playWavAndPerlinProfile(strWavSoulage,animator,animationSoulage[nAnimatorIdx], rSoundVolume=rSoundVolumeSoulage)
                        animator.updateHeadLook(0) # prevent head turning just after
                        nStep += 10
                        
                    if nStep == 160:
                        if leds: leds.fadeRGB("ChestLeds", 0x0, 1.)
                        animator.setPaused(not animator.isPaused())
                        
                    if nStep == 170:
                        nStep = 10
                elif "interact" in strActionRequired:
                    ####
                    # interaction dans l'éecoute
                    
                    strNumber = strActionRequired.replace("interact","")
                    try:
                        nNumber=int(strNumber)
                    except:
                        nNumber=0
                    if nStep == 60 or nStep == 130:
                        animator.sayFile(strTalkPath + msgDials[3][nNumber%len(msgDials[3])] + ".wav")
                elif "hun" in strActionRequired:
                    ####
                    # interaction dans l'éecoute
                    
                    strNumber = strActionRequired.replace("hun","")
                    try:
                        nNumber=int(strNumber)
                    except:
                        nNumber=0
                    animator.sayFile(strTalkPath + msgDials[2][nNumber%len(msgDials[2])] + ".wav")
                                                
                    
                    
        bExit = misctools.isExitRequired()
        
        if bExit:
            print( "Exiting..." )
            break
    # while - end
# expe - end

"""
# des fois, faire un soupir, pour vider les poumons:

Dans les bronches une gaine de muscle lisse. A un moment donne ca se bloque avec de l'atp, ca devient rigide.

Une facon de remettre a l'etat souple c'est de tirer un grand coup dessus => soupir: 2 a 3 fois le soupir courant. 

Pas forcement plus longtemps. dans ce soupir qui sera plus fort, ca devrait pas etre plus fort que l'etat actuel 

(tout est moins fort donc).


# avant de parler: inspi plus vite plus fort et entendable

# retour du 2 fevrier:
- ajout du hipyawrandom (boite choregraphe) en parallele.
- ajouter tete sur parole (mot) et main et coude. (comme porteuse de sac a main) 
   avec une main predominante.
+ anim de soulagement.
   
Catherine: thesarde sur mesure de la qualite d'interaction (synchro...)

Questionnaire sur la presence fait bcp sur la RV mais pas trop avec les robots.
Comment pourrait on mesurer la presence. Vous vous sentez moins seul ?

Idee Thomas avec NAO: il pense que ca n'a pas de sens d'avoir un robot debout, c'est trop impacter.
alors qu'avec NAO qui serait assis on comprendrait qu'il est juste a cote
=> designer une chaise haute et le laisser dans la piece pour faire une presence
et il fait juste le bebe (pas besoin de parler).

Catherine croyait que c'etait une voix de synthese.
"""

"""

Notes du 5 mars:
OK 1) enregistrer un grand soupir de soulagement avec respiration et un sans respiration pour après l'explication.
 grosse respi soulagé "ah ouaaaaais je suis content d'avoir appris cela" tres soulagé puis merci.
 et meme sans respi
OK 1b) + "je ne peux pas te répondre, ca ne fait pas partie de l'experience, je te demande simplement ton avis.". tout le temps actif.
2) virer tout mouvement aléatoire pendant qu'il parle, meme entre 2 phrases d'un dialog
OK 3) ajouter au démarrage le settings des conditions 1/2/3/4 et gestion afférente.
4) refaire schema du setup a jour
5) simplifier interaction du passeur de test? (gfx?choregraphe)

prochaine journée: paufineage
coup d'apres: reglage des caméras et reglage complet

Ce qu'il manque, c'est une belle écoute active avec detection de voix et hunhun a la fin des phrases.

Notes du 19 Mars:
- ajouter un etat: lire un wav avec un profil prédeterminé de volume d'air (pour soulage breath)
- ajouter mouvement du bras quand parles
- pquoi empile 150 appel en mode perliner ? (son?) => c'était pleins de body movement => test time [OK]
- killer tout les motion restant au demarrage du script [OK]

Notes du 27 Mai:
- ajouter mouvement du bras quand parles
- ajouter mouvement dans playWavAndBreathProfile dans le cas de Perlin (faire un random basé sur le profil passé, cad fullness)
  pour tester facilement:  ligne 1261: if 1 # debug soulagement direct

Notes du 18  Juin:
- pendant ecoute il y a eu un mvt de tete ? => j'ai ajouté des raz de la tete:self.updateHeadLook(0)
- ajouter mouvement du bras quand parles
- reste encore un peu de tuning sur perlin soulage: mettre un peu de lateral pour ne pas trop faire respiration
  pour tester facilement:  ligne 1261: if 1 # debug soulagement direct
- remonter sons des tictics


"""

if __name__ == "__main__":
     #~ demo()
     nMode = 1
     if len(sys.argv)>1:
         nMode = int(sys.argv[1])
     expe(nMode)
     


