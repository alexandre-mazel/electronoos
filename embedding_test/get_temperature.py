# coding: cp1252
import sys
import os

sys.path.append("../camembert")
import sentence_embedding

global_loadedEmbedPosNeg = None

# a list of tagged reference,
# the idea if to find closer sentence and get it's positiveness
listPosNegRef = [
    # mettre a la fois des phrase a la premiere et troisieme personne, attention a bien les balancer
    # si une a la 3ieme, mettre son contraire aussi a la 3ieme
    ["super",1.],
    ["agréable",1.],
    ["c'est agréable",1.],
    ["c'est bien",0.6],
    ["c'est très bien",0.6],
    ["c'est bon",0.7],
    ["j'adore beaucoup",1.],
    ["j'adore",0.8],
    ["j'aime beaucoup",0.8],
    ["je kiffe",1.],
    #~ ["c'est génial",1.], # genere trop d'erreur: "c'est execrable" 0.32 et "c'est naze" 0.16 match directement la dessus en best a 0.37
    ["c'est du génie",1.],
    ["j'aime beaucoup",1.],
    #~ ["c'est appétissant",0.7], # trop orienté bouffe
    ["j'aime",0.8],
    ["moyen",0],
    ["passable",0],
    ["bof",-0.2],
    ["c'est insipide",-0.2],
    ["naze",-0.6],
    ["c'est naze",-0.6],
    ["pourri",-0.7],
    ["nul",-1.],
    ["c'est nul",-0.8],
    ["c'est très nul",-1.],
    ["c'est mauvais",-1.],
    ["exécrable",-1.],
    ["c'est exécrable",-1.],
    ["c'est execrable",-1.],
    ["c'est détestable",-1.],
    ["répugnant",-1.],
    ["c'est répugnant",-1.],
    ["dégoutant",-1.],
    ["c'est dégoutant",-1.],
    #~ ["c'est à vomir",-1.], # trop orienté bouffe
    ["je déteste",-1.],
    ["je n'aime pas du tout",-1.],
]

def loadPosNeg():
    global global_loadedEmbedPosNeg
    if global_loadedEmbedPosNeg !=  None:
        return global_loadedEmbedPosNeg
        
    bForceGeneration = 1
    #~ bForceGeneration = 0
    
    fn_embed = "posneg_embed_camembert.txt"
    if not os.path.isfile(fn_embed) or bForceGeneration:
        print("generating embedding to %s..." % fn_embed)
        listOnlyStr = [e[0] for e in listPosNegRef]
        #~ print(listOnlyStr)
        global_loadedEmbedPosNeg = sentence_embedding.camEmbedList( listOnlyStr )
        sentence_embedding.saveEmbed(fn_embed,global_loadedEmbedPosNeg)
    else:
       print("loading from %s..." % fn_embed)
       global_loadedEmbedPosNeg = sentence_embedding.loadEmbed(fn_embed)
    return global_loadedEmbedPosNeg

def getPosNeg(s,bVerbose=0):
    """
    return a float [-1,1] of the positivness of a sentence
    eg:
        - "C'est super" => 1.
        - "C'est trop nul" => -1.
    """
    bPrint = 1
    #~ bPrint = bVerbose
    
    s = s.replace(".","").replace("!","")
    embed = loadPosNeg()
    bests = sentence_embedding.getBests(s,embed,bVerbose=bVerbose,listWordForVerbose=listPosNegRef)
    if bPrint: print("DBG: getPosNeg: bests: %s" % bests)
    if bPrint: print("DBG: getPosNeg: refs: %s and %s" % (listPosNegRef[bests[0][0]],listPosNegRef[bests[1][0]]))
    imax = bests[0][0]
    simi = bests[0][1]
    conf = min(simi/0.36,1.)
    sref,vref = listPosNegRef[imax]
    if bPrint: print("# 1: getPosNeg: %s => %d: %s %.2f (conf: %.2f)" % (s,imax,sref,vref,conf ) )
    imax2 = bests[1][0]
    simi2 = bests[1][1]
    conf2 = min(simi2/0.36,1.)
    sref2,vref2 = listPosNegRef[imax2]
    if bPrint: print("# 2: getPosNeg: %s => %d: %s %.2f (conf: %.2f)" % (s,imax2,sref2,vref2,conf2 ) )
    
    if abs(vref-vref2)>0.8:
        if bPrint: print("WRN: getPosNeg: two different results, may be false!")
        conf *= 0.7 # apply a malus on conf
        return vref,conf
        
    
    # normally if we have enough example in our base, first and second will be both quite correct
    rCoefFirst = 1.
    rCoefFirst = 0.75
    rCoefFirst = 0.66
    rCoefFirst = 0.5
    vref = vref*rCoefFirst+vref2*(1-rCoefFirst)
    conf = conf*rCoefFirst+conf2*(1-rCoefFirst)
    if bPrint: print("# avg: getPosNeg: %s => %.2f (conf:%.2f)" % (s,vref,conf ) )
    return vref,conf
    
def autotest():
    
    bVerbose = 1
    bVerbose = 0
    
    al = [
             ["Je suis content",0.8],
             ["J'adore beaucoup",1.],
             ["J'adore",0.8],
             ["Nous adorons",0.8],
             ["Je kiffe",0.7],
             # 1: getPosNeg: Je kiffe => 9: je kiffe 1.00 (conf: 0.97)
             # 2: getPosNeg: Je kiffe => 15: bof -0.20 (conf: 0.80)
             
             ["Je kiffe ma race",0.7],
             # 1: getPosNeg: Je kiffe ma race => 9: je kiffe 1.00 (conf: 0.67)
             # 2: getPosNeg: Je kiffe ma race => 32: je déteste -1.00 (conf: 0.61)

             ["Je suis triste", -1.], # j'aurai aimé 0.2, mais c'est tres neg
             ["C'est nul ce truc",-0.5],
             ["J'aime pas du tout",-0.7],
             ["C'est vraiment pourri",-0.5],
             ["c'est naze",-0.8],
             ["C'est naze",-0.8],
             ["C'est naze.",-0.8],
             ["C'est naze!",-0.8],
             # j'ai enlevé le ! dans le getPosNeg, sinon ca matche avec "c'est bien", étonnant !
             # DBG:   1: getPosNeg: C'est naze! => 18: c'est naze -0.60 (conf: 0.99)
             # DBG:   2: getPosNeg: C'est naze! => 3: c'est bien 0.60 (conf: 0.73)
             ["C'est trop naze",-0.8],
             ["C'est très bien",0.8],
             ["C'est trop bien",0.8],
             ["C'etait vraiment naze",-0.8],
             ["C'est agréable",0.7],
             ["C'est génial",0.7],
             ["C'est exécrable",-0.8],
             ["J'adore les pois gourmands",0.8],
             ["J'aime les haricots verts",0.8],
             ["Je deteste les yaourts",-0.8],
             #~ ["On mange souvent des pates",0.], # hard to tell
             # DBG:   1: getPosNeg: On mange souvent des pates => 15: bof -0.20 (conf: 0.34)
             # DBG:   2: getPosNeg: On mange souvent des pates => 30: dégoutant -1.00 (conf: 0.32)
             ["Emmanuel Macron",0.],
             # 1: getPosNeg: Emmanuel Macron => 10: c'est du génie 1.00 (conf: 0.33)
             # 2: getPosNeg: Emmanuel Macron => 15: bof -0.20 (conf: 0.32)

             ["Michael Jacskon",0.8], # should be 0 but seem to be globally positive
             ["Mére Thérésa",-0.2], # why is neg?
             ["L'abbé Pierre",-0.2], # should ne positif but, output répugnant!
             ["Michael Francois",0.],
             ["Adolf Hitler",-0.8],
             ["Ben Laden",-0.8],
             ["nazi",-1.],
             
             ["Aimes-tu?",1.],
             # 1: getPosNeg: Aimes-tu? => 7: j'adore 0.80 (conf: 1.00)
             # 2: getPosNeg: Aimes-tu? => 12: j'aime 0.80 (conf: 1.00)
             
             ["Detestes-tu?",-1.],
             # 1: getPosNeg: Detestes-tu? => 33: je déteste -1.00 (conf: 1.00)
             # 2: getPosNeg: Detestes-tu? => 7: j'adore 0.80 (conf: 0.76)

             ["Et toi, aimes-tu?",1.],
             # 1: getPosNeg: Et toi, aimes-tu? => 7: j'adore 0.80 (conf: 1.00)
             # 2: getPosNeg: Et toi, aimes-tu? => 12: j'aime 0.80 (conf: 1.00)
             
             ["Et toi, detestes-tu?",-1.],
             # 1: getPosNeg: Et toi, detestes-tu? => 33: je déteste -1.00 (conf: 0.80)
             # 2: getPosNeg: Et toi, detestes-tu? => 9: je kiffe 1.00 (conf: 0.67)
             
             ["J'ai adoré ce restaurant",1.],
             ["J'ai pas aimé du tout cette pièce de théatre",-0.7],
        ]
        
    nCptError = 0
    nCptRealError = 0
    nCptErrorLowConf = 0
    rSumConfError = 0
    rSumConf = 0
    for s,r in al:
        print("\nINF: PosNeg for '%s':" % s)
        r2,conf = getPosNeg(s,bVerbose)
        rSumConf += conf
        rDiff = abs(r-r2)
        print(" => %s ref: %2f,  found: %.2f, diff: %.2f (conf: %.2f)" % (s,r,r2,rDiff,conf))
        if rDiff > 0.5:
            nCptError += 1
            if conf < 0.5:
                print("ERREUR avec faible conf\n")
                nCptErrorLowConf += 1
            else:
                print("!!! REELLE ERREUR !!!\n")
                nCptRealError+=1
            rSumConfError += conf
    
    if nCptError > 0:
        print("\nINF: nCptRealError: %d, nCptErrorLowConf: %d, ConfavgConfErreur: %.2f (rAvgConf:%.2f)" % (nCptRealError,nCptErrorLowConf,rSumConfError/nCptError,rSumConf/len(al)))
            
        # INF: nCptRealError: 0, nCptErrorLowConf 1, ConfavgConfErreur: 0.23  (rAvgConf:0.80)
        
if __name__ == "__main__":
    autotest()
