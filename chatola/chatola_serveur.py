from flask import Flask, request

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def receive():
    data = request.json
    print("Reçu :", data)
    return {"status": "ok"}

app.run(
    host="0.0.0.0",
    port=5000,
    ssl_context=("/chemin/vers/fullchain.pem", "/chemin/vers/privkey.pem")
)