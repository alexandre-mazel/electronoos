# -*- coding: cp1252 -*-

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import stringtools

import time


import wikipedia # pip install wikipedia

wikipedia.set_lang("fr")

if 0:
    ret = wikipedia.summary("francois miterrand", sentences=1)
    print(stringtools.removeAccentString(ret))

if 0:
    ny = wikipedia.page("New York")
    print("title: " + ny.title)
    print("url: " + ny.url)
    print(stringtools.removeAccentString(ny.content))
    print("link: " + stringtools.removeAccentString(str(ny.links)))
    
    
if 1:
    # creation d'une base de données
    import json
    
    def storeInfos(fn,data):
        print("INF: storeInfos: storing %d page(s)" % len(data))
        misctools.backupFile(fn)
        f = open(fn,"wt")
        f.write(json.dumps(data))
        f.close()
        
    def loadInfos(fn):
        try:
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
        except FileNotFoundError as err:
            data = {}
            
        print("INF: loadInfos: loaded %d page(s)" % len(data))
        return data
        
    listInfos = dict() # page_name =>title, summary
    fn = "wiki_knowledge.txt"
    listInfos = loadInfos(fn)
    
    def retrieveInfoOnPage( page_name, depth = 0 ):       
        """
        return nbr of page stored
        """
        nbr_added = 0

            
        if depth > 3:
            # too depth!
            return nbr_added
            
        
        if depth > 0 and page_name in listInfos:
            print("INF: retrieveInfoOnPage: already in list: page_name: '%s'" % page_name )
            return nbr_added
        
        print("page_name: %s" % stringtools.removeAccentString( page_name))
        try:
            p = wikipedia.page(page_name)
        except:
            # various problem
            return nbr_added
            
        title = p.title
        print("title: %s" % title)
        sum = p.summary.strip().strip("\n")
        if len(sum) < 4:
            return nbr_added
            
        for k,v in listInfos.items():
            if v[0] == title:
                print("already in base")
                break
        else:            
            print( "sum: %s" % stringtools.removeAccentString(sum) )
            # really adding to the list
            listInfos[page_name] = (title,sum)
            if len(listInfos) % 100 == 0:
                storeInfos(fn,listInfos)
            nbr_added += 1
        
        #~ print( p.links )
        for l in p.links:
            l = str(l)
            if "(homonymie)" in l:
                continue
            if "API" in l and len(l)<6:
                continue
            if len(l)<5: # 1885, .eu, ...
                continue
            if l in  [".de",".eu",".en"]:
                continue
            nb = retrieveInfoOnPage(l,depth=depth+1)
            if nb > 0: 
                nbr_added += nb
                print("nbr_added: %s" % nbr_added )
                time.sleep(0.2) # give some time to server...
                
            if nbr_added > 1000:
                break # enough for today (but we are in profoundeur d'abord donc on ne s'arrete jamais)
        return nbr_added
        
    retrieveInfoOnPage("Puissance (physique)")
    storeInfos(fn,listInfos)
