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
            self.msgs.append({"role": "system", "content": "Tu es un robot de compagnie d'une personne agée."})
        if 1:
            self.msgs.append({"role": "system", "content": "I'm a man very busy man. you must give me the shortest possible answer"})
            self.msgs.append({"role": "user", "content": "J'ai 2 enfants, un garcon de 16 ans nommé Corto et une fille de 11 ans nommée Gaia."})
            self.msgs.append({"role": "user", "content": "Ne me donne que des informations juste et vérifiable."})
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
p = "summarize me this text: Le lycée doit son nom à l'écrivain et philosophe Voltaire. Réalisé par l'architecte Eugène Train, il est inauguré le 13 juillet 18911,2 par le président Sadi Carnot et est longtemps le seul lycée du nord-est parisien. À l'ouverture, le lycée est un établissement réservé aux garçons, avant de devenir progressivement mixte à partir de 1973. Dans la seconde moitié du XIXe siècle, la probité du personnel enseignant est surveillée. Toutefois, faute de pouvoir réglementer leurs loisirs aussi strictement que pour les élèves, les autorités, souhaitant éviter qu'ils ne trainent dans des cabarets, aménagent dans plusieurs lycées des salons de jeux et de lecture pour leur détente, comme au lycée Janson-de-Sailly à partir de 18933. "
#~ response = llama3(p)
#~ print(response)

loop_dialog("Alexandre")

