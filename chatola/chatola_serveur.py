
"""
Ne pas oublier de lancer ollama avec les bonnes options:
(export OLLAMA_HOST=0.0.0.0:11435 && export OLLAMA_NO_CLOUD=1 && export OLLAMA_CONTEXT_LENGTH=8192 && ollama serve)
"""

from flask import Flask, request # sudo apt install python3-flask
import os
import time

def getHostName():
    if os.name == "nt":
        hostname = os.environ['COMPUTERNAME']
    else:
        unames = os.uname()
        #~ print("unames: %s" % str(unames))
        hostname = unames[1]
        #~ print(hostname)
    return hostname.replace(" ", "_")

import chatola_tchat
import traceback

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def receive():
    data = request.json
    print("Recu :", data)
    return {"status": "ok"}
    
@app.route("/tchat", methods=["POST"])
def receivetchat():
    data = request.json
    print("INF: Tchat: Recu :", data)
    debug_msg = ""
    timeBegin = time.time()
    try:
        ret = chatola_tchat.handle_user_tchat( data["user_id"], data["msg"] )
    except BaseException as err:
        ret = "?"
        debug_msg += "ERR: " + str(err) + "\nstack: " + traceback.format_exc()
    duration = time.time() - timeBegin
    return {"status": "ok", "ans": ret, "debug": debug_msg, "duration": duration}

certname = "azure."

if getHostName() == "champion1":
    certname = ""
    
fullpath = "/etc/letsencrypt/live/%sobo-world.com/" % certname

if getHostName() == "champion1" or 1: # le vrai test serait: si j'ai pas les droits car on ne m'a pas lance en sudo (ce qui est plutot bien)
    fullpath = ""
            
keyfn = fullpath + "privkey.pem"
certfn = fullpath + "cert.pem"
fullfn = fullpath + "fullchain.pem"

app.run(
    host="0.0.0.0",
    port=45001,
    ssl_context=(fullfn,keyfn)
)