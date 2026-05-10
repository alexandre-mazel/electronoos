# -*- coding: utf-8 -*-

# import ollama
# or pure http below:
import socket
import json

def ask_ollama_http( model, messages ):
    print( "DBG: ask_ollama_http: model: %s, prompt:\n%s" % (model, messages) )
    
    strHost = "localhost"
    port = 11434
    
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

    # ---- Open raw TCP socket ----
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {strHost}:{port}...")
        s.connect((strHost, port))

        print("Sending HTTP request...")
        s.sendall(request)

        # ---- Receive full response ----
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

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
    
    # prompt_eval_count: taille du contexte envoy� (historique + prompt)
    # eval_count: nombre de tokens g�n�r�s
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


strModel = "gemma3:270m" # un rapide pour tester
strModel = "llama3.2"

class TchatUser:    
    def __init__( self, user_id, firstname = "", name = "" ):
        """
        Name is a nicely name
        """
        self.user_id = user_id
        self.firstname = firstname
        self.name = name
        self.context = [] # a list of sentence sent to tchatter
        self.context = [{"role":"system","content":"Tu es un chatbot sympa. Répond toujours avec des phrases pas trop longues et limitées a 2 ou phrases max en texte pur, sans émoticone ou truc fancy du genre."}]
        if 0:
            self.context.append( {"role":"system","content":"Si on te demande un restaurant dans le coin (on est dans le 16ieme arrt de paris), tu peux parler de Ragazzi 2.0 au 83 rue de Longchamp ou La matta au 23 rue de l'annonciation"} )
        
    def getAns( self, msg ):
        
        #~ response = ollama.chat( model=strModel, messages=[  {"role": "user", "content": msg} ], options= {"temperature": 0.0, "thinking":1,"seed": 1234}  )
        #~ print(response)
        #~ res = response["message"]["content"]
        
        print( "DBG: TchatUser.getAns: name: %s, context:\n%s" % (self.user_id,self.context) )
        
        self.context.append({"role":"user","content":msg})
        
        """
        et ensuite ce message doit fonctionner:
        hello 2 fois doit pas donner la meme reponse
        actuellement:
        Hello! How can I assist you today?
        my name is alexandre, memorize it! now what's my name ?
        """
        
        prompt = self.context[:]
        
        
        if 1:
            kdb = []
            #~ kdb = knowledge.get_knowledge_related_to( msg )
            # je pense qu'il faut garder les resultats de connaissances sur au moins 3-5 echanges
            # sinon si il file une adresse de resto, et que je dit c'est ou? il a oublié entre temps
            # j'ai monté les token a 8k dans le systeme du daemon (a reloader)
            
            # mettre aussi des infos sur paris un peu plus globale et le tourisme en france
            if "manger" in msg:
                kdb = [
                    "restaurant italien La Petite Tour au 11 rue de la Tour 75116 Paris",
                    "restaurant Le Paris Seize au 18 rue des Belles Feuilles 75116 Paris",
                    "pizzeria Pop's Pizza proche de l’avenue Victor Hugo 75116 Paris",
                    "restaurant japonais Planet Sushi avenue Victor Hugo 75116 Paris",
                    "place du Trocadéro idéale pour voir la tour Eiffel"
                ]
            for k in kdb:
                print( "Adding k: '%s'" % k )
                prompt.insert(0, {"role": "system","content": k} )
        
        res = ask_ollama_http( strModel, prompt )
        
        if "ERR: " not in res:
            self.context.append({"role":"assistant", "content": res})
                
        return res

class TchatUserManager:
    
    def __init__( self ):
        self.users = {} # user_id => TchatUser
        
    def createUser( self, user_id ):
        u = TchatUser( user_id )
        self.users[user_id] = u
        
    def getUser( self, user_id ):
        if not user_id in self.users:
            self.createUser( user_id )
        return self.users[user_id]
    

tum = TchatUserManager()

def handle_user_tchat(user_id, msg):
    u = tum.getUser( user_id )
    ans = u.getAns( msg )
    return ans