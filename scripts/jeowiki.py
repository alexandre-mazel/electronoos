import os
import sys
import random

sys.path.append("../openai_test") # TODO: clean it
import test_wikipedia

def jeowiki():
    listInfos = test_wikipedia.loadInfos("../data/wiki_knowledge_5100art.txt")
    listKeys = list(listInfos.keys())
    while 1:
        idx = random.randint(0,len(listInfos))
        title,suma = listInfos[listKeys[idx]]
        print(title)
        print(suma)
        idxest = suma.find('est')
        print("question:")
        print(suma[idxest+4:])
        key = input()
        if key == 27 or key == ord('q'):
            break
        
        
        
if __name__ == "__main__":
    jeowiki()