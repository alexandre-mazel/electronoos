import os
import time
import wave

"""
a lancer depuis le venv-tts dans champion/chatola (utilise un autre python3.11)
"""

USE_CHATTERBOX = True # 3.5G VRAM
#~ USE_CHATTERBOX = False

OUTPUT_DIR = os.path.expanduser( "~/recordings/tts" )

if USE_CHATTERBOX:
    # pour eviter qu'il essaye de recharger a chaque fois (mais si il manque un modele un jour, il faudra commenter cette ligne temporairement bien sur)
    os.environ["HF_HUB_OFFLINE"] = "1"
    
    import torchaudio
    from chatterbox.tts import ChatterboxTTS # pip install chatterbox-tts
    
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS # pour le fr


else:
    import soundfile as sf
    from kokoro_onnx import Kokoro # pip install kokoro-onnx soundfile
    # a copier dans data: kokoro-v1.0.onnx, voices-v1.0.bin
    # wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    # wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin




class AudioSynthesiser:
    def __init__( self ):
        os.makedirs( OUTPUT_DIR, exist_ok = True )

        if USE_CHATTERBOX:
            print( "INF: AudioSynthesiser: loading Chatterbox model..." )
            #~ self.model = ChatterboxTTS.from_pretrained(
            self.model = ChatterboxMultilingualTTS.from_pretrained( # pour du fr
                device = "cuda"
                #~ device = "cpu"
            )
            
            self.model.prepare_conditionals("datas/voice_fr_ref.wav") # pour du francais il faut lui faire un modele de francais pour qu'il copie la voix # ici chargé une seule fois
            self.model.prepare_conditionals("datas/voice_fr_ref_gaia.wav")
            self.model.prepare_conditionals("datas/voice_fr_ref_gaia2.wav")
            self.model.prepare_conditionals("datas/voice_fr_ref_vieux3.wav")
            
        else:
            self.model = Kokoro(
                "datas/kokoro-v1.0.onnx",
                #~ "datas/kokoro-v1.0.int8.onnx", # moins de ram, mais etonnament plus lent...
                "datas/voices-v1.0.bin"
            )

    def synthesise( self, text ):
        time_begin = time.time()

        timestamp = time.strftime( "%Y%m%d_%H%M%S" )
        timestamp += "_%03d" % int( ( time.time() % 1 ) * 1000 )

        filename = os.path.join(
            OUTPUT_DIR,
            "tts_%s.wav" % timestamp
        )

        if USE_CHATTERBOX:
            audio = self.model.generate( text, language_id = "fr", 
                # audio_prompt_path = "datas/voice_fr_ref.wav"  # ne pas le passer a chaque coup, pour gagner du temps...
                    exaggeration = 0.3, # default 0.5
                    cfg_weight = 0.7, # de combien on colle a la ref ? default: 0.5
                    temperature = 0.2 # default: 0.8
            )

            torchaudio.save(
                filename,
                audio.cpu(),
                self.model.sr
            )
        else:
            samples, sample_rate = self.model.create(
                text,
                voice = "ff_siwis",
                speed = 1.0,
                lang = "fr-fr"
            )

            sf.write(
                filename,
                samples,
                sample_rate
            )

        duration = time.time() - time_begin

        print( "generated:", filename )
        print( "generation duration: %.2fs" % duration )

        return filename


def autotest():
    synthesiser = AudioSynthesiser()

    text = (
        "Bonjour ! Je suis NAO. "
        "Je peux maintenant parler avec une voix générée "
        "entièrement localement sur votre ordinateur."
    )
    
    text = ( "Bonjour ! C'est Gaia! Papa, je te promet que plus jamais je n'oublierai de me laver les dents le soir, meme si j'ai la super flaime. Promis, et si j'oublie une seule fois, je ne mangerai plus jamais de chocolat de ma vie. Promis juré!")

    for i in range(1):
        time_begin = time.time()
        filename = synthesiser.synthesise( text )

        print( "audio:", filename )
        print( "duration: %.2fs" % (time.time() - time_begin) ) # pour un son de 6 sec: chatterbox: cuda sur champion1: 4.7s (3.78 si on charge le modele de voix fr une seule fois avant), cpu sur champion1: 36s, kokoro: 1.60s, kokoro int8: 7.22s ?
        # resultat top quand meme pour le temps sur ordi, c'est le meilleur je trouve, et le clonage c'est ouf !
        # mais qwen si on n'est pas préssé et encore plus ouf!

if __name__ == "__main__":
    autotest()