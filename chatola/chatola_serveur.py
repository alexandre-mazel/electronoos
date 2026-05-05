from flask import Flask, request # sudo apt install python3-flask
import time

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
    timeBegin = time.time()
    ret = handle_user_tchat( data["user_id"], data["msg"] )
    duration = time.time() - timeBegin
    return {"status": "ok", "ans": ret, "debug": "", "duration": duration}

certname = "azure."
keyfn = "/etc/letsencrypt/live/%sobo-world.com/privkey.pem" % certname
certfn = "/etc/letsencrypt/live/%sobo-world.com/cert.pem" % certname
fullfn = "/etc/letsencrypt/live/%sobo-world.com/fullchain.pem" % certname

app.run(
    host="0.0.0.0",
    port=10000,
    ssl_context=(fullfn,keyfn)
)