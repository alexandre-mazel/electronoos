##########################################
# Portable way to handle way playing (windows, linux, pepper, nao, raspberry)
# - preload
# - play in background
#- fx ?
##########################################

import os

class SoundPlayer:
    """
    handles playing of wav sound with preloading, caching...
    
    sp = SoundPlayer()
    sp.playFile(filename)
    """
    
    def __init__( self ):
        
        self.pyGameSoudPlayer = None
        
        if os.name == "nt":
            try:
                import pygame_tools
                self.pyGameSoudPlayer = pygame_tools.soundPlayer
            except BaseException as err:
                print("WRN: SoundPlayer: pygames not found, using standard windows call, functionnalities reduced...\nerr: %s" % str(err) )
            
        self.changePlayFreq()
        
    def changePlayFreq( self, newFreq = 44100 ):
        if os.name == "nt":
            if self.pyGameSoudPlayer:
                self.pyGameSoudPlayer.changePlayFreq(newFreq)
        
        self.listPreloadedSound = {} 
        
    def loadFile( self, strFilename ):
        """
        preload file before playing them
        """
        if os.name == "nt":
            if self.pyGameSoudPlayer:
                sound = self.pyGameSoudPlayer.loadFile(strFilename)

        return sound
        
        
    def playFile( self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        if os.name == "nt":
            if self.pyGameSoudPlayer:
                return self.pyGameSoudPlayer.playFile(strFilename, bWaitEnd = bWaitEnd, rSoundVolume=rSoundVolume)

        
    def stopAll( self ):
        if os.name == "nt":
            if self.pyGameSoudPlayer:
                return self.pyGameSoudPlayer.stopAll()
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

def testPlay():
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    
if __name__ == "__main__":
    testPlay()
