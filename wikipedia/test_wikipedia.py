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
import wikipedia_tools

wikipedia.set_user_agent("AlmaBot/0.6 (http://human-machine-interaction.org; alexandre.mazel@human-machine-interaction.org)")

wikipedia.set_lang("fr")

if 0:
    ret = wikipedia.summary("francois miterrand", sentences=1)
    print(stringtools.removeAccentString(ret))

if 0:
    ny = wikipedia.page("New York")
    print("dir: " + str(dir(ny)))
    print("title: " + ny.title)
    print("url: " + ny.url)
    print("summary: " + stringtools.removeAccentString(ny.summary[:1000]+"...\n"))
    print("contents: " + stringtools.removeAccentString(ny.content[:1000]+"...\n"))
    print("link: " + stringtools.removeAccentString(str(ny.links[:10])+"..."))
    print("images: " + stringtools.removeAccentString(str(ny.images[:4])+"..."))
    exit(0)
    
if 0:
    # page that does not match test
    wikipedia.set_lang("en")
    
    page_name = "Billy Burke"
    p = wikipedia.page(page_name,auto_suggest =1)
    wikipedia_tools.printWikipediaPage(p)
    exit(0)
    

def hasNumber(s):
    return any(char.isdigit() for char in s)
    
def retrieveInfoOnPage( page_name, depth = 0 ):       
    """
    return nbr of page stored
    """
    nbr_added = 0
    bVerbose = 1
    #~ bVerbose = 0

    
    if depth > 1: # was 3 # 1 is great when going from a page like Lists_of_American_actors
        # too depth!
        splitted = page_name.split(" ")
        nbr_word = len(splitted)
        bLooksLikeFirstAndLastName = nbr_word == 2 and not "century" in page_name.lower() and not "BC" in page_name and not "AD" in page_name and not hasNumber(page_name)
        if not bLooksLikeFirstAndLastName or depth > 4: # on laisse un coup de plus si ca ressemble a un prenom
            print("%sDBG: retrieveInfoOnPage: nbr_word: %s (splitted:%s)" % ("\t"*depth,nbr_word,str(splitted) ))
            if bVerbose: print("%sDBG: retrieveInfoOnPage: page_name: '%s' => too depth (%d)" % ("\t"*depth, page_name, depth) )
            return nbr_added
    
    if depth > 0 and page_name in listInfos:
        print("%sINF: retrieveInfoOnPage: already in list: page_name: '%s'" % ("\t"*depth,page_name ) )
        return nbr_added
    
    print("%sDBG:page_name: %s" % ("\t"*depth,stringtools.removeAccentString( page_name)) )
    try:
        p = wikipedia.page(page_name,auto_suggest =0)
    except KeyboardInterrupt as err:
        print("WRN: retrieveInfoOnPage: keyboard interrupt: %s" % str(err))
        exit(-1)
    except BaseException as err:
        # various problem
        print("WRN: retrieveInfoOnPage: exception occurs: %s" % str(err))
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
            # no categ
            listInfos[page_name] = (title,sum)
        if 1:
            # save all images
            import nettools
            try:
                listImages = p.images
                for link_image in listImages:
                    fn = os.path.basename(link_image)
                    name,ext = os.path.splitext(fn)
                    if ext.lower() not in [".jpg",".jpeg",".png"]:
                        continue
                    name = name[:110]
                    fn = name + ext
                    fn_dst = "stored_images/"+page_name+"__"+fn
                    print("DBG: retrieveInfoOnPage: saving image '%s' to '%s'..." % (fn,fn_dst))
                    if os.path.isfile(fn_dst):
                        print("DBG: retrieveInfoOnPage: image already in dst")
                    else:
                        nettools.download(link_image,fn_dst)
                        time.sleep(0.3)
            except KeyError as err:
                print("WRN: retrieveInfoOnPage: KeyError: err: %s" % err )
                pass
            
            
        if len(listInfos) % 100 == 0:
            wikipedia_tools.storeInfos(fn,listInfos)
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
        try:
            time.sleep(0.01)
            nb = retrieveInfoOnPage(l,depth=depth+1)
        except BaseException as err:
            print("WRN: Received exception in sub retrieve on '%s', err: '%s'" % (l,str(err)))
            time.sleep(0.4)
            nb = 0
            if(str(err)=="-1"):
                print("INF: user want to quit...")
                exit(-2)
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
        listInfos = wikipedia_tools.loadInfos(fn)
        if 1:
            #~ retrieveInfoOnPage("Puissance (physique)")
            #~ retrieveInfoOnPage("Maryline monroe")
            #~ retrieveInfoOnPage("Montpellier")
            #~ retrieveInfoOnPage("Le Plessis-Robinson")
            #~ retrieveInfoOnPage("Autoroute")
            #~ retrieveInfoOnPage("Dollar australien")
            wikipedia.set_lang("en")
            #~ retrieveInfoOnPage("List_of_American_film_actresses")
            #~ retrieveInfoOnPage("List_of_American_television_actresses")
            retrieveInfoOnPage("List_of_French_actors")
            wikipedia_tools.storeInfos(fn,listInfos)
