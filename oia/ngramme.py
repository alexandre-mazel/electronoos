import random

def addStat( d, k1, k2 ):
    if k1 not in d:
        d[k1] = [0, {}] # occ, followers
    if k2 not in d[k1][1]:
        d[k1][1][k2] = 0
    d[k1][0] += 1
    d[k1][1][k2] += 1

def constructNGram(txt,n=2):
    txt = txt.replace("\n", " ")
    words = txt.split( " ")
    i = 0
    ngram = {}
    occ = {}
    while i < len(words)-1:
        seqw = words[i]
        seqsuiv = words[i+1]
        addStat(ngram, seqw, seqsuiv)
        i += 1        
    
    # affiche les 10 premiers (pour tester)
    cpt = 1
    for k,v in sorted(ngram.items(),key=lambda x:x[1][0],reverse=True):
        occ = v[0]
        follow = v[1]
        print("\n%s: %d occ" % (k,occ))
        for k2, v2 in sorted(follow.items(),key=lambda x:x[1],reverse=True):
            print("   %s: %d" % (k2,v2))
        cpt += 1
        if cpt > 10:
            break
            
    return ngram

# constructNGram - end

def generateSentence(ng, startWord,deep=1):
    if deep == 1:
        print("\ngenerateSentence begin:")
    print(startWord)
    occ = ng[startWord]
    list_follow = sorted(occ[1].items(),key=lambda x:x[1],reverse=True)
    #~ print("list_follow: %s" % str(list_follow))
    word_and_occ = (random.choice(list_follow[:5]))
    #~ print("word_and_occ: %s" % str(word_and_occ))
    word = word_and_occ[0]
    if deep > 128:
        print("\n")
        return
    #~ try:
        #~ del ng[startWord]
    #~ except: pass
    generateSentence(ng,word,deep+1)
    
"""
Structure recommanded:
Un dictionnaire avec pour chaque mot,
un dictionnaire des mots suivants.

par exemple:
{
    "le": {"chat": 14, "chien": 12}, 
    # 14: nombre de fois que le mot "chat" suit le mot "le"
    # 12: nombre de fois que le mot "chien" suit le mot "le"
    "la": {"voiture": 13, "chevre": 2},
    # 13: nombre de fois que le mot "voiture" suit le mot "la"
}

# ou pour aider a faire des stats:
{
    "le": (26, {"chat": 14, "chien": 12}),
    # 26: nombre de fois que le mot le apparait dans le texte
    "la": (15, {"voiture": 13, "chevre": 2}),
}


d = {}
d["toto"] = "Un super bonhomme"

"""


textfile = "La_guerre_et_la_paix_tolstoi_pg17949.txt"
f = open(textfile,"rt",encoding="utf-8")
buf = f.read()
f.close()

ng = constructNGram(buf)
generateSentence(ng, "le")
generateSentence(ng, "La")
generateSentence(ng, "Ensuite")
generateSentence(ng, "email")