# coding: cp1252

import os
import json
import time
import sentence_transformers
#~ from scipy.spatial.distance import cdist
import numpy as np

print("INF: sentence_transformers: loading distiluse...")
print("WRN: don't know where is locally stored the used base!!!")
timeBegin = time.time()
model = sentence_transformers.SentenceTransformer('distiluse-base-multilingual-cased')
print("INF: sentence_transformers: loading distiluse - end (loaded in %.2fs)" % (time.time()-timeBegin))


def camEmbed(s):
    o = model.encode(s, show_progress_bar=False)
    #~ print("DBG: camEmbed: '%s' => %s" % (s,str(o)))
    # transform the nd_array en list:
    #~ print(type(o))
    #~ print(type(o[0]))
    #~ print(type(o[0][0]))
    
    o = o.tolist()
    
    #~ print("apres:")
    #~ print(type(o))
    #~ print(type(o[0]))
    #~ print(type(o[0][0]))

    return o

def camEmbedList(list_s):
    #~ o = model.encode(s, show_progress_bar=False)
    #~ print("DBG: camEmbed: '%s' => %s" % (s,str(o)))
    #~ return o
    return camEmbed(list_s)
    
def getSimiSentences(s1,s2):
    e1,e2 = camEmbedList([s1,s2])
    return np.dot(e1,e2)
    
def saveEmbed(fn,data):
    f = open(fn,"wt")
    f.write(json.dumps(data))
    f.close()
    
def loadEmbed(fn):
    f = open(fn,"rt")
    buf = f.read()
    data = json.loads(buf)
    if 0:
        print("DBG: loadEmbed: converting...")
        # convert to numpy
        print("DBG: loadEmbed: len data: %s" % len(data))
        print("DBG: loadEmbed: len data[0]: %s" % len(data[0]))
        for i in range(3):
            print("DBG: loadEmbed: type data0: %s" % type(data[0][i]))
            print("DBG: loadEmbed: data0: %s" % str(data[0][i]))
        
        for j in range(len(data)):
            for i in range(len(data[j])):
                data[j][i] = float(data[j][i])
    f.close()
    return data
    
def precomputeList(list_s,filenametostore):
    if not os.path.isfile(filenametostore):
        print("generating embedding to %s..." % filenametostore)
        embedList = camEmbedList( list_s )
        saveEmbed(filenametostore,embedList)
    else:
       print("loading from %s..." % filenametostore)
       embedList = loadEmbed(filenametostore)
       if len(embedList) != len(list_s):
           print("WRN: camPrecomputeList: file '%s' not up to date ? (contains: %d and asked: %d)" % (len(embedQ),len(list_s)) )
    return embedList
    
def getBests(s,listEmbed):
    """
    find best simi between a sentence and a list of already computing embedding.
    return the index in the list, and the simi
    """
    simiMax = 0
    imax = -1
    simiMax2 = 0
    imax2 = -1
    e = camEmbed(s)
    for i,v in enumerate(listEmbed):
        simi = np.dot(e,v)
        if simi > simiMax:
            simiMax2 = simiMax
            imax2 = imax
            simiMax = simi
            imax = i
        elif simi > simiMax2:
            simiMax2 = simi
            imax2 = i
            
    return [(imax,simiMax),(imax2,simiMax2)]

def autotest():
    tresh = 0.4
    simi = getSimiSentences("Bonjour tout le monde", "Salut la foule")
    print("simi1: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.55) # 0.59
    
    # dès qu'on a de l'anglais, ca fait un *2 sur la similarity
    simi = getSimiSentences("Bonjour tout le monde", "Hello everybody")
    print("simi2: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.9) # 0.97
    
    simi = getSimiSentences("Bonjour tout le monde", "Le président de la république s'appelle Jacques Chirac")
    print("simi3: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.1) # 0.06

    simi = getSimiSentences("Bonjour tout le monde", "The president of the united states is Barack Obama")
    print("simi4: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.2) # 0.03

    simi = getSimiSentences("J'aime le beurre président", "The president of the united states is Barack Obama")
    print("simi5: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.4)  # 0.33

    simi = getSimiSentences("J'aime le beurre président", "Le président de la république s'appelle Jacques Chirac")
    print("simi6: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.3) # 0.25
    
    simi = getSimiSentences("Qui est le président du pays?", "Le président de la république s'appelle Jacques Chirac")
    print("simi7: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.4) # 0.40
    
    simi = getSimiSentences("Le gras c'est bon", "J'aime le beurre président")
    print("simi8: %.2f" % simi)
    #~ assert(simi>tresh) # ne fonctionne pas
    assert(simi<0.3) # 0.26 (dommage)

    simi = getSimiSentences("Fat is good", "I like butter")
    print("simi9: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.4) # 0.47 (mieux)

    simi = getSimiSentences("J'ai 2 enfants", "J'ai faim")
    print("simi10: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.4) # 0.27
    
    simi = getSimiSentences("J'ai 2 enfants", "I'm hungry")
    print("simi11: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.4) # 0.28
    
    simi = getSimiSentences("I have two kids", "I'm hungry")
    print("simi12: %.2f" % simi)
    assert(simi<tresh)
    assert(simi<0.4) # 0.29
    
    simi = getSimiSentences("I have two kids", "J'ai des enfants")
    print("simi13: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.6) # 0.64
    
    simi = getSimiSentences("I have two kids", "Je n'ai pas d'enfants")
    print("simi14: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.5) # 0.58
    
    simi = getSimiSentences("J'ai des enfants", "Je n'ai pas d'enfants")
    print("simi15: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.5) # 0.55
    
    simi = getSimiSentences("J'ai 1 enfant", "J'ai 2 enfants")
    print("simi16: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.5) # 0.68
    
    simi = getSimiSentences("J'ai 1 enfants", "J'ai 2 enfants")
    print("simi17: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.5) # 0.74
    
    simi = getSimiSentences("J'ai un garcon et une fille", "J'ai 2 enfants")
    print("simi18: %.2f" % simi)
    assert(simi>tresh)
    assert(simi>0.4) # 0.45 (bof)
    
if __name__ == "__main__":
    autotest()