"""
faire ca avant:

export LD_LIBRARY_PATH=$HOME/.local/lib/python3.8/site-packages/nvidia/cublas/lib:$HOME/.local/lib/python3.8/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

"""

from faster_whisper import WhisperModel # pip install faster-whisper # python -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
import time

DEFAULT_MODEL = "large-v3-turbo"
#~ DEFAULT_MODEL = "large-v3"

DEFAULT_COMPUTE_TYPE = "float16" # normal => 2.29 GB en turbo, 3.63 en normal
DEFAULT_COMPUTE_TYPE = "int8_float16" # normal: 1.33 en turbo, 2.0 en normal
#~ DEFAULT_COMPUTE_TYPE = "int8" # normal: 1.33 en turbo, 2.0 en normal


use_whisper = True # sinon c'est faster_whisper
use_whisper = False
if use_whisper:
    import whisper # python -m pip install -U openai-whisper

class Whisper:
    def __init__( self ):
        if not use_whisper:
            self.model = WhisperModel( DEFAULT_MODEL, device="cuda", compute_type= DEFAULT_COMPUTE_TYPE )
        else:
            self.model = whisper.load_model( DEFAULT_MODEL, device="cuda" )
            
        self.initial_prompt = ""
        self.hotwords = ""
        
    def add_initial_prompt( self, txt ):
        self.initial_prompt += txt
        
    def add_hotwords( self, txt ):
        self.hotwords += txt + "\n"
        
    def analyse( self, audio_filename ):
        time_begin = time.time()
        segments, info = self.model.transcribe( audio_filename, language="fr", condition_on_previous_text=True,
                                                initial_prompt = self.initial_prompt, hotwords=self.hotwords, 
                                                #~ hotwords_sensitivity=0.8 
                                                )
        duration = time.time() - time_begin
        print( "sound duration: %.2fs" % (info.duration) )
        print( "processing duration: %.3fs" % (duration) )
        print( "info:", info )
        print( "segments: ", segments )
        text = "".join(segment.text for segment in segments)
        return text


def autotest():
    w = Whisper()
    list_wav = []
    list_wav.append( "datas/test_quel_heure_est_il.wav" )
    list_wav.append( "datas/test_assis_toi.wav" )
    list_wav.append( "datas/test_parle_moi_de_greffe_de_cheveux.wav" )
    list_wav.append( "datas/test_c_quoi_la_fue.wav" )
    list_wav.append( "datas/test_desc_de_la_fue.wav" ) # son de 9s, 0.040s en v3, 0.039s en v3-turbo
    
    w.add_initial_prompt( "on parle de chirurgie estethique du cheveux par exemple: greffe des cheveux, et FUE." )
    w.add_hotwords( "assis toi!" )
    # en large-v3-turbo, les prompt permette de passer de greve du cheveux a greffe du cheveux !
    # mais assis toi n'est pas reconnu
    # en large-v3 tout est correctement reconnu meme sans les hotword et initial prompt
    
    for fn in list_wav:
        for i in range(1): # mettre plus pour avoir le temps de voir la vram utilise
            txt = w.analyse( fn )
            print(txt)
    
    
    
if __name__ == "__main__":  
    autotest()



