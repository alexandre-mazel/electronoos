import base64
import json
import requests
import time

HOST = "engrenage.studio"

OLLAMA_URL = f"http://{HOST}:45035/api/chat"


def encode_image(filename):
    with open(filename, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def analyze_image( filename, strModel, extra_instruction = "", verbose=False ):
    
    if verbose: print( "INF: analyze_image: '%s'..." % filename )
    
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
Omet toute introduction du type "L'image montre ..."

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

    if verbose: print( "INF: analyze_image: posting..." )

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
                "temperature": 0.,
                "seed": 42,
            }
        },
        timeout = 300
    )

    response.raise_for_status()
    
    duration = time.time() - time_begin
    
    if verbose: print( "duration: %.3fs" % duration )

    result = response.json()
    
    if verbose: print( "result: " + str(result) )
    
    ans = result["message"]["content"]
    
    # que si python2
    if 0:
        if isinstance(ans, unicode):
            ans_utf8 = ans.encode("utf-8")
        else:
            ans_utf8 = answer
    else:
        ans_utf8 = ans
            
    if verbose: print( "ans: " + ans_utf8 )

    return json.loads(result["message"]["content"])


def main():
    strModel = "qwen2.5vl:7b" # qwen2.5vl:7b    5ced39dfa4ba    5.9 GB    100% GPU     8192
    # fonctionne tres bien et reproductible et format bien maintenu, parfait!
    
    
    #~ strModel = "gemma3:12b" # gemma3:12B    f4031aab637d    9.0 GB    13%/87% CPU/GPU    8192
    
    list_img = [ "20260901_111820_small", "20260901_160631_small","20260906_210413_small","20260910_130425_small","20260911_173947_small","girl-4051811_960_720"]
    list_img.extend( ["20240102_105013_small","20240109_161443_small","20240223_094710_small"] )
    print( "\n*** %s ***\n" % strModel )
    
    time_begin_total  = time.time()
    
    for img in list_img:
        
        print( "img: '%s'" % img )
        
        time_begin = time.time()
        
        result = analyze_image( "../test/%s.jpg" % img, strModel )
        
        duration = time.time() - time_begin
        print( "duration: %.3fs" % duration )

        print( "desc: " + result["description"])
        print( "kw: " + (", ".join(result["keywords"]) ) )
        print( "txt: " + (", ".join(result["text"]) ) )
        print("")
        
    duration = time.time() - time_begin_total
    print( "=> total duration: %.3fs" % duration )
    
"""

*** qwen2.5vl:7b ***

img: '20260901_111820_small'
duration: 1.948s
desc: Une bicyclette colorée avec un siège pour enfant est accrochée à un poteau sur un trottoir. Le siège est attaché avec des cordes. En arrière-plan, on voit des tables de café et des personnes qui discutent. Le cadre de la bicyclette est multicolore, avec des tons de rose, de bleu et de jaune. Il y a aussi des paniers sur le côté de la bicyclette. Le trottoir est en béton et il y a des plantes vertes sur le côté.
kw: bicyclette, siège enfant, trottoir, café, tables, poteau, multicolore, paniers, plantes, trottoir, ville
txt: Initial, 110

img: '20260901_160631_small'
duration: 1.631s
desc: Un pot en verre avec un couvercle hermétique contenant une préparation granuleuse, probablement des céréales ou des graines, avec des morceaux de fruits séchés. Le pot est posé sur une surface sombre, entouré de divers objets de cuisine, dont un bol métallique et des bouteilles. Des graines sont éparpillées sur la surface.
kw: pot, couvercle, granules, fruits séchés, cuisine, surface sombre, boulangerie, préparation, céréales, graines, bocal, bouteilles, bol métallique
txt: FORMAT, Nestle, tr

img: '20260906_210413_small'
duration: 1.459s
desc: Une personne assise à une table avec des livres et des cahiers, portant un chapeau jaune et un t-shirt avec un dessin coloré. Elle tient un stylo et semble faire des devoirs. L'environnement montre une cuisine avec des armoires rouges et un réfrigérateur.
kw: personne, table, livres, cahiers, chapeau, jaune, t-shirt, dessin, cuisine, armoires, réfrigérateur
txt: Je m'entraîne, Je m'entraîne

img: '20260910_130425_small'
duration: 2.236s
desc: Un homme présente devant un écran interactif dans une salle de conférence. L'écran affiche une présentation sur le sommeil, avec des graphiques et des textes. Des personnes sont assises devant l'écran, regardant la présentation. L'environnement est un bureau avec des câbles et des équipements électroniques.
kw: homme, écran, conférence, présentation, sommeil, graphiques, textes, salle, câbles, équipements
txt: Saliency, Complexity, Not possible during sleep, Possible in some sleep stages or individuals, Possible in most sleep stages or individuals, Cognitive determinants of sleep processing: saliency of sensory information and complexity of cognitive processing, Some processing seem to be virtually always present, others in light sleep only and some never (i.e., require conscious awareness?), Sleep's sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation), Oudiette & Andriolli (under review)

img: '20260911_173947_small'
duration: 1.426s
desc: Une personne tient un t-shirt plié avec l'inscription 'ADL international 3eme trophée de KARTING' sur l'avant. Le t-shirt est blanc avec un logo bleu et texte bleu. L'arrière de la personne est visible, montrant une partie de son bras et son torse.
kw: t-shirt, plié, blanc, bleu, logo, inscription, carting, trophée, ADL, international, 3eme
txt: ADL, international, 3eme, trophée, de, KARTING

img: 'girl-4051811_960_720'
duration: 1.425s
desc: Une femme assise en tailleur sur un trottoir pavé, sourit largement. Elle porte un ensemble de sport noir et des chaussures de running. À côté d'elle, il y a un réveil vert, une bouteille d'eau bleue et une paire de chaussures de sport. Le fond montre une rue avec des voitures et des arbres.
kw: femme, sport, tailleur, sourire, trottoir, pavé, réveil, bouteille d'eau, chaussures de sport, rue, voitures, arbres
txt: 

img: '20240102_105013_small'
duration: 1.393s
desc: Une personne portant un imperméable de couleur vert fluo avec une capuche intégrale et un casque de couleur verte se tient sur le bord d'une rue. L'environnement montre des arbres dénudés, des maisons, des voitures et des pots de fleurs sur le trottoir. La météo semble pluvieuse ou venteuse.
kw: imperméable, vert fluo, casque, rue, arbres, maisons, voitures, trottoir, pluie, vent
txt: 

img: '20240109_161443_small'
duration: 1.786s
desc: Quatre personnes se trouvent devant un stand vert avec des affiches et des panneaux. Deux d'entre elles portent des costumes de vache, l'une en orange et l'autre en noir et blanc. Un homme en costume noir et un autre en sweat blanc observent la scène. Le stand est soutenu par KOICA et Bodit Inc., avec des messages sur l'agriculture et la technologie agricole.
kw: costume, vache, agriculture, KOICA, stand, affiches, technologie, personnes, costumes, exposition, agricole
txt: KOICA, Bodit Inc., Farmers hand, Animal Welfare, Precision Farming, Sustainable Livestock Farming, 61313

img: '20240223_094710_small'
duration: 1.303s
desc: L'image montre un homme avec des cheveux noirs et une barbe grise. Il porte un pull noir avec des boutons noirs et un collier violet. Derrière lui, on peut voir une porte en verre et une autre porte bleue avec des fenêtres. Il semble être à l'intérieur d'un bâtiment.
kw: homme, cheveux noirs, barbe grise, pull noir, boutons noirs, collier violet, porte en verre, porte bleue, fenêtres, intérieur, bâtiment
txt: 

=> total duration: 14.608s




*** gemma3:12b ***

img: '20260901_111820_small'
duration: 7.039s
desc: L'image montre plusieurs vélos stationnés autour d'un poteau. Au premier plan, un vélo de couleur irisée (violet, bleu, vert) est solidement attaché au poteau. Il est équipé d'un panier avant en métal et d'un siège enfant à l'arrière. D'autres vélos, dont certains sont noirs, sont également stationnés à proximité. En arrière-plan, on aperçoit une terrasse de café avec des tables et des chaises, ainsi que des personnes assises et debout. Une enseigne lumineuse est visible au-dessus du café. Le sol est en béton et en partie recouvert de végétation.
kw: vélo, poteau, siège enfant, panier, terrasse, café, stationnement, irisé, couleur, personnes, ville, pédale, jante, frein, asphalte, vélos, extérieur, pneus, cadre
txt: Initial

img: '20260901_160631_small'
duration: 5.824s
desc: Une jarre en verre à clip hermétique, remplie d'un mélange de noix, graines et morceaux de céréales, est placée sur un plan de travail de cuisine. Des miettes sont éparpillées autour de la jarre. En arrière-plan, on aperçoit un sac bleu avec des inscriptions, une boîte de céréales rouge et plusieurs autres bocaux en verre. Un saladier métallique est également présent sur le plan de travail.
kw: jarre, verre, clip, noix, graines, céréales, cuisine, plan de travail, sac, boîte, bocaux, saladier, mélange, nourriture, ingrédients, miettes, rouge, bleu, cuisine
txt: FORMAT, TR

img: '20260906_210413_small'
duration: 10.041s
desc: Une jeune personne est assise à une table ronde recouverte d'un tissu à motifs colorés. La personne porte un bonnet jaune moutarde et un t-shirt noir avec des motifs orange et rose. Elle est penchée sur un cahier ouvert posé sur la table, tenant un stylo à la main. L'arrière-plan montre une cuisine avec des meubles blancs, un évier et des fenêtres. Des coussins bleus turquoise sont visibles sur un canapé à proximité. La lumière est douce et diffuse, suggérant un éclairage intérieur.
kw: jeune personne, bonnet, t-shirt, table, cahier, stylo, cuisine, fenêtre, coussin, motif, jaune, noir, orange, rose, turquoise, meubles, éclairage, intérieur, apprentissage, étude
txt: De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende

img: '20260910_130425_small'
duration: 7.215s
desc: L'image montre un écran plat fixé à un mur dans ce qui semble être un environnement de recherche ou un laboratoire. L'écran affiche un diagramme complexe et du texte relatif à la cognition et au sommeil. Un bureau en bois clair est visible en bas de l'image, avec des chaises et d'autres équipements. L'éclairage est uniforme et la scène est bien définie.
kw: écran, diagramme, sommeil, recherche, bureau, chaise, mur, laboratoire, cognition, texte, graphique, équipement, éclairage, bois, plat
txt: RESPONDING DURING SLEEP, Cognitive determinants of sleep processing, salience of sensory information and complexity of cognitive processing, Some processing seem to be virtually always present, others in light sleep only and some never (i.e. require conscious awareness?), Sleep’s sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation), Cudenne & Andrillon (under review)

img: '20260911_173947_small'
duration: 5.997s
desc: Une personne tient un t-shirt blanc. Le t-shirt porte un logo bleu et blanc avec les lettres 'ADL' en grand, suivies de 'international' en plus petit. En dessous, on peut lire '3eme trophée de KARTING'. La personne porte également un pantalon bleu foncé. Une étiquette blanche avec une inscription est visible sur le haut du dos du t-shirt. L'arrière-plan est flou et semble être un intérieur avec un mur en bois.
kw: t-shirt, homme, logo, karting, ADL, vêtement, trophée, blanc, bleu, étiquette, international, inscription, pantalon, intérieur, mur, texte
txt: ADL, international, 3eme trophée, de KARTING

img: 'girl-4051811_960_720'
duration: 5.884s
desc: Une femme en tenue de sport noire, assise par terre sur un sol pavé, semble prendre une pause après une activité physique. Elle est souriante et regarde vers la gauche. Elle porte des chaussures de sport noires et grises. À côté d'elle se trouvent une bouteille d'eau turquoise et un haut-parleur vert. L'arrière-plan montre une rue résidentielle avec des bâtiments, des arbres et des voitures. Le ciel est bleu et le soleil brille.
kw: femme, sport, bouteille, haut-parleur, pavé, rue, bâtiment, arbre, voiture, tenue de sport, chaussures, turquoise, vert, soleil, pause, activité physique, sourire, extérieur, résidentiel
txt: 

=> total duration: 42.000s
"""


if __name__ == "__main__":
    main()