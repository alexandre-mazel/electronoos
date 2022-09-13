# -*- coding: cp1252 -*-

# catherine: 06.48.16.07.20

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
    perso = ["je","tu", "moi", "j'ai", "j'aime", "me", "te"] # ca me, ca te
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
    
    if nGene != 0:
        ratio = nPerso/nGene
    else:
        if nPerso == 0:
            ratio = 1.
        else:
            ratio = 666
    return ratio
    
# "moi je peux etre malade du virus, et pas toi." ca semble personnel et pourtant c'est une généralité.
# => erreur de codage
# la regle: si je peux remplacer je par "les humains" et "tu" par les robots.

s="si bah c'est normal pepper bleu c'est parce que nous la nuit on dort et à la fin de la journée quand on rentre on dort pour récupérer de la journée donc c'est ça qui fait la différence c'est que toi t'as pas besoin de dormir la nuit contrairement à nous."

    
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
    if nChangeDict == 2:
        bSeparated = True
        respi_list = ["je sais pas", "je ne sais pas"]
        #on a chopper par erreur: moins, moitié, respiratoire, obligatoire => ajout de l'option separated
    n = 0
    for sub in respi_list:
        n += count_substring(txt,sub,bSeparated)
    return n*100/len(txt) # 2 possibles: nbr lettre or nbr word ?
    #~ return n*100/len(txt.split())
            
    
#~ print("respi sample: %s%%" % getRespirationLexiqueRatio(txt_sample))
#respi sample: 0.9779951100244498%
#~ exit()

def getPolaRatio(txt):
    sumPola = 0
    cpt = 0
    import train_feelings
    list_answer = txt.split("\n")
    print("nbr answer: %s" % len(list_answer))
    for answer in list_answer: 
        sentences = answer.split(".")
        print("nbr sentences: %s" % len(sentences))
        for sentence in sentences:
            if len(sentence)>3:
                pola = train_feelings.classify(sentence)
                sumPola += pola
                cpt += 1
                print("getPolaRatio: cpt: %d, sumPola: %s" % (cpt,sumPola) )
    #~ return sumPola/cpt
    return sumPola # as pola is -1 1, sum is enough



def analyse():
    perso_c = perso_r = 0
    perso_j = perso_m = 0
    perso_1 = perso_2 = 0
    
    if 0:
        # pour valider les fonctions
        # cherche la phrase la plus forte et la moins bonne de toute la base
        vmin = 99999
        vmax = -9999
        smin = ""
        smax = ""
        for i,f in enumerate(listFiles):
            file = open(f+".txt","rt",encoding="cp1252")
            txt = file.read()
            file.close()
        
            lines = txt.split("\n")
            for s in lines:
                if len(s)<2:
                    continue
                v = getPerso(s)
                if v > vmax:
                    vmax = v
                    smax = s
                if v < vmin:
                    vmin = v
                    smin = s
        print("%.3f: %s" % (vmin,smin))
        print("%.3f: %s" % (vmax,smax))
        exit()
                

    for i,f in enumerate(listFiles):
        file = open(f+".txt","rt",encoding="cp1252")
        txt = file.read()
        file.close()
        
        nbrLine = len(txt.split("\n"))
        #~ print("%s: %d lines" % (f,nbrLine)) #tout le temps 20 lignes
        
        ratio = getPerso(txt) # change on control/respi: 1.14 jour/masque: 1.16 et q1/q2: 1.56 (q2: on voit que c'est un robot insensible et donc on repond plus générique?)
        
        #~ ratio = getRespirationLexiqueRatio(txt)
        # sur concept de respiration: control/respi: 0.29,  jour/masque: 0.00,  q1/q2: 1.17
        
        #~ ratio = getRespirationLexiqueRatio(txt,1)
        # sur concept de difference: control/respi: 1.11
        
        #~ ratio = getRespirationLexiqueRatio(txt,2)
        # sur concept de "je sais pas": control/respi: 0.8,  jour/masque: 2.38,  q1/q2: 1.15
        
        #~ ratio = getAdresse(txt) # no change but on q1/q2: 0.80 (q2 donne plus envie de l'interpeller?)
        
        
        #~ ratio = getPolaRatio(txt) # control/respi: 0.96,  jour/masque: 1.48,  q1/q2: 0.77 
        # pb: neutre => 0
        # => [bof, on a en fait que 20 para avec ~4 phrases par groupe, et donc c'est vite fait d'avoir des diff?] ?
        # diff pas flagrante et attention ratio trompeurs quand on est dans les negatifs!

#~ control: -79.00
#~ respira: -82.00
#~ ratio: 0.96

#~ jour: -96.00
#~ masque: -65.00
#~ ratio: 1.48

#~ q1: -70.00
#~ q2: -91.00
#~ ratio: 0.77
        
        
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
        #~ break
    # for each file - end
    print()
    
    print("control: %.2f" % (perso_c) )
    print("respira: %.2f" % (perso_r) )    
    print("ratio: %.2f (%.2f)" % ( (perso_c/perso_r), (perso_r/perso_c)) )
    print()
    
    print("jour: %.2f" % (perso_j) )
    print("masque: %.2f" % (perso_m) )   
    print("ratio: %.2f (%.2f)" % ( (perso_j/perso_m), (perso_m/perso_j) ) )
    print()    

    print("q1: %.2f" % (perso_1) )
    print("q2: %.2f" % (perso_2) )
    print("ratio: %.2f (%.2f)" % ( (perso_1/perso_2), (perso_2/perso_1)) )
    print()    
    
# analyse - end

# todo: polarité. stat des 3 mots les plus courants

    
analyse()