import datetime
import os
import sys
import time
import analyse_image_client

import pathlib
import requests


"""
Necessite analyse_image_serv.py running sur le serveur
"""

def getElectronoosPath():
    if os.name == "nt":
        strElectroPath = "C:/Users/"+os.getlogin()+"/dev/git/electronoos/"
        if not os.path.isdir(strElectroPath):
            strElectroPath = "c:/dev/git/electronoos/"
    else:
        if os.path.expanduser("~") == "/var/www": # from modpython
            strElectroPath = os.path.expanduser("/home/na/dev/git/electronoos/")
        else:
            if os.geteuid() == 0:
                strElectroPath = os.path.expanduser("/home/na/dev/git/electronoos/") # when started in root
            else:
                strElectroPath = os.path.expanduser("~/dev/git/electronoos/")
    return strElectroPath
        
sys.path.append( getElectronoosPath()+"alex_pytools/" )
import store_info_on_file


def getHourMin():
    dtn = datetime.datetime.now()
    return dtn.hour, dtn.minute
    
    
def inc_dic( d, k, inc_val = 1 ):
    if k in d:
        d[k] += inc_val
    else:
        d[k] = inc_val
    
def listdirrec( path ):
    o = []
    for f in sorted( os.listdir(path) ):
        absf = path + os.sep + f
        if os.path.isfile( absf ):
            o.append( absf )
        elif os.path.isdir( absf ):
            o.extend( listdirrec(absf) )
        # sinon: on fait rien sur les liens symbolique ou ...
    return o
    
cache_embed = None

def ollama_local_embed( s ):
    global cache_embed
    print("INF: ollama_local_embed: compute embedding for '%s'..." % s )
    if cache_embed == None:
        cache_embed = store_info_on_file.StoredInfo( "embed_qwen3-embedding" )
        cache_embed.load()
    emb = cache_embed.getDatas( s )
    if emb != None:
        return emb
        
    time_begin = time.time()
    strModel = "qwen3-embedding:latest"
    strUrl = "http://127.0.0.1:11434/api/embed"
    dOptions = { "temperature": 0, "seed": 42,"num_ctx": 4096 }
    dJson = { "model": strModel, "input": s, "stream": False, "options": dOptions}
    response = requests.post( strUrl, json=dJson, timeout=600 )
    print( response )
    embed = response.json()["embeddings"][0]
    duration  = time.time() - time_begin
    print( "embed len: %s" % len(embed) )
    print( "duration: %.2fs" % duration )
    cache_embed.storeDatas( s, embed )
    cache_embed.saveSometimes( 100 )
    return embed
    
if 1:
    ret = ollama_local_embed( "hello") # 0.75-0.95s on RPI5 sur hello
    #~ print( ret )
    exit(1)
    
def render_image( filename ):
    """
    return False si l'user veut quitter
    """
    if 0:
        import cv2
        cv2.imread(filename)
        cv2.imshow("gaia")
        cv2.waitKey(100)
        
    retvalue = True
    
    def close_image(event=None):
        nonlocal retvalue # global serait dans le module, hors ici on veut celle de la fonction du dessus
        retvalue = False
        #~ print( "DBG: close_image: retvalue False" )
        root.destroy()
        
    import tkinter as tk
    from PIL import Image, ImageTk
    import pathlib

    image = Image.open( filename ).convert("RGB")
    image.thumbnail((1200, 800))

    root = tk.Tk()
    root.title("Image Viewer")

    photo = ImageTk.PhotoImage(image)
    
    image_path = pathlib.Path(filename)

    title_text = f"{image_path.parent.parent.name}/{image_path.parent.name}/{image_path.name}"

    title = tk.Label(root, text=title_text, font=("Arial", 12, "bold"))
    title.pack(padx=5, pady=5)

    label = tk.Label(root, image=photo)
    label.pack()
    
    label.bind("<Button-1>", lambda event: root.destroy())
    root.bind("<Escape>", close_image)

    root.mainloop()
    
    #~ print( "DBG: render_image: returning: %s" % retvalue )
    return retvalue
    
def find_element( alist, list_to_find, bAnd, bComputePoint ):
    """
    find in alist if element of list_to_find are present.
    - bAnd: if set, all element of list_to_find must be present.
    - bComputePoint: give more point if found element are in start of list 
    
    return 0 if no match, or 1 or more if bComputePoint is set
    """
    if len(alist) < 1 or len(list_to_find) < 1:
        return 0
        
    pt = 0
    for e in list_to_find:
        try:
            idx = alist.index( e )
        except ValueError as err:
            if bAnd:
                return 0
            continue
            
        score = ( len(alist) - idx ) / len( alist )
        score += 1 / len(alist) # plus la liste est courte plus il y a un bonus
        pt += score
        
    return pt
    
    
def find( sentence, keywords, texts, peoples ):
    print( "INF: find: '%s', kw: %s, text: %s, peoples: %s" % (sentence, keywords, texts, peoples) )
    
    bRenderImage = 1
    #~ bRenderImage = 0
    
    out = [] # filename then nbr point
    
    
    stats_keyword = {}
    stats_text = {}
    stats_name = {}
    
    cache = store_info_on_file.StoredInfo( "img_desc_qwen2_5vl_7b_fr" )
    cache.load()
    d = cache.getAllDatas().items()
    
    if len(sentence) > 0:
        embed_sentence = ollama_local_embed( sentence )

    for filename,v in d:
        #~ print( "%s => %s" % (filename,str(v)) )
        s,ks,ts,ps = v
        found = False
        pts = 0
        
        if len(sentence) > 0 and len(s) > 0:
            v2 = ollama_local_embed( sentence )
            simi = numpy.dot( embed_sentence, v2 )
            

        if len(keywords) > 0:
            #~ print( "INF: find: filtering on keywords" )
            
            # les keyword semblent etre par ordre d'importance, on prend ca en compte
            
            if ks == []:
                continue
                
            pt = find_element( ks, keywords, True, False )
            if pt > 0:
                found = True
                pts += pt
            
        if len(peoples) > 0 and found:
            print( "INF: find: filtering on people" )
                
            if 0:
                # or
                for people in peoples:
                    if people in ps:
                        print( "found '%s' in '%s'" % (people, ps ) )
                        found = True
                        break
            else:
                # and
                if ps == []:
                    continue
                    
                for people in peoples:
                    if people not in ps:
                        break
                    print("found '%s' in '%s'" % (people, ps) )
                else:
                    found = True
                       
        # stats

        for k in ks:
            inc_dic( stats_keyword, k )
            
        for t in ts:
            inc_dic( stats_text, t )
            
        for p in ps:
            inc_dic( stats_name, p )
            
        if found:
            if 0:
                if bRenderImage and not render_image( filename ):
                    break
                
            out.append( (pts,filename) )

    # for each file - end
    
    print( "\nINF: find: nbr_find: %s / %s" % ( len( out ), cache.getNbrElement() ) )
    out = sorted( out, reverse=True )
    num = 0
    for pt,f in out:
        name = pathlib.Path(f).name
        print( "\n%4d: %.02f: %s" % (num,pt,name) )
        if 1:
                infos = cache.getDatas(f)
                print(infos)
        
        if bRenderImage and not render_image( f ):
            break
        num += 1
                
    print( "stats_keyword:" + str( sorted( filter(lambda x:x[1]>2,list(stats_keyword.items()) ), key=lambda x:-x[1] ) ) )
    print( "stats_text:" + str( sorted( filter(lambda x:x[1]>2,list(stats_text.items()) ), key=lambda x:-x[1] ) ) )
    print( "stats_name:" + str( sorted( list(stats_name.items()), key=lambda x:-x[1] ) ) )

def generate_desc_for_cloud( path ):
    """
    generate desc a fond, mais que de 21h a 23h30
    """
    allfiles = listdirrec(path)
    allfiles = sorted(allfiles)
    
    cache = store_info_on_file.StoredInfo( "img_desc_qwen2_5vl_7b_fr" ) # si on change le modele, il faudra changer ce nom de fichier!
    # TODO: avoir un moyen de demander au serveur le modele qu'il utilise et faire un assert
    cache.load()
    
    if 0:
        # test just un fichier pour tracker la fuite de vram:
        absf = "./files/alex/A52s/internal/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/IMG-20260919-WA0000.jpg"
        for i in range( 100 ): # J'ai force temporarirement dans le serveur un recalcul meme si dans le cache
            ret = analyse_image_client.send_image_to_analyse( absf, lang="fr" )
            print( "ret: " + str(ret) )
        return
    
    num_file = 0
    num_processed = 0
    num_error = 0
    while num_file < len(allfiles):
        h,m = getHourMin()
        if ( h < 21 or (h == 23 and m > 30) ) and 0:
            print( "sleeping...")
            time.sleep( 60*2 )
            continue
            
        absf = allfiles[num_file]
        
        print("%d/%d/%d/%d: '%s'" % (num_file,num_processed,num_error, len(allfiles), absf) )
        
        if not os.path.isfile( absf ):
            num_file += 1
            continue
            
        ext = os.path.splitext(absf)[1][1:].lower()
        # print( "DBG: ext: '%s'" % str(ext) )
        
        if ext not in ["jpg","jpeg","png","gif","bmp","pcx","tga","pcx"]:
            print( "INF: Skipping because of extension: '%s'" % ext )
            num_file += 1
            continue
            
        desc = cache.getDatas( absf )
        if desc != None:
            print( "INF: Skipping because already in cache: %s" % str(desc))
            num_file += 1
            continue
            
        ret = analyse_image_client.send_image_to_analyse( absf, lang="fr" )
        print(ret)
        if ret[0] == None: 
            print( "INF: Erreur dans l'analyse !?!" )
            num_error += 1
            num_file += 1
            continue
            
        cache.storeDatas( absf, ret )
        
        if 1:
            print("sleeping...")
            time.sleep(1.) # laisse le gpu respirer... (en fait on a deja 2s pour envoyer l'image alors bon...)(a cause d'un bug qu'on avait dans la resolution du dns)
        
        num_processed += 1
        if num_processed % 10 == 0:
            print( "Saving to %s ..." % cache.getSaveFileName() )
            cache.save()
        
        num_file += 1
        
    
    
    
    
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        generate_desc_for_cloud("files/")
    
    sentence = ""
    sentence = "geste avec les mains"
    
    keywords = []
    #~ keywords = ["arbres"]
    #~ keywords = ["robe","bleu"]
    
    texts = []
    
    peoples = []
    #~ peoples = ["Jc"] # que des gars qui sont pas Jc
    #~ peoples = ["Gaia","Alexandre"]
    
    find( sentence, keywords, texts, peoples)
    
    if cache_embed != None:
        cache_embed.save()