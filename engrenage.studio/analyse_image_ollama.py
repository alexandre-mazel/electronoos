# -*- coding: utf-8 -*-

import base64
import json
import requests
import time

HOST = "engrenage.studio"

OLLAMA_DEFAULT_URL = f"http://{HOST}:45035/api/chat"

def encode_image(filename):
    with open(filename, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def analyse_image_from_filename( host_url, image_filename, strModel, people_identification = "", extra_instruction = "", lang = "fr", verbose=False ):
    if verbose: print( "INF: analyse_image_from_filename: '%s'..." % image_filename )
    image = encode_image(image_filename)
    return analyse_image_buffer_b64( host_url, image, strModel, people_identification=people_identification, extra_instruction = extra_instruction, lang=lang, verbose=verbose )



def analyse_image_buffer( host_url, image, strModel, people_identification = "", extra_instruction = "", lang = "fr", verbose=False ):
    img_b64 = base64.b64encode(image).decode("utf-8")
    return analyse_image_buffer_b64( host_url, img_b64, strModel, people_identification=people_identification, extra_instruction = extra_instruction, lang=lang, verbose=verbose )
    
def analyse_image_buffer_b64( host_url, image, strModel, people_identification = "", extra_instruction = "", lang = "fr", verbose=False ):
    
    time_begin = time.time()

    prompt_fr = """
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

IMPORTANT — IDENTIFICATION DES PERSONNES :

Des prénoms correspondant aux personnes présentes dans l'image
peuvent être fournis ci-dessous.

Si un prénom est fourni, tu DOIS utiliser ce prénom pour désigner
la personne correspondante dans la description.

Ne dis PAS "une personne", "un homme", "une femme", "un individu"
ou "quelqu'un" lorsque cette personne possède un prénom fourni.

PEOPLE_IDENTIFICATION

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

""" 

    prompt_en = """
Analyze this image very precisely.

Return exclusively a valid JSON object with exactly these three fields:

{
  "description": "detailed description of the image",
  "keywords": ["word1", "word2", "word3"],
  "text": ["word1", "word2", "word3"],
}

DESCRIPTION:
Describe only what is actually visible.
Describe the people, objects, animals, environment,
actions, colors, visible text, and important elements.
Do not infer information that is not visible.
The description must be natural, precise, and in English.
Omit any introduction such as "The image shows ..."

IMPORTANT: PEOPLE IDENTIFICATION:

First names corresponding to people present in the image
may be provided below.

If a first name is provided, you MUST use that first name to refer
to the corresponding person in the description.

Do NOT say "a person", "a man", "a woman", "an individual"
or "someone" when that person has a provided first name.

PEOPLE_IDENTIFICATION

KEYWORDS:
Produce between 5 and 20 relevant keywords in English.
The keywords must correspond to elements that are actually visible.
Use simple and useful terms for subsequent searches
in an image database.
Avoid overly generic words such as "image", "photo", "object".
Use singular nouns when appropriate.

TEXT:
Transcribe exactly all text that is actually readable in the image.
Do not rephrase or translate the text.
Preserve spelling, numbers, symbols, and capitalization
as accurately as possible.
Each distinct text element must be returned as a separate string
in the array.
If no text is readable, return an empty array.
Never guess text that is not clearly visible.

"""

   
    if lang == "fr":
        prompt = prompt_fr.replace( "PEOPLE_IDENTIFICATION", people_identification )
    else:
        prompt = prompt_en.replace( "PEOPLE_IDENTIFICATION", people_identification )


    prompt += extra_instruction
    
    prompt += """Do not explain your reasoning.
Do not discuss whether the text is upside down, mirrored, reversed, rotated, or correct.
Do not compare it with the example.
If the text is visually ambiguous, make your best reading and stop.
"""
    

    if verbose: print( "prompt:\n%s" % prompt )

    if verbose: print( "INF: analyse_image: posting..." )

    response = requests.post(
        host_url,
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
                "temperature": 0,
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
    
    print( "DBG: done_reason: " + result["done_reason"] )
    if ans == "":
        print( "WRN: ans is empty!" )
        return {"description":"","keywords":"","text":""} 

    return json.loads(result["message"]["content"])


def main():
    strModel = "qwen2.5vl:7b" # qwen2.5vl:7b    5ced39dfa4ba    5.9 GB    100% GPU     8192 5.9 ca fait 8.4 dans la ram avec ollama, auquel tu peux ajouter 1.4 d'analyse de visage... c'est un peu juste.
    # fonctionne tres bien et reproductible et format bien maintenu, parfait!
    
    
    strModel = "gemma3:12b" # gemma3:12B    f4031aab637d    9.0 GB    13%/87% CPU/GPU    8192
    # parfois un peu long
    
    strModel = "qwen3-VL:8b" # Qwen3-VL:8b    901cae732162    6.4 GB    100% GPU     8192 
    # super long et parfois ne donne pas de resultat (car part en boucle dans le thinking alors que j'avais essayé de le desactiver)
    
    strModel = "gemma4:12b" # gemma4:12B    4eb23ef187e2    8.1 GB    100% GPU 
    # super long
    
    strModel = "qwen3-vl:30b-a3b" # Qwen3-VL:30b-a3b    eda0be100877    20 GB    60%/40% CPU/GPU    8192
    # ultra long


    list_img = [ "20260901_111820_small", "20260901_160631_small","20260906_210413_small","20260910_130425_small","20260911_173947_small","girl-4051811_960_720"]
    list_img.extend( ["20240102_105013_small","20240109_161443_small","20240223_094710_small"] )
    
    
    if 1:
        # pas dans le bench actuel
        list_img.extend( ["20260922_135754_tableau_courbet"] )
    
        
        # force juste le dernier
        list_img = list_img[-1:]


    # charge un coup
    print("Ensuring model is loaded...")
    result = analyse_image_from_filename( OLLAMA_DEFAULT_URL, "../test/%s.jpg" % list_img[0], strModel )

    verbose = 1
    verbose = 0


    print( "\n*** %s ***\n" % strModel )

    
    time_begin_total  = time.time()
    
    for img in list_img:
        
        print( "img: '%s'" % img )
        
        time_begin = time.time()
        
        result = analyse_image_from_filename( OLLAMA_DEFAULT_URL, "../test/%s.jpg" % img, strModel,verbose=verbose )
        
        duration = time.time() - time_begin
        print( "duration: %.3fs" % duration )

        print( "desc: " + result["description"])
        print( "kw: " + (", ".join(result["keywords"]) ) )
        print( "txt: " + (", ".join(result["text"]) ) )
        print("")
        
    duration = time.time() - time_begin_total
    print( "=> total duration: %.3fs" % duration )
    
"""

! a chaque fois je le lance avant pour que le modele soit deja chargé en vram. !


*** qwen2.5vl:7b ***

img: '20260901_111820_small'
duration: 2.031s
desc: Une bicyclette colorée avec un siège pour enfant est accrochée à un poteau sur un trottoir. Le siège est attaché avec des cordes. En arrière-plan, on voit des tables de café et des personnes qui discutent. Le cadre de la bicyclette est multicolore, avec des tons de rose, de bleu et de jaune. Il y a aussi des paniers sur le côté de la bicyclette. Le trottoir est en béton et il y a des plantes vertes sur le côté.
kw: bicyclette, siège enfant, trottoir, café, tables, poteau, multicolore, paniers, plantes, trottoir, ville
txt: Initial, 110

img: '20260901_160631_small'
duration: 1.592s
desc: Un pot en verre avec un couvercle hermétique contenant une préparation granuleuse, probablement des céréales ou des graines, avec des morceaux de fruits séchés. Le pot est posé sur une surface sombre, entouré de divers objets de cuisine, dont un bol métallique et des bouteilles. Des graines sont éparpillées sur la surface.
kw: pot, couvercle, granules, fruits séchés, cuisine, surface sombre, boulangerie, préparation, céréales, graines, bocal, bouteilles, bol métallique
txt: FORMAT, Nestle, tr

img: '20260906_210413_small'
duration: 1.525s
desc: Une personne assise à une table avec des livres et des cahiers, portant un chapeau jaune et un t-shirt avec un dessin coloré. Elle tient un stylo et semble faire des devoirs. L'environnement montre une cuisine avec des armoires rouges et un réfrigérateur.
kw: personne, table, livres, cahiers, chapeau, jaune, t-shirt, dessin, cuisine, armoires, réfrigérateur
txt: Je m'entraîne, Je m'entraîne

img: '20260910_130425_small'
duration: 2.233s
desc: Un homme présente devant un écran interactif dans une salle de conférence. L'écran affiche une présentation sur le sommeil, avec des graphiques et des textes. Des personnes sont assises devant l'écran, regardant la présentation. L'environnement est un bureau avec des câbles et des équipements électroniques.
kw: homme, écran, conférence, présentation, sommeil, graphiques, textes, salle, câbles, équipements
txt: Saliency, Complexity, Not possible during sleep, Possible in some sleep stages or individuals, Possible in most sleep stages or individuals, Cognitive determinants of sleep processing: saliency of sensory information and complexity of cognitive processing, Some processing seem to be virtually always present, others in light sleep only and some never (i.e., require conscious awareness?), Sleep's sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation), Oudiette & Andriolli (under review)

img: '20260911_173947_small'
duration: 1.424s
desc: Une personne tient un t-shirt plié avec l'inscription 'ADL international 3eme trophée de KARTING' sur l'avant. Le t-shirt est blanc avec un logo bleu et texte bleu. L'arrière de la personne est visible, montrant une partie de son bras et son torse.
kw: t-shirt, plié, blanc, bleu, logo, inscription, carting, trophée, ADL, international, 3eme
txt: ADL, international, 3eme, trophée, de, KARTING

img: 'girl-4051811_960_720'
duration: 1.489s
desc: Une femme assise en tailleur sur un trottoir pavé, sourit largement. Elle porte un ensemble de sport noir et des chaussures de running. À côté d'elle, il y a un réveil vert, une bouteille d'eau bleue et une paire de chaussures de sport. Le fond montre une rue avec des voitures et des arbres.
kw: femme, sport, tailleur, sourire, trottoir, pavé, réveil, bouteille d'eau, chaussures de sport, rue, voitures, arbres
txt: 

img: '20240102_105013_small'
duration: 1.430s
desc: Une personne portant un imperméable de couleur vert fluo avec une capuche intégrale et un casque de couleur verte se tient sur le bord d'une rue. L'environnement montre des arbres dénudés, des maisons, des voitures et des pots de fleurs sur le trottoir. La météo semble pluvieuse ou venteuse.
kw: imperméable, vert fluo, casque, rue, arbres, maisons, voitures, trottoir, pluie, vent
txt: 

img: '20240109_161443_small'
duration: 1.839s
desc: Quatre personnes se trouvent devant un stand vert avec des affiches et des panneaux. Deux d'entre elles portent des costumes de vache, l'une en orange et l'autre en noir et blanc. Un homme en costume noir et un autre en sweat blanc observent la scène. Le stand est soutenu par KOICA et Bodit Inc., avec des messages sur l'agriculture et la technologie agricole.
kw: costume, vache, agriculture, KOICA, stand, affiches, technologie, personnes, costumes, exposition, agricole
txt: KOICA, Bodit Inc., Farmers hand, Animal Welfare, Precision Farming, Sustainable Livestock Farming, 61313

img: '20240223_094710_small'
duration: 1.308s
desc: L'image montre un homme avec des cheveux noirs et une barbe grise. Il porte un pull noir avec des boutons noirs et un collier violet. Derrière lui, on peut voir une porte en verre et une autre porte bleue avec des fenêtres. Il semble être à l'intérieur d'un bâtiment.
kw: homme, cheveux noirs, barbe grise, pull noir, boutons noirs, collier violet, porte en verre, porte bleue, fenêtres, intérieur, bâtiment
txt: 

=> total duration: 14.870s

Bonus:
img: '20260922_135754_tableau_courbet'
duration: 2.898s
desc: Cette peinture représente deux personnages nus allongés sur un lit. L'homme est allongé sur le dos, la tête sur l'épaule de la femme, qui est allongée sur le côté. Ils sont entourés de bijoux, de fleurs dans un vase et d'objets sur une table. Le tableau est encadré d'un cadre doré orné de motifs floraux.
kw: peinture, nus, amour, bijoux, fleurs, cadre doré, table, lit, homme, femme
txt: Gustave Courbet, 1852, Le Sommeil

=> total duration: 2.898s




*** gemma3:12b ***

img: '20260901_111820_small'
duration: 6.559s
desc: L'image montre plusieurs vélos stationnés autour d'un poteau. Au premier plan, un vélo de couleur irisée (violet, bleu, vert) est solidement attaché au poteau. Il est équipé d'un panier avant en métal et d'un siège enfant à l'arrière. D'autres vélos, dont certains sont gris, sont également stationnés à proximité. En arrière-plan, on aperçoit une terrasse de café avec des tables et des chaises, ainsi que des personnes assises et debout. Une enseigne lumineuse est visible au-dessus du café. Le sol est en béton et en partie recouvert de végétation.
kw: vélo, poteau, siège enfant, panier, terrasse, café, stationnement, irisé, couleur, asphalte, personnes, enseigne, vélos, extérieur, ville, transport, mobilité, pédale, jante, frein
txt: Initial

img: '20260901_160631_small'
duration: 5.505s
desc: Une jarre en verre à clip hermétique, remplie d'un mélange de noix, graines et morceaux de céréales, est placée sur un plan de travail de cuisine. Des miettes sont éparpillées autour de la jarre. En arrière-plan, on aperçoit un sac bleu avec des inscriptions, une boîte de céréales rouge et plusieurs autres bocaux. Un saladier métallique est également présent sur le plan de travail.
kw: jarre, verre, clip, noix, graines, céréales, cuisine, plan de travail, sac, boîte, bocaux, saladier, mélange, nourriture, ingrédients, miettes, rouge, bleu, cuisine
txt: FORMAT, TR

img: '20260906_210413_small'
duration: 9.854s
desc: Une jeune personne est assise à une table ronde recouverte d'un tissu à motifs colorés. La personne porte un bonnet jaune moutarde et un t-shirt noir avec des motifs orange et rose. Elle est penchée sur un cahier ouvert posé sur la table, tenant un stylo à la main. L'arrière-plan montre une cuisine avec des meubles blancs, un évier et des fenêtres. Des coussins bleus turquoise sont visibles sur un canapé à proximité. La lumière est douce et semble provenir de l'extérieur.
kw: jeune personne, bonnet, t-shirt, table, cahier, stylo, cuisine, fenêtre, coussin, canapé, motif, jaune, noir, orange, rose, turquoise, meubles, éclairage, intérieur, apprentissage, étude
txt: De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende, De wereldomspannende

img: '20260910_130425_small'
duration: 7.063s
desc: L'image montre un écran affiché sur un support métallique, probablement dans un environnement de recherche ou d'étude. L'écran présente un diagramme et du texte relatif à la cognition et au sommeil. Un bureau en bois clair est visible en arrière-plan, ainsi qu'une chaise de bureau. L'éclairage semble être artificiel et uniforme.
kw: écran, diagramme, sommeil, cognition, bureau, chaise, support, recherche, étude, métal, bois, texte, graphique, salience, complexité, traitement, sensorielles, adaption
txt: RESPONDING DURING SLEEP, Cognitive determinants of sleep processing, salience of sensory information and complexity of cognitive processing, Some processing seem to be virtually always present, others in light sleep only and some never (i.e. require conscious awareness?), Sleep’s sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation), Cudenne & Andrle (under review)

img: '20260911_173947_small'
duration: 5.602s
desc: Une personne tient un t-shirt blanc. Le t-shirt porte un logo bleu avec les lettres "ADL" en grand, suivies du mot "international" en plus petit. En dessous, on peut lire "3eme trophée de KARTING". La personne porte également un pantalon bleu foncé. Une étiquette blanche avec une inscription est visible sur le côté du t-shirt. L'arrière-plan est flou et semble être un intérieur avec un mur en bois.
kw: t-shirt, homme, logo, ADL, karting, trophée, vêtement, blanc, bleu, étiquette, inscription, pantalon, intérieur, mur, texte
txt: ADL, international, 3eme trophée, de KARTING

img: 'girl-4051811_960_720'
duration: 6.141s
desc: Une femme en tenue de sport noire, assise par terre sur un sol pavé, semble prendre une pause après une activité physique. Elle est souriante et regarde vers la gauche. Elle porte des chaussures de sport noires et grises. À côté d'elle se trouvent une bouteille d'eau turquoise et un haut-parleur vert. L'arrière-plan montre une rue résidentielle avec des bâtiments, des arbres et des voitures. Le ciel est bleu et le soleil brille.
kw: femme, sport, bouteille, haut-parleur, pavé, rue, bâtiment, arbre, voiture, tenue de sport, chaussures, turquoise, vert, soleil, pause, activité physique, sourire, extérieur, résidentiel
txt: 

img: '20240102_105013_small'
duration: 5.738s
desc: Un jeune garçon se tient debout sur un trottoir pluvieux. Il porte un casque vert fluo, une veste jaune fluo avec une cape noire par-dessus, et semble regarder directement l'appareil photo. Derrière lui, on aperçoit une rue résidentielle avec des arbres, des bâtiments et une camionnette blanche. Le ciel est gris et nuageux. Des pots de fleurs sont visibles sur le trottoir à gauche.
kw: garçon, casque, vélo, veste, cape, rue, trottoir, bâtiment, camionnette, arbre, pluie, jaune, vert, noir, résidentiel, tête, enfant, extérieur, ciel, nuageux
txt: 

img: '20240109_161443_small'
duration: 8.136s
desc: L'image montre quatre personnes devant un stand d'exposition. Deux d'entre elles portent des déguisements de mascotte : une en costume de vache marron et beige, l'autre en costume de vache noire et blanche. Un homme en costume sombre, portant un badge, se tient entre les deux. Un jeune homme en sweat à capuche blanc se trouve à côté de la mascotte en vache marron. Le stand est décoré de panneaux avec des informations sur l'agriculture de précision et le bien-être animal. On peut voir des logos et des textes sur le stand, notamment "Farm & Hand" et "KOICA". Le sol est carrelé et l'arrière-plan suggère un grand espace intérieur, probablement une salle d'exposition.
kw: exposition, stand, vache, mascotte, agriculture, bien-être animal, homme, jeune homme, costume, panneau, badge, salle, carrelage, KOICA, Farm & Hand
txt: Supported by KOICA, Farm & Hand, Animal Welfare, Precision Farming, Sustainable Livestock Farming, KO, Korea International Cooperation, 61313, #61313

img: '20240223_094710_small'
duration: 5.671s
desc: Un homme regarde directement la caméra. Il a les cheveux noirs coiffés en arrière, avec des cheveux grisonnants visibles sur les tempes. Il porte un pull noir avec des boutons dorés et un col violet. Il a une petite goatee. L'arrière-plan montre une porte noire avec des moulures blanches, une fenêtre avec des rideaux bleus et une autre personne partiellement visible dans le fond. L'éclairage est uniforme, mettant en évidence les traits du visage de l'homme.
kw: homme, portrait, pull, goatee, cheveux noirs, cheveux gris, porte, fenêtre, col violet, boutons, regard, intérieur, éclairage, visage, personne, moulures, rideaux
txt: 

=> total duration: 60.268s

Bonus:
img: '20260922_135754_tableau_courbet'
DBG: done_reason: stop
duration: 8.357s
desc: Une peinture à l'huile encadrée est accrochée à un mur. La peinture représente une femme nue, allongée sur un lit recouvert de draps blancs. Elle a des cheveux bouclés châtain clair et une peau claire. Elle est partiellement recouverte d'un drap gris foncé. À côté du lit, sur une table, se trouvent une bouteille en verre, un collier de perles et un vase rempli de fleurs multicolores. Un petit objet, peut-être un rouge à lèvres, repose sur le sol près du lit. Le cadre est doré et orné de motifs complexes. Une plaque d'identification est visible sur le côté droit du cadre. Le mur est de couleur crème.
kw: peinture, femme, nue, lit, drap, cheveux, collier, perles, fleurs, vase, table, cadre, doré, rouge à lèvres, plaque d'identification, art, intérieur, boudoir, portrait
txt: Eugène Carrière, Musée d'Orsay, Don de la famille de Jean et Simone Levrat

=> total duration: 8.357s




*** qwen3-VL:8b ***

img: '20260901_111820_small'
DBG: done_reason: stop
duration: 30.223s
desc: Un vélo coloré avec un siège bébé noir et gris, un panier métallique noir et des poignées en bois est stationné près d'un poteau métallique sur une rue piétonne. Plusieurs vélos sont garés en arrière-plan, dont un avec un siège noir. Une personne en chemise beige et pantalon gris marche près d'un café avec des tables et chaises en extérieur. Un camion blanc portant l'inscription 'Initial' est visible sur la route. Des bâtiments colorés, dont un rouge, bordent la rue. Une enseigne bleue affiche le chiffre '3.2'. Plusieurs personnes sont présentes : une en chemise bleue assise à une table, une autre en chemise beige marchant, et une personne en veste verte près d'un bâtiment. Le sol est en béton avec des marques de stationnement.
kw: vélo, siège bébé, panier, rue, café, camion, poteau, personnes, bâtiments, enseigne, stationnement, enfant, route
txt: Initial, 3.2

img: '20260901_160631_small'
DBG: done_reason: length
WRN: ans is empty!
duration: 64.575s
desc: 
kw: 
txt: 

img: '20260906_210413_small'
DBG: done_reason: stop
duration: 36.243s
desc: Une personne assise à une table recouverte d'une nappe colorée aux motifs feuillages, portant un bonnet jaune et un t-shirt gris orné d'un ballon de tennis jaune et rose. Elle tient un stylo rouge et regarde un livre ouvert contenant des illustrations et du texte. Sur la table, un cahier à carreaux présente des notes manuscrites. En arrière-plan, une cuisine avec des armoires rouges, un frigo blanc décoré de photos et de magnets, un mur bleu, un coussin bleu sur une chaise, un tabouret blanc, un carrelage à motifs carrés, et un tapis rouge sur le sol.
kw: bonnet jaune, t-shirt gris, ballon de tennis, stylo rouge, cahier, livre ouvert, nappe colorée, cuisine, armoire rouge, frigo, mur bleu, coussin bleu, tabouret blanc, carrelage, notes manuscrites, livre de texte
txt: la montagne

img: '20260910_130425_small'
DBG: done_reason: length
WRN: ans is empty!
duration: 64.579s
desc: 
kw: 
txt: 

img: '20260911_173947_small'
DBG: done_reason: stop
duration: 23.874s
desc: Une personne tient un T-shirt blanc avec un logo bleu. Le T-shirt affiche 'ADL' en grandes lettres bleues sur un rectangle bleu, suivi de 'international', puis '3eme trophée de KARTING'. Une étiquette sur le col indique 'W/0240'. L'arrière-plan montre une surface sombre et des carreaux de pierre.
kw: T-shirt, blanc, bleu, ADL, international, trophée, karting, étiquette, col, carreaux de pierre, main, surface sombre
txt: ADL, international, 3eme trophée de KARTING, W/0240

img: 'girl-4051811_960_720'
DBG: done_reason: stop
duration: 17.662s
desc: Une femme en tenue de sport noir (tank top et leggings) est assise sur une rue pavée ensoleillée, effectuant un étirement. À sa gauche, un haut-parleur vert est posé sur le sol, et à sa droite, une bouteille d'eau bleue. L'arrière-plan montre des arbres, des voitures stationnées (une voiture blanche, une noire et un SUV), des maisons résidentielles avec des toits en tuiles, et un ciel clair. Elle porte des chaussures de sport noires avec semelles blanches.
kw: femme, tenue de sport, leggings, bouteille d'eau, haut-parleur, rue pavée, arbre, voiture, maison, étirement, soleil
txt: 

img: '20240102_105013_small'
DBG: done_reason: stop
duration: 23.109s
desc: Une personne portant une combinaison de pluie verte néon et noire avec un casque assorti se tient sur une rue résidentielle. La chaussée est mouillée, indiquant une pluie récente. En arrière-plan, des arbres sans feuilles, des immeubles résidentiels, des véhicules stationnés (dont un fourgon blanc), des pots de fleurs sur le trottoir, et un poteau électrique sont visibles. De la végétation et des herbes poussent le long du bord de la route.
kw: combinaison de pluie, casque, rue résidentielle, arbres sans feuilles, immeubles résidentiels, pots de fleurs, poteau électrique, chaussée mouillée, véhicules stationnés, végétation
txt: 

img: '20240109_161443_small'
DBG: done_reason: stop
duration: 44.885s
desc: Quatre personnes se tiennent devant un stand vert et bleu. À gauche, une personne en sweat blanc et pantalon gris. Au centre gauche, une personne en costume ours marron et beige, tenant une tablette affichant 'Farmhand'. À côté, un homme en costume noir avec un badge 'KOICA' et un badge 'Bodit Inc.' sur le stand. À droite, une personne en costume vache blanc avec taches noires, tenant un appareil photo. Le stand affiche 'Supported by KOICA', 'Bodit Inc.', 'Farmhand', 'KO', 'Korea International Cooperation', ainsi que les hashtags '#Animal Welfare', '#Precision Farming', '#Sustainable Livestock Farming'. Un écran derrière montre un logo d'oiseau bleu. Le sol est recouvert d'un tapis avec le numéro '#61313'. Un panneau indique 'B-G G 16'.
kw: costume animal, costume ours, costume vache, stand d'exposition, KOICA, Farmhand, élevage bovin, bien-être animal, élevage précis, agriculture durable, tablette, badge, logo oiseau bleu, tapis de sol, numéros, vaches, salon professionnel, conférence, exposition
txt: Supported by KOICA, Bodit Inc., Farmhand, KO, Korea International Cooperation, #Animal Welfare, #Precision Farming, #Sustainable Livestock Farming, #61313, B-G G 16

img: '20240223_094710_small'
DBG: done_reason: stop
duration: 24.740s
desc: Un homme avec une barbe courte (goatee), cheveux noirs coiffés en arrière, vêtu d'un sweater noir à col violet et boutons sur les épaules, se tient dans une pièce intérieure. L'arrière-plan montre un mur bleu, une fenêtre à deux vitres laissant entrer la lumière, un plafond avec une fissure visible, une porte vitrée à gauche, et un objet jaune près de la fenêtre. Une décoration murale, comme un manteau suspendu, est également visible.
kw: homme, barbe, sweater noir, mur bleu, fenêtre, plafond, fissure, porte vitrée, objet jaune, décoration murale
txt: 

=> total duration: 329.892s

Bonus:
img: '20260922_135754_tableau_courbet' => ans vide done reason length




*** gemma4:12b ***

img: '20260901_111820_small'
DBG: done_reason: stop
duration: 18.416s
desc: Un vélo au cadre aux couleurs de l'arc-en-ciel (rose, bleu, jaune, rouge) est stationné sur un trottoir, appuyé contre un poteau de lampadaire. Le vélo est équipé d'un grand panier noir à l'avant et d'un siège large avec un dossier haut de couleur noire. Les pneus sont marqués "SCHWALBE". En arrière-plan, une terrasse de café est visible avec des clients et des tables. Une rue s'étend derrière le vélo, où un camion blanc portant l'inscription "Inifitial" est garé. Un autre vélo est visible en arrière-plan. Le sol est un mélange de pavés et de bitume.
kw: vélo, arc-en-ciel, panier, siège, trottoir, café, rue, camion, Schwalbe, urbain, cadre multicolore, vélo de ville, poteau
txt: Inifitial, SCHWALBE

img: '20260901_160631_small'
DBG: done_reason: stop
duration: 15.454s
desc: Un grand bocal en verre avec un couvercle à fermeture métallique est rempli d'un mélange de céréales, de graines et de fruits secs. Le bocal est posé sur une surface sombre où sont éparpillés quelques grains. À droite du bocal se trouve un bol en métal contenant de la farine et des morceaux sombres. En arrière-plan, on aperçoit un sac bleu, une boîte rouge avec les inscriptions "FORMAT" et "NESTLE", ainsi que d'autres bocaux en verre et des bouteilles.
kw: bocal, verre, muesli, céréales, graines, fruits secs, bol, métal, farine, cuisine, boîte, sac, préparation
txt: FORMAT, NESTLE, tr

img: '20260906_210413_small'
DBG: done_reason: stop
duration: 32.654s
desc: Une femme aux cheveux clairs portant un bonnet en tricot jaune et un t-shirt gris foncé avec un motif circulaire pastel est assise à une table. Elle regarde vers l'objectif et tient un stylo dans sa main droite au-dessus d'un grand cahier ouvert. Le cahier contient du texte en japonais et des illustrations. La table est recouverte d'une nappe à motifs géométriques multicolores. L'arrière-plan montre un intérieur avec un mur bleu à gauche et une ouverture menant à une cuisine avec des meubles rouges et un four noir.
kw: femme, bonnet jaune, t-shirt, cahier, japonais, étude, table, nappe, cuisine, intérieur, stylo, écriture, motif géométrique
txt: 日本語, 日本語

img: '20260910_130425_small'
DBG: done_reason: length
WRN: ans is empty!
duration: 108.406s
desc: 
kw: 
txt: 

img: '20260911_173947_small'
DBG: done_reason: stop
duration: 11.500s
desc: Une main tient un t-shirt blanc sur lequel est imprimé un logo et du texte en bleu. Le mot "ADL" est écrit en grandes lettres majuscules à l'intérieur d'un rectangle bleu. Juste en dessous, le mot "international" est écrit en minuscules. En dessous de ce mot, on peut lire "3ème trophée" suivi de "de KARTING" en lettres capitales. Le t-shirt présente quelques légères taches et semble être en coton. L'arrière-plan est flou et montre un sol en terre ou en gravier.
kw: t-shirt, blanc, texte bleu, ADL, international, trophée, karting, sport, vêtement, main
txt: ADL, international, 3ème trophée, de KARTING

img: 'girl-4051811_960_720'
DBG: done_reason: length
WRN: ans is empty!
duration: 109.135s
desc: 
kw: 
txt: 

img: '20240102_105013_small'
DBG: done_reason: stop
duration: 17.102s
desc: Une personne se tient debout au premier plan, face à l'objectif, portant un casque de protection et une veste de protection de couleur jaune fluo. La veste est bicolore, avec une partie supérieure jaune fluo et une partie inférieure noire. Le casque est assorti à la couleur de la veste. En arrière-plan, on aperçoit une rue bordée de maisons et d'arbres sans feuilles sous un ciel couvert. Un camion blanc est garé sur le côté de la route. Sur la gauche, deux pots de fleurs sont posés sur le bord du trottoir. Un poteau électrique est visible sur la droite.
kw: personne, casque, veste, jaune fluo, rue, maison, arbre, camion, pot de fleurs, trottoir, hiver, extérieur
txt: 

img: '20240109_161443_small'
DBG: done_reason: stop
duration: 42.075s
desc: Une scène d'intérieur montrant un stand d'exposition avec quatre personnes. À gauche, un homme en sweat à capuche blanc et pantalon gris regarde vers la droite. À sa droite, une femme sourit en portant un costume de type "onesie" marron et orange avec une capuche d'animal. Au centre, un homme en veste noire et chemise noire porte un badge autour du cou. À droite, une personne porte un costume à motif de vaches noir et blanc avec une capuche et tient un petit panneau. Le fond est un grand panneau vert et bleu avec des inscriptions "Farm-Chain", "Smart Farming" et "Smart Farm". Le logo "KOICA" et le nom "Korea International Cooperation Agency" sont visibles. Le sol est un tapis gris avec des marquages "#6133". En haut à droite, un panneau indique "B-G" et "G 10". Le plafond est de style industriel avec des luminaires.
kw: exposition, stand, KOICA, Farm-Chain, costume, vaches, agriculture, technologie, promotion, salon, homme, femme, public, marketing, Korea
txt: Supervised by KOICA, Farm-Chain, Smart Farming, Smart Farm, Korea International Cooperation Agency, B-G, G 10, #6133, KOICA

img: '20240223_094710_small'
DBG: done_reason: stop
duration: 15.453s
desc: Portrait en gros plan d'un homme aux cheveux courts et foncés avec une petite moustache sous la lèvre inférieure. Il porte un pull noir avec un liseré violet au niveau du col. En arrière-plan, on aperçoit une porte vitrée sur la gauche et un couloir avec un mur bleu et une fenêtre sur la droite. Une silhouette humaine est visible au loin dans le couloir.
kw: homme, portrait, visage, cheveux courts, pull noir, soulpatch, intérieur, mur bleu, fenêtre, couloir
txt: 

=> total duration: 370.200s

Bonus:
img: '20260922_135754_tableau_courbet'
DBG: done_reason: stop
duration: 20.454s
desc: Une peinture à l'huile représentant un couple nu est présentée dans un large cadre doré richement sculpté et orné. La femme, aux longs cheveux sombres, est allongée sur le côté, tandis que l'homme, aux cheveux blonds bouclés, est blotti contre elle. Ils reposent sur un drap blanc froissé. Dans le coin inférieur gauche, un petit meuble sombre supporte un verre et un petit vase. En haut à droite, un vase décoré contient un bouquet de fleurs colorées. Le fond de la peinture est sombre et texturé. La signature "G. Courbet" est visible en bas à droite de la toile. Une petite étiquette blanche est fixée au mur à droite du cadre.
kw: peinture, cadre doré, nu, couple, lit, fleurs, vase, signature, Courbet, musée, galerie, art, huile, toile, draperie
txt: G. Courbet

=> total duration: 20.454s


*** qwen3-vl:30b-a3b ***

img: '20260901_111820_small'
DBG: done_reason: stop
duration: 89.222s
desc: Une bicyclette à cadre arc-en-ciel est attachée à un poteau sur un trottoir. Elle possède un panier noir à l'avant et un siège enfant noir à l'arrière. Derrière elle, une autre bicyclette noire est également attachée. En arrière-plan, des magasins avec des façades rouges et blanches abritent un café où des personnes sont assises à des tables. Un homme en chemise marron et un pantalon gris marche sur le trottoir, tandis qu'une femme aux cheveux gris est assise à une table. Un camion blanc avec l'inscription "Initial" est visible sur la rue. Le pneu de la bicyclette porte l'inscription "SCHWALBE". Le soleil éclaire la scène, projetant des ombres sur le sol.
kw: bicyclette, siège enfant, panier, trottoir, rue, café, personnes, camion, poteau, cadre arc-en-ciel, pneu, SCHWALBE, Initial
txt: Initial, SCHWALBE

img: '20260901_160631_small'
DBG: done_reason: stop
duration: 156.761s
desc: Un bocal en verre avec couvercle à fermeture éclair métallique contenant un mélange de granola (flocons d'avoine, amandes, graines de tournesol). À droite, un bol en métal avec des résidus et une cuillère. En arrière-plan, des bocaux en verre avec couvercles à fermeture éclair, des bouteilles sombres, un sac bleu avec le texte 'tr' visible, et une boîte rouge 'Nestle' avec 'FORMAT' en lettres blanches. Le comptoir sombre est parsemé de miettes.
kw: bocal en verre, couvercle à fermeture éclair, granola, bol métal, sac bleu, boîte Nestle, comptoir sombre, miettes, amandes, graines
txt: Nestle, FORMAT, tr

img: '20260906_210413_small'
DBG: done_reason: length
WRN: ans is empty!
duration: 235.361s
desc: 
kw: 
txt: 

img: '20260910_130425_small'
DBG: done_reason: stop
duration: 195.062s
desc: Un homme en chemise rouge pointe vers un écran de projection affichant un diaporama intitulé "Responding During Sleep". Le diaporama présente une section "Saliency" avec des illustrations et le texte "Sleep's sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation)". À droite, on voit "Cognitive determinants of sleep processing: saliency of sensory information and complexity of cognitive processing" et "Some processing seem to be virtually always present, others in light sleep only and some never (i.e., require conscious awareness?)". Un graphique intitulé "Functional tradeoff" est visible, avec les axes "Disconnection" et "Connection", et des termes comme "Dreaming", "Perception", "Sleep", "Restoration", "Consolidation". Sur une table à gauche, il y a un ordinateur portable, un appareil noir et des câbles. Plusieurs personnes sont présentes en arrière-plan, dont certaines ont les cheveux bruns. Le mur est blanc, avec des prises électriques et des câbles noirs en dessous. En bas à gauche du diaporama, on lit "Oudiette & Aniol (under review)".
kw: présentation, écran, diaporama, sommeil, saliency, traitement sensoriel, graphique, câbles, table, ordinateur, personnes, murs blancs, texte, déterminants cognitifs, compromis fonctionnel, Dreaming, Perception, Restoration, Consolidation, Oudiette & Aniol
txt: Responding During Sleep, Saliency, Sleep's sensory (dis)connection might reflect a tradeoff between different functions or consequences of sleep (adaptation), Cognitive determinants of sleep processing: saliency of sensory information and complexity of cognitive processing, Some processing seem to be virtually always present, others in light sleep only and some never (i.e., require conscious awareness?), Functional tradeoff, Disconnection, Connection, Dreaming, Perception, Sleep, Restoration, Consolidation, Oudiette & Aniol (under review)

img: '20260911_173947_small'
DBG: done_reason: stop
duration: 112.187s
desc: Un T-shirt blanc est tenu par une personne. Le T-shirt présente un logo rectangulaire bleu avec les lettres "ADL" en grandes lettres bleues. En dessous du logo, le mot "international" est imprimé en bleu. Plus bas, le texte "3eme trophée de KARTING" apparaît en bleu. La personne tenant le T-shirt a un bras visible, portant un short gris et un vêtement orange. L'arrière-plan comprend un mur sombre et une structure en pierre.
kw: T-shirt, ADL, international, trophée, karting, bleu, blanc, main, bras, short, orange, gris, mur, pierre
txt: ADL, international, 3eme trophée de KARTING

img: 'girl-4051811_960_720'
DBG: done_reason: stop
duration: 112.131s
desc: Une femme assise sur une rue pavée, vêtue d'une tenue de sport noire (top sans manches et leggings), sourit en regardant vers le bas. Elle porte des chaussures de sport noires et a les jambes écartées, les mains posées sur les genoux. À sa gauche (côté droit de l'image), une bouteille d'eau bleue est visible. À sa droite (côté gauche de l'image), un speaker portable vert repose sur le sol. En arrière-plan, une rue avec des voitures garées, des arbres, des immeubles et un ciel bleu clair. Le soleil brille, créant des ombres nettes sur les pavés.
kw: femme, sport, tenue noire, chaussures sport, bouteille eau, speaker, vert, bleu, gris, rue pavée, soleil, arbre, voiture, immeuble, sourire, genoux, jambes
txt: 

img: '20240102_105013_small'
DBG: done_reason: stop
duration: 121.816s
desc: Une personne porte un casque vert vif et un manteau de pluie vert et noir avec capuche. Le manteau présente un logo noir sur la poitrine. La personne se tient sur un trottoir à côté d'une rue. En arrière-plan, on observe des arbres sans feuilles, des immeubles résidentiels, un camion blanc garé sur la rue, des pots de fleurs sur le trottoir, un poteau électrique avec des fils, et un vélo partiellement visible à droite. Le ciel est couvert.
kw: manteau de pluie, casque vert, rue, arbres, immeubles, pots de fleurs, trottoir, camion blanc, vélo, ciel couvert, capuche, poteau électrique, appartements
txt: 

img: '20240109_161443_small'
DBG: done_reason: length
WRN: ans is empty!
duration: 234.127s
desc: 
kw: 
txt: 

img: '20240223_094710_small'
DBG: done_reason: stop
duration: 105.305s
desc: Un homme avec des cheveux noirs coiffés en arrière porte un pull noir à col violet. Il a une moustache et une barbe sous le menton. En arrière-plan, on observe un intérieur avec des murs bleus, une fenêtre laissant passer la lumière, un plafond avec une corniche sombre et des meubles.
kw: homme, pull, noir, col, violet, moustache, barbe, cheveux, bleu, fenêtre, plafond, corniche, meubles
txt: 

=> total duration: 1361.971s
"""


if __name__ == "__main__":
    main()