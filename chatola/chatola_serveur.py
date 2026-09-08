
"""
Ne pas oublier de lancer ollama avec les bonnes options:
(export OLLAMA_HOST=0.0.0.0:11435 && export OLLAMA_NO_CLOUD=1 && export OLLAMA_CONTEXT_LENGTH=8192 && ollama serve)

Pour voir les ps:
OLLAMA_HOST=127.0.0.1:11435 ollama ps

"""

from flask import Flask, request, send_file # sudo apt install python3-flask ou en venv: pip install flask
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

import test_whisper
whisp = test_whisper.Whisper()

tts = None
gbUseTTS = 1 # doit alors etre lancer dans le venv qui a tts activable (cf tts_perso sur champion1)

if gbUseTTS:
    import audio_tts
    tts = audio_tts.AudioSynthesiser()

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
    
    
@app.route( "/voice", methods = ["POST"] )
def receive_voice():
    timeBegin = time.time()

    try:
        user_id = request.headers.get( "X-User-Id" )

        audio_data = request.get_data()

        if not audio_data:
            return {
                "status": "error",
                "ans": "",
                "debug": "No audio data"
            }, 400

        filename = "/tmp/voice_%d.wav" % int( time.time() * 1000 )

        with open( filename, "wb" ) as f:
            f.write( audio_data )

        print(
            "INF: Voice: received %.2f KB"
            % ( len( audio_data ) / 1024 )
        )

        recognised_text = whisp.analyse( filename )
        
        print( "INF: receive_voice: recognised_text:", recognised_text )
        print( "INF: receive_voice: speech reco duration: %.3fs" % (time.time() - timeBegin) )
        
        ret = ""
        debug_msg = ""
        
        if 1:
            try:
                ret = chatola_tchat.handle_user_tchat( user_id, recognised_text )
            except BaseException as err:
                ret = "?"
                debug_msg += "ERR: " + str(err) + "\nstack: " + traceback.format_exc()

        #~ os.unlink( filename )

        duration = time.time() - timeBegin

        print( "INF: receive_voice: total duration: %.2fs" % duration )
        
        if tts:
            output_filename = tts.synthesise(ret) # todo test me !
            retclean = ret.replace("\n", " " ) # Header values must not contain newline characters.
            return send_file( output_filename, mimetype = "audio/wav", as_attachment = False ),  200, {"X-Text": retclean }

        return {
            "status": "ok",
            "recognized": recognised_text,
            "ans": ret, "debug": debug_msg,
            "duration": duration
        }

    except BaseException as err:
        debug_msg = (
            "ERR: " +
            str( err ) +
            "\nstack: " +
            traceback.format_exc()
        )

        print( debug_msg )

        return {
            "status": "error",
            "ans": "",
            "debug": debug_msg,
            "duration": time.time() - timeBegin
        }, 500

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