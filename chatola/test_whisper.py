from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3-turbo",
    device="cuda",
    compute_type="int8_float16"
)

segments, info = model.transcribe(
    "test_greffe.wav",
    language="fr",
    condition_on_previous_text=True
)

text = "".join(segment.text for segment in segments)
print(text)

