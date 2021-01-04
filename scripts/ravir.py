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
import pygame_tools
import wav

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
        
        self.rExcitationRate = 1 # va modifier la quantite d'air circulant par seconde, 1: normal, 0.5: tres cool, 2: excite, 3: tres excite 
        self.bReceiveExcitationFromExternal = False
        
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
        pygame_tools.soundPlayer.stopAll()
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
        print("Play %s" % f.split('/')[-1] )
        rSoundVolume = 0.2 * self.rExcitationRate
        if rSoundVolume < 0.12: rSoundVolume = 0.12
        if rSoundVolume > 0.7: rSoundVolume = 0.7
        misctools.playWav(f, bWaitEnd=False, rSoundVolume=rSoundVolume)
        
        
    def update( self ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        # update fullness
        if self.nState == Breather.kStateIn:
            self.rFull += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateOut:
            self.rFull -= self.rNormalOutPerSec*self.rExcitationRate*rTimeSinceLastUpdate
        
            
        nPrevState = self.nState
        
        if self.nState != Breather.kStateIn and (self.rFull <= 0.1 or (self.rFull <= 0.3 and random.random()>0.95) ):
            self.nState = Breather.kStateIn
            
        if self.nState != Breather.kStateOut and self.rFull >= 0.95:
            self.nState = Breather.kStateOut
            
        if self.nState != nPrevState:
            # play a sound
            if self.nState == Breather.kStateIn:
                rTimeEstim = (1. - self.rFull) / (self.rNormalInPerSec*self.rExcitationRate)
                self.playBreath( self.aBreathIn, rTimeEstim )
                
            if self.nState == Breather.kStateOut:
                rTimeEstim = (self.rFull-0.1) / (self.rNormalOutPerSec*self.rExcitationRate)
                self.playBreath( self.aBreathOut, rTimeEstim )  
                
            
            self.rExcitationRate += noise.getSimplexNoise(time.time())/10. # random.random()*3 (change trop violemment)
            if self.rExcitationRate < 0.1: self.rExcitationRate = 0.1
            print("%5.2fs: INF: Breather.update: rFull: %4.2f, state: %s, rExcitation: %5.1f" % (time.time(),self.rFull,self.nState,self.rExcitationRate) )
        
            if self.bReceiveExcitationFromExternal:
                if self.rExcitationRate > 1.:
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
    breather.loadBreathIn( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_intake/")
    breather.loadBreathOut( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_outtake/")
    while 1:
        breather.update()
        time.sleep(0.05)
        if misctools.getKeystrokeNotBlocking() != 0:
            breather.increaseExcitation(0.1)
        
    
    
        
if __name__ == "__main__":
    demo()