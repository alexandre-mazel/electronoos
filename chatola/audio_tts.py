import os
import time
import wave

USE_CHATTERBOX = False

OUTPUT_DIR = os.path.expanduser( "~/recordings/tts" )

if USE_CHATTERBOX:
    import torchaudio
    from chatterbox.tts import ChatterboxTTS
else:
    import soundfile as sf
    from kokoro_onnx import Kokoro # pip install kokoro-onnx soundfile
    # a copier a cote: kokoro-v1.0.onnx, voices-v1.0.bin



class AudioSynthesiser:
    def __init__( self ):
        os.makedirs( OUTPUT_DIR, exist_ok = True )

        if USE_CHATTERBOX:
            self.model = ChatterboxTTS.from_pretrained(
                device = "cuda"
            )
        else:
            self.model = Kokoro(
                "kokoro-v1.0.onnx",
                "voices-v1.0.bin"
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
            audio = self.model.generate( text )

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

    filename = synthesiser.synthesise( text )

    print( "audio:", filename )


if __name__ == "__main__":
    autotest()
s