# -*- coding: cp1252 -*-


listFiles = ["cj1","cj2","cm1","cm2","rj1","rj2","rm1","rm2"]



def getPerso(txt):
    """
    return ratio perso / genéralité
    """
    perso = ["je","tu"]
    general = ["on", "nous", "vous", "ils"]
    words = txt.split()
    nPerso = nGene = 0
    for w in words:
        #~ print(w)
        if w.lower() in perso:
            nPerso += 1
        if w.lower() in general:
            nGene += 1
    return nPerso/nGene


def analyse():
    perso_c = perso_r = 0
    perso_j = perso_m = 0
    perso_1 = perso_2 = 0
    
    for i,f in enumerate(listFiles):
        file = open(f+".txt","rt",encoding="cp1252")
        txt = file.read()
        perso = getPerso(txt)
        bControl = i < 4
        bJour = (i % 4) < 2
        bQuestion1 = (i % 2) < 1
        if bControl:
            perso_c += perso
        else:
            perso_r += perso         
            
        if bJour:
            perso_j += perso
        else:
            perso_m += perso  
            
        if bQuestion1:
            perso_1 += perso
        else:
            perso_2 += perso  
            
        print("%s: %.2f" % (f,perso) )
        file.close()
    
    print("control perso: %.2f" % (perso_c) )
    print("respira perso: %.2f" % (perso_r) )    

    print("jour perso: %.2f" % (perso_c) )
    print("masque perso: %.2f" % (perso_r) )    

    print("q1 perso: %.2f" % (perso_1) )
    print("q2 perso: %.2f" % (perso_2) )
    
# analyse - end
    
analyse()