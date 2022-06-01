"""
some addons to the pygame libs
"""

import pygame as pg # pip install pygame
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
        strErr = ""
        try:
            return self.listPreloadedSound[strFilename]
        except KeyError as err:
            try:
                sound = pg.mixer.Sound(strFilename)
            except BaseException as err:
                sound = None
                strErr = str(err)
            if not sound: print("WRN: pygame_tools.loadFile: loading error: '%s' (err:%s)" % (strFilename,strErr))
            self.listPreloadedSound[strFilename] = sound
        return sound
        
    def playFile( self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        if ".mp3" in strFilename.lower():
            return self.playFileMp3(strFilename,bWaitEnd=bWaitEnd,rSoundVolume=rSoundVolume )
            
        sound = self.loadFile( strFilename )
        if sound == None:
            print("WRN: pygame_tools.playFile: can't play this sound, as it hasn't been loaded: '%s'" % strFilename )
            return False
        sound.set_volume(rSoundVolume)
        sound.play()
        # how often to check active playback
        frame_rate = 30
        if bWaitEnd:
            clock = pg.time.Clock()
            while pg.mixer.get_busy():
                clock.tick(frame_rate)
        return True
        
    def playFileMp3(self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        pg.mixer.music.load(strFilename)
        pg.mixer.music.play()
        if bWaitEnd:
            clock = pg.time.Clock()
            while pg.mixer.music.get_busy():
                clock.tick(30)
        
    def stopAll( self ):
        pg.mixer.stop()
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

if __name__ == "__main__":
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    time.sleep(1)
        