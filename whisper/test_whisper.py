import whisper # pip install openai-whisper
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
    # and resampling as necessary.  Requires the ffmpeg CLI in PATH.
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
print("model loaded in %.2fs" % duration ) # mstab7 base: 0.85s, azure large: 

time_begin = time.time()
#~ result = model.transcribe("on_the_fly_mehdi.wav")
result = model.transcribe("on_the_fly_mehdi.wav", fp16=False, verbose=True) # , language="fr",

duration = time.time() - time_begin
print("transcribed in %.2fs" % duration )

print(f'The text in audio: \n {result["text"]}')
print(f'Lang detected: {result["language"]}')
#~ print(dir(result))
#~ print(result)
#~ print(result.avg_logprob)

print("Detail:")
for s in result["segments"]:
    print( "[%s --> %s]: %s" % (s["start"], s["end"], s["text"]) )
    print( "  temp: %.2f, avg_logprob: %.2f, compression_ratio: %.2f, no_speech_prob: %.2f\n" % (s["temperature"], s["avg_logprob"], s["compression_ratio"], s["no_speech_prob"] ) )
    
    
"""
Result model base on mstab7:

Lang detected: fr
Detail:
[0.0 --> 6.0]:  Il dit � mailleur, on voit, bah �a doit �tre pas mal, bah voil� �a doit �tre pareil.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[7.0 --> 10.0]:  Surtout que c'est fatag�, �a appartient l�.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[10.0 --> 13.0]:  Il a y compris un mot de texte d'un homme politique.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[15.0 --> 17.0]:  C'est �a faire la n�e des entretiens.
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[18.0 --> 20.0]:  Est-ce que c'est clair pour tout le monde, �a ?
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[22.0 --> 23.0]:  Ouais, ou pas ?
  temp: 0.00, avg_logprob: -0.61, compression_ratio: 1.47, no_speech_prob: 0.32

[24.0 --> 34.0]:  Ok, donc, pas un zim�, il faut en transcrire � la main, pas � la main, si c'est pas � la main, c'est en local.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[35.0 --> 40.0]:  Ensuite, il faut bien relire faire un zim�, d�couper le texte en petit go�t.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[41.0 --> 50.0]:  Et ensuite, il faut pr�senter les discours des uns et des autres sur chacun des th�mes que vous avez d�coup�.
  temp: 0.00, avg_logprob: -0.25, compression_ratio: 1.63, no_speech_prob: 0.07

[50.0 --> 55.0]:  Normalement, c'est les th�mes de la dame d'entretiens, c'est les m�mes, sur qui �a arrive pas.
  temp: 0.00, avg_logprob: -0.38, compression_ratio: 1.11, no_speech_prob: 0.11

"""