# -*- coding: cp1252 -*-

import requests
import json
import time
import os

# using a running ollana instance server
# models seems to be stored (windows) in C:\Users\alexa\.ollama\models\blobs

url = "http://localhost:11434/api/chat"
strModel = "llama3.2:1B" # size: 2.2GB
#~ strModel = "llama3.2" # 3B? # size: 3.5GB
#~ strModel = "llama3.1:8B" # size: 4.9GB


class Conversation:
    
    def __init__(self):
        self.msgs = [] # de la forme [ { "role": "user","content": "un prompt" } ]
        self.addBootstrap()

    def addBootstrap(self):
        self.msgs.append({"role": "system", "content": "Tu es un robot de compagnie d'une personne agée."})
        
    def addSentenceUser( self, ans ):
        self.msgs.append({"role": "user", "content": ans})
        
    def addSentenceAssistant( self, ans ):
        self.msgs.append({"role": "assistant", "content": ans})
        
        
    def getMessages( self ):
        return self.msgs
        
        
conv = Conversation()
        
def llama3_histo(prompt):
    conv.addSentenceAssistant(prompt)
    ans = llama3(conv.getMessages()[:])
    print(ans)
        

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
    if os.name == "nt" or 0:
        bUseVoice = 1
    
    while 1:
        msg = ""
        while msg == "":
            if bUseVoice:
                msg = myGetTextFromSpeechReco()
            else:
                msg = input("%s: " % strHumanName)
        msglo = msg.lower()
        if msglo in ["quit","quit()", "bye","au revoir", "a+", "a plus tard"] or "au revoir" in msglo: # condition facile pour la tts
            print("AI: a+")
            break
    
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
#~ response = llama3(p)
#~ print(response)

loop_dialog("Alexandre")

