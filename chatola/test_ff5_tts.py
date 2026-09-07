import time

from f5_tts.api import F5TTS  # pip install f5-tts

def autotest():
    text = (
    "Bonjour ! Je suis NAO. "
    "Je peux maintenant parler avec une voix générée "
    "entièrement localement sur votre ordinateur."
    )

    model = F5TTS(
        device = "cuda",
        #~ model = "F5TTS_French", # pour forcer le francais (non en fait non)
    )

    time_begin = time.time()

    model.infer(
        ref_file = "datas/voice_fr_ref.wav",
        ref_text = "bonjour, je m'appelle Alexandre, comment allez vous ? tuyau de pipe",
        gen_text = text,
        file_wave = "f5_test_fr.wav",
    )

    print( "generation duration: %.2fs" % ( time.time() - time_begin ) )
    print( "audio: f5_test_fr.wav" )
    
    # 2.3GO VRAM, 1.63s, mais ca sonne pas francais du tout, peut etre que mon exemple est trop court?


if __name__ == "__main__":
    autotest()