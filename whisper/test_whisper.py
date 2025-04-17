# -*- coding: utf-8 -*-

import whisper # pip install openai-whisper
import math
import os
import time

time_begin = time.time()

if os.name == "nt":
    model = whisper.load_model("base")
else:
    model = whisper.load_model("large")

"""
Cette fonction va entre autres appeller ffmpeg en cli:
seen in C:\\Python39\\Lib\\site-packages\\whisper\\audio.py:

    # This launches a subprocess to decode audio while down-mixing
    # and resampling as necessary. Requires the ffmpeg CLI in PATH.
    # fmt: off
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-threads", "0",
        "-i", file,
        "-f", "s16le",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        "-ar", str(sr),
        "-"
    ]
    # fmt: on
    try:
        out = run(cmd, capture_output=True, check=True).stdout
    except CalledProcessError as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
"""
duration = time.time() - time_begin
print("Model loaded in %.2fs" % duration ) # mstab7 base: 0.85s, azure large: 8.88s

time_begin = time.time()

soundname = ""
if len(sys.argv) > 1:
    # syntaxe: <scriptname> <soundname>
    # eg: pyt3 test_whisper.py ~/records/filipe.wav
    soundname = sys.argv[1]
    
if soundname == "":

    soundname = "on_the_fly_mehdi.wav"
    #~ soundname = "alex_test.wav"
    soundname = "alex_test_en.wav" # si on force en francais, ca fait un moche résultat avec une expprod a 0.01: Final que je suis en batterie fossil sociale alors que 0.54 en anglais.
    #~ soundname = "alex_count_2.wav" # si on lui dit pas, il croit que c'est de l'anglais
    soundname = "alex_perfect.wav" # si on le force en francais, ca donne c'est donc parfait avec 0.41 si en anglais: expprob: 0.55.
    soundname = "on_the_fly_mehdi2.wav"
    soundname = "C:/Users/alexa/perso/docs_nextcloud_edu/2024_09_DU_inspe/memoire_docs/record/josse.wav"
    soundname = "test_itw.wav"
    
#~ result = model.transcribe(soundname)
result = model.transcribe(soundname, fp16=False, verbose=True ) # , language="en"
# for a 55s sound:
# mstab7 base: 6.61s, azure large: 38.6s


duration = time.time() - time_begin
print("Transcribed in %.2fs" % duration )

print("Soundname: %s" % soundname )

print(f'The text in audio: \n {result["text"]}')
print(f'Lang detected: {result["language"]}')
#~ print(dir(result))
#~ print(result)
#~ print(result.avg_logprob)

print("Detail:")
for s in result["segments"]:
    print( "[%s --> %s]: %s" % (s["start"], s["end"], s["text"]) )
    print( "  temper: %.2f, avg_logprob: %.2f, expprob: %.2f,  compression_ratio: %.2f, no_speech_prob: %.2f\n" % (s["temperature"], s["avg_logprob"], math.exp(s["avg_logprob"]), s["compression_ratio"], s["no_speech_prob"] ) )
    
    
"""
*** Result model base on mstab7:

Lang detected: fr
Detail:
[0.0 --> 6.0]:  Il dit à mailleur, on voit, bah ça doit être pas mal, bah voilà ça doit être pareil.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[7.0 --> 10.0]:  Surtout que c'est fatagé, ça appartient là.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[10.0 --> 13.0]:  Il a y compris un mot de texte d'un homme politique.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[15.0 --> 17.0]:  C'est ça faire la née des entretiens.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[18.0 --> 20.0]:  Est-ce que c'est clair pour tout le monde, ça ?
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[22.0 --> 23.0]:  Ouais, ou pas ?
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[24.0 --> 34.0]:  Ok, donc, pas un zimé, il faut en transcrire à la main, pas à la main, si c'est pas à la main, c'est en local.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[35.0 --> 40.0]:  Ensuite, il faut bien relire faire un zimé, découper le texte en petit goût.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[41.0 --> 50.0]:  Et ensuite, il faut présenter les discours des uns et des autres sur chacun des thèmes que vous avez découpé.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[50.0 --> 55.0]:  Normalement, c'est les thèmes de la dame d'entretiens, c'est les mêmes, sur qui ça arrive pas.
  temp: 0.00, avg_logprob: -0.38, compression_ratio: 1.11, no_speech_prob: 0.11
  

Soundname: alex_test.wav
Detail:
[0.0 --> 5.6000000000000005]:  Ouais, je suis tout à fait d'accord, c'est trop pareil. Oui oui, tout à fait. Mais toi ? Ouais.
  temp: 0.00, avg_logprob: -0.47, compression_ratio: 1.28, no_speech_prob: 0.26

[7.36 --> 9.36]:  Je suis un peu d'accord, un puits.
  temp: 0.00, avg_logprob: -0.47, compression_ratio: 1.28, no_speech_prob: 0.26
  
Soundname: alex_test_en.wav:
Lang detected: en
Detail:
[0.0 --> 4.0]:  What? I'm totally agree with him.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 0.80, no_speech_prob: 0.17
  
*** Result model large on azure:

Lang detected: fr
Detail:
[0.0 --> 3.74]:  Il dit à Maynard, ouais, ça doit être pas mal, ben voilà, ça doit être pareil.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[5.28 --> 6.24]:  Voilà, c'est pareil.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[7.640000000000001 --> 10.200000000000001]:  Sauf que c'est pas tagué, ça apparaît là.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[10.3 --> 13.4]:  Et là, ils ont pris un bout de texte d'un homme politique.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[15.06 --> 16.52]:  C'est ça, faire l'analyse des entretiens.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[18.2 --> 20.0]:  Est-ce que c'est clair pour tout le monde, ça ?
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[21.16 --> 22.38]:  Ouais.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[22.38 --> 22.44]:  Ouais.
  temp: 0.00, avg_logprob: -0.30, compression_ratio: 1.52, no_speech_prob: 0.16

[22.44 --> 25.44]:  Ouais.
  temp: 0.00, avg_logprob: -0.82, compression_ratio: 0.43, no_speech_prob: 0.07

[52.44 --> 55.44]:  Tiens, c'est les mêmes, sauf que ça arrive pas dans...
  temp: 0.00, avg_logprob: -0.14, compression_ratio: 0.89, no_speech_prob: 0.01
  
Soundname: alex_test.wav
Detail:

[0.0 --> 10.200000000000001]:  ouais je suis tout à fait d'accord c'est trop pareil oui oui tout à fait et toi ouais je suis un peu d'accord avec lui
  temp: 0.00, avg_logprob: -0.07, compression_ratio: 1.41, no_speech_prob: 0.00
  
Soundname: alex_test_en.wav:

Lang detected: en
Detail:
[0.0 --> 5.0]:  I'm totally agree with him
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 0.76, no_speech_prob: 0.04


"""