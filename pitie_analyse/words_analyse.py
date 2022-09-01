# -*- coding: cp1252 -*-


listFiles = ["cj1","cj2","cm1","cm2","rj1","rj2","rm1","rm2"]
txt_sample = "euh bah y a un temps de repos qui est nécessaire dans la vie euh on va dire biologique et même machinique je pense euh c'est bien d'avoir un temps de repos après une journée bien remplie et donc parfois on s'ennuit  mais c'est parfois du bon ennui et je pense que c'est nécessaire pour être en pleine forme et pour reprendre une bonne journée après avec ce qu'on a à faire et ce qu'on veut faire surtout voila"


def count_substring(s,sub, bSeparated=False):
    """
    count how much time are sub in s
    """
    if 1:
        bVerbose=1
        #~ bVerbose=0
        n = 0
        while 1:
            i = s.find(sub)
            if i == -1:
                return n

            bOk = False
            if not bSeparated:
                bOk = True
            else:
                sepa = [" ", ",", ".", ";", "'","-","\n"]
                if      ( i==0 or s[i-1] in sepa ) \
                    and ( i+len(sub)>=len(s) or s[i+len(sub)] in sepa ) \
                :
                    bOk = True
                else:
                    if bVerbose: 
                        start = max(0,i-10)
                        print("DBG: count_substring: '%s' and '%s'   <= pas separated" % (sub, s[start:i+len(sub)+10].replace("\n","N")) )
            if bOk:
                n += 1
                if bVerbose: 
                    start = max(0,i-10)
                    print("DBG: count_substring: '%s' and '%s'" % (sub,s[start:i+len(sub)+10].replace("\n","N")) )
            s = s[i+len(sub):]
        return -1
    return s.count(sub)  # faster ? (i guess) mais pas autant de maitrise

def getPerso(txt):
    """
    return ratio perso / genéralité
    """
    bVerbose = 1
    bVerbose = 0
    txt = txt.lower()
    perso = ["je","tu", "moi", "j'ai", "j'aime"]
    general = ["on", "nous", "vous", "ils"]
    general_sub = ["je pense"] # pb: Sophie dit que "je pense" c'est du générique
    words = txt.split()
    nPerso = nGene = 0
    for w in words:
        #~ print(w)
        if w in perso:
            if bVerbose: print("perso: " + w)
            nPerso += 1
        if w in general:
            if bVerbose: print("gene: " + w)
            nGene += 1
            
    if 1:
        # add substring
        for sub in general_sub:
            nGene += count_substring(txt,sub)
    return nPerso/nGene
    
def getAdresse(txt):
    """
    return percentage of adressage a la personne en face
    """
    bVerbose = 1
    bVerbose = 0
    txt = txt.lower()
    perso = ["tu", "toi","pepper"] # et te ?
    words = txt.split()
    nCount = nGene = 0
    for w in words:
        #~ print(w)
        if w in perso:
            if bVerbose: print("addresse: " + w)
            nCount += 1
    return nCount/len(txt)

#~ print("perso sample: %s" % getPerso(txt_sample))
# perso sample: 0.5

#~ exit()

def getRespirationLexiqueRatio(txt,nChangeDict=0):
    bVerbose = 1
    bVerbose = 0
    txt = txt.lower()
    bSeparated = True
    #~ respi_list = ["respi", "inspi", "souffle", "étouff", "air", "oxyg", "etouff"] # avec not separated, mais choppe faire quand air, bad!
    respi_list = ["respire", "respires", "respiratoire", "respiratoires", "respirer", "inspi", "souffle", "étouffer", "air", "oxyg", "etouff"] # avec not separated, mais choppe faire quand air, bad!
    if nChangeDict == 1:
        bSeparated = True
        respi_list = ["différence", "different", "differente", "différent", "différents","différente", "différentes", "toi", "moi", "contrairement à toi"] # indique la différence mais va compter: on n'est pas différent comme 1, args!
        #on a chopper par erreur: moins, moitié, respiratoire, obligatoire => ajout de l'option separated
    n = 0
    for sub in respi_list:
        n += count_substring(txt,sub,bSeparated)
    return n*100/len(txt) # 2 possibles: nbr lettre or nbr word ?
    #~ return n*100/len(txt.split())
            
    
#~ print("respi sample: %s%%" % getRespirationLexiqueRatio(txt_sample))
#respi sample: 0.9779951100244498%
#~ exit()



def analyse():
    perso_c = perso_r = 0
    perso_j = perso_m = 0
    perso_1 = perso_2 = 0
    
    for i,f in enumerate(listFiles):
        file = open(f+".txt","rt",encoding="cp1252")
        txt = file.read()
        file.close()
        
        nbrLine = len(txt.split("\n"))
        #~ print("%s: %d lines" % (f,nbrLine)) #tout le temps 20 lignes
        
        #~ ratio = getPerso(txt) # change on jour/masque: 1.26 et q1/q2: 1.65
        
        #~ ratio = getRespirationLexiqueRatio(txt)
        # sur concept de respiration: control/respi: 0.33,  jour/masque: 0.04,  q1/q2: 1.09
        
        #~ ratio = getRespirationLexiqueRatio(txt,1)
        # sur concept de difference: control/respi: 1.10
        
        ratio = getAdresse(txt) # no change but on q1/q2: 0.81
        
        
        bControl = i < 4
        bJour = (i % 4) < 2
        bQuestion1 = (i % 2) < 1
        if bControl:
            perso_c += ratio
        else:
            perso_r += ratio         
            
        if bJour:
            perso_j += ratio
        else:
            perso_m += ratio  
            
        if bQuestion1:
            perso_1 += ratio
        else:
            perso_2 += ratio  
            
        print("%s: %.2f" % (f,ratio) )
        
        if 0:
            print("\n%s: words:" % f)
            # 3 mots les plus fréquents
            from collections import Counter
            cnt = Counter(txt.lower().split())
            n = 0
            #~ print(cnt)
            for word, freq in sorted(cnt.items(),key=lambda x: x[1],reverse=True):
                if len(word)<4:
                    continue
                if word in ["c'est","donc","mais","pour", "parce", "dans", "alors", "voila", "voilà", "quand"]:
                    continue
                print("  %s:%s" % (word,freq))
                n += 1
                if n > 10:
                    break
            print("")
    
    print()
    
    print("control: %.2f" % (perso_c) )
    print("respira: %.2f" % (perso_r) )    
    print("ratio: %.2f" % (perso_c/perso_r))
    print()
    
    print("jour: %.2f" % (perso_j) )
    print("masque: %.2f" % (perso_m) )   
    print("ratio: %.2f" % (perso_j/perso_m))
    print()    

    print("q1: %.2f" % (perso_1) )
    print("q2: %.2f" % (perso_2) )
    print("ratio: %.2f" % (perso_1/perso_2))
    print()    
    
# analyse - end

# todo: polarité. stat des 3 mots les plus courants

    
analyse()