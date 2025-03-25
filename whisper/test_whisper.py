import whisper # pip install openai-whisper
#~ model = whisper.load_model("base")
model = whisper.load_model("large")

#~ result = model.transcribe("on_the_fly_mehdi.wav")
result = model.transcribe("on_the_fly_mehdi.wav", language="fr", fp16=False, verbose=True)

print(f' The text in video: \n {result["text"]}')