import numpy as np

dictInfSup = {} # for each model it's inf/sup


def getNormalisation( strModel ):
    inf,sup = dictInfSup[strModel]
    return sup-inf


def computeMaximum( strModel ):
    """
    Compute maximum of a model (so we could normalise it later)
    """
    if 0:
        # on regarde les evolutions entre les valeurs des vecteurs
        txts = ["Hello boys, how are you?", "Comment tu va?", "Les chaussettes de l'archi duchesse sont elle seche ?", "2+2=4"]
        inf = 2**32
        sup = -2**32
        for txt in txts:
            v = llama3_embedding( txt, strModel )
            inf = min( inf,min(v) )
            sup = max( sup, max(v) )
        print( "DBG: computeMaximum for model '%s': inf: %.3f, sup: %.3f" % (strModel, inf, sup) )
        dictInfSup[strModel] = (inf,sup)
    else:
        # on regarde la similitude max entre 2 phrases données
        pair_sentences = [
                ("J'ai froid", "je me caille"),
                ( "I'm hungry", "I'm starving")
        ]
        maxi = 0
        for t1, t2 in pair_sentences:
            simi = compare_two_texts( t1, t2, strModel )
            if simi > maxi:
                maxi = simi
        dictInfSup[strModel] = (0,maxi)

def llama3_embedding(text, strModel ):
    #~ print( "INF: llama3_embedding: using model: '%s'" % strModel )
    import ollama # to be run from ~/dev/llama_env + ollama server running internally
    
    out  = ollama.embeddings( model=strModel, prompt=text )
    #~ print(out)
    return out['embedding']
    
if 0:  
    # use camembert to compare results
    print("Using Camembert (size: 512)")
    import sys
    sys.path.append("../camembert/")
    import sentence_embedding
    def llama3_embedding(text):
        return sentence_embedding.camEmbed(text)
    

def computeDistance(v1,v2):
    #~ sum = 0
    #~ for i in range(len(v1)):
        #~ sum += abs(v1-v2)
        
    dist = np.linalg.norm(np.array(v1)-np.array(v2))
    return dist
    
    
def compare_two_vect( v1, v2 ):
    simi = np.dot(v1,v2)
    return simi
        

def compare_two_texts(t1,t2, strModel ):
    v1 = llama3_embedding(t1, strModel )
    v2 = llama3_embedding(t2, strModel )
    simi = np.dot(v1,v2)
    print("'%s'  and  '%s'  => %s" % (t1,t2,simi) )
    return simi
    
def compare_all(listText):
    allv = []
    for t in listText:
        v = llama3_embedding(t)
        allv.append(v)
    
    for j,t1 in enumerate(listText):
        simi_maxi = 0
        imaxi = 0
        simi_maxi2 = 0 # 2nd best
        imaxi2 = 0
        for i,t2 in enumerate(listText):
            if t1 == t2:
                continue
            #~ simi = np.dot(allv[i],allv[j])
            #~ simi = 100-computeDistance(allv[i],allv[j])  # seems to return quite same results
            simi = cosine_similarity([allv[i]],[allv[j]])[0][0]
            #~ print(type(simi))
            #~ print(simi.shape)
            #~ print("  simi: %.2f for %s and %s" % (simi,t1,t2) )
            if simi > simi_maxi:
                simi_maxi2 = simi_maxi
                imaxi2 = imaxi
                simi_maxi = simi
                imaxi = i
            elif simi > simi_maxi2:
                simi_maxi2 = simi
                imaxi2 = i
        print("Similar to '%s'  is  '%s'  with score %.2f" % (t1,listText[imaxi],simi_maxi) )
        print("   2nd: is '%s'  with score %.2f (%.1f%%)" % (listText[imaxi2],simi_maxi2,simi_maxi2*100/simi_maxi) )
        print("")
