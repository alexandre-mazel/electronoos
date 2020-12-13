"""
process big wav file, cut them...
"""
import wav

import pygame_tools

import time

def autocut(wavfile, rSilenceMinDuration = 0.3 ):
    w = wav.Wav(wavfile,bQuiet=False)
    print(w)
    #~ w.write("/tmp/t.wav")
    seq = w.split(rSilenceTresholdPercent=0.6,rSilenceMinDuration=rSilenceMinDuration)
    for i,s in enumerate(seq):
        s.normalise()
        name = "/tmp/s%03d.wav" % i 
        s.write(name)
        print("playing: %s" % name )
        pygame_tools.soundPlayer.playFile(name)
        time.sleep(0.5)
            
    
    
    
if __name__ == "__main__":
    #autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec1_fx.wav")
    autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec2_fx.wav",rSilenceMinDuration=0.5)
    
    
