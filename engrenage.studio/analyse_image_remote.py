import base64
import json
import requests
import time

HOST = "engrenage.studio"

OLLAMA_URL = f"http://{HOST}:45035/api/chat"


def encode_image(filename):
    with open(filename, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def analyze_image( filename, strModel, extra_instruction = "" ):
    
    print( "INF: analyze_image: '%s'..." % filename )
    
    time_begin = time.time()
    
    image = encode_image(filename)

    prompt = """
Analyse cette image très précisément.

Retourne exclusivement un objet JSON valide avec exactement ces deux champs :

{
  "description": "description détaillée de l'image",
  "keywords": ["mot1", "mot2", "mot3"]
}

DESCRIPTION :
Décris uniquement ce qui est réellement visible.
Décris les personnes, objets, animaux, environnement,
actions, couleurs, textes visibles et éléments importants.
Ne déduis pas une information qui n'est pas visible.
La description doit etre naturelle, précise et en francais.

KEYWORDS :
Produis entre 5 et 20 mots-clés pertinents en francais.
Les mots-clés doivent correspondre a des éléments réellement visibles.
Utilise des termes simples et utiles pour effectuer une recherche
ultérieure dans une base d'images.
evite les mots trop génériques comme "image", "photo", "objet".
Utilise des noms au singulier lorsque c'est pertinent.

""" + extra_instruction

    print( "INF: analyze_image: posting..." )

    response = requests.post(
        OLLAMA_URL,
        json = {
            "model": strModel,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image]
                }
            ],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "description",
                    "keywords"
                ]
            },
            "options": {
                "temperature": 0.
            }
        },
        timeout = 300
    )

    response.raise_for_status()
    
    duration = time.time() - time_begin
    
    print( "duration: %.3fs" % duration )

    result = response.json()
    
    print( "result: " + str(result) )
    
    ans = result["message"]["content"]
    
    # que si python2
    if 0:
        if isinstance(ans, unicode):
            ans_utf8 = ans.encode("utf-8")
        else:
            ans_utf8 = answer
    else:
        ans_utf8 = ans
            
    print( "ans: " + ans_utf8 )

    return json.loads(result["message"]["content"])


def main():
    strModel = "qwen2.5vl:7b" # qwen2.5vl:7b    5ced39dfa4ba    5.9 GB    100% GPU     8192
    result = analyze_image( "../test/20260901_111820_small.jpg", strModel )

    print( "desc: " + result["description"])
    print()
    print("kw: " + (", ".join(result["keywords"]) ) )
    
"""
20260901_111820_small.jpg:

desc: Une bicyclette colorée avec un siège pour enfant est accrochée à un poteau de rue. Le cadre de la bicyclette est multicolore, avec des tons de rose, de bleu et de jaune. Le siège pour enfant est noir et gris, fixé sur le siège arrière de la bicyclette. Le poteau de rue est brun et métallique. En arrière-plan, on peut voir des tables et des chaises de café, des personnes qui se promènent et des vélos garés. La scène se déroule dans une rue animée, avec des voitures et des piétons en arrière-plan.
kw: bicyclette, siège enfant, poteau, rue, café, tables, chaises, voitures, piétons, multicolore, cadre, siège arrière, ville, activité, urbain, vélo, garage, rue animée
"""


if __name__ == "__main__":
    main()