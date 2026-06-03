# -*- coding: utf-8 -*-

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
                    
                    # token: (input/output): 26/8 (pourquoi 26 juste pour hello?)
                    [ "Load+Hello", [{"role":"user","content":"Hello"}] ],  # premier pour charger le modele, second pour test speed
                    [ "Hello", [{"role":"user","content":"Hello"}] ], 
                    
                    [ "comput", [{"role":"user","content":"Hello, give me precisely the results of 16*16, print only the result and nothing else."}] ],
                    
                    [ "long1", [{"role":"user","content":"Parle moi de calvitie"}] ], # question courte, reponse longue
                    
                    [ "long2", [{"role":"user","content":"Parle moi de calvitie, mais avec une reponse courte de 2 phrases max."}] ], # question longue avec context, reponse longue
                    
                    [ "carwash", [{"role":"user","content":"je dois aller au carwash laver ma voiture, il fait beau c'est a 100m de chez moi, est ce qu'il vaut mieux y aller a pied ou en voiture ? repond en une phrase de moins de 15 mots!"}] ], # question longue avec context, reponse longue
                
                
                ]
                
    normal_answer = ["How can I assist you today?","How can I assist you today?","256"]
    
    if 1:
        # long message
        import knowledge
        knowledge.classic_init()
        kdb = knowledge.get_knowledge_related_to( "calvitie", max=4,verbose = False )
        for k in kdb:
            print( "Adding k: '%s'" % str(k) )
            msgss[4][1].insert( 0, {"role": "system","content": k} )
        print("")
    
    # 2 models running in 10GB VRAM
    #~ model = "ministral-3:14b"
    #~ model = "deepseek-r1:8b"
    #~ model = "gemma4:e4b " # todo: add this one
    #~ model = "llama3:70b" # enorme modele!
    
    #~ model = "qwen3.6:35b"  # bonne qualité
    #~ model = "qwen3.6-35b-a3b-q8" # optimisé ?



    #  a nice recent one
    model = "llama3.2"
    res = []
    i = 0
    for title_test, messages in msgss:
        time_begin = time.time()
        ret = ask_ollama_http( model, messages )
        print( ret )
        if i < len(normal_answer) and model == "llama3.2":
            assert( ret == normal_answer[i] )
        
        duration = time.time() - time_begin
        print( "%s: duration: %.3fs\n" % (title_test, duration) )
        res.append( duration )
        i += 1
        
        
    print( "cpu: %s" % strCpu )
    for i in range( len(msgss) ):
        print( "%-10s\t: %.3fs" % ( msgss[i][0], res[i] ) )
        
        """
        Azure: 
        cpu: Intel(R) Xeon(R) Platinum 8272CL CPU @ 2.60GHz
        
        Hello               : 0.669s # 4.6 si model pas encore charge
        comput           : 0.818s
        long1              : 43.806s
        long2              : 190.068s / 246.041s avec get_knowledge_related_to a max=4
        
        ### Champion1 en 100%  cpu:
        cpu: Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz
        Load+Hello      : 2.690s
        Hello               : 0.751s
        comput           : 0.491s
        long1              : 69.791s
        long2              : 257.479s
        

        ### Champion1 en 100%  Gpu (3080 10GB) (le modele fait 3.4GB dans ollama ps, ca prend 3.4GB dans nvidia-smi!)
        NVIDIA-SMI 570.133.07             Driver Version: 570.133.07     CUDA Version: 12.8
        (ca fonctionnait pas car mes drivers était en 11.4)
            

        Load+Hello      : 1.811s        
        Hello               : 0.135s         (token: 26/8)
        comput            : 0.109s        (token: 46/2)
        long1              : 3.334s         (token: 32/599) (a peu pres 180 token/sec)
        long2              : 1.405s         (token: 5782/85)
        (les timings sont bien régulier)
        
        avec deepseek-r1:8b (6.6GB VRAM)
        Load+Hello      : 5.109s
        Hello               : 2.117s            (token: 3/224)
        comput            : 1.904s            (token: 555/35)
        long1               : 16.052s         (token: 9/1707)
        long2               : 4.821s           (token: 5752/315)
        
        avec ministral-3:14b (11GB 16%/84% CPU/GPU )
        Load+Hello      : 6.576s            
        Hello               : 1.781s            (token: 555/35)
        comput            : 0.411s            (token: 577/4)
        long1               : 83.570s         (token: 561/1709) 
        long2               : 8.515s           (token: 4910/111)
        
        ### Apple M2 Max (de Yann)
        Load+Hello      : 2.5s
        Hello               : 0.220s
        comput            : 0.182s
        long1               : 9.83s
        long2               : 6.87s


        ### d'apres ChatGpt Xavier AGX:

        Comparaison rapide Jetson Xavier AGX
        Setup	Tokens/sec
        CPU only	2–4
        CUDA partiel	5–10
        CUDA optimisé	8–14
        PC RTX 4090	70–150


        ### DGX Spark (peak a 297w) (idle: 112w)
        
        Load+Hello      : 3.476s
        Hello               : 0.297s
        comput            : 0.204s
        long1               : 8.028s
        long2               : 2.219s
        carwash           : 0.437s (a pied)
        
        avec ministral-3:14b (51GB en 100 % GPU (context 262144))
        Load+Hello      : 12.270s
        Hello               : 2.751s
        comput            : 0.401s
        long1              : 50.396s
        long2              : 6.233s
        
        avec deepseek-r1:8b (25GB VRAM, 131k context))
        Load+Hello      : 21.305s
        Hello               : 4.713s
        comput           : 1.960s
        long1              : 53.264s
        long2              : 11.136s

        llama3:70b (42GB en 100% GPU context 8192)
        Load+Hello      : 42.716s
        Hello               : 4.725s
        comput           : 0.632s
        long1              : 123.608s
        long2              : 27.755s
        carwash:         : 1.41 (a pied)
        
        qwen3.6:35b (29 GB    100% GPU     262144)
        Load+Hello   : 22.752s
        Hello            : 2.534s
        comput        : 5.881s
        long1           : 22.364s
        long2           : 8.408s
        
        qwen3.6-35b-a3b-q8 (43 GB    100% GPU     262144)
        qwen optimised:  install avec: 
        wget https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/blob/main/Qwen3.6-35B-A3B-Q8_0.gguf
        echo FROM ./Qwen3.6-35B-A3B-Q8_0.gguf > modelfile
        ollama create qwen3.6-35b-a3b-q8 -f modelfile
        
        Load+Hello      : 29.711s
        Hello           : 4.216s
        comput          : 7.186s
        long1           : 28.902s
        long2           : 18.605s
        carwash       : 12.314s
        

        
        # 3080 cutpaste:
        Load+Hello      : 1.811s        
        Hello               : 0.135s         (token: 26/8)
        comput            : 0.109s        (token: 46/2)
        long1              : 3.334s         (token: 32/599) (a peu pres 180 token/sec)
        long2              : 1.405s         (token: 5782/85)
        
        avec deepseek-r1:8b (6.6GB VRAM)
        Load+Hello      : 5.109s
        Hello               : 2.117s            (token: 3/224)
        comput            : 1.904s            (token: 555/35)
        long1               : 16.052s         (token: 9/1707)
        long2               : 4.821s           (token: 5752/315)
        
        avec ministral-3:14b (11GB 16%/84% CPU/GPU )
        Load+Hello      : 6.576s            
        Hello               : 1.781s            (token: 555/35)
        comput            : 0.411s            (token: 577/4)
        long1               : 83.570s         (token: 561/1709) 
        long2               : 8.515s           (token: 4910/111)
        
        
        

        

# a checker cette reponse sur dgx: 
---- MODEL RESPONSE ----
La calvitie est un phénomène naturel où les cheveux commencent à tomber, souvent en raison d'une production excessive d'hormones mâles ou d'un dérèglement hormonal. Elle peut être héréditaire et touche principalement les hommes, mais également les femmes, avec des causes variées telles que le stress, une mauvaise alimentation ou la chimiothérapie.

A ajouter dans le test: 
"je dois aller au carwash laver ma voiture, il fait beau c'est a 100m de chez moi, est ce qu'il vaut mieux y aller a pied ou en voiture ? repond en une phrase de moins de 15 mots!"
"Le fromage sur la pizza n'arrete pas de couler sur la table, car la table est inclinée"
        """
    
#todo
# faire le bench avec differentes seed pour la phrase du carwash, car certaines fonctionnent seed fonctionnenet mieux que d'autrss
    
    
if __name__ == "__main__":
    testperf()
    