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

Retourne exclusivement un objet JSON valide avec exactement ces trois champs :

{
  "description": "description détaillée de l'image",
  "keywords": ["mot1", "mot2", "mot3"],
  "text": ["mot1", "mot2", "mot3"],
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

TEXT :
Recopie exactement tout le texte réellement lisible dans l'image.
Ne reformule pas et ne traduis pas le texte.
Conserve autant que possible l'orthographe, les chiffres, les symboles
et les majuscules/minuscules.
Chaque élément de texte distinct doit être retourné comme une chaîne
séparée dans le tableau.
Si aucun texte n'est lisible, retourne un tableau vide.
Ne devine jamais un texte qui n'est pas clairement visible.

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
                    },
                "text": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                }, # end of properties
                "required": [
                    "description",
                    "keywords",
                    "text"
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
    
    list_img = [ "20260901_160631_small","20260901_160631_small","20260906_210413_small","20260910_130425_small","20260911_173947_small","girl-4051811_960_720"]
    
    for img in list_img:
        result = analyze_image( "../test/%s.jpg" % img, strModel )

        print( "desc: " + result["description"])
        print( "kw: " + (", ".join(result["keywords"]) ) )
        print( "txt: " + (", ".join(result["text"]) ) )
    
"""
20260901_111820_small:
1.8-2.243s
desc: Une bicyclette colorée avec un siège pour enfant est accrochée à un poteau de rue. Le cadre de la bicyclette est multicolore, avec des tons de rose, de bleu et de jaune. Le siège pour enfant est noir et gris, fixé sur le siège arrière de la bicyclette. Le poteau de rue est brun et métallique. En arrière-plan, on peut voir des tables et des chaises de café, des personnes qui se promènent et des vélos garés. La scène se déroule dans une rue animée, avec des voitures et des piétons en arrière-plan.
kw: bicyclette, siège enfant, poteau, rue, café, tables, chaises, voitures, piétons, multicolore, cadre, siège arrière, ville, activité, urbain, vélo, garage, rue animée

20260901_160631_small:
1.5s
desc: Un pot en verre avec un couvercle hermétique contenant une préparation granuleuse, probablement des céréales ou des graines, avec des morceaux de fruits séchés. Le pot est posé sur une surface sombre, entouré de divers objets de cuisine, dont des bouteilles et des contenants en verre. Un bol métallique est également visible à côté du pot.
kw: pot, verre, couvercle, granules, fruits séchés, cuisine, surface sombre, bouteilles, contenants, bol métallique
txt: Nestlé, FORMAT,

"""


if __name__ == "__main__":
    main()