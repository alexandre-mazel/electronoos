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
    # non a faire que si en chunked
    isChunked = "Transfer-Encoding: chunked" in headers
    print( "INF: isChunked: ", isChunked )
    if( isChunked ):
        idx = body.index("{")
        idx2 = len(body) - 1
        while  body[idx2] != "}" and idx2 > 0:
            idx2 -= 1
        body = body[idx:idx2+1]

        print("\n---- BODY cleaned ----")
        print(body)

    # ---- Parse JSON result ----
    
    data = json.loads(body)
    
    # prompt_eval_count: taille du contexte envoy?historique + prompt)
    # eval_count: nombre de tokens g?r?
    print( "DBG: prompt_eval_count (input token): %s" % str( data["prompt_eval_count"] ) )
    print( "DBG: eval_count (answer token): %s" % str( data["eval_count"] ) )
    
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
    import sys
    sys.path.append( "../alex_pytools/")
    import misctools
    strCpu = misctools.getCpuModel(bShort=True)
    print( "cpu: %s" % strCpu )
    msgss =   [
                    #~ [{"user":"hello"}] # amusant ca sort un truc incomprehensible un code python qui fait du sklearn !?!
                    
                    # token: (input/output): 26/8 (pourquoi 26?)
                    [ "Hello", [{"role":"user","content":"Hello"}] ],  # premier pour charger le modele, second pour test speed
                    [ "Hello", [{"role":"user","content":"Hello"}] ], 
                    
                    # token: 46/2
                    [ "avg", [{"role":"user","content":"Hello, give me precisely the results of 16*16, print only the result and nothing else."}] ],
                    
                    # token: 32/662
                    [ "long1", [{"role":"user","content":"Parle moi de calvitie"}] ], # question courte, reponse longue
                    
                    # token: 4609/79
                    [ "long2", [{"role":"user","content":"Parle moi de calvitie, mais avec une reponse courte de 2 phrases max."}] ], # question longue avec context, reponse longue
                ]
    if 1:
        # long message
        import knowledge
        knowledge.classic_init()
        kdb = knowledge.get_knowledge_related_to( "calvitie", max=4,verbose = False )
        for k in kdb:
            print( "Adding k: '%s'" % str(k) )
            msgss[3][1].insert( 0, {"role": "system","content": k} )
        print("")
    
    model = "llama3.2"
    res = []
    for title_test, messages in msgss:
        time_begin = time.time()
        print( ask_ollama_http( model, messages ) )
        duration = time.time() - time_begin
        print( "%s: duration: %.3fs\n" % (title_test, duration) )
        res.append( duration )
        
    for i in range( len(msgss) ):
        print( "%5s: %.3fs" % ( msgss[i][0], res[i] ) )
        
        """
        Azure: 
        cpu: Intel(R) Xeon(R) Platinum 8272CL CPU @ 2.60GHz
        
        Hello: 0.669s # 4.6 si model pas encore charge
          avg: 0.818s
        long1: 43.806s
        long2: 190.068s / 246.041s avec get_knowledge_related_to a max=4


        """
    
    
    
if __name__ == "__main__":
    testperf()
    