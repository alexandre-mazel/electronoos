# -*- coding: cp1252 -*-
    
import json
import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import stringtools

def storeInfos(fn,data):
    print("INF: storeInfos: storing %d page(s)" % len(data))
    misctools.backupFile(fn)
    f = open(fn,"wt")
    f.write(json.dumps(data))
    f.close()


    
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
    first_article = list(data.keys())[0]
    print("DBG: loadInfos: first article len: %s" % len(data[first_article]))
    if len(data[first_article]) == 2:
        print("DBG: loadInfos: converting to new format")
        # conversion to new format: from (title,sum) to (title,categs,type,sum)
        for k,v in data.items():
            data[k] = [data[k][0],"","",data[k][1]]
    
    return data
    
def printPage(tuplePage):
    print("title: %s" % tuplePage[0])
    print("type: %s" % tuplePage[2])
    print("categ: %s" % tuplePage[1])
    print("summa: %s" % stringtools.removeAccentString(tuplePage[3]))
    
def createEmbedForPages(listInfos,versionname=""):
    sys.path.append("../camembert")
    import sentence_embedding
    # store key list, cause order can change
    
    fn_keylist = "generated/wiki_keylist%s.txt" % versionname
    if os.path.isfile(fn_keylist):
        f = open(fn_keylist,"rt")
        buf = f.read()
        listKeys = json.loads(buf)
        f.close()
    else:
        # need to be done at the same time than embedding!
        listKeys = list(listInfos.keys())
        f = open(fn_keylist,"wt")
        f.write(json.dumps(listKeys))
        f.close()
        
    list_title = [listInfos[x][0] for x in listKeys]
    list_sum = [listInfos[x][3] for x in listKeys]
    #~ print(list_title[:3])
    #~ print(stringtools.removeAccentString(list_sum[0]))
    embTitle = sentence_embedding.precomputeList(list_title,"generated/wiki_embed_title%s.txt" % versionname)
    embSum = sentence_embedding.precomputeList(list_sum,"generated/wiki_embed_summary%s.txt" % versionname)
    embSumPara = sentence_embedding.precomputeParagraph(list_sum,"generated/wiki_embed_summary_paragraph%s.txt" % versionname)
    
    return listKeys,embTitle,embSum,embSumPara
    

def find(req):
    """
    find a wikipedia page best matching a sentence
    """
    print("INF: find: '%s'" % req )
    sys.path.append("../camembert")
    import sentence_embedding
    versionname = ""
    versionname = "_maryline"
    versionname = "_5100art"
    fn = "wiki_knowledge%s.txt" % versionname
    listInfos = loadInfos(fn)
    if 0:
        # test one shot
        listKeys = list(listInfos.keys())
        list_sum = [listInfos[x][3] for x in listKeys]
        list_sum = stringtools.removeAccentString(list_sum[0]).replace('\n','.').split('.')
        print("list_sum: %s" % str(list_sum))
        for i,s in enumerate(list_sum):
            print("%d:%s" % (i,s))
        emb = sentence_embedding.camEmbedList(list_sum)
        for i,e in enumerate(emb):
            print("%d:%s" % (i,str(e[:5])))
        b = sentence_embedding.getBests(req,emb)
        print(b)
        (i1,sim1),(i2,sim2) = b
        print(stringtools.removeAccentString(list_sum[i1]))
        print(stringtools.removeAccentString(list_sum[i2]))
        emb = sentence_embedding.camEmbed(req)
        print("req: %s" % (str(emb[:5])))
        exit(1)
        
    listK,embTitle,embSum,embSumPara = createEmbedForPages(listInfos,versionname)
    for nEmbeddingUsed,emb in enumerate([embTitle,embSum,embSumPara]):
        print("*"*20)
        print("- %s:"% ["title", "summary", "summary among sentence"][nEmbeddingUsed])
        if nEmbeddingUsed==2:
            bests = sentence_embedding.getBestParagraphs(req,emb)
            idxBestSentence = bests[2]
            bests = bests[:2]
            
            nPara = bests[0][0]
            kPara = listK[nPara]
            txtPara = listInfos[kPara][3]
            print("nPara:%s" % nPara)
            print("kPara:%s" % kPara)
            print("txtPara:%s" % stringtools.removeAccentString(txtPara))
            if idxBestSentence>0:
                strBest = sentence_embedding.cutParagraphToSentences(txtPara)[idxBestSentence-1]
            else: 
                strBest = "(the average)"
            print("strBest: %s\n" % strBest  )
        else:
            bests = sentence_embedding.getBests(req,emb)
        #~ (i1,sim1),(i2,sim2) = bests
        print("find results: bests:%s" % str(bests))
        for best in bests:
            i,sim = best
            k = listK[i]
            print("k: %s" % k)
            printPage(listInfos[k])
            print("simi: %.2f\n" % sim)
            
# find - end

    
    
if __name__ == "__main__":
    #~ find("actrice de cinéma")
    #~ find("actrice, mannequin et chanteuse")
    find("actrice de cinéma blonde")
    #~ find("Elle se destine initialement au mannequinat avant d'etre reperee")
    #~ find("Elle se destine initialement au mannequinat avant d'etre reperee par Ben Lyon et de signer son premier contrat d'actrice avec la 20th Century Fox en aout 1946")