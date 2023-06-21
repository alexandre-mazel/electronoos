# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import json
import socket
import pickle 
import argparse
try:import tiktoken
except: print("WRN: no tiktoken found")

# get song from youtube:
# https://www.justgeek.fr/headset-lecteur-de-musique-open-source-95893/

"""
3mai 16h: test avec Brice.
- pb1: coupe la parole. il dit "ecoute moi" et marque un blanc puis commence une phrase et l'IA coupe en disant: "je t'écoute".
- pb2: politiquement correct sur illuminati: ne décroche pas de la réponse mesurée et politiquement correct:
Je suis d\u00e9sol\u00e9 si je me r\u00e9p\u00e8te. Cependant, je tiens \u00e0 souligner que les informations que je t'ai fournies sont bas\u00e9es sur des sources fiables et v\u00e9rifi\u00e9es. Il n'y a pas de preuve concr\u00e8te que Jacob Rothschild ait un r\u00f4le dans les Illuminatis ou dans tout autre groupe secret. Si tu as d'autres questions ou si tu as besoin d'aide pour rechercher des informations, n'h\u00e9site pas \u00e0 me le dire."
- pb3: parle plus lentement => a recuperer avant.

bienveillance vs compétence
"""

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
#~ {"role": "system", "content": "Tu es un assistant dévoué programmé pour tenir compagnie a une personne agée."},
{"role": "system", "content": "Tu es un robot de compagnie d'une personne agée."},
#~ {"role": "system", "content": "Cette personne est une femme nommée Pierrette, elle a 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
#~ {"role": "system", "content": "Le mari de Pierrette, Jean est mort du cancer a l'age de 65 ans."},
{"role": "user", "content": "Je suis une femme nommée Pierrette, j'ai 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
{"role": "user", "content": "Mon mari Jean est mort du cancer a l'age de 65 ans."},
#~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié?"},
#~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'après midi?"},
#~ {"role": "user", "content": "Bonjour, comment va tu ? ai-je des enfants?"},
#~ {"role": "user", "content": "Ca va bien, et vous ? au fait quel est mon nom ?"},
]

def test():

    messages = [
    {"role": "system", "content": "Tu es un assistant dévoué programmé pour tenir compagnie a une personne agée."},
    #~ {"role": "system", "content": "Cette personne est une femme nommée Pierrette, elle a 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
    #~ {"role": "system", "content": "Le mari de Pierrette, Jean est mort du cancer a l'age de 65 ans."},
    {"role": "user", "content": "Je suis une femme nommée Pierrette, j'ai 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
    {"role": "user", "content": "Mon mari Jean est mort du cancer a l'age de 65 ans."},
    #~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié?"},
    #~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'après midi?"},
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
    if os.name == "nt":
        bUseVoice = 1
    
    if os.name == "nt":
        # model cl100k_base 	gpt-4, gpt-3.5-turbo, text-embedding-ada-002
        enc_tiktoken = tiktoken.get_encoding("cl100k_base") # count token in sentence
        
    bUseVoice = 0
        
    
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
        print("l'ia réfléchit...\r",end="")
        
        historicToUse = []
        
        # limit historic to limit money spending
        if 0 or len(historic)<13:
            historicToUse = historic[:]
        else:
            # => ~400 tokens input, and ~100 output => 0.1 cents per sentence.
            
            historicToUse = historic[:3]+historic[-10:]
            #~ print("historicToUse: %s" % str(historicToUse))
        
        nNbrMaxToken = 128 # size of completion, prompt + completion are limited by model size, eg 4k for gpt3.5
        # si on met trop peu, le moteur coupe au milieu et il faut dire "continue" (continue en francais)
        # pour qu'il continue
        # default 4k or inf, depending of the model.
        
        # other way to cut is to define a stop sequence (eg \n or .)
        # or stop:
        """
        string or array
        Optional
        Defaults to null

        Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
        cf https://platform.openai.com/docs/api-reference/completions/create
        
        # pricing:
        https://openai.com/pricing
        mes depenses:
        https://platform.openai.com/account/usage
        """

        if os.name == "nt":
            if 1:
                # count token
                nNbrToken = 0
                for h in historicToUse:
                    tokens = enc_tiktoken.encode(h["content"])
                    n = len(tokens)
                    nNbrToken += n
                    tokens = enc_tiktoken.encode(h["role"])
                    n = len(tokens)
                    nNbrToken += n
                print("nNbrToken sent: %s" % nNbrToken)
                #~ return
                
        
        try:
            completion = openai.ChatCompletion.create(
                              model="gpt-3.5-turbo",
                              messages=historicToUse,
                              temperature=0.2,
                              user=username,
                              max_tokens=nNbrMaxToken
                            )
        except BaseException as err:
            print("ERR: %s" % err)
            print("retrying in 1min...")
            time.sleep(60)
            completion = openai.ChatCompletion.create(
                          model="gpt-3.5-turbo",
                          messages=historic,
                          temperature=0.2,
                          user=username,
                          max_tokens=nNbrMaxToken
                        )
        
        print(completion)
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
