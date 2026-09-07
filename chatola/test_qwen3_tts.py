import time

import torch
import soundfile as sf

from qwen_tts import Qwen3TTSModel # python -m pip install -U qwen-tts

MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
REF_AUDIO = "datas/voice_fr_ref.wav"
REF_AUDIO = "datas/voice_fr_ref2.wav"
OUTPUT_AUDIO = "qwen3_test_fr2.wav"

def autotest():
    text = (
    "Bonjour ! Je suis NAO. "
    "Je peux maintenant parler avec une voix générée "
    "entièrement localement sur votre ordinateur."
    )

    ref_text = "bonjour, je m'appelle Alexandre, comment allez vous ? tuyau de pipe"

    print( "loading model..." )

    model = Qwen3TTSModel.from_pretrained(
        MODEL_NAME,
        device_map = "cuda:0",
        dtype = torch.bfloat16,
        attn_implementation = "sdpa"
    )

    print( "generating..." )

    time_begin = time.time()

    wavs, sample_rate = model.generate_voice_clone(
        text = text,
        language = "French",
        ref_audio = REF_AUDIO,
        ref_text = ref_text
    )

    sf.write(
        OUTPUT_AUDIO,
        wavs[0],
        sample_rate
    )

    duration = time.time() - time_begin

    print( "generated:", OUTPUT_AUDIO )
    print( "sample rate:", sample_rate )
    print( "generation duration: %.2fs" % duration ) # 2.4GB VRAM, 14sec (joli resultat)


if __name__ == "__main__":
    autotest()