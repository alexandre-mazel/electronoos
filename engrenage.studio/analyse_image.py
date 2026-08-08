# -*- coding: utf-8 -*-

import ollama


def analyse_image( filename ):

    response = ollama.chat(
        model="moondream",
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
                "images": ["photo.jpg"]
            }
        ]
    )

    ret = response["message"]["content"]
    return ret
    
    
fn = "./files/alex/A52s/internal/Pictures/WhatsApp/IMG-20260804-WA0011.jpg"