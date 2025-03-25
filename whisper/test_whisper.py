import whisper # pip install openai-whisper
import os

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

#~ result = model.transcribe("on_the_fly_mehdi.wav")
result = model.transcribe("on_the_fly_mehdi.wav", language="fr", fp16=False, verbose=True)

print(f'The text in audio: \n {result["text"]}')
print(f'Lang detected: \n {result["language"]}')
#~ print(dir(result))
#~ print(result)
#~ print(result.avg_logprob)

print("Detail:")
for s in result["segments"]:
    print( "[%s --> %s]: %s" % (s["start"], s["end"], s["text"]) )
    print( "  temp: %.2f, avg_logprob: %.2f, compression_ratio: %.2f, no_speech_prob: %.2f\n" % (s["temperature"], s["avg_logprob"], s["compression_ratio"], s["no_speech_prob"] ) )