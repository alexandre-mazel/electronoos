import time

import torch
import soundfile as sf

from qwen_tts import Qwen3TTSModel # python -m pip install -U qwen-tts

MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
REF_AUDIO = "datas/voice_fr_ref.wav"
#~ REF_AUDIO = "datas/voice_fr_ref2.wav"
REF_AUDIO = "datas/voice_fr_ref_gaia.wav" # son pour epti
REF_AUDIO = "datas/voice_fr_ref_gaia2.wav" # devant le bus
#~ REF_AUDIO = "datas/voice_fr_ref_vieux3.wav"
REF_AUDIO = "datas/voice_fr_ref4_majordome.wav"
REF_AUDIO = "datas/voice_fr_ref4_charmeur.wav"

OUTPUT_AUDIO = "qwen3_test_fr_%d.wav" % int(time.time())

def autotest():
    text = (
        "Bonjour ! Je suis NAO. "
        "Je peux maintenant parler avec une voix générée "
        "entièrement localement sur votre ordinateur."
        )
        
    text = ("Bonjour ! C'est Gaia! Papa, je te promet que plus jamais je n'oublierai de me laver les dents le soir, meme si j'ai la super flaime. Promis, et si j'oublie une seule fois, je ne mangerai plus jamais de chocolat de ma vie. Promis juré!")
    text = ("Corto, arrête de jouer a Valorante, tu t'énerve et après t'es tout chafouin!")
    text = ("Alexandre, maintenant tu va te mettre au travail au lieu de jouer avec tous ses synthétiseurs à la noix!")
    #~ text = ("Salut lily, ça va? ça te dit qu'on s'appelle ce soir pour discuter et tout ? et comment elle s'est passé votre éval de français du coup ?")


    ref_text = "bonjour, je m'appelle Alexandre, comment allez vous ? tuyau de pipe"
    ref_text = "Merci, toi aussi, et heu, toi aussi envoie moi une photo de ton outfits"
    ref_text = "Allez c'est parti on attend le, on attend le bus, aujourd'hui on a 2 heures de francais, 2 heures de math, heu, une heure de techno encore, et heu, et une heure d'histoire et après on a fini les cours. Ouais, Ha ha ha ha"
    #~ ref_text = "Non, j'ai dit non, j'veux pas c'est tout. Oui je sais. Dommage ! Vous savez très bien comment je vais Little John. C'est pas une infraction au code de la route que vous avez commise, comme si tout ce que vous aviez fait c'était avoir pris un sens interdit. J'ai eu une idée pour promouvoir les mises en place de plans de successions que propose le cabinet: nous allons faire une vidéo virale. Dites à votre chef Linguini que je prendrais ce qu'il aura l'audace de me servir, dites lui qu'il me surprenne, si toutes fois il en est capable!"
    
    # voice_fr_ref4_majordome:
    ref_text = "Je lui ai dit qu'elle allait être adopter par la famille Legrand, madame."
    
    # voice_fr_ref4_charmeur:
    ref_text = "Par tout les saints du ciel, regardez vos fleurs ! As-ton jamais vu quelque chose de plus magnifique? Madame Dubose, les jardins de Bagatelle ne possèdent rien de comparable à vos fleurs."

    print( "loading model..." )

    model = Qwen3TTSModel.from_pretrained(
        MODEL_NAME,
        device_map = "cuda:0",
        dtype = torch.bfloat16,
        attn_implementation = "sdpa"
    )

    print( "generating..." )

    time_begin = time.time()
    
    instruct = (
        "Parle naturellement en français, sans sur-articuler. "
        "Style conversationnel, détendu, légèrement nonchalant, "
        "avec des variations naturelles de rythme et d'intonation."
        #~ "comme une ado de 13 ans."
        #~ "Parle un peu vite sans articuler de trop."
    )

    wavs, sample_rate = model.generate_voice_clone(
        text = text,
        language = "French",
        ref_audio = REF_AUDIO,
        ref_text = ref_text,
        instruct  = instruct,
        do_sample = True, # stochastique : il tire aléatoirement parmi plusieurs tokens possibles, selon leurs probabilités. (donne plus de variation)
        
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