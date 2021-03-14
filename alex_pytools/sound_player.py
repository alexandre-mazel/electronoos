##########################################
# Portable way to handle way playing (windows, linux, pepper, nao, raspberry)
# - preload
# - play in background
#- fx ?
##########################################

import os


# we don't want to import misctools here (cyclic import)
def isNaoqi():
    try:
        f = open("/proc/cpuinfo", "rt")
        buf=f.read()
        f.close()
    except:
        return False
    bIsNaoqi = "Geode" in buf  or "Intel(R) Atom(TM)" in buf
    return bIsNaoqi

class SoundPlayer:
    """
    handles playing of wav sound with preloading, caching...
    
    sp = SoundPlayer()
    sp.playFile(filename)
    """
    
    def __init__( self ):
        
        self.player = None
        
        bTryPygame = False
        bIsNaoqi = isNaoqi()
        
        if os.name == "nt" or not bIsNaoqi:
            bTryPygame = True
            
        if bTryPygame:
            try:
                import pygame_tools
                self.player = pygame_tools.soundPlayer
                print("INF: SoundPlayer: using pygame") 
                
            except BaseException as err:
                print("WRN: SoundPlayer: pygames not found, using standard call, functionnalities might be reduced...\nerr: %s" % str(err) )
    
        if bIsNaoqi:
            import naoqi_tools
            self.player = naoqi_tools.soundPlayer
            print("INF: SoundPlayer: using naoqi")
            
        self.changePlayFreq()
        
    def changePlayFreq( self, newFreq = 44100 ):
        self.player.changePlayFreq(newFreq)
        
    def loadFile( self, strFilename ):
        """
        preload file before playing them
        """
        sound = self.player.loadFile(strFilename)
        if not sound: print("WRN: sound_player.loadFile: loading error: '%s'" % strFilename)
        return sound
        
        
    def playFile( self, strFilename, bWaitEnd = True, rSoundVolume = 1. ):
        if self.player: 
            return self.player.playFile(strFilename, bWaitEnd = bWaitEnd, rSoundVolume=rSoundVolume)
        
        if os.name == "nt":
            #windows standard
            print("DBG: SoundPlayer.playFile: using standard windows api")
            import winsound
            flags = winsound.SND_FILENAME
            if not bWaitEnd:
                flags |= winsound.SND_ASYNC | winsound.SND_NOSTOP
            
            try:
                import winsound
                winsound.PlaySound( strFilename, flags )
                return True
            except BaseException as err:
                print("ERR: SoundPlayer.playFile: err: %s" % str(err) )

        
    def stopAll( self ):
        if self.player: return self.player.stopAll()
                
        
# class SoundPlayer - end
        
soundPlayer = SoundPlayer()

def testPlay():
    import time
    soundPlayer.playFile( "../data/ting.wav")
    soundPlayer.playFile( "../data/ting.wav", False)
    time.sleep(0.2)
    soundPlayer.stopAll() #the second sound must be heard cut
    time.sleep(1.) #ensure the stopAll has cut everything, and not because we're leaving the script
    
if __name__ == "__main__":
    testPlay()
