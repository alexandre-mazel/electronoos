"""
process big wav file, cut them...
"""
import wav

def autocut(wavfile):
    w = wav.Wav(wavfile,bQuiet=False)
    print(w)
    w.write("/tmp/t.wav")
    
    
if __name__ == "__main__":
    autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/robot1.wav")
    
    
