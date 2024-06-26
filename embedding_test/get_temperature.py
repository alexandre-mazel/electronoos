# coding: cp1252
import sys
import os

sys.path.append("../camembert")
import sentence_embedding

global_loadedEmbedPosNeg = None

# a list of tagged reference,
# the idea if to find closer sentence and get it's positiveness
#
# imagine the text as an answer to the question: tu aime ce film ?
#
listPosNegRef = [
    # mettre a la fois des phrase a la premiere et troisieme personne, attention a bien les balancer
    # si une a la 3ieme, mettre son contraire aussi a la 3ieme
    ["super",1.],
    #~ ["top",1.],  # TODO: pourquoi ca ajoute une erreur?
    ["agr�able",1.],
    #~ ["passionnant",1.], # nazi et ben laden sortent sur passionnant en 2ieme au lieu de d�goutant et nul!
    ["c'est agr�able",1.],
    ["completly",1.],
    ["compl�tement",1.],
    ["carr�ment",1.],
    ["c'est bien",0.6],
    ["c'est tr�s bien",0.6],
    ["c'est bon",0.7],
    ["j'adore beaucoup",1.],
    ["j'adore",0.8],
    ["j'aime beaucoup",0.8],
    ["je kiffe",1.],
    #~ ["c'est g�nial",1.], # genere trop d'erreur: "c'est execrable" 0.32 et "c'est naze" 0.16 match directement la dessus en best a 0.37
    ["c'est du g�nie",1.],
    ["j'aime beaucoup",1.],
    #~ ["c'est app�tissant",0.7], # trop orient� bouffe
    ["j'aime",0.8],
    ["moyen",0],
    ["passable",0],
    ["un peu",0.3],
    ["bof",-0.2],
    ["c'est insipide",-0.2],
    ["naze",-0.6],
    ["c'est naze",-0.6],
    ["pourri",-0.7],
    ["nul",-1.],
    ["c'est nul",-0.8],
    ["c'est tr�s nul",-1.],
    ["c'est mauvais",-1.],
    ["ex�crable",-1.],
    ["c'est ex�crable",-1.],
    ["c'est execrable",-1.],
    ["c'est d�testable",-1.],
    ["r�pugnant",-1.],
    ["c'est r�pugnant",-1.],
    ["d�goutant",-1.],
    ["c'est d�goutant",-1.],
    #~ ["c'est � vomir",-1.], # trop orient� bouffe
    ["je d�teste",-1.],
    ["je n'aime pas du tout",-1.],
]

# imagine la question: As tu dormi ? / as tu mang� ?
listYesNoRef = [
    # mettre toujours au moins 2 synonymes pour avoir une bonne moyenne
    # d'ou l'id�e d'avoir les synonymes en anglais
    ["tout � fait",1.],
    ["completely",1.],
    ["exactly",1.],
    ["absolutely",1.],
    ["compltly",1.],
    ["compl�tement",1.],
    ["correct",1.],
    ["true",1.],
    ["vrai",1.],
    ["oui",0.9],
    ["yes",0.9],
    ["un peu",0.3],
    ["moyen",0.],
    ["bof",0.],
    ["average",0.],
    ["soso",0.],
    ["pas trop",-0.3],
    ["non",-0.9],
    ["no",-0.9],
    ["pas du tout",-1.],
    ["not at all",-1.],
    ["wrong",-1.],
    ["faux",-1.],
]

def loadEmbed( listValueRef, strFileNameEmbedCache,bForceGeneration = False ):
    # use a global variable to cache this embedding
    globalVarName = strFileNameEmbedCache + "_global"
    if globalVarName in globals():
        return globals()[globalVarName]
        
    #~ bForceGeneration = 1

    if not os.path.isfile(strFileNameEmbedCache) or bForceGeneration:
        print("INF: loadPosNeg: generating embedding and storing %d embedding to %s..." % (len(listValueRef),strFileNameEmbedCache))
        listOnlyStr = [e[0] for e in listValueRef]
        #~ print(listOnlyStr)
        embed = sentence_embedding.camEmbedList( listOnlyStr )
        sentence_embedding.saveEmbed(strFileNameEmbedCache,embed)
    else:
        print("INF: loadPosNeg: loading from %s..." % strFileNameEmbedCache)
        embed = sentence_embedding.loadEmbed(strFileNameEmbedCache)
        print("INF: loadPosNeg: %d embedding(s) loaded" % len(embed))
        #~ print("DBG: loadPosNeg: %d sentences in ref" % len(listValueRef))
        if len(embed) != len(listValueRef):
            if bForceGeneration:
                print("ERR: generation error size differs (%d!=%d)" % (len(embed),len(listValueRef)))
                return None
            print("WRN: loadPosNeg: regenerating (size differs: %d)" % len(embed))
            return loadEmbed(listValueRef=listValueRef,strFileNameEmbedCache=strFileNameEmbedCache,bForceGeneration=True)
        global_loadedEmbedPosNeg = embed
     
    globals()[globalVarName] = embed
    return embed
    
def getValueFromEmbed( s, listRef, strFileNameEmbedCache, bVerbose=False, rGoodSimi=0.36 ):
    """
    compute average value of the two bests similarity
    return value, confidence
    - rGoodSimi: similarity to have a confidence of 1
    """
    bPrint = 1
    bPrint = bVerbose
    
    s = s.replace(".","").replace("!","")
    embed = loadEmbed(listRef,strFileNameEmbedCache)
    bests = sentence_embedding.getBests(s,embed,bVerbose=bVerbose,listWordForVerbose=listRef)
    if bPrint: print("DBG: getPosNeg: bests: %s" % bests)
    if bPrint: print("DBG: getPosNeg: refs: %s and %s" % (listRef[bests[0][0]],listRef[bests[1][0]]))
    imax = bests[0][0]
    simi = bests[0][1]
    conf = min(simi/rGoodSimi,1.)
    sref,vref = listRef[imax]
    if bPrint: print("# 1: getPosNeg: %s => %d: %s %.2f (conf: %.2f)" % (s,imax,sref,vref,conf ) )
    imax2 = bests[1][0]
    simi2 = bests[1][1]
    conf2 = min(simi2/rGoodSimi,1.)
    sref2,vref2 = listRef[imax2]
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
    
    
    
def getPosNeg(s,bVerbose=0):
    """
    return a float [-1,1] of the positivness/likeliness of a sentence
    eg:
        - "C'est super" => 1.
        - "C'est trop nul" => -1.
    """
    return getValueFromEmbed(s,listPosNegRef,"posneg_embed_camembert_cache.txt",bVerbose=bVerbose)
    
    
def getYesNo(s,bVerbose=0):
    """
    return a float [-1,1] of the positivness of a sentence
    eg:
        - "oui" => 1.
        - "non" => -1.
    """
    return getValueFromEmbed(s,listYesNoRef,"yesno_embed_camembert_cache.txt",bVerbose=bVerbose,rGoodSimi=0.5)


def autotestPosNeg():
    
    bVerbose = 1
    bVerbose = 0
    
    al = [
                ["Je suis content",0.8],
                ["J'adore beaucoup",1.],
                ["J'adore",0.8],
                ["J'aime bien",0.8],

                ["Nous adorons",0.8],
                ["Je kiffe",0.7],
                # 1: getPosNeg: Je kiffe => 9: je kiffe 1.00 (conf: 0.97)
                # 2: getPosNeg: Je kiffe => 15: bof -0.20 (conf: 0.80)
                
                ["completement",0.8], # Argh, il y a compl�tement dans la liste, et ca sort tr�s bas!
                # 1: getPosNeg: completement => 3: completly 1.00 (conf: 1.00)
                # 2: getPosNeg: completement => 27: ex�crable -1.00 (conf: 1.00)
                # 3: getPosNeg: completement => 3: compl�tement 1.00 (conf: 1.00)

                ["Je kiffe ma race",0.7],
                # 1: getPosNeg: Je kiffe ma race => 9: je kiffe 1.00 (conf: 0.67)
                # 2: getPosNeg: Je kiffe ma race => 32: je d�teste -1.00 (conf: 0.61)

                ["Je suis triste", -1.], # j'aurai aim� 0.2, mais c'est tres neg
                ["C'est nul ce truc",-0.5],
                ["J'aime pas du tout",-0.7],
                ["C'est vraiment pourri",-0.5],
                ["c'est naze",-0.8],
                ["C'est naze",-0.8],
                ["C'est naze.",-0.8],
                ["C'est naze!",-0.8],
                # j'ai enlev� le ! dans le getPosNeg, sinon ca matche avec "c'est bien", �tonnant !
                # DBG:   1: getPosNeg: C'est naze! => 18: c'est naze -0.60 (conf: 0.99)
                # DBG:   2: getPosNeg: C'est naze! => 3: c'est bien 0.60 (conf: 0.73)
                ["C'est trop naze",-0.8],
                ["C'est tr�s bien",0.8],
                ["C'est trop bien",0.8],
                ["C'etait vraiment naze",-0.8],
                ["C'est agr�able",0.7],
                ["C'est g�nial",0.7],
                ["C'est ex�crable",-0.8],
                ["J'adore les pois gourmands",0.8],
                ["J'aime les haricots verts",0.8],
                ["Je deteste les yaourts",-0.8],
                #~ ["On mange souvent des pates",0.], # hard to tell
                # DBG:   1: getPosNeg: On mange souvent des pates => 15: bof -0.20 (conf: 0.34)
                # DBG:   2: getPosNeg: On mange souvent des pates => 30: d�goutant -1.00 (conf: 0.32)
                ["Emmanuel Macron",0.],
                # 1: getPosNeg: Emmanuel Macron => 10: c'est du g�nie 1.00 (conf: 0.33)
                # 2: getPosNeg: Emmanuel Macron => 15: bof -0.20 (conf: 0.32)

                ["Michael Jacskon",0.8], # should be 0 but seem to be globally positive
                ["M�re Th�r�sa",-0.2], # why is neg?
                ["L'abb� Pierre",-0.2], # should ne positif but, output r�pugnant!
                ["Michael Francois",0.],
                ["Adolf Hitler",-0.8],
                ["Ben Laden",-0.8],
                ["nazi",-1.],

                ["Aimes-tu?",1.],
                # 1: getPosNeg: Aimes-tu? => 7: j'adore 0.80 (conf: 1.00)
                # 2: getPosNeg: Aimes-tu? => 12: j'aime 0.80 (conf: 1.00)

                ["Detestes-tu?",-1.],
                # 1: getPosNeg: Detestes-tu? => 33: je d�teste -1.00 (conf: 1.00)
                # 2: getPosNeg: Detestes-tu? => 7: j'adore 0.80 (conf: 0.76)

                ["Et toi, aimes-tu?",1.],
                # 1: getPosNeg: Et toi, aimes-tu? => 7: j'adore 0.80 (conf: 1.00)
                # 2: getPosNeg: Et toi, aimes-tu? => 12: j'aime 0.80 (conf: 1.00)

                ["Et toi, detestes-tu?",-1.],
                # 1: getPosNeg: Et toi, detestes-tu? => 33: je d�teste -1.00 (conf: 0.80)
                # 2: getPosNeg: Et toi, detestes-tu? => 9: je kiffe 1.00 (conf: 0.67)

                ["J'ai ador� ce restaurant",1.],
                ["J'ai pas aim� du tout cette pi�ce de th�atre",-0.7],
                ["La fin du monde",-0.7],
                ["un peu",0.2],
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
        print(" => %s ref: %.2f,  posneg: %.2f, diff: %.2f (conf: %.2f)" % (s,r,r2,rDiff,conf))
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
        print("\nINF: autotestPosNeg: nCptRealError: %d, nCptErrorLowConf: %d, rAvgConfErreur: %.2f (rAvgConf:%.2f)" % (nCptRealError,nCptErrorLowConf,rSumConfError/nCptError,rSumConf/len(al)))
            
    # INF: autotestPosNeg: nCptRealError: 0, nCptErrorLowConf: 1, rAvgConfErreur: 0.23 (rAvgConf:0.79)
   
def autotestYesNo():
    
    bVerbose = 1
    bVerbose = 0
    
    al = [
            ["oui",0.8],
            ["yeah!",0.8],
            ["non",-0.8],
            ["OUI",0.8], # tres decevant ! (est ce un acronyme en anglais?)
            # 1: getPosNeg: OUI  => 10: bof 0.00 (conf: 1.00)
            # 2: getPosNeg: OUI  => 7: yes 0.90 (conf: 1.00)
            
            #~ ["OUI !!!",0.8],
            # same problem
            
            #["OUUUUUI",0.8],
            # 1: getPosNeg: OUUUUUI => 10: bof 0.00 (conf: 1.00)
            # 2: getPosNeg: OUUUUUI => 7: yes 0.90 (conf: 1.00)
            
            #~ ["NOOOOOOOOOOOOON",-0.8],
            # 1: getPosNeg: NOOOOOOOOOOOOON => 15: no -0.90 (conf: 1.00)
            # 2: getPosNeg: NOOOOOOOOOOOOON => 7: yes 0.90 (conf: 1.00)
            
            #~ ["Nah!",-0.8],
            # 1: getPosNeg: Nah => 7: yes 0.90 (conf: 1.00)
            # 2: getPosNeg: Nah => 15: no -0.90 (conf: 1.00)
            
            ["Correct",0.8],
            ["completement",0.8],
            ["Exact",0.8],
            ["Richtig",1.],
            ["Exactemente",1.],
            ["Tout a fait Thierry!",0.8],
            ["Sure !",0.8],
            ["Sure as 1 + 1 equal 2",0.8],
            ["ok",0.8],
            ["OK",0.8],
            ["OKAY",0.8],
        ]
        
    nCptError = 0
    nCptRealError = 0
    nCptErrorLowConf = 0
    rSumConfError = 0
    rSumConf = 0
    for s,r in al:
        print("\nINF: YesNo for '%s':" % s)
        r2,conf = getYesNo(s,bVerbose)
        rSumConf += conf
        rDiff = abs(r-r2)
        print(" => %s ref: %.2f,  posneg: %.2f, diff: %.2f (conf: %.2f)" % (s,r,r2,rDiff,conf))
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
        print("\nINF: autotestYesNo: nCptRealError: %d, nCptErrorLowConf: %d, rAvgConfErreur: %.2f (rAvgConf:%.2f)" % (nCptRealError,nCptErrorLowConf,rSumConfError/nCptError,rSumConf/len(al)))
            
        
    # INF: autotestYesNo: nCptRealError: 1, nCptErrorLowConf: 0, rAvgConfErreur: 0.70 (rAvgConf:0.87)
    


def autotest():
        autotestPosNeg()
        autotestYesNo()
        
def interactiveLoop():
    print("\nApprenons � mieux nous connaitre!\n")
    elements = ["cin�ma", "pates", "haricots verts", "manga", "cerises", "yaourts","couscous"]
    for elem in elements:
        print("Aime-tu le(s) %s ?" % elem)
        ans = input()
        score = getPosNeg(ans)
        print("=>"+str(score))
        print("")
 
if __name__ == "__main__":
    autotest()
    interactiveLoop()
    # a voir, pouvoir dire top!
