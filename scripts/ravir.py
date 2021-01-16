"""
Breath engine for RAVIR project
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
import tts


class Breather:
    kStateIdle = 0
    kStateIn = 1 # inspiration
    kStateOut = 2 # expiration
    kStateSpeak = 3
    kStateInBeforeSpeak = 4
    
    def __init__( self ):
        
        # physical specification
        self.rSpeakDurationWhenFull = 5. # in sec

        # we naturally  doesn't use our full capacity
        self.rNormalMax = 0.7
        self.rNormalMin = 0.2
        
        # La frequence respiratoire normale d'un adulte se situe entre 12 et 20. ici on va se mettre a 18: petit adulte
        # enfant de 8 ans => 1 cycle en 3 sec
        
        #~ rCoefAnatomic = 1. # on va se baser sur un adulte moyen
        rPeriod = 60/16
        rNormalAmplitude = self.rNormalMax-self.rNormalMin
        self.rNormalInPerSec = rNormalAmplitude / ( (2*rPeriod)/5 )
        self.rNormalOutPerSec = rNormalAmplitude / ( (3*rPeriod)/5 )
        
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
        
        if os.name != "nt":
            self.motion = naoqi.ALProxy("ALMotion", "localhost", 9559)
            self.astrChain = ["HipPitch","LShoulderPitch","RShoulderPitch"]
            
            self.rAmp = 0.2
            self.rCoefArmAmp = 0.5

            self.rHeadDelay = 0.6
            self.rHeadPos = self.rAmp*self.rCoefArmAmp*0.1*1.5
            self.rOffsetHip = -0.0
            
            
        tts.tts.load()
        
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
        
        rSoundVolume = 0.2 * self.rExcitationRate
        if rSoundVolume < 0.12: rSoundVolume = 0.12
        if rSoundVolume > 0.4: rSoundVolume = 0.4
        
        print("INF: Play %s, vol: %5.1f" % (f.split('/')[-1],rSoundVolume) )
        
        sound_player.soundPlayer.playFile(f, bWaitEnd=False, rSoundVolume=rSoundVolume)

            
        
        
    def update( self ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        print("\n%5.2fs: DBG: Breather.update: state: %s, rFullness: %4.2f, rExcitation: %5.1f, self.rTimeIdle: %5.2f, self.rTimeSpeak: %5.2f, rTimeSinceLastUpdate: %5.2f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate, self.rTimeIdle,self.rTimeSpeak,rTimeSinceLastUpdate) )

        
        nPrevState = self.nState
        
        # update fullness
        if self.nState == Breather.kStateIn:
            self.rFullness += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateOut:
            self.rFullness -= self.rNormalOutPerSec*self.rExcitationRate*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateIdle:
            self.rTimeIdle -= rTimeSinceLastUpdate
            if self.rTimeIdle < 0:
                self.nState = Breather.kStateIn

        if self.nState == Breather.kStateSpeak:
            self.rTimeSpeak -= rTimeSinceLastUpdate
            if self.rTimeSpeak < 0:
                self.nState = Breather.kStateIdle
                
                
        if self.strFilenameToSay != "" and self.nState != self.kStateSpeak:
            if self.rFullnessToSay < self.rFullness:
                self.nState = Breather.kStateSpeak
            else:
                self.nState = Breather.kStateIn

        
        if self.nState != self.kStateSpeak:
            # automatic change of in/out
            if self.nState != Breather.kStateIn and (self.rFullness <= self.rNormalMin or (self.rFullness <= self.rNormalMin+0.2 and random.random()>0.93) ):
                self.nState = Breather.kStateIdle
                
            if self.nState != Breather.kStateOut  and self.rFullness >= self.rTargetIn:
                self.nState = Breather.kStateOut
            
        if self.nState != nPrevState:
            # play a sound
            
            if self.nState == Breather.kStateIn:
                self.rTargetIn = self.rNormalMax
                if  random.random()>0.95:
                    print( "INF: full respi" )
                    self.rTargetIn = 1.
                rTimeEstim = ( self.rTargetIn - self.rFullness) / (self.rNormalInPerSec*self.rExcitationRate)
                if self.motion != None:
                    self.motion.stopMove()
                    self.motion.post.angleInterpolation( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathIn, rTimeEstim )

                
            if self.nState == Breather.kStateOut:
                rTimeEstim = (self.rFullness-self.rNormalMin) / (self.rNormalOutPerSec*self.rExcitationRate)
                if self.motion != None:
                    self.motion.stopMove()
                    self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathOut, rTimeEstim )  
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle = random.random() # jusqu'a 1sec d'idle

            if self.nState == Breather.kStateSpeak:
                sound_player.soundPlayer.stopAll()
                sound_player.soundPlayer.playFile(self.strFilenameToSay, bWaitEnd=False)
                self.strFilenameToSay = ""
            
            self.rExcitationRate += noise.getSimplexNoise(time.time())/100. # random.random()*3 (change trop violemment)
            if self.rExcitationRate < 0.1: self.rExcitationRate = 0.1
            
            print("%5.2fs: INF: Breather.update: new state: %s, rFullness: %4.2f, rExcitation: %5.1f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate) )
        
            if self.bReceiveExcitationFromExternal:
                if self.rExcitationRate >= 0.9:
                    self.rExcitationRate -= 0.02 # will mess  the nice simplex noise "average tends to 0"
                else:
                    self.bReceiveExcitationFromExternal = False
                
    def say( self, strText ):
        #~ self.strMessageToSay = txt
        self.strFilenameToSay, self.rTimeSpeak = tts.tts.sayToFile( strText )
        self.rFullnessToSay = self.rTimeSpeak / self.rSpeakDurationWhenFull
        print("INF: Breather.say: rTimeSpeak: %5.2fs, rFullnessToSay: %5.2f" % (self.rTimeSpeak,self.rFullnessToSay) )
        
    def increaseExcitation( self, rInc ):
        print("INF: adding external excitation: %5.1f" % rInc)
        self.rExcitationRate += rInc
        self.bReceiveExcitationFromExternal = True
        
# class Breather - end


breather = Breather()

def demo():
    
    if os.name == "nt":
        breather.loadBreathIn( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_intake/")
        breather.loadBreathOut( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_outtake/")
    else:
        breather.loadBreathIn( "/home/nao/breath/selected_intake/")
        breather.loadBreathOut( "/home/nao/breath/selected_outtake/")    
        import naoqi
        mem = naoqi.ALProxy("ALMemory", "localhost", 9559)
        
    rT = 0
    rBeginT = time.time()
    rTimeLastSpeak = time.time()-10
    while 1:
        rT = time.time() - rBeginT
        
        breather.update()
        
        time.sleep(0.05)
        
        
        if int(rT)%10 == 0 and time.time()-rTimeLastSpeak>2.:
            #~ msgs = ["oui", "d'accord", "Ah oui, je suis tout a fait d'accord!"]
            msgs = ["moi aimer toi!"]
            breather.say(msgs[random.randint(0,len(msgs)-1)])
            rTimeLastSpeak = time.time()
        
        
        # interaction with the world
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
            
        bTouch |= misctools.getActionRequired() != False
        
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

"""
# des fois, faire un soupir, pour vider les poumons:

Dans les bronches une gaine de muscle lisse. A un moment donne ca se bloque avec de l'atp, ca devient rigide.

Une facon de remettre a l'etat souple c'est de tirer un grand coup dessus => soupir: 2 a 3 fois le soupir courant. 

Pas forcement plus longtemps. dans ce soupir qui sera plus fort, ca devrait pas etre plus fort que l'etat actuel 

(tout est moins fort donc).


# avant de parler: inspi plus vite plus fort et entendable
"""
    
        
if __name__ == "__main__":
    demo()