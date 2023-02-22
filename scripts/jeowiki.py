# -*- coding: cp1252 -*-
import os
import sys
import random
import time

sys.path.append("../openai_test") # TODO: clean it
import test_wikipedia

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

def jeowiki():
    listInfos = test_wikipedia.loadInfos("../data/wiki_knowledge_5100art.txt")
    listKeys = list(listInfos.keys())
    listLetter = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    #~ nbrChoice = 5
    #~ nbrChoice = 10
    nbrChoice = 20
    while 1:
        idx = random.randint(0,len(listInfos))
        title,suma = listInfos[listKeys[idx]]
        if 0:
            print(title)
            print(suma)
        idxest = suma.find(' est ')
        if idxest != -1 and idxest < 80:
            suma = suma[idxest+5:]
        suma = suma.replace(title, "mememe")
        suma = suma.replace(title.lower(), "mememe")
        maxlen = 400
        if len(suma)>maxlen:
            suma = suma[:maxlen] + "..."
        print("\nla reponse est:")
        print(suma)
        print("\nproposition:")
        order = misctools.shuffle(list(range(nbrChoice)),nbrChoice)
        aliens = []
        for i in range(nbrChoice-1):
            aliens.append(random.randint(0,len(listInfos)))
        good_ans = 'z'
        for numQ,numAns in enumerate(order):
            if numAns == 0:
                title_ans = title
                good_ans = listLetter[numQ]
            else:
                title_ans = listInfos[listKeys[aliens[numAns-1]]][0]
            end = "\t"
            if (numQ % 2) == 1:
                end = "\n"
            print("%s: %-40s" % (listLetter[numQ],title_ans),end=end)
        key = input("Votre reponse?\n")
        if key == good_ans:
            print("Bonne réponse !")
        else:
            print("Ha dommage!")
            print("La bonne réponse était: %s: %s" % (good_ans,title))
        time.sleep(2)
        if key == 27 or key == ord('q'):
            break
        
        
        
if __name__ == "__main__":
    jeowiki()