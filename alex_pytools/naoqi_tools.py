# -*- coding: utf-8 -*-

###########################################################
# Naoqi very light compatibility layer
# Author: A. Mazel  (c) 2021
###########################################################

import time

class SoundPlayer:
    """
    handles playing of wav sound with preloading, caching...
    
    sp = SoundPlayer()
    sp.playFile(filename)
    """
    
    def __init__( self, strIP = "localhost" ):
        import naoqi
        self.ap = naoqi.ALProxy("ALAudioPlayer", strIP, 9559)
        
    def changePlayFreq( self, newFreq = 44100 ):
        # we could mess with the system here
        # TODO
        self.listPreloadedSound = {} # a dict filename => play task ID
        
    def loadFile( self, strFilename ):
        """
        preload file before playing them
        """
        try:
            return self.listPreloadedSound[strFilename]
        except:
            sound = self.ap.loadFile(strFilename)
            self.listPreloadedSound[strFilename] = sound
        return sound
        
        
    def playFile( self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        soundID = loadFile(strFilename)
        if bWaitEnd:
            self.ap.play( soundID, rSoundVolume, 0.)
        else:
            self.ap.post.play( soundID, rSoundVolume, 0.)

        return True
        
    def stopAll( self ):
        self.ap.stop()
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

if __name__ == "__main__":
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    time.sleep(1)