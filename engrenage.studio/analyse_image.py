# -*- coding: utf-8 -*-

import ollama
import time

"""
Modèle	Taille Ollama	Vision	Mon avis RPi 5
Moondream 1.8B	~1.7 GB	✅	⭐⭐⭐⭐⭐ très léger
Qwen2.5-VL 3B	~3.2 GB	✅	⭐⭐⭐⭐ meilleur compromis
Qwen2.5-VL 7B	~6 GB	✅	⭐⭐ trop gros pour mon premier choix

Pour un Raspberry Pi 5 CPU, je donnerais ces ordres de grandeur, avec une grosse marge d'incertitude :

Modèle vision	Temps/image estimé	RAM	Avis
Moondream 1.8B	~10–30 s	~2 Go	🟢 très intéressant
Qwen2.5-VL 3B	~20–60 s	~3–4 Go	🟢 meilleur résultat
Gemma 4 E2B	~20–60 s	~3–5 Go	🟢 à tester
Qwen3.5 2B	~30–70 s	~3 Go	🟡
modèles 7B+ vision	~1–3 min+	5–8+ Go	🔴 je déconseille
"""


def analyse_image( filename ):
    
    print( "INF: analyse_image: '%s'" % filename )
    time_begin = time.time()

    response = ollama.chat(
        model="moondream", # try also qwen2.5vl:3b
        messages=[
            {
                "role": "user",
                "content": """Analyse cette image.

    Donne exactement :
    1. Une seule phrase courte décrivant l'image.
    2. Une liste de 5 à 10 tags pertinents, séparés par des virgules.

    Format obligatoire :
    Description: <une phrase>
    Tags: <tag1>, <tag2>, <tag3>, ...

    Ne donne rien d'autre.""",
                "images": [filename]
            }
        ]
    )
    
    print( "duration: %.3fs" % (time.time()-time_begin) )

    ret = response["message"]["content"]
    return ret
    
    
fn = "./files/alex/A52s/internal/Pictures/WhatsApp/IMG-20260804-WA0011.jpg"
#~ fn = fn.replace("/files/","/thumb/")
print(analyse_image(fn))