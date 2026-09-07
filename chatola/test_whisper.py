"""
faire ca avant:

export LD_LIBRARY_PATH=$HOME/.local/lib/python3.8/site-packages/nvidia/cublas/lib:$HOME/.local/lib/python3.8/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

"""

from faster_whisper import WhisperModel

class Whisper:
    def __init__( self ):
        self.model = WhisperModel( "large-v3-turbo", device="cuda", compute_type="int8_float16" )
        
    def analyse( self, audio_filename ):
        segments, info = self.model.transcribe( audio_filename, language="fr", condition_on_previous_text=True )
        text = "".join(segment.text for segment in segments)
        return text


def autotest():
    w = Whisper()
    fn = "datas/test_parle_moi_de_greffe_de_cheveux.wav"
    txt = w.analyse( fn )
    print(txt)
    
    
    
if __name__ == "__main__":  
    autotest()



