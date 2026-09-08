import time
import torch
import scipy.io.wavfile

from transformers import VitsModel, AutoTokenizer, set_seed

"""

MMS-TTS avec modele francais

cuda: 596MB VRAM pour un son de 8.7s: prend 0.49s puis 0.05s (rapide) (x17.5) (mais caching ou ?)

"""


MODEL_NAME = "facebook/mms-tts-fra"


print("Chargement du modèle...")

device = "cuda" if torch.cuda.is_available() else "cpu"

print("device:", device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = VitsModel.from_pretrained(
    MODEL_NAME
).to(device)

model.eval()

print("Modèle chargé.")
print("sampling rate:", model.config.sampling_rate)

for i in range(1):


    text = (
        "Bonjour ! Je suis Gaïa. "
        "Je vais vous parler de chirurgie esthétique des cheveux, "
        "et notamment de la greffe de cheveux et de la technique FUE, ... houpsse pardon,. je veux dire la tek-nique F. U. E."
    )
    
    #~ text = ("Alexandre, maintenant tu va te mettre au travail au lieu de jouer avec tous ses synthétiseurs à la noix!")


    # MMS est entraîné en minuscules et sans ponctuation.
    # Le tokenizer normalise normalement le texte lui-même.
    inputs = tokenizer(
        text,
        return_tensors="pt"
    ).to(device)


    # Reproductibilité
    set_seed(555)


    print("Synthèse...")

    time_begin = time.time()

    with torch.no_grad():
        output = model(**inputs)

    duration = time.time() - time_begin

    waveform = output.waveform[0]

    audio_duration = len(waveform) / model.config.sampling_rate
    
    print(
        "audio duration: %.2fs"
        % (audio_duration)
    )

    print(
        "generation duration: %.2fs (x%.1f)"
        % (duration,audio_duration/duration)
    )


    filename = "mms_fr.wav"

    scipy.io.wavfile.write(
        filename,
        rate=model.config.sampling_rate,
        data=waveform.cpu().numpy()
    )


    print("written:", filename)