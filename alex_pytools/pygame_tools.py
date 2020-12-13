"""
some addons to the pygame libs
"""

import pygame as pg
import time

class SoundPlayer:
    """
    handles playing of wav sound with preloading, caching...
    
    sp = SoundPlayer()
    sp.playFile(filename)
    """
    
    def __init__( self ):
        self.changePlayFreq()
        
    def changePlayFreq( self, newFreq = 44100 ):
        FREQ = newFreq   # changing that can change the playing of some wav
        BITSIZE = -16  # here unsigned 16 bit
        CHANNELS = 2   # 1 is mono, 2 is stereo
        BUFFER = 1024  # audio buffer size, number of samples

        pg.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        
        self.listPreloadedSound = {}        
        
    def loadFile( self, strFilename ):
        """
        preload file before playing them
        """
        try:
            return self.listPreloadedSound[strFilename]
        except:
            sound = pg.mixer.Sound(strFilename)
            self.listPreloadedSound[strFilename] = sound
        return sound
        
        
    def playFile( self, strFilename, bWaitEnd = True ):
        sound = self.loadFile( strFilename )
        sound.play()
        # how often to check active playback
        frame_rate = 30
        if bWaitEnd:
            clock = pg.time.Clock()
            while pg.mixer.get_busy():
                clock.tick(frame_rate)
        
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

if __name__ == "__main__":
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    time.sleep(1)
        