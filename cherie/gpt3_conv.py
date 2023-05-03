# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import json
import socket
import pickle 
import argparse

# get song from youtube:
# https://www.justgeek.fr/headset-lecteur-de-musique-open-source-95893/

import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

api_key = misctools.getEnv("OPENAI_KEY",None,0);
if api_key == None:
    print("ERR: please pour your api key in the .env file")
    exit(-1)
openai.api_key = api_key
username = "alexandre_zelma_conv_01"

def printEngines():
    print("\nEngines:")
    engines = openai.Engine.list()
    for d in engines.data:
        print(d.id)

    print("\nModels:")        
    engines = openai.Model.list()
    for d in engines.data:
        print(d.id)

#~ printEngines()

initial_historic = [
#~ {"role": "system", "content": "Tu es un assistant d�vou� programm� pour tenir compagnie a une personne ag�e."},
{"role": "system", "content": "Tu es un robot de compagnie d'une personne ag�e."},
#~ {"role": "system", "content": "Cette personne est une femme nomm�e Pierrette, elle a 82 ans, un enfant nomm� Corto de 45 ans et une fille Gaia de 40 ans."},
#~ {"role": "system", "content": "Le mari de Pierrette, Jean est mort du cancer a l'age de 65 ans."},
{"role": "user", "content": "Je suis une femme nomm�e Pierrette, j'ai 82 ans, un enfant nomm� Corto de 45 ans et une fille Gaia de 40 ans."},
{"role": "user", "content": "Mon mari Jean est mort du cancer a l'age de 65 ans."},
#~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je mari�?"},
#~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je mari�? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'apr�s midi?"},
#~ {"role": "user", "content": "Bonjour, comment va tu ? ai-je des enfants?"},
#~ {"role": "user", "content": "Ca va bien, et vous ? au fait quel est mon nom ?"},
]

def test():

    messages = [
    {"role": "system", "content": "Tu es un assistant d�vou� programm� pour tenir compagnie a une personne ag�e."},
    #~ {"role": "system", "content": "Cette personne est une femme nomm�e Pierrette, elle a 82 ans, un enfant nomm� Corto de 45 ans et une fille Gaia de 40 ans."},
    #~ {"role": "system", "content": "Le mari de Pierrette, Jean est mort du cancer a l'age de 65 ans."},
    {"role": "user", "content": "Je suis une femme nomm�e Pierrette, j'ai 82 ans, un enfant nomm� Corto de 45 ans et une fille Gaia de 40 ans."},
    {"role": "user", "content": "Mon mari Jean est mort du cancer a l'age de 65 ans."},
    #~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je mari�?"},
    #~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je mari�? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'apr�s midi?"},
    #~ {"role": "user", "content": "Bonjour, comment va tu ? ai-je des enfants?"},
    #~ {"role": "user", "content": "Ca va bien, et vous ? au fait quel est mon nom ?"},
    ]

    # conclusion:
    # - heure et date fausses

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages,
      temperature=0.2,
      user=username
    )
    print(completion.choices[0].message)
    

strHumanName = "Pierrette"

def getUserNameToFilename(strUserName):
    return "data/%s.dia"%strUserName
    
def getListKnownUsers():
    users = []
    listF = sorted(os.listdir("data/"))
    for f in listF:
        if ".bak" in f:
            continue
        f = f.replace(".dia","")
        users.append(f)
        
    if users == []:
        users.append("Pierrette")
    return users
    

def loadHistoric(strUserName,defaultHistoric):
    historic = defaultHistoric
    try:
        f = open(getUserNameToFilename(strUserName), "rt")
        newdict = json.load(f)
        if len(newdict)>1:
            print("INF: loadHistoric: good: %d exchanges loaded" % (len(newdict)))
            historic = newdict
        else:
            print("WRN: historic for '%s' looks empty !" % strUserName )
        f.close()
    except FileNotFoundError as err:
        print("WRN: can't load historic for '%s'" % strUserName )
    return historic
    
def saveHistoric(strUserName,historic,bQuiet=0):
    filename = getUserNameToFilename(strUserName)
    misctools.backupFile(filename,bQuiet=1)
    f = open(filename, "wt")
    json.dump(historic,f,indent=0)
    if not bQuiet: print("INF: loadHistoric: good: %d exchanges saved" % (len(historic)))
    f.close()
    
def askUserName():
    users = getListKnownUsers()
    print("Qui etes vous ?")
    for i,u in enumerate(users):
        print("%d: %s" % (i+1, u))
    num = input("Taper le nombre qui correspond: ")
    num = int(num)
    name = users[num-1]
    print("INF: askUserName: selecting %s" % name)
    return name
    
def mySayText(txt):
    sys.path.append("../scripts/")
    import tts_say
    tts_say.say(txt,bUseGoogle=False)
    
#~ mySayText("coucou")

global_sentenceHeard = ""
def wordsCallback(words,confidence):
    if confidence<0.6:
        return
    if len(words)<4:
        return
    import microphone
    microphone.stop_loop()
    print("INF: heard: '%s'" % words)
    global global_sentenceHeard
    global_sentenceHeard = words

def myGetTextFromSpeechReco():
    # my own one
    import microphone
    microphone.loopProcess(wordsCallback)
    global global_sentenceHeard
    return global_sentenceHeard
    
#~ txt = myGetTextFromSpeechReco()
#~ print("txt: '%s'" % txt)
        
def loopDialog(strHumanName):
    # more info here:
    # https://platform.openai.com/docs/api-reference
    
    print("Starting a dialog with '%s'" % strHumanName )
    historic = loadHistoric(strHumanName,initial_historic)
    
    print("")
    
    if len(historic)>4:
        print("3 Prev:")
        
        for conv in historic[-3:]:
            print("%s: %s" % (conv['role'], conv['content']))
        print("")
        
    bUseVoice = 0
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
        historic.append({"role":"user","content":msg})
        saveHistoric(strHumanName,historic,bQuiet=1)
        print("l'ia r�fl�chit...\r",end="")
        try:
            completion = openai.ChatCompletion.create(
                              model="gpt-3.5-turbo",
                              messages=historic,
                              temperature=0.2,
                              user=username
                            )
        except BaseException as err:
            print("ERR: %s" % err)
            print("retrying in 1min...")
            time.sleep(1)
            completion = openai.ChatCompletion.create(
                          model="gpt-3.5-turbo",
                          messages=historic,
                          temperature=0.2,
                          user=username
                        )
        
        #~ print(completion.choices[0].message)
        answer = completion.choices[0].message["content"]
        print("AI: " + answer )
        if bUseVoice:
            mySayText(answer)
        historic.append({"role":"assistant", "content": answer})
        
    #~ print(historic)
    saveHistoric(strHumanName,historic)
        
strUsername = "Pierrette"
strUsername = askUserName()
loopDialog(strUsername)
