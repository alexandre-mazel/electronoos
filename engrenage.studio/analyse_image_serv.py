
"""
Un service qui ecoute sur un port et analyse des images serieusement

"""

from flask import Flask, request, send_file # sudo apt install python3-flask ou en venv: pip install flask
import cv2
import numpy as np
import os
import re
import sys
import time
import unicodedata

logdir = os.path.expanduser( "~/logs/" )

import traceback

def getHostName():
    if os.name == "nt":
        hostname = os.environ['COMPUTERNAME']
    else:
        unames = os.uname()
        #~ print("unames: %s" % str(unames))
        hostname = unames[1]
        #~ print(hostname)
    return hostname.replace(" ", "_")
    
    
def extract_infos_from_img( img_raw, filename, user_id ):
    """
    img_raw est le buffer compresse' direct (eg jpg)
    """
    print( "INF: extract_infos_from_img: filename: '%s', user_id: '%s'" % ( filename, user_id ) )
    sys.path.append( "../../face_tools/")
    import facerecognizer3
    
    peoples = []
        
    fr = facerecognizer3.faceRecognizer3
    filename_for_caching = "%s__%s" % (user_id, filename)
    fr.load()
    img = cv2.imdecode( np.frombuffer(img_raw, dtype=np.uint8), cv2.IMREAD_COLOR )
    faces = fr.recognizeFromImg( img, filename_for_caching, find_match = True )
    fr.save() # for embedding
    if len(faces) > 0:
        print( "found %d faces" % len(faces) )
        extra_instruction = "PRENOMS :\nDe haut en bas puis pour chaque rangée de gauche a droite, les personnes ont pour prénom: "
        for i,face in enumerate( faces ):
            name = face.reco[0]
            if name != "":
                name = name.capitalize()
                peoples.append( name )
                extra_instruction += name
                if i < len( faces ) - 1:
                    extra_instruction += ", "
        extra_instruction += "." 
        extra_instruction +=  " Prend cela en compte dans la génération de la description."
        
        extra_instruction_hardcoded = """PRENOMS :
        Dans cette image, les personnes sont identifiées de haut en bas,
puis de gauche à droite :

        - Personne 1 : Gaia

Donc, si la personne 1 est visible, écris "Gaia" dans la description.

Exemple :
INCORRECT : "Une personne est assise à une table avec des livres."
CORRECT : "Gaia est assise à une table avec des livres."
"""
        #~ extra_instruction  = extra_instruction_hardcoded
        print( "DBG: extract_infos_from_img: extra_instruction: %s" % extra_instruction )

        
    
    import analyse_image_ollama
    strModel = "qwen2.5vl:7b"
    strModel = "gemma3:12b"
    result = analyse_image_ollama.analyse_image_buffer( "http://localhost:11435/api/chat", img_raw,strModel, 
                                                    extra_instruction=extra_instruction, verbose=1 )
    description = result["description"]
    keywords = result["keywords"]
    text = result["text"]
    
    return description, keywords, text, peoples


app = Flask(__name__)


@app.route("/anaimg", methods=["POST"])
def receive_img():
    try:
        # Nom du fichier transmis dans le header HTTP
        filename = request.headers.get("X-Image-Filename")
        user_id = request.headers.get("X-User-Id")

        if not filename:
            return {
                "error": "Missing X-Filename header"
            }, 400

        # Lire les donnees binaires de l'image
        data = request.get_data()

        if not data:
            return {
                "error": "Empty request body"
            }, 400

        # Securiser le nom de fichier :
        # on ne conserve que le nom, pas un eventuel chemin fourni par le client.
        filename = os.path.basename(filename)

        if filename in ("", ".", ".."):
            return {
                "error": "Invalid filename"
            }, 400
            
            
        if 0:
            # Optionnel : creer un repertoire de reception
            receivedir = os.path.expanduser("~/received_images")
            os.makedirs(receivedir, exist_ok=True)

            filepath = os.path.join(receivedir, filename)

            # Sauvegarder l'image
            with open(filepath, "wb") as outfile:
                outfile.write(data)

            print(
                "INF: receive_img: received '%s' (%d bytes)"
                % (filepath, len(data))
            )
            
        if 1:
            description, keywords, text, peoples = extract_infos_from_img( data, filename, user_id )

        return {
            "status": "ok",
            "filename": filename,
            "size": len(data),
            "description":description,
            "keywords":keywords,
            "text":text,
            "peoples":peoples,
        }, 200

    except Exception:
        traceback.print_exc()

        return {
            "error": "Internal server error"
        }, 500

    
certname = "azure."

if getHostName() == "champion1":
    certname = ""
    
fullpath = "/etc/letsencrypt/live/%sobo-world.com/" % certname

if getHostName() == "champion1" or 1: # le vrai test serait: si j'ai pas les droits car on ne m'a pas lance en sudo (ce qui est plutot bien)
    fullpath = "../chatola/"
            
keyfn = fullpath + "privkey.pem"
certfn = fullpath + "cert.pem"
fullfn = fullpath + "fullchain.pem"

context  = (fullfn,keyfn)

if 0:
    # abaisse le requirement a tls v1.0 pour etre compatible avec les vieux NAO (sur mon 2.1 ca fonctionne meme pas)
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    context.load_cert_chain(
        certfile=fullfn,
        keyfile=keyfn
    )

    # TEST UNIQUEMENT : accepter TLS 1.0
    context.minimum_version = ssl.TLSVersion.TLSv1
    context.maximum_version = ssl.TLSVersion.TLSv1

print( "INF: Running app..." )

app.run(
    host="0.0.0.0",
    port=45003,
    ssl_context=context
)