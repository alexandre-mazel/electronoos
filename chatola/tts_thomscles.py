import os
import time

"""
TTS Chatterbox French - Thomcles

A lancer depuis le venv-tts dans champion/chatola.

Modèle :
    Thomcles/Chatterbox-TTS-French

Le modèle Thomcles est un fine-tuning français de Chatterbox.
Le checkpoint t3_cfg.safetensors est chargé par-dessus le modèle
Chatterbox de base.

Dépendances :
    pip install chatterbox-tts soundfile huggingface_hub safetensors
"""

import torch
import soundfile as sf

from chatterbox.tts import ChatterboxTTS
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file


MODEL_REPO = "Thomcles/Chatterbox-TTS-French"
CHECKPOINT_FILENAME = "t3_cfg.safetensors"

OUTPUT_DIR = os.path.expanduser("~/recordings/tts")

# Fichier optionnel pour cloner une voix.
#
# None = voix générée par le modèle
#
# Exemple :
# AUDIO_PROMPT_PATH = "datas/voice_fr_ref.wav"
#
AUDIO_PROMPT_PATH = None


class AudioSynthesiser:

    def __init__(self):

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("INF: AudioSynthesiser: loading Chatterbox French model...")
        print("INF: device:", self.device)

        # ------------------------------------------------------------
        # 1. Charger le modèle Chatterbox de base
        # ------------------------------------------------------------

        self.model = ChatterboxTTS.from_pretrained(
            device=self.device
        )

        # ------------------------------------------------------------
        # 2. Télécharger / récupérer le checkpoint français
        # ------------------------------------------------------------

        print("INF: loading Thomcles French checkpoint...")

        checkpoint_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=CHECKPOINT_FILENAME
        )

        print("INF: checkpoint:", checkpoint_path)

        # Charger sur CPU pour éviter un pic VRAM inutile
        t3_state = load_file(
            checkpoint_path,
            device="cpu"
        )

        # Remplacer les poids T3 du modèle de base
        self.model.t3.load_state_dict(t3_state)

        # Libérer immédiatement le state dict CPU
        del t3_state

        print("INF: Thomcles French model loaded.")

        if AUDIO_PROMPT_PATH:
            print(
                "INF: voice cloning reference:",
                AUDIO_PROMPT_PATH
            )

    def synthesise(self, text):

        time_begin = time.time()

        print(
            "INF: AudioSynthesiser: synthesising:",
            text
        )

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        timestamp += "_%03d" % int(
            (time.time() % 1) * 1000
        )

        filename = os.path.join(
            OUTPUT_DIR,
            "tts_%s.wav" % timestamp
        )

        # ------------------------------------------------------------
        # Génération
        # ------------------------------------------------------------

        with torch.inference_mode():

            if AUDIO_PROMPT_PATH:

                audio = self.model.generate(
                    text=text,
                    audio_prompt_path=AUDIO_PROMPT_PATH,

                    # Valeurs de départ raisonnables
                    exaggeration=0.5,
                    temperature=0.6,
                    cfg_weight=0.3
                )

            else:

                audio = self.model.generate(
                    text=text,

                    exaggeration=0.5,
                    temperature=0.6,
                    cfg_weight=0.3
                )

        # ------------------------------------------------------------
        # Sauvegarde
        #
        # On utilise soundfile et PAS torchaudio.save().
        # Cela évite torchcodec/libnvrtc.
        # ------------------------------------------------------------

        samples = audio.squeeze().cpu().numpy()

        sf.write(
            filename,
            samples,
            self.model.sr
        )

        # ------------------------------------------------------------
        # Stats
        # ------------------------------------------------------------

        duration = time.time() - time_begin

        audio_duration = len(samples) / self.model.sr

        print("generated:", filename)
        print("audio duration: %.2fs" % audio_duration)
        print("generation duration: %.2fs" % duration)

        if audio_duration > 0:
            print(
                "RTF: %.2f"
                % (duration / audio_duration)
            )

        if torch.cuda.is_available():

            allocated = (
                torch.cuda.max_memory_allocated()
                / 1024**2
            )

            reserved = (
                torch.cuda.max_memory_reserved()
                / 1024**2
            )

            print(
                "VRAM peak allocated: %.1f MB"
                % allocated
            )

            print(
                "VRAM peak reserved: %.1f MB"
                % reserved
            )

            torch.cuda.reset_peak_memory_stats()

        return filename


def autotest():

    synthesiser = AudioSynthesiser()

    text = (
        "Bonjour ! Je suis Gaia. "
        "Je peux maintenant parler français avec une voix "
        "générée entièrement localement sur votre ordinateur."
    )

    # Test plus intéressant pour le français
    text = (
        "Paris ! Vous pouvez trouver la gare Avenue Henri Martin "
        "du RER C ou la station de métro Rue de la Pompe, "
        "ligne 9, pour vous rendre au coeur de la ville. "
        "La synthèse doit également prononcer correctement "
        "les termes techniques, comme Kubernetes, CUDA, "
        "PyTorch, CTranslate2 et NVIDIA."
    )

    filename = synthesiser.synthesise(text)

    print("audio:", filename)


if __name__ == "__main__":
    autotest()
