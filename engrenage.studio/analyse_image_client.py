import cv2
import requests


def send_image_to_analyse( filename_img, lang = "en" ):
    print( "\nINF: analyse_image_client: send_image_to_analyse..." )

    # Non c'est le binaire tel quel qu'il faut envoyer
    if 0:
        image_bytes = cv2.imread( filename_img )
        if image_bytes is None:
            print( "ERR: send_image_to_analyse: can't open '%s'" % filename_img )
            return 
        success, encoded = cv2.imencode(".jpg", image_bytes)  # ou alors le reencoder en jpg, mais c'est dommage
    
    with open( filename_img, "rb" ) as f:
        image_bytes = f.read()
        

    
    headers = {
        "X-Image-Filename": filename_img,
        "X-User-Id": "tester",
        "Lang": lang,
        "Content-Type": "application/octet-stream",
    }

    url = "https://engrenage.studio:45003/anaimg"
    response = requests.post( url, data=image_bytes, headers=headers )


    if response.status_code != 200:
        print("ERREUR SERVEUR:", response.status_code)
        print(response.text)
        return

    result = response.json()
    
    print(result)

    description = result["description"]
    keywords = result["keywords"]
    text = result["text"]
    peoples = result["peoples"]
    
    print( "INF: analyse_image_client: results:" )
    print( "description: %s" % description )
    print( "keywords: %s" % keywords )
    print( "text: %s" % text )
    print( "peoples: %s" % peoples )
    
    
def test():
    names = ["20260906_210413_small","WA_corto_niko_et_myr","WA_famille_regarde_film"]; template = "../test/%s.jpg"
    names = ["2025_03_19-02h20m14s148114ms","side_boobs_07","2024_06_10-09h20m08s449379ms","2020_10_05-10h35m32s214730ms","2021_11_30-14h44m50s655809ms"]; template = "/tmp/%s.jpg"
    #~ names = names[1:2]
    for name in names:
        fn = template % name
        ret = send_image_to_analyse( fn, "fr" ) # bizarrement le 2ieme foire des fois quand le client est sur PC avec une liste de mot cle infini avec "seance de photos", "seance de photos", "seance de photos", ... => relancer avec une autre seed si trop pourri.
        #~ print( "ret: %s" % ret )
        if 1:
            im = cv2.imread( fn )
            cv2.imshow("view", im )
            cv2.waitKey(100)
        #~ break
        
        
"""
la suite: on lance l'extraction, puis on embedde la desc totale dans un texte, ainsi que chaque phrase. ensuite on aura une recherche en mot cle pur et en texte pur.
on pourrait aussi faire une recherche en enbed de mot cle et en embed de texte pur.
qu'est ce qui marcherait le mieux ?
"""
        
"""

*** qwen2.5vl:7b ***


description: Une personne assise à une table dans une cuisine, portant un chapeau jaune et un t-shirt avec un dessin coloré. Elle tient un stylo et semble faire des devoirs. Devant elle, il y a un cahier de notes et un livre ouvert avec des illustrations et des textes. La cuisine a des armoires rouges, un réfrigérateur et une table à carreaux colorés.
keywords: ['personne', 'chapeau', 't-shirt', 'table', 'cuisine', 'livre', 'cahier', 'notes', 'stylo', 'dessin', 'réfrigérateur', 'armoires', 'carreaux']
text: ["Je m'entraîne", "Je m'entraîne"]
peoples: ['Gaia']

description: Trois personnes se tiennent dans une pièce avec un sol en bois. À gauche, Corto porte un blazer noir et des lunettes. Au milieu, Niko porte un sweat à capuche beige et des lunettes. À droite, Myriam porte un sweat à capuche beige et des lunettes. Derrière eux, une porte est ouverte, révélant une pièce avec des chaises et des fenêtres. Sur le mur, il y a une décoration en forme de chiffre huit arc-en-ciel et une série de chats blancs avec des motifs rouges. Un sac et une boîte sont posés contre le mur à côté de Myriam.
keywords: ['salle', 'personnes', 'bois', 'fenêtre', 'chaise', 'décoration', 'sac', 'chat', 'sweat', 'lunettes', 'porte', 'mur', 'blazer', 'salle de séjour']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: Une réunion informelle dans une pièce à murs bleus avec des personnes assises sur des canapés et des chaises. Les participants semblent engagés dans une discussion. Des tableaux et des objets décoratifs sont visibles sur les murs. Une personne tient un verre de vin. L'atmosphère est conviviale et détendue.
keywords: ['réunion', 'informelle', 'canapé', 'murs bleus', 'tableaux', 'décoratifs', 'verre de vin', 'discussion', 'conviviale', 'détendue']
text: ['1', '1']
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']

* SEED 43 *

description: Une personne assise à une table dans une cuisine, portant un chapeau jaune et un t-shirt avec un dessin coloré. Elle tient un stylo et semble faire des devoirs. Devant elle, il y a un cahier de notes et un livre ouvert avec des illustrations et des textes. La table a une nappe à motifs géométriques. Derrière elle, on peut voir une cuisine avec des armoires rouges, un réfrigérateur et des ustensiles de cuisine.
keywords: ['personne', 'table', 'chapeau', 't-shirt', 'cuisine', 'livre', 'cahier', 'notes', 'stylo', 'dessin', 'nappe', 'réfrigérateur', 'armoires', 'ustensiles']
text: ["Je m'entraîne", "Je m'entraîne"]
peoples: ['Gaia']

description: Trois personnes se tiennent dans une pièce avec un sol en bois. À gauche, Corto porte un blazer noir et des lunettes. Au centre, Niko porte un sweat à capuche beige et des lunettes. À droite, Myriam porte un sweat à capuche beige et des lunettes. Derrière eux, une pièce avec des chaises et une sculpture arc-en-ciel est visible. Sur le mur, des images de chats sont accrochées. Un tapis est posé sur le sol.
keywords: ['salle', 'personnes', 'séance', 'photographie', 'chaises', 'sculpture', 'séance', 'photographie', 'chats', 'tapis', 'mur', 'séance', 'photographie', 'séance', 'photographie', 'séance', 'photographie', 'séance', 'photographie']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: Une réunion informelle dans une pièce à murs bleus avec des personnes assises sur des canapés et des chaises. Des tableaux et des objets décoratifs sont visibles sur les murs. Les personnes semblent engagées dans une conversation. Une personne porte un foulard rouge et une autre un costume bleu. Une lampe dorée est placée sur une table basse. Des fleurs artificielles sont suspendues à gauche. Un ballon numéro 1 est accroché à droite. Une personne tient un verre à la main.
keywords: ['réunion', 'canapé', 'murs bleus', 'tableaux', 'foulard rouge', 'costume bleu', 'lampe dorée', 'fleurs artificielles', 'ballon numéro 1']
text: ['1']
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']

* SEED 430 *

Idescription: Une personne assise à une table dans une cuisine, portant un chapeau jaune et un t-shirt avec un dessin coloré. Elle tient un stylo et semble étudier, avec un cahier et un livre ouvert devant elle. Le livre contient des illustrations et des textes, et le cahier a des notes écrites dessus. Le fond montre une cuisine avec des armoires rouges, un réfrigérateur et des ustensiles de cuisine.
keywords: ['personne', 'chapeau', 't-shirt', 'table', 'cuisine', 'livre', 'cahier', 'stylo', 'notes', 'étudier', 'dessin', 'réfrigérateur', 'armoires', 'ustensiles']
text: ["Je m'entraîne", "Je m'entraîne"]
peoples: ['Gaia']

Idescription: Trois personnes se tiennent dans une pièce avec un sol en bois. À gauche, Corto porte un blazer noir et des lunettes. Au centre, Niko porte un sweat à capuche beige et des lunettes. À droite, Myriam porte un sweat à capuche beige et des lunettes. Derrière eux, une pièce avec des chaises et une sculpture arc-en-ciel est visible. Sur le mur, des images de chats sont accrochées. Un tapis est posé sur le sol.
keywords: ['salle', 'personnes', 'séance', 'photographie', 'chaises', 'sculpture', 'séance', 'photographie', 'chats', 'tapis', 'mur', 'séance', 'photographie', 'séance', 'photographie', 'séance', 'photographie', 'séance', 'photographie']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: Une réunion informelle dans une pièce à murs bleus avec des personnes assises sur des canapés et des chaises. Des tableaux et des objets décoratifs sont visibles sur les murs. Les personnes semblent engagées dans une discussion. Une personne porte un foulard rouge et une autre un costume bleu. Une lampe dorée est placée sur une table basse. Des fleurs artificielles sont suspendues à gauche. Un ballon numéro 1 est visible à droite. Les personnes sont assises sur des canapés et des chaises disposés en demi-cercle.
keywords: ['réunion', 'informelle', 'murs bleus', 'tableaux', 'objets décoratifs', 'personnes assises', 'discussion', 'foulard rouge', 'costume bleu', 'lampe dorée', 'fleurs artificielles', 'ballon numéro 1']
text: []
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']


* SEED 42, temperature 0.2 *

description: Une personne assise à une table, portant un chapeau jaune et un t-shirt noir avec un dessin coloré, écrit dans un cahier. Devant elle se trouve un livre ouvert avec des pages blanches et des illustrations, et un cahier de papier à carreaux. L'environnement montre une cuisine avec des armoires rouges, un réfrigérateur et des ustensiles de cuisine. La table a une nappe avec un motif géométrique multicolore.
keywords: ['personne', 'table', 'chapeau', 'livre', 'cahier', 'cuisine', 'réfrigérateur', 'armoires', 'dessin', 'écriture', 'maison', 'intérieur', 'domestique']
text: ["je m'entraîne", 'je referme']
peoples: ['Gaia']

description: Trois personnes se tiennent dans un intérieur moderne. Corto et Niko sont de la première rangée, tandis que Myriam est de la deuxième. Corto porte un blazer noir et un pantalon noir, Niko est en veste rouge et noir, et Myriam porte un sweat à capuche beige avec des écouteurs autour du cou. Le fond montre des fenêtres, des chaises design, et des décorations murales, notamment un motif de chat et un arc-en-ciel. L'ambiance semble informelle et conviviale.
keywords: ['intérieur', 'personnes', 'blazer', 'sweat', 'écouteurs', 'fenêtres', 'chaises', 'décorations', 'chat', 'arc-en-ciel', 'vintage', 'style moderne']
text: ['chat', 'arc-en-ciel']
peoples: ['Corto', 'Niko', 'Myriam']

description: Une réunion informelle dans une pièce aux murs bleus, avec des personnes assises sur des canapés et des chaises. Des tableaux et des objets décoratifs sont visibles sur les murs. Les personnes semblent discuter ou écouter, certaines tenant des verres. La pièce est bien éclairée avec des lumières douces.
keywords: ['réunion', 'canapé', 'tableaux', 'décoration', 'verre']
text: ['1']
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']


* EN *

description: A person wearing a yellow knit beanie and a dark t-shirt with a colorful design is sitting at a table. They are holding a red pen and appear to be studying or working on homework. The table has a patterned tablecloth and an open book with text and images. There is a notebook with handwritten notes next to the book. The background shows a kitchen with red cabinets, a refrigerator, and various kitchen items.
keywords: ['person', 'yellow beanie', 'dark t-shirt', 'study', 'homework', 'red pen', 'book', 'notebook', 'handwritten notes', 'kitchen', 'red cabinets', 'refrigerator']
text: ["Je m'entraîne", "Je m'entraîne"]
peoples: ['Gaia']

description: Three individuals are standing indoors in a room with wooden flooring and dark blue walls. The person on the left, Corto, is wearing a dark jacket and has long hair. The person in the middle, Niko, is wearing a red jacket over a black shirt and glasses. The person on the right, Myriam, is wearing a beige hoodie and glasses. There is a colorful abstract sculpture on the wall to the left, and a white curtain is visible in the background. The room has a casual and lived-in feel with various items and decorations around, including a poster with cat illustrations on the wall to the right.
keywords: ['room', 'indoors', 'wooden floor', 'dark blue walls', 'abstract sculpture', 'white curtain', 'casual', 'lived-in', 'colorful', 'cat poster', 'glasses', 'jacket', 'hoodie', 'long hair', 'red jacket', 'black shirt', 'beige hoodie']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: A group of people is gathered in a cozy room with blue walls and wooden flooring. They are seated on a black leather couch and a chair, engaged in conversation. The room is decorated with various items, including a lamp, a projector, and some artwork on the walls. The people are dressed in casual and semi-formal attire, and some are holding drinks. The atmosphere appears relaxed and informal.
keywords: ['group', 'conversation', 'room', 'blue walls', 'wooden floor', 'couch', 'lamp', 'projector', 'artwork', 'casual attire', 'informal', 'drinks']
text: ['1']
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']


*** gemma3:12b ***

description: Gaia est assise à une table ronde recouverte d'un tissu à motifs colorés. Elle porte un bonnet jaune texturé et un pull noir avec des motifs orange et rose. Gaia est penchée sur un cahier ouvert posé sur la table, tenant un stylo à la main. Le cahier contient des pages avec des illustrations et du texte. Une chaise turquoise est visible à côté de la table. En arrière-plan, on aperçoit une cuisine avec des armoires blanches, un plan de travail et des appareils électroménagers. La lumière est douce et diffuse, suggérant une ambiance chaleureuse.
keywords: ['Gaia', 'bonnet', 'pull', 'table', 'cahier', 'stylo', 'cuisine', 'chaise', 'turquoise', 'orange', 'rose', 'motif', 'illustration', 'texte', 'éclairage', 'intérieur', 'table ronde', 'apprentissage', 'étudiant', 'jeune femme']
text: ['De wereldomspannende', '1.1 De wereldomspannende', '1.2 De wereldomspannende', '1.3 De wereldomspannende', '1.4 De wereldomspannende', '1.5 De wereldomspannende', '1.6 De wereldomspannende', '1.7 De wereldomspannende', '1.8 De wereldomspannende', '1.9 De wereldomspannende', '1.10 De wereldomspannende', '1.11 De wereldomspannende', '1.12 De wereldomspannende', '1.13 De wereldomspannende', '1.14 De wereldomspannende', '1.15 De wereldomspannende', '1.16 De wereldomspannende', '1.17 De wereldomspannende', '1.18 De wereldomspannende', '1.19 De wereldomspannende', '1.20 De wereldomspannende']
peoples: ['Gaia']


description: Corto se tient à gauche, portant un costume noir sur chemise claire et pantalon noir. Il porte des lunettes. Niko est à côté de Corto, vêtu d'un sweat à capuche rouge sur t-shirt, et d'un pantalon noir. Myriam est à droite, portant un sweat à capuche gris, avec des écouteurs autour du cou. Ils se trouvent dans une pièce avec un sol en bois clair. Un mur est peint en bleu foncé avec des cadres contenant des images. Une porte-fenêtre laisse entrevoir un extérieur lumineux. Un tableau abstrait coloré est visible sur le mur à gauche. Une chaise en rotin est également présente.
keywords: ['Corto', 'Niko', 'Myriam', 'costume', 'sweat', 'porte-fenêtre', 'tableau', 'rotin', 'lunettes', 'mur', 'sol', 'bois', 'cadre', 'image', 'intérieur', 'pièce', 'bleu foncé', 'rouge', 'gris', 'pantalon']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: La scène se déroule dans une pièce à l'ambiance feutrée, aux murs bleu foncé à panneaux. Un homme, assis sur un tabouret noir, effectue une performance artistique au sol, apparemment une sorte de danse ou de mime. Il porte un pantalon à motifs et des chaussures vertes. Alex est assis sur un canapé en cuir marron, portant un costume bleu marine et un foulard rouge. Gaia est assise à côté d'Alex, vêtue d'un pull rose. Myriam est assise à côté de Gaia, portant un pull rouge. Niko est assis à côté de Myriam, portant un pull rouge. Un homme est assis à côté de Niko, portant un pull gris. Un homme est assis sur un fauteuil à gauche, portant un chapeau et des lunettes. Une femme est assise à côté de lui, portant des lunettes. Un tableau représentant une femme et un serpent est accroché au mur. Des décorations d'Halloween, dont des citrouilles illuminées, sont visibles sur une étagère. Une lampe de chevet diffuse une lumière jaune. Le sol est en bois.
keywords: ['performance', 'danse', 'mime', 'canapé', 'homme', 'femme', 'Alex', 'Gaia', 'Myriam', 'Niko', 'tableau', 'serpent', 'Halloween', 'citrouille', 'lampe', 'bois', 'costume', 'foulard', 'pull', 'chapeau']
text: []
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']

* SEED 43 *

description: Gaia est assise à une table ronde recouverte d'un tissu à motifs colorés. Elle porte un bonnet jaune moutarde et un pull noir avec des motifs orange et rose. Gaia est penchée sur un cahier ouvert, tenant un stylo à la main. Le cahier contient des pages avec des illustrations et du texte. Une chaise turquoise est visible à côté de la table. En arrière-plan, on aperçoit une cuisine avec des armoires blanches, un plan de travail et des appareils électroménagers. La lumière est douce et diffuse.
keywords: ['Gaia', 'table', 'cahier', 'stylo', 'bonnet', 'pull', 'cuisine', 'chaise', 'turquoise', 'jaune', 'orange', 'rose', 'motif', 'illustration', 'texte', 'fond', 'intérieur', 'meubles', 'appareil électroménager', 'éclairage']
text: ['De wereldomspannende', '1.1 De wereldomspannende', '1.2 De wereldomspannende', '1.3 De wereldomspannende', '1.4 De wereldomspannende', '1.5 De wereldomspannende', '1.6 De wereldomspannende', '1.7 De wereldomspannende', '1.8 De wereldomspannende', '1.9 De wereldomspannende', '1.10 De wereldomspannende', '1.11 De wereldomspannende', '1.12 De wereldomspannende', '1.13 De wereldomspannende', '1.14 De wereldomspannende', '1.15 De wereldomspannende', '1.16 De wereldomspannende', '1.17 De wereldomspannende', '1.18 De wereldomspannende', '1.19 De wereldomspannende', '1.20 De wereldomspannende']
peoples: ['Gaia']

description: Corto se tient à gauche, portant un costume noir sur chemise claire et pantalon noir, avec des chaussures noires. Il a les cheveux longs et foncés. Niko est à côté de Corto, portant un sweat à capuche rouge sur un t-shirt, et un pantalon noir. Il a une barbe rousse. Myriam se trouve à droite, portant un sweat à capuche gris, avec des écouteurs autour du cou. Elle a les cheveux foncés. Ils se trouvent dans une pièce avec un sol en bois clair. Un mur est peint en bleu foncé avec des cadres contenant des images. Une porte-fenêtre laisse entrevoir un extérieur lumineux. Un tableau abstrait coloré est visible sur le mur à gauche. Un fauteuil en rotin est également présent.
keywords: ['Corto', 'Niko', 'Myriam', 'costume', 'sweat à capuche', 'porte-fenêtre', 'tableau', 'rotin', 'sol en bois', 'mur bleu', 'cadres', 'images', 'cheveux longs', 'barbe rousse', 'écouteurs', 'intérieur', 'pièce', 'porte', 'fenêtre', 'meuble']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: Une scène se déroule dans une pièce à vivre aux murs bleu foncé à panneaux. Un homme âgé, portant un béret et des lunettes, est assis sur un canapé en cuir noir. À sa droite, une femme porte des lunettes et un foulard. Alex est assis à côté d'elle, portant un pull rouge. Gaia est assise à côté d'Alex, souriante. Myriam est assise à côté de Gaia, également souriante. Niko est assis à côté de Myriam. Un homme est assis sur un siège en face d'eux. Un homme est allongé sur le sol, vêtu d'un chemise à motifs et de pantalons à motifs, et semble effectuer une action théâtrale. Un tableau représentant une femme et un serpent est accroché au mur. Une lampe de chevet diffuse une lumière jaune. Des décorations d'Halloween, dont des citrouilles et des guirlandes lumineuses, sont visibles sur une étagère. Le sol est en bois.
keywords: ['salon', 'canapé', 'homme', 'femme', 'tableau', 'serpent', 'Halloween', 'citrouille', 'guirlande lumineuse', 'lampe', 'béret', 'foulard', 'chemise', 'pantalon', 'sourire', 'bois', 'intérieur', 'Alex', 'Gaia', 'Niko']
text: []
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']



* EN *

description: Gaia is seated at a small, round table covered with a patterned tablecloth featuring blue, orange, and white designs. She is wearing a black t-shirt with orange and yellow accents and a yellow pom-pom hat. Gaia is looking directly at the camera with a slight smile, holding a pen in her right hand. Open notebooks are spread across the table in front of her, filled with handwritten notes and diagrams. The notebooks appear to be schoolwork. Behind Gaia, the room is dimly lit, revealing a kitchen area with white cabinets, a countertop, and various kitchen appliances. A teal-colored wall is visible to the left of Gaia, with a blue cushioned chair partially visible. The floor is tiled.
keywords: ['Gaia', 'notebook', 'tablecloth', 'pen', 'hat', 'kitchen', 'chair', 'tile floor', 'textbook', 'student', 'yellow', 'black', 'orange', 'teal', 'white', 'room', 'desk', 'writing', 'study', 'pom-pom']
text: ['De wereldomgeving', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.18', '1.19', '1.20']
peoples: ['Gaia']

description: Three people stand in a hallway with a doorway leading to a brightly lit room. Corto, wearing a dark blazer over a light-colored shirt and dark pants, stands on the left. Next to him is Niko, wearing a red shirt and dark pants. Myriam, wearing a gray hooded sweatshirt and headphones, stands slightly behind and to the right of Niko. The hallway walls are painted dark blue-green. Above the people, a series of framed prints depicting stylized animal faces are visible. A large, colorful spiral artwork is visible through the doorway. The floor is made of wooden planks. A chair and other furniture are partially visible in the room beyond the doorway. A framed poster is visible on the right wall.
keywords: ['hallway', 'people', 'Corto', 'Niko', 'Myriam', 'doorway', 'room', 'artwork', 'prints', 'framed', 'furniture', 'chair', 'poster', 'blazer', 'hoodie', 'spiral', 'wooden floor', 'dark walls', 'animal faces']
text: []
peoples: ['Corto', 'Niko', 'Myriam']

description: A group of people are gathered in a room with dark teal walls and wood-paneled trim. A man is performing what appears to be a theatrical movement on the floor, facing away from the audience. Alex is seated on a dark blue sofa, looking towards the performer with a slight smile. Gaia is seated next to Alex, also looking at the performer. Myriam is seated next to Gaia, and Niko is seated next to Myriam. A woman is seated next to Niko. An older man is seated in a chair to the left, wearing a cap. Another man is standing near the back of the room. A painting hangs on the wall above the sofa, depicting a woman with a snake. A lamp illuminates the scene. There are pumpkins and other decorations visible in the corner of the room. The floor is made of wooden planks.
keywords: ['room', 'teal', 'wood paneling', 'sofa', 'performance', 'painting', 'lamp', 'pumpkins', 'decoration', 'Alex', 'Gaia', 'Myriam', 'Niko', 'man', 'woman', 'floor', 'chair', 'theatre', 'audience', 'dark blue', 'wooden planks']
text: []
peoples: ['Gaia', 'Alex', 'Myriam', 'Niko']

"""


if __name__ == "__main__":
    test()
    
