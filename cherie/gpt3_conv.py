# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import socket
import pickle 
import argparse

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

historic = [
#~ {"role": "system", "content": "Tu es un assistant dévoué programmé pour tenir compagnie a une personne agée."},
{"role": "system", "content": "Tu es un robot de compagnie d'une personne agée."},
#~ {"role": "system", "content": "Cette personne est une femme nommée Pierrette, elle a 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
#~ {"role": "system", "content": "Le mari de Pierrette, Jean est mort du cancer a l'age de 65 ans."},
{"role": "user", "content": "Je suis une femme nommée Pierrette, j'ai 82 ans, un enfant nommé Corto de 45 ans et une fille Gaia de 40 ans."},
{"role": "user", "content": "Mon mari Jean est mort du cancer a l'age de 65 ans."},
#~ {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié?"},
{"role": "user", "content": "Bonjour, comment va tu ? Suis je marié? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'après midi?"},
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
    {"role": "user", "content": "Bonjour, comment va tu ? Suis je marié? ais je des enfants ? quel jour sommes nous ? on est le matin ou l'après midi?"},
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
    
def loopDialog():
    while 1:
        msg = input("humain: ")
        msglo = msg.lower()
        if msglo in ["quit","bye"]:
            print("AI: a+")
            break
        historic.append({"role":"user","content":msg})
        print("l'ia réfléchit...\r",end="")
        completion = openai.ChatCompletion.create(
                          model="gpt-3.5-turbo",
                          messages=historic,
                          temperature=0.2,
                          user=username
                        )
        
        #~ print(completion.choices[0].message)
        print("AI: " + completion.choices[0].message["content"])
        historic.append(completion.choices[0].message)
        
    print(historic)
        
loopDialog()
