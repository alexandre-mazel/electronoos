import datetime
import os
import sys
import time
import analyse_image_client

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
        
        if 0:
            print("sleeping...")
            time.sleep(0.5) # laisse le gpu respirer... (en fait on a deja 2s pour envoyer l'image alors bon...)(a cause d'un bug qu'on avait dans la resolution du dns)
        
        num_processed += 1
        if num_processed % 10 == 0:
            print( "Saving to %s ..." % cache.getSaveFileName() )
            cache.save()
        
        num_file += 1
        
    
    
    
    
    

if __name__ == "__main__":
    generate_desc_for_cloud("files/")