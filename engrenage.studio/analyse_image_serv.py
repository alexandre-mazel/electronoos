
"""
Un service qui ecoute sur un port et analyse des images serieusement

"""

from flask import Flask, request, send_file # sudo apt install python3-flask ou en venv: pip install flask
import os
import re
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
    
    
def extract_infos_from_img( img, filename, user_id ):
    
    import analyse_image_ollama
    result = analyse_image_ollama.analyse_image_buffer( "http://localhost:11435/api/chat", img,"qwen2.5vl:7b", verbose=1 )
    description = result["description"]
    keywords = result["keywords"]
    text = result["text"]
    
    peoples = []
    
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