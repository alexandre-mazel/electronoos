"""
faire ca avant:

export LD_LIBRARY_PATH=$HOME/.local/lib/python3.8/site-packages/nvidia/cublas/lib:$HOME/.local/lib/python3.8/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

"""

from faster_whisper import WhisperModel
import time

class Whisper:
    def __init__( self ):
        self.model = WhisperModel( "large-v3-turbo", device="cuda", compute_type="int8_float16" )
        self.initial_prompt = ""
        self.hotwords = ""
        
    def add_initial_prompt( self, txt ):
        self.initial_prompt += txt
        
    def add_hotwords( self, txt ):
        self.hotwords += txt + "\n"
        
    def analyse( self, audio_filename ):
        time_begin = time.time()
        segments, info = self.model.transcribe( audio_filename, language="fr", condition_on_previous_text=True,
                                                initial_prompt = self.initial_prompt, hotwords=self.hotwords, hotwords_sensitivity=0.8 )
        duration = time.time() - time_begin
        print( "sound duration: %.2fs" % (info.duration) )
        print( "processing duration: %.2fs" % (duration) )
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
    list_wav.append( "datas/test_desc_de_la_fue.wav" )
    
    w.add_initial_prompt( "on parle de chirurgie estethique du cheveux par exemple: greffe des cheveux, et FUE." )
    w.add_hotwords( "assis toi!" )
    # de rajouter ca on passe de greve du cheveux a greffe du cheveux !
    
    for fn in list_wav:
        txt = w.analyse( fn )
        print(txt)
    
    
    
if __name__ == "__main__":  
    autotest()



