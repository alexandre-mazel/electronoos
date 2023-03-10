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

if 1:
    ny = wikipedia.page("New York")
    print("title: " + ny.title)
    print("url: " + ny.url)
    print(stringtools.removeAccentString(ny.content))
    print("link: " + stringtools.removeAccentString(str(ny.links)))
    exit(0)
    


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
    print("title: %s" % stringtools.removeAccentString(title) )
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
        if 1:
            # add categs et type (unfinished)
            categs = p.categories[:]
            #~ print(categs)
            i = 0
            while i < len(categs):
                # clean each categ
                categs[i] = categs[i].replace("Catégorie:", "")
                
                startCategToRemove = ["Article ", "Page pointant ", "Page utilisant ", "Bon article"]
                bFound = 0
                for startRemo in startCategToRemove:
                    #~ print("'%s'?"%categs[i][:len(startRemo)])
                    if categs[i][:len(startRemo)] == startRemo:
                        bFound = 1
                        break
                if bFound:
                    #~ print("=> match: '%s'" % categs[i] )
                    del categs[i]
                    continue
                #~ print("=> no match: '%s'"% categs[i])
                i += 1
            print(categs)
            typeGuess = {
                # en minuscule
                "Personnage": ["article biographique"],
                "Ville": ["unité urbaine","commune de france"],
                "Infrastructure": ["infrastructure"],
                "Monnaie": ["monnaie"],
                }
            
            type = ""
            bFound = 0
            for k,v in typeGuess.items():
                for match in v:
                    for categ in categs:
                        if match in categ.lower():
                            bFound = 1
                            break
                    if bFound: break
                if bFound: 
                    type = k
                    break
            print("type: '%s'" % type )
            listInfos[page_name] = (title,categs,type,sum)
            #~ exit(1)
        else:
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
            
        if nbr_added > 4000:
            break # enough for today (but we are in profoundeur d'abord donc on ne s'arrete jamais)
    return nbr_added
    
# retrieveInfoOnPage - end
    
if __name__ == "__main__":
    if 1:
        listInfos = dict() # page_name => title, categories, summary
        fn = "wiki_knowledge.txt"
        listInfos = loadInfos(fn)
        if 1:
            #~ retrieveInfoOnPage("Puissance (physique)")
            retrieveInfoOnPage("Maryline monroe")
            #~ retrieveInfoOnPage("Montpellier")
            #~ retrieveInfoOnPage("Le Plessis-Robinson")
            #~ retrieveInfoOnPage("Autoroute")
            #~ retrieveInfoOnPage("Dollar australien")
            storeInfos(fn,listInfos)
