# import ollama
# or pure http below
import socket
import json

def ask_ollama_http( model, prompt ):
    strHost = "localhost"
    port = "11434"
    
    # ---- Build JSON payload ----
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,        # easier to parse than streaming mode
          "options": 
            {
                "temperature": 0.1,   # 0 = deterministe, 1 = plus aleatoire
                "seed": 42,              # pour reproductibilite
                #~ "max_tokens": 3        # nombre maximum de tokens a generer (not working?)
            }
    }

    body = json.dumps(payload).encode("utf-8")

    # ---- Manually build HTTP request ----
    request = (
        "POST /api/generate HTTP/1.1\r\n"
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
    idx = body.index("{")
    idx2 = body.index("}")
    body = body[idx:idx2+1]

    print("\n---- BODY cleaned ----")
    print(body)

    # ---- Parse JSON result ----
    data = json.loads(body)
    print("\n---- MODEL RESPONSE ----")
    ret = data["response"]
    return ret
    
# ask_ollama_http - end


strModel = "gemma3:270m" # un rapide pour tester
#~ strModel = "llama3.2"

class TchatUser:    
    def __init__( self, firstname = "", name = "" ):
        """
        Name is a nicely name
        """
        self.firstname = firstname
        self.name = name
        self.context = [] # a list of sentence sent to tchatter
        
    def getAns( self, msg ):
        
        #~ response = ollama.chat( model=strModel, messages=[  {"role": "user", "content": msg} ], options= {"temperature": 0.0, "thinking":1,"seed": 1234}  )
        #~ print(response)
        #~ res = response["message"]["content"]
        res = ask_ollama_http( strModel, msg )
        return res

class TchatUserManager:
    
    def __init__( self ):
        self.users = {} # user_id => TchatUser
        
    def createUser( self, user_id ):
        u = TchatUser()
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