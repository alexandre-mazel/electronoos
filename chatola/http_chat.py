# import ollama
# or pure http below:
import socket
import json

import time

def ask_ollama_http( model, messages, strHost = "localhost", port = 11434 ):
    print( "DBG: ask_ollama_http: model: %s, prompt:\n%s" % (model, messages) )
    
    """
    /generate ? expects string prompt
    /chat ? accepts structured messages (role/content)
    """
    
    # ---- Build JSON payload ----
    payload = {
        "model": model,
        #~ "prompt": prompt, # quand on est en mode generate
        "messages": messages,
        "stream": False,        # easier to parse than streaming mode
          "options": 
            {
                "temperature": 0.1,   # 0 = deterministe, 1 = plus aleatoire
                "seed": 42,              # pour reproductibilite
                #~ "max_tokens": 3        # nombre maximum de tokens a generer (not working?)
            }
    }

    body = json.dumps(payload).encode("utf-8")
    
    bChat = 1

    # ---- Manually build HTTP request ----
    request = (
        "POST /api/chat HTTP/1.1\r\n"
        f"Host: {strHost}:{port}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body
    
    timeout = 10*60 # 10 min

    # ---- Open raw TCP socket ----
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        print(f"Connecting to {strHost}:{port}...")
        s.connect((strHost, port))

        print("Sending HTTP request...")
        s.sendall(request)

        # ---- Receive full response ----
        response = b""
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
        except socket.timeout:
            print("ERR: Socket timeout reached")

    # ---- Separate headers and body ----
    header_bytes, _, body_bytes = response.partition(b"\r\n\r\n")

    headers = header_bytes.decode()
    body = body_bytes.decode(errors="replace",encoding="utf-8")

    print("---- HTTP HEADERS ----")
    print(headers)

    print("\n---- RAW BODY ----")
    print(body)

    # keep only between {} # why garbage around ?
    # a faire que si en mode generate
    if( not bChat ):
        idx = body.index("{")
        idx2 = body.index("}")
        body = body[idx:idx2+1]

        print("\n---- BODY cleaned ----")
        print(body)

    # ---- Parse JSON result ----
    
    data = json.loads(body)
    
    # prompt_eval_count: taille du contexte envoy?historique + prompt)
    # eval_count: nombre de tokens g?r?
    print( "DBG: prompt_eval_count (input token): %s" % str( data["prompt_eval_count"] ) )
    
    print("\n---- MODEL RESPONSE ----")
    try:
        if not bChat:
            ret = data["response"]
        else:
            ret = data["message"]["content"]
    except BaseException as err:
        s = "ERR: ask_ollama_http: %s" % str(err)
        if "error" in data:
            s += " (ollama error: %s)" % ( str(data["error"]) )
        print( s )
        ret = s
    return ret
    
# ask_ollama_http - end

def testperf():
    msgss =   [
                    [{"user":"hello"}]
                ]
    model = "llama2.3"
    for messages in msgss:
        time_begin = time.time()
        print( ask_ollama_http( model, messages ) )
        duration = time.time() - time_begin
        print( "duration: 0.3f" % duration )
    
    
    
if __name__ == "__main__":
    testperf()
    