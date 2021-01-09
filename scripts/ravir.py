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


class Breather:
    kStateIdle = 0
    kStateIn = 1 # inspiration
    kStateOut = 2 # expiration
    kStateSpeak = 3
    
    def __init__( self ):
        
        # physical specification
        self.rSpeakDurationWhenFull = 5. # in sec
        self.rNormalInPerSec = 1/1.2
        self.rNormalOutPerSec = 1/1.8
        
        self.rFull = 0. # fullness of limb from 0 to 1
        self.nState = Breather.kStateIdle
        self.timeLastUpdate = time.time()
        
        self.rExcitationRate = 0.5 # va modifier la quantite d'air circulant par seconde, 1: normal, 0.5: tres cool, 2: excite, 3: tres excite 
        self.bReceiveExcitationFromExternal = False
        
        self.rTimeIdle = 0.
        
        self.motion = None
        
        if os.name != "nt":
            self.motion = naoqi.ALProxy("ALMotion", "localhost", 9559)
            self.astrChain = ["HipPitch","LShoulderPitch","RShoulderPitch"]
            
            self.rAmp = 0.2
            self.rCoefArmAmp = 0.5

            self.rHeadDelay = 0.6
            self.rHeadPos = self.rAmp*self.rCoefArmAmp*0.1*1.5
            self.rOffsetHip = -0.0
        
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
        if rSoundVolume > 0.5: rSoundVolume = 0.5
        
        print("INF: Play %s, vol: %5.1f" % (f.split('/')[-1],rSoundVolume) )
        
        sound_player.soundPlayer.playFile(f, bWaitEnd=False, rSoundVolume=rSoundVolume)

            
        
        
    def update( self ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        nPrevState = self.nState
        
        # update fullness
        if self.nState == Breather.kStateIn:
            self.rFull += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateOut:
            self.rFull -= self.rNormalOutPerSec*self.rExcitationRate*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateIdle:
            self.rTimeIdle -= self.timeLastUpdate
            if self.rTimeIdle < 0:
                self.nState = Breather.kStateIn
            

        
        if self.nState != Breather.kStateIn and (self.rFull <= 0.1 or (self.rFull <= 0.3 and random.random()>0.9) ):
            self.nState = Breather.kStateIdle
            
        if self.nState != Breather.kStateOut and self.rFull >= 0.95:
            self.nState = Breather.kStateOut
            
        if self.nState != nPrevState:
            # play a sound
            if self.nState == Breather.kStateIn:
                rTimeEstim = (1. - self.rFull) / (self.rNormalInPerSec*self.rExcitationRate)
                if self.motion != None:
                    self.motion.stopMove()
                    self.motion.post.angleInterpolation( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathIn, rTimeEstim )

                
            if self.nState == Breather.kStateOut:
                rTimeEstim = (self.rFull-0.1) / (self.rNormalOutPerSec*self.rExcitationRate)
                if self.motion != None:
                    self.motion.stopMove()
                    self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathOut, rTimeEstim )  
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle = random.random() # jusqu'a 1sec d'idle
                
            
            self.rExcitationRate += noise.getSimplexNoise(time.time())/100. # random.random()*3 (change trop violemment)
            if self.rExcitationRate < 0.1: self.rExcitationRate = 0.1
            print("%5.2fs: INF: Breather.update: rFull: %4.2f, state: %s, rExcitation: %5.1f" % (time.time(),self.rFull,self.nState,self.rExcitationRate) )
        
            if self.bReceiveExcitationFromExternal:
                if self.rExcitationRate >= 0.8:
                    self.rExcitationRate -= 0.1 # will mess  the nice simplex noise average tends to 0
                else:
                    self.bReceiveExcitationFromExternal = False
                
    def say( self, txt ):
        pass
        
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
    while 1:
        breather.update()
        time.sleep(0.05)
        
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
        if bTouch:
            breather.increaseExcitation(rInc)

"""
pb: trop en arriere: -2 sur KneePitch, -4 sur ravir
son sur ravir moteur: robot a 60 pour excitation a 1, 65 pour 0.5, = 90 sur mon ordi

# des fois, faire un soupir, pour vider les poumons:
Dans les bronches une gaine de muscle lisse. A un moment donne ca se bloque avec de l'atp, ca devient rigide.
Une facon de remettre a l'etat souple c'est de tirer un grand coup dessus => soupir: 2/3 fois le soupir courant. 
Pas forcement plus longtemps. dans ce soupir qui sera plus fort, ca devrait pas etre plus fort que l'etat actuel 
(tout est moins fort donc).

# avant de parler: inspi plus vite plus fort et entendable
"""
    
    
        
if __name__ == "__main__":
    demo()