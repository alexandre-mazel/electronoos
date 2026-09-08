print( "INF: tts_mms.py: importing..." )
import torch
import scipy.io.wavfile
import os
import time

print( "INF: tts_mms.py: begin importing - med" )

from transformers import VitsModel, AutoTokenizer, set_seed

print( "INF: tts_mms.py: begin importing - end" )

"""

MMS-TTS avec modele francais

cuda: 596MB VRAM pour un son de 8.7s: prend 0.49s puis 0.05s (rapide) (x17.5) (mais caching ou ?)
(dans le code, ca affiche 287.8 MB de VRAM)

en cpu pur (champion1): pour un son de 13s: 3.11s soit x4.2 ca reste rapide.

a lancer depuis le venv-tts dans champion/chatola
utilise Python 3.11

Installation :
    pip install torch transformers scipy

Modèle :
    facebook/mms-tts-fra
"""



OUTPUT_DIR = os.path.expanduser("~/recordings/tts")

MODEL_NAME = "facebook/mms-tts-fra"


class AudioSynthesiser:
    def __init__(self):
        print( "INF: tts_mms:AudioSynthesiser: initing..." )
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        import torch
        from transformers import VitsModel, AutoTokenizer

        self.torch = torch

        # Utilise CUDA si disponible, sinon CPU.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = "cpu" # force cpu

        print( "INF: AudioSynthesiser: loading MMS-TTS model..." )
        print( "INF: AudioSynthesiser: device:", self.device )

        self.tokenizer = AutoTokenizer.from_pretrained( MODEL_NAME )

        self.model = VitsModel.from_pretrained( MODEL_NAME ).to(self.device)

        self.model.eval()

        self.sample_rate = self.model.config.sampling_rate

        print( "INF: AudioSynthesiser: MMS-TTS loaded" )

        print(
            "INF: AudioSynthesiser: sample rate:",
            self.sample_rate
        )

        if self.device == "cuda":
            print(
                "INF: AudioSynthesiser: GPU:",
                torch.cuda.get_device_name(0)
            )

            print(
                "INF: AudioSynthesiser: VRAM after load: %.1f MB"
                % (
                    torch.cuda.memory_allocated()
                    / 1024
                    / 1024
                )
            )
            
        print( "INF: tts_mms:AudioSynthesiser: initing - end" )


    def synthesise(self, text):
        time_begin = time.time()

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        timestamp += "_%03d" % int(
            (time.time() % 1) * 1000
        )

        filename = os.path.join(
            OUTPUT_DIR,
            "tts_%s.wav" % timestamp
        )


        print(
            "INF: AudioSynthesiser: synthesising:",
            text
        )


        # ---------------------------------------------------------
        # Préparation du texte
        # ---------------------------------------------------------

        inputs = self.tokenizer(
            text,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }


        # ---------------------------------------------------------
        # Mesure du pic VRAM
        # ---------------------------------------------------------

        if self.device == "cuda":
            self.torch.cuda.reset_peak_memory_stats()


        # ---------------------------------------------------------
        # Synthèse
        # ---------------------------------------------------------

        with self.torch.no_grad():
            output = self.model(
                **inputs
            )


        # ---------------------------------------------------------
        # Récupération du waveform
        # ---------------------------------------------------------

        audio = output.waveform[0]


        # ---------------------------------------------------------
        # Sauvegarde WAV
        # ---------------------------------------------------------

        import scipy.io.wavfile

        scipy.io.wavfile.write(
            filename,
            self.sample_rate,
            audio.cpu().numpy()
        )


        # ---------------------------------------------------------
        # Statistiques
        # ---------------------------------------------------------

        duration = time.time() - time_begin

        audio_duration = (
            len(audio)
            / self.sample_rate
        )

        print(
            "generated:",
            filename
        )

        print(
            "audio duration: %.2fs"
            % audio_duration
        )

        print( "generation duration: %.2fs (x%.1f)" % (duration,audio_duration/duration) )


        if self.device == "cuda":
            vram_peak = (
                self.torch.cuda.max_memory_allocated()
                / 1024
                / 1024
            )

            print(
                "VRAM peak: %.1f MB"
                % vram_peak
            )


        return filename
        
# class AudioSynthesiser - end


def autotest():
    synthesiser = AudioSynthesiser()

    text = (
        "Bonjour ! Je suis Gaia ! "
        "Papa, je te promets que plus jamais "
        "je n'oublierai de me laver les dents le soir, "
        "même si j'ai la super flemme. "
        "Promis, et si j'oublie une seule fois, "
        "je ne mangerai plus jamais de chocolat de ma vie. "
        "Promis juré !"
    )

    text = (
        "Bonjour ! Je suis Gaïa. "
        "Je vais vous parler de chirurgie esthétique des cheveux, "
        "et notamment de la greffe de cheveux et de la technique FUE, ... houpsse pardon,. je veux dire la tek-nique F. U. E."
        )
    
    #~ text = ("Alexandre, maintenant tu va te mettre au travail au lieu de jouer avec tous ses synthétiseurs à la noix!")


    for i in range(1):
        time_begin = time.time()

        filename = synthesiser.synthesise(
            text
        )

        print(
            "audio:",
            filename
        )

        print(
            "duration: %.2fs"
            % (time.time() - time_begin)
        )


if __name__ == "__main__":
    autotest()