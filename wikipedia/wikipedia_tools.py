# -*- coding: cp1252 -*-
    
import json

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
    return data
    

def find(req):
    """
    find a wikipedia page best matching a sentences
    """
    fn = "wiki_knowledge.txt"
    listInfos = loadInfos(fn)
    
    
if __name__ == "__main__":
    find("actrice de cinéma")