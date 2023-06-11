# coding: cp1252
import sys
import os

sys.path.append("../camembert")
import sentence_embedding

global_loadedEmbedPosNeg = None

# a list of tagged reference,
# the idea if to find closer sentence and get it's positiveness
listPosNegRef = [
    ["super",1.],
    ["agréable",1.],
    ["j'adore",1.],
    ["j'aime trop",1.],
    ["j'aime",0.8],
    ["moyen",0],
    ["passable",0],
    ["bof",-0.2],
    ["naze",-0.6],
    ["c'est naze",-0.6],
    ["pourri",-0.7],
    ["nul",-1.],
    ["exécrable",-1.],
    ["répugnant",-1.],
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
        global_loadedEmbedPosNeg = sentence_embedding.camEmbedList( listOnlyStr )
        sentence_embedding.saveEmbed(fn_embed,global_loadedEmbedPosNeg)
    else:
       print("loading from %s..." % fn_embed)
       global_loadedEmbedPosNeg = sentence_embedding.loadEmbed(fn_embed)
    return global_loadedEmbedPosNeg

def getPosNeg(s):
    """
    return a float [-1,1] of the positivness of a sentence
    eg:
        - "C'est super" => 1.
        - "C'est trop nul" => -1.
    """
    embed = loadPosNeg()
    bests = sentence_embedding.getBests(s,embed)
    print("DBG: getPosNeg: bests: %s" % bests)
    print("DBG: getPosNeg: refs: %s and %s" % (listPosNegRef[bests[0][0]],listPosNegRef[bests[1][0]]))
    imax = bests[0][0]
    simi = bests[0][1]
    conf = min(simi/0.36,1.)
    sref,vref = listPosNegRef[imax]
    print("DBG:   1: getPosNeg: %s => %d: %s %.2f (conf: %.2f)" % (s,imax,sref,vref,conf ) )
    imax2 = bests[1][0]
    simi2 = bests[1][1]
    conf2 = min(simi2/0.36,1.)
    sref2,vref2 = listPosNegRef[imax2]
    print("DBG:   2: getPosNeg: %s => %d: %s %.2f (conf: %.2f)" % (s,imax2,sref2,vref2,conf2 ) )
    # normally if we have enough example in our base, first and second will be both quite correct
    rCoefFirst=0.66
    vref = vref*rCoefFirst+vref2*(1-rCoefFirst)
    conf = conf*rCoefFirst+conf2*(1-rCoefFirst)
    print("DBG: avg: getPosNeg: %s => %.2f (conf:%.2f)" % (s,vref,conf ) )
    return vref,conf
    
def autotest():
    al = [
             ["Je suis content",0.8],
             ["J'adore",0.8],
             ["Je kiffe",0.7],
             ["Je suis triste", 0.2],
             ["C'est nul ce truc",-0.5],
             ["J'aime pas du tout",-0.7],
             ["C'est vraiment pourri",-0.5],
             ["c'est naze",-0.8],
             ["C'est naze",-0.8],
             ["C'est naze.",-0.8],
             ["C'est naze!",-0.8],
             ["C'est trop naze",-0.8],
             ["C'etait vraiment naze",-0.8],
             ["C'est exécrable",-0.8],
             ["J'adore les pois gourmands",0.8],
             ["J'aime les haricots verts",0.8],
             ["Je deteste les yaourts",-0.8],
             ["On mange souvent des pates",0.4],
             ["Manuel Macron",0.],
             ["Michael Jacskon",0.8], # should be 0 but seem to be globally positive
             ["Michael Francois",0.],
             ["Adolf Hitler",0.],
             ["nazi",-1.],
        ]
        
    nCptErreur = 0
    for s,r in al:
        print("\nINF: PosNeg for '%s':" % s)
        r2,conf = getPosNeg(s)
        rDiff = abs(r-r2)
        print(" => %s ref: %2f,  found: %.2f, diff: %.2f (conf: %.2f)" % (s,r,r2,rDiff,conf))
        if rDiff > 0.5:
            print("!!! ERREUR !!!\n")
            nCptErreur+=1
    
    print("INF: nCptErreur: %d" % nCptErreur)
            
if __name__ == "__main__":
    autotest()
