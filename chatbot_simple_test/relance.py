# -*- coding: cp1252 -*-
import os
import time
if os.name == "nt":
    from msvcrt import getche, getch, kbhit
else:
    from getch import getch, getche, kbhit
    
def chatbot_answer(user_input):
    if "bonjour" in user_input:
        return "Salut ca va ?"
    return "je n'ai pas compris"
    
def chatbot_run():
    timeRelance = time.time() + 5

    print("Je t'écoute...")
    question = ""
    while 1:
        if kbhit():
            c = getche()
            if( ord(c) != 13 ):
                question += c.decode('cp1252') # ou ansi
                timeRelance += 3
            else:
                print("Votre phrase: '%s'" % question )
                a = chatbot_answer(question)
                print(a)
                question = ""
        time.sleep(0.02)
        # gestion relance
        if time.time() > timeRelance:
            timeRelance = time.time() + 5
            print("Au fait, tu aimes les choux fleurs ?")
        
chatbot_run()