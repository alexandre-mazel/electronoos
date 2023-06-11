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
    ["pourri",-0.7.],
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
    sref,vref = listPosNegRef[imax]
    print("DBG: getPosNeg: %s => %d: %s %.2f" % (s,imax,sref,vref ) )
    return vref
    
def autotest():
    al = [
             ["Je suis content",0.8],
             ["J'adore",0.8],
             ["Je kiffe",0.7],
             ["Je suis triste", 0.2],
             ["C'est nul ce truc",-0.5],
             ["J'aime pas du tout",-0.7],
             ["C'est vraiment pourri",-0.5],
             ["C'etait vraiment naze",-0.8],
             ["C'est exécrable",-0.8],
        ]
        
    for s,r in al:
        print("INF: PosNeg for '%s':" % s)
        r2 = getPosNeg(s)
        print(" => %s ref: %2f: %.2f\n" % (s,r,r2))
        
if __name__ == "__main__":
    autotest()
