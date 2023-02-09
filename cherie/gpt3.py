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
start_chat_log = '''Human: Hello, who are you?
AI: I am doing great. How can I help you today?
'''
chat_log = None
completion = openai.Completion()
def ask(question, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    prompt = f'{chat_log}Human: {question}\nAI:'
    response = completion.create(
        prompt=prompt, engine="davinci", stop=['\nHuman'], temperature=0.9,
        top_p=1, frequency_penalty=0, presence_penalty=0.6, best_of=1,
        max_tokens=100)
    answer = response.choices[0].text.strip()
    return answer
    
def append_interaction_to_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    return f'{chat_log}Human: {question}\nAI: {answer}\n'


def interact(q):
    global chat_log
    print("ques: %s" % q )
    answ=ask(q,chat_log)
    chat_log = append_interaction_to_chat_log(q ,answ, chat_log)
    print("answ: %s" % answ)
    return answ
    
while 1:
    s = input("?")
    interact(s)

interact("hello !")
interact("how are you?")
interact("my name is alexandre, and you?")
interact("what time is it?")
interact("do you know me?")
interact("what is my name?")
if 0:
    interact("parle moi en francais!")
    interact("Mon fils s'appelle Rodrigue!")
    interact("c’est une énorme caractéristique des espagnols: il n’est pas courageux, il ne veut pas dire en face ce qu’il pense qui ne fera pas plaisir. Il attend que tu t’épuise, en réalité je t’ai plus blessé dans les actes. Comme un mec ou une nana qui n’a plus envie de vivre avec l’autre mais qui n’ose pas le dire. Evite la scène de la confession. Peur de mettre des mauvaises notes aux élèves. Achete la paix. Je sais qu’il ne pourra pas etre heureux. Il se rend compte qu’il se fait chier avec les espagnols, pas assez bête pour se contenter d’une vie tapas, vinho et cerveza.")
    interact("Je me souviens plus, ais je des enfants?")
    interact("que sais tu de Rodrigue?")
    interact("As tu manger des oeufs de boeuf?")
interact("I have a son nammed Rodrigue!")
interact("He's selfish, do you think it's a good person?")
interact("He live in spain, and speaks a lot")
interact("Today the wheather is great.")
interact("Please tell me what you know about Rodrigue")
interact("I have also a daughter nammed Natalia.")
interact("Do you remember if i have children?")
interact("Are you sure that's all?")
interact("I feel alone, could you help me?")


exit(0)
        
parser=argparse.ArgumentParser()
parser.add_argument("port", help="server port", type=int, default="4000")


args=parser.parse_args()

port = args.port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(),port))
while(True):
    msg=s.recv(1024)
    msg=msg.decode()
    if(len(msg)>0):
        if(msg=="exit"):
            break
        answ=ask(msg,chat_log)
        chat_log = append_interaction_to_chat_log(msg ,answ, chat_log)
        print(answ)
        s.send(answ.encode())
  
  