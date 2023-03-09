# -*- coding: cp1252 -*-
    
import json
import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import stringtools

    
def loadInfos(fn):
    """
    format: listInfos[page_name] = (title,categs,type,sum)
    """
    try:
        f = open(fn,"rt")
        buf = f.read()
        data = json.loads(buf)
        if 0:
            print("DBG: loadInfos: converting...")
            # convert to numpy
            print("DBG: loadInfos: len data: %s" % len(data))
            print("DBG: loadInfos: len data[0]: %s" % len(data[0]))
            for i in range(3):
                print("DBG: loadInfos: type data0: %s" % type(data[0][i]))
                print("DBG: loadInfos: data0: %s" % str(data[0][i]))
            
            for j in range(len(data)):
                for i in range(len(data[j])):
                    data[j][i] = float(data[j][i])
        f.close()
    except FileNotFoundError as err:
        data = {}
        
    print("INF: loadInfos: loaded %d page(s)" % len(data))
    return data
    
def printPage(tuplePage):
    print("title: %s" % tuplePage[0])
    print("type: %s" % tuplePage[2])
    print("categ: %s" % tuplePage[1])
    print("summa: %s" % stringtools.removeAccentString(tuplePage[3]))
    
def createEmbedForPages(listInfos):
    sys.path.append("../camembert")
    import sentence_embedding
    list_title = [x[0] for x in listInfos.values()]
    list_sum = [x[3] for x in listInfos.values()]
    print(list_title[:3])
    print(stringtools.removeAccentString(list_sum[0]))
    embTitle = sentence_embedding.precomputeList(list_title,"wiki_embed_title.txt")
    embSum = sentence_embedding.precomputeList(list_sum,"wiki_embed_summary.txt")
    return embTitle,embSum
    

def find(req):
    """
    find a wikipedia page best matching a sentences
    """
    sys.path.append("../camembert")
    import sentence_embedding
    fn = "wiki_knowledge.txt"
    listInfos = loadInfos(fn)
    embTitle,embSum = createEmbedForPages(listInfos)
    bests = sentence_embedding.getBests(req,embTitle)
    #~ (i1,sim1),(i2,sim2) = bests
    for best in bests:
        i,sim = best
        k = list(listInfos.keys())[i]
        printPage(listInfos[k])
        print("simi: %.2f" % sim)

    
    
if __name__ == "__main__":
    find("actrice de cinéma")