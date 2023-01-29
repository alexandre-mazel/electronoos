# -*- coding: cp1252 -*-
import io

def clean_string(s):
    conversion_list = [ 
                ("?",""), 
                ("'"," "), 
                (":"," sep ")
                
    ]
    s = s.lower()
    for c in conversion_list:
        s = s.replace(c[0],c[1])
    return s
        
tableau_questions_reponses = [
    [ ["bonjour", "hello", "salut","coucou"], "Salut Humain!"],
    [ ["comment ca va", "ca boume", "tu va bien"], "moi ca va!"],
    [ ["au revoir", "bye"], "a+"],
]
def loadFaqSimple( filename ):
    """

    Charge un fichier de Frequently Asked Questions
    return a list of pair (q,ans)
    
    Version simple sans check d'erreur
    
    les faq sont sous la forme
    question1
    reponse1
    (ligne vide)
    question2
    reponse2
    (ligne vide)
    ...
    """
    faq = []
    f = io.open(filename,"r",encoding='cp1252')
    while 1:
        q = f.readline()
        if q == "":
            break  # je suis a la fin du fichier
        a = f.readline()
        dummy = f.readline()
        faq.append((q[:-1],a[:-1].strip())) # :-1: => enleve le \n (retour a la ligne)
    print("INF: loadFaqSimple: %d loaded info(s))" % len(faq))
    f.close()
    return faq
    
def loadFaq( filename ):
    """
    Charge un fichier de Frequently Asked Questions
    return a list of pair (q,ans)
    
    les faq sont sous la forme
    question1
    reponse1
    (ligne vide)
    question2
    reponse2
    (ligne vide)
    ...
    """
    faq = []
    f = io.open(filename,"r",encoding='cp1252')
    blob = [] # a block of lines separated by an empty line
    bContinue = 1
    while bContinue:
        line = f.readline()
        if len(line)<1:
            bContinue = 0
        if bContinue and line[-1] == '\n': line = line[:-1]
        if len(line)<1:
            if len(blob)>1:
                # end of faq
                question = " ".join(blob[:-1])
                answer = blob[-1]
                faq.append( (question,answer) )
            blob = []
        else:
            blob.append(line)
    #~ print("DBG: load: blob: %s" % str(blob))
    #~ print(self.thous)
    print("INF: loadFaq: %d loaded info(s))" % len(faq))
    return faq
    
    
faq = loadFaqSimple("faq_informatique.txt")
#~ faq = loadFaq("faq_informatique.txt")

def trim_usual_and_lower(words):
    o = []
    for w in words:
        w = w.lower()
        if w in ["", "c","est","quoi","le","la","les","c'est","un","une","dans","dis","moi", "qu", "est", "ce"]:
            continue
        o.append(w)
    return o

def chatbot(user_input):
    user_input = clean_string(user_input)
    for qr in tableau_questions_reponses:
        qs,r = qr
        if user_input in qs:
            return r
    
    words = user_input.split(" ")
    words = trim_usual_and_lower(words)
    for q,a in faq:
        q_words = trim_usual_and_lower(clean_string(q).split(" "))
        #~ print("test '%s' in '%s'" % (words,q))
        for w in words:
            if w in q_words:
                #~ print("found '%s' in '%s'" % (w,q))
                print("=> Tu veux savoir %s ?"% q )
                return a
    return "je sais pas"
        
    
def chatbot_run():
    while 1:
        s = input()
        a = chatbot(s)
        print(a)
        if a.lower() in ["a+","bye"]: break
    
def autotest():
    assert(chatbot("Salut") == "Salut Humain!")
    assert(chatbot("Ca boume?") == "moi ca va!")
    assert(chatbot("bye") == "a+")
    assert(chatbot("pipi") == "je sais pas")
    assert(chatbot("parle moi de ram") == "C'est la mémoire vive, espace virtuelle où évoluent les programmes quand ils sont lancés.")
    
    
autotest()
chatbot_run()