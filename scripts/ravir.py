"""
Breath engine for RAVIR project
"""

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import wav

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
        
    
        
    def playBreathIn( self, rApproxDuration ):
        """
        Find a sample equal or slightly shorter than rApproxDuration and play it
        """
        nIdxBest = -1
        rBestApprox = -1
        i = 0
        while i < len( self.aBreathIn ):
            af,r = self.aBreathIn[i]
            if r <= rApproxDuration and r > rBestApprox:
                rBestApprox = r
                nIdxBest = i
            i += 1
        misctools.playWav(self.aBreathIn[nIdxBest][0], bWaitEnd=False)
        
        
    def update( self ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        # update fullness
        if self.nState == Breather.kStateIn:
            self.rFull += self.rNormalInPerSec*rTimeSinceLastUpdate
            
        if self.nState == Breather.kStateOut:
            self.rFull -= self.rNormalOutPerSec*rTimeSinceLastUpdate
        
            
        nPrevState = self.nState
        
        if self.rFull <= 0.1:
            self.nState = Breather.kStateIn
            
        if self.rFull >= 1.:
            self.nState = Breather.kStateOut
            
        if self.nState != nPrevState:
            # play a sound
            if self.nState == Breather.kStateIn:
                rTimeInEstim = (1. - self.rFull) / self.rNormalInPerSec
                self.playBreathIn( rTimeInEstim )
            
        print("INF: Breather.update: rFull: %4.2f, state: %s" % (self.rFull,self.nState) )
        
        
    def say( self, txt ):
        pass
        
# class Breather - end


breather = Breather()

def demo():
    breather.loadBreath( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_intake/")
    while 1:
        breather.update()
        time.sleep(0.05)
        
    
    
        
if __name__ == "__main__":
    demo()