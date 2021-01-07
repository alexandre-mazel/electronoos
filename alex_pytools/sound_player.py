##########################################
# Portable way to handle way playing (windows, linux, pepper, nao, raspberry)
# - preload
# - play in background
#- fx ?
##########################################


class SoundPlayer:
    """
    handles playing of wav sound with preloading, caching...
    
    sp = SoundPlayer()
    sp.playFile(filename)
    """
    
    def __init__( self ):
        
        if os.name == "nt":
            self.bUsePyGame = True
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
        
        
    def playFile( self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        sound = self.loadFile( strFilename )
        sound.set_volume(rSoundVolume)
        sound.play()
        # how often to check active playback
        frame_rate = 30
        if bWaitEnd:
            clock = pg.time.Clock()
            while pg.mixer.get_busy():
                clock.tick(frame_rate)
        
    def stopAll( self ):
        pg.mixer.stop()
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

def testPlay()
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    
if __name__ == "__main__":
    testPlay()
