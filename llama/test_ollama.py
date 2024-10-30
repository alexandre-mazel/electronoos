# -*- coding: cp1252 -*-

import requests
import json
import time
import os

# using a running ollana instance server
# models seems to be stored (windows) in C:\Users\alexa\.ollama\models\blobs

url = "http://localhost:11434/api/chat"
strModel = "llama3.2:1B" # size: 1.3GB, running: 2.2GB
strModel = "llama3.2" # 3B? #size:  2.0GB, running: 3.5GB
#~ strModel = "llama3.1:8B" # size: 4.7GB, running: 6.3GB
#~ strModel = "llama3.1:8B-instruct" # size: 4.7GB, running: 6.3GB  # no size

# todo test avec plus gros contexte:
#   "options": {"num_ctx": 256000}

class Conversation:
    
    def __init__(self):
        self.msgs = [] # de la forme [ { "role": "user","content": "un prompt" } ]
        self.addBootstrap()

    def addBootstrap(self):
        if 0:
            self.msgs.append({"role": "system", "content": "Tu es un robot de compagnie d'une personne ag�e."})
        if 1:
            self.msgs.append({"role": "system", "content": "I'm a man very busy man. you must give me the shortest possible answer"})
            self.msgs.append({"role": "user", "content": "J'ai 2 enfants, un garcon de 16 ans nomm� Corto et une fille de 11 ans nomm�e Gaia."})
            self.msgs.append({"role": "user", "content": "Ne me donne que des informations juste et v�rifiable."})
        if 0:
            self.msgs.append({"role": "system", "content": "Je suis un jeune, et je parle de maniere vachement coolos. J'aime rigoler, sois cool avec moi, parle moi comme a un super pote! Wesh!"})
        
        
    def addSentenceUser( self, ans ):
        self.msgs.append({"role": "user", "content": ans})
        
    def addSentenceAssistant( self, ans ):
        self.msgs.append({"role": "assistant", "content": ans})
        
        
    def getMessages( self ):
        return self.msgs
        
        
conv = Conversation()
        
def llama3_histo(prompt):
    conv.addSentenceUser(prompt)
    
    print( "INF: llama3_histo: using model: '%s'" % strModel )
    data = {
        "model": strModel,
        "messages": conv.getMessages(),
        "temperature": 0.2,
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("INF: llama3: posting...")
    timeBegin = time.time()
    response = requests.post(url, headers=headers, json=data)
    duration = time.time()-timeBegin
    print("INF: llama3: received in %5.2fs" % duration)
    
    resp = response.json()
    if "error" in resp:
        print("ERR: llama3: " + resp["error"])
        return resp
    ans = resp['message']['content']
    conv.addSentenceAssistant(ans)
    return ans
    
        

def llama3(prompt):
    print( "INF: llama3: using model: '%s'" % strModel )
    data = {
        "model": strModel,
        "messages": [
            {
              "role": "user",
              "content": prompt
            }
        ],
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("INF: llama3: posting...")
    timeBegin = time.time()
    response = requests.post(url, headers=headers, json=data)
    duration = time.time()-timeBegin
    print("INF: llama3: received in %5.2fs" % duration)
    
    resp = response.json()
    if "error" in resp:
        print("ERR: llama3: " + resp["error"])
        return resp
    return(resp['message']['content'])
    
    
def loop_dialog(strHumanName):
    
    bUseVoice = 0
    if os.name == "nt" and 0:
        bUseVoice = 1
    
    while 1:
        msg = ""
        while msg == "":
            if bUseVoice:
                msg = myGetTextFromSpeechReco()
            else:
                msg = input("\n%s: " % strHumanName)
        msglo = msg.lower()
        if msglo in ["quit","quit()", "bye","au revoir", "a+", "a plus tard"] or "au revoir" in msglo: # condition facile pour la tts
            print("\nAI: a+")
            break
            
        ans = llama3_histo(msg)
        print("\nAI: " + ans )
    
    print("")
    print(conv.getMessages())
    
# perf:
# p = "who wrote the book godfather"
# 4.5s on mstab7 with llama3.2:1B
# 10s-15s on mstab7 with llama3.2:8B

# p = "traduis moi 'je suis content' en anglais"
# 2s-10s on mstab7 with llama3.2:1B
# 8s-20s on mstab7 with llama3.2:8B

 
p = "who wrote the book godfather"
#~ p = "traduis moi 'je suis content' en anglais"
p = "draw me an unicorn"
p = "draw me a square"
p = "dit moi une blague a leur sujet"
p = "summarize me this text: Le lyc�e doit son nom � l'�crivain et philosophe Voltaire. R�alis� par l'architecte Eug�ne Train, il est inaugur� le 13 juillet 18911,2 par le pr�sident Sadi Carnot et est longtemps le seul lyc�e du nord-est parisien. � l'ouverture, le lyc�e est un �tablissement r�serv� aux gar�ons, avant de devenir progressivement mixte � partir de 1973. Dans la seconde moiti� du XIXe si�cle, la probit� du personnel enseignant est surveill�e. Toutefois, faute de pouvoir r�glementer leurs loisirs aussi strictement que pour les �l�ves, les autorit�s, souhaitant �viter qu'ils ne trainent dans des cabarets, am�nagent dans plusieurs lyc�es des salons de jeux et de lecture pour leur d�tente, comme au lyc�e Janson-de-Sailly � partir de 18933. "
#~ response = llama3(p)
#~ print(response)

loop_dialog("Alexandre")

