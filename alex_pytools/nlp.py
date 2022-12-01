# -*- coding: cp1252 -*-
import nltk
if 0:
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('treebank')
    nltk.download('book_grammars')
    
    
    

def assert_equal(a,b):
    print( "%s\n == %s ?" % (str(a),str(b)) )
    if (a)!=(b):
        if type(b) != int:
            print("%s\n!=\n%s"%(a,b))
        else:
            print("%s != %s"%(a,b))
        print("assert_equal: assert error")
        
        assert(0)
    
"""
English:
CC: Coordinating conjunction
CD: Cardinal number
DT: Determiner
EX: Existential there
FW: Foreign word
IN: Preposition or subordinating conjunction
JJ: Adjective
VP: Verb Phrase
JJR: Adjective, comparative
JJS: Adjective, superlative
LS: List item marker
MD: Modal
NN: Noun, singular or mass
NNS: Noun, plural
PP: Preposition Phrase
NNP: Proper noun, singular Phrase
NPS: Proper noun, plural
PDT: Pre determiner
POS: Possessive ending
PRP: Personal pronoun Phrase
PRP: Possessive pronoun Phrase
RB: Adverb
RBR: Adverb, comparative
RBS: Adverb, superlative
RP: Particle
S: Simple declarative clause
SBAR: Clause introduced by a (possibly empty) subordinating conjunction
SBARQ: Direct question introduced by a wh-word or a wh-phrase.
SINV: Inverted declarative sentence, i.e. one in which the subject follows the tensed verb or modal.
SQ: Inverted yes/no question, or main clause of a wh-question, following the wh-phrase in SBARQ.
SYM: Symbol
VBD: Verb, past tense
VBG: Verb, gerund or present participle
VBN: Verb, past participle
VBP: Verb, non-3rd person singular present
VBZ: Verb, 3rd person singular present
WDT: Wh-determiner
WP: Wh-pronoun
WP: Possessive wh-pronoun
WRB: Wh-adverb
"""

"""
French:
tag Category 	Extra Info
ADJ 	adjectif 	
ADJWH 	adjectif 	
ADV 	adverbe 	
ADVWH 	adverbe 	
CC 	conjonction de coordination 	
CLO 	pronom 	obj
CLR 	pronom 	refl
CLS 	pronom 	suj
CS 	conjonction de subordination 	
DET 	déterminant 	
DETWH 	déterminant 	
ET 	mot étranger 	
I 	interjection 	
NC 	nom commun 	
NPP 	nom propre 	
P 	préposition 	
P+D 	préposition + déterminant 	
PONCT 	signe de ponctuation 	
PREF 	préfixe 	
PRO 	autres pronoms 	
PROREL 	autres pronoms 	rel
PROWH 	autres pronoms 	int
U 	? 	
V 	verbe 	
VIMP 	verbe imperatif 	
VINF 	verbe infinitif 	
VPP 	participe passé 	
VPR 	participe présent 	
VS 	subjonctif
"""

txtBiz = "The fourth Wells account moving to another agency is the packaged paper-products division of Georgia-Pacific Corp., which arrived at Wells only last fall. Like Hertz and the History Channel, it is also leaving for an Omnicom-owned agency, the BBDO South unit of BBDO Worldwide. BBDO South in Atlanta, which handles corporate advertising for Georgia-Pacific, will assume additional duties for brands like Angel Soft toilet tissue and Sparkle paper towels, said Ken Haldin, a spokesman for Georgia-Pacific in Atlanta."
txtBiz_fr = "Le quatrième compte de Wells à changer d'agence est la division des produits en papier emballé de Georgia-Pacific Corp, qui n'est arrivée chez Wells qu'à l'automne dernier. Comme Hertz et History Channel, elle part également pour une agence appartenant à Omnicom, l'unité BBDO South de BBDO Worldwide. BBDO South à Atlanta, qui s'occupe de la publicité d'entreprise pour Georgia-Pacific, assumera des tâches supplémentaires pour des marques telles que le papier hygiénique Angel Soft et les essuie-tout Sparkle, a déclaré Ken Haldin, un porte-parole de Georgia-Pacific à Atlanta."
txtDog = "We saw the yellow dog"
txtDog2 = "the little yellow dog barked at the cat"
txtDog2 = "the little yellow dog barked at the funny girl"
#~ txtDog2 = "Rapunzel let down her long golden hair"
txtDog1_fr = "le petit chien jaune aboie sur la fille rieuse"
txtDog2_fr = "Rapunzel décida de laisser détaché ses longs cheveux dorés"

txtCv1_fr = "cosmetiques et aime egalement lanimation"
txtCv2_fr = """Dao
Woringer

C O N S E I L L È R E   B E A U T É

Je  suis  une  passionnée  de  la  science  des

cosmétiques  et  aime  également  l'animation

et  le  conseil  personnalisé.    Conseiller  et

satisfaire sont mes valeurs et ma devise. 

EXPERIENCES

Conseillère beauté
(Maquillage, soin et parfum)

KS BEAUTÉ ET ALADINOO Depuis 2019

Makeup artist

Conseil maquillage, soin et parfum

 Pratique de soin institut Guerlain

Conseillère beauté
Sephora 2019
"""


txtCv2_fr_sorted = """
COMPÉTENCES
Maquillage
Soin
Parfum
cosmétiques
Science des
cosmétiques
Science des
PASSIONS
Dao
Woringer
Dao
Woringer
CONSEILLÈRE BEAUTÉ
Je suis une passionnée de la science des
cosmétiques et aime également l'animation
et le conseil personnalisé. Conseiller et
satisfaire sont mes valeurs et ma devise.
EXPERIENCES
FORMATION ET DIPLOME
0650005779
woringercamille@gmail.com
95100, Argenteuil
3 rue des Allobroges
Maquillage et soin
Voyages
Sport extrème
Voyages
Sport extrème
Conseillère beauté
(Maquillage, soin et parfum)
KS BEAUTÉ ET ALADINOO Depuis 2019
Makeup artist
Conseil maquillage, soin et parfum
Pratique de soin institut Guerlain
Conseillère beauté
Sephora 2019
Conseil et vente
Marchandising
Réception de colis
Formations marques de cosmétique
Hôtesse événementielle
États-Unis et Japon 2017-2018
Accueil clients et placement
Prise de réservation
CFA AFFIDA
Baccalauréat Professionnel de Commerce
Gestion, animation et vente
"""

txtCv2_fr_sorted_ext = """Je suis une passionnée de la science des
cosmétiques et aime également l'animation
et le conseil personnalisé. Conseiller et
satisfaire sont mes valeurs et ma devise.
"""

txtLike = "Alexandre aime les haricots verts, mais n'aime pas le caca."
txtLikeShort = "Alexandre aime les haricots verts, mais pas le caca."
txtLikeSimpleCompound = "Alexandre aime les haricots verts et aussi les tortues."
txtLikeSimple = "Alexandre aime les haricots verts."

#~ txtDog2_fr = txtCv1_fr
#~ txtDog2_fr = txtCv2_fr

        
def _treeToStrInner(tree):
    o = ""
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            o += subtree.label() + "(" + _treeToStrInner(subtree) + ")"
        elif type(subtree) == tuple:
            o += subtree[0] + '/' + subtree[1]
        elif type(subtree) == str:
            o += str(subtree) # prevent having ' ' around str
        else:
            o += repr(subtree)
            assert(0)
    return o
        
def treeToStr(tree):
    """
    transform a tree to a unique compact representation
    """
    #~ print("DBG: treeToStr %s" % tree )
    o = ""
    #~ for subtree in tree:
        #~ if type(subtree) == str or type(subtree) == tuple:
            #~ continue
        #~ print("DBG: getAllPhrases subtrees: type: %s, %s" % (type(subtree),subtree ) )
        #~ if type(subtree) == nltk.tree.Tree:
            #~ if subtree.label() == "PHRASE" or subtree.label() == "PHRASE_ELID" :
                #~ o.append(subtree)
            #~ else:
                #~ o.extend( self.getAllPhrasesFromTree(subtree) )
        #~ else:
            #~ print("DBG: getAllPhrases unhandled case!")
            #~ assert(0)
    #~ return o
    o += "-----\n"
    o +=  _treeToStrInner(tree) 
    o += "\n"
    return o
    
def treesListToStr( listTrees ):
    o = ""
    o += "[\n"
    for t in listTrees:
        o += (treeToStr(t))
    o += "]\n"
    return o
    

listEGFrEn = {
    "ADJ": "JJ",
    "DET": "DT",
    "NC": "NN",
    "NPP": "NNP",
    "P": "IN",
    "U": "NN",
    "V": "VBD", # verbe conjugué
    "VINF": "VBG", # infinitve
    "VPP": "VBN", # participe passé
}

def convertEG_fr_to_en(eg):
    return listEGFrEn[eg]

def text_preprocess_en(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences_pos = [nltk.pos_tag(sent) for sent in sentences]
    print("text_preprocess_en: out: " + str(sentences_pos) )
    return sentences_pos

def text_preprocess_fr(document):
    from transformers import AutoTokenizer, AutoModelForTokenClassification

    tokenizer = AutoTokenizer.from_pretrained("gilf/french-camembert-postag-model")
    model = AutoModelForTokenClassification.from_pretrained("gilf/french-camembert-postag-model")
    from transformers import pipeline
    nlp_token_class = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)
    sentences_pos = nlp_token_class(document)
    print("text_preprocess_fr: 1: " + str(sentences_pos) )
    # convert from french to en
    sentences_pos_en = []
    for info in sentences_pos:
        print(info)
        word = info['word']
        eg = info['entity_group']
        type=convertEG_fr_to_en(eg)
        sentences_pos_en.append((word,type))
        
    print("text_preprocess_fr: out: " + str(sentences_pos_en) )
    return  [sentences_pos_en]
    

def explore():
        
    s1 = """At eight o'clock on Thursday morning Arthur didn't feel very good."""
    s2 = "â€”Aucunement. Il les Ã©change contre du millet. J' aime elsa et les haricots verts. Tu aimes les noix. Ils aiment les tableaux."

    # Tokenize and tag some text
    tokens = nltk.word_tokenize(s2)
    print(tokens)

    tagged = nltk.pos_tag(tokens)
    print(tagged)

    #identify nammed entities
    entities = nltk.chunk.ne_chunk(tagged)
    print(entities)
    #~ entities.draw()

    # Display a parse tree
    from nltk.corpus import treebank
    t = treebank.parsed_sents('wsj_0001.mrg')[0]
    print(t)
    #~ t.draw()

    nltk.data.show_cfg('grammars/book_grammars/sql0.fcfg')
    nltk.data.show_cfg('grammars/book_grammars/sql1.fcfg')

    from nltk import load_parser
    cp = load_parser('grammars/book_grammars/sql1.fcfg')
    query = 'Which cities are located in China and have populations above 1,000,000' # the grammar doesn't handle other countries like france
    trees = list(cp.parse(query.split()))
    answer = trees[0].label()['SEM']
    answer = [s for s in answer if s]
    q = ' '.join(answer)
    print(q)
    
def explore2():
    # grammar try to match starting from beginning,
    # NP: {<DT>?<JJ>*<NN>} will override later NP: {<DT>?<JJ>*<NN>} 
    grammar = """
    NP: {<PRP\$>*<DT|PP\$>?<JJ>*<NN><JJ>*}
    NP:  {<NNP>+}

    """
    # was:
    """
    NP: {<DT>?<JJ>+<NN><JJ>+}
    NP: {<DT>?<JJ>+<NN>}
    NP: {<DT>?<NN>+<JJ>}
    NP: {<DT>?<NN>}
    """
    cp = nltk.RegexpParser(grammar)

    txtDogPosEn = text_preprocess_en(txtDog2)
    txtDogPosFr = text_preprocess_en(txtDog2_fr)
    txtDogPosFr = text_preprocess_fr(txtDog2_fr)
    #~ txtDogPos = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"), ("dog", "NN"), ("barked", "VBD"), ("at", "IN"),  ("the", "DT"), ("cat", "NN")]
    #~ print("txtDogPos: " + str(txtDogPos) )

    result = cp.parse(txtDogPosEn[0])
    print(result)
    print("explore2: sent to parse: " + str(txtDogPosFr[0]))
    result = cp.parse(txtDogPosFr[0])
    print(result)
    #~ result.draw()

    print(nltk.boolean_ops())

        
    if 0:
        # need prover9 (linux only)
        read_expr = nltk.sem.Expression.fromstring
        SnF = read_expr('SnF')
        NotFnS = read_expr('-FnS')
        R = read_expr('SnF -> -FnS')
        prover = nltk.Prover9()
        prover.prove(NotFnS, [SnF, R])
        

def exploreTrees():
    s = '(ROOT (S (NP (NNP Europe)) (VP (VBZ is) (PP (IN in) (NP (DT the) (JJ same) (NNS trends)))) (. .)))'
    s = """(S
  (PHRASE
    (NP Alexandre/NPP)
    aime/V
    (NPS (NP les/DET haricots/NC verts/ADJ) (NP ./NC))))"""
    
    s = """(S
  (NPS (NP COMPÉTENCES Maquillage/NC) (NP So/U in/ADJ))
  (NPS (NP Parfum/U cosmétiques/ADJ) (NP Science/NC))
  des/PetD
  (NPS (NP cosmétiques Science/NC) des/PetD (NP PASSIONS/NC))
  (PHRASE
    (NP Dao Woringer Dao Woringer/NPP)
    CONSEIL/V
    (NP L/DET ÈRE/ADJ BEAUTÉ/NC))
  (PHRASE
    Je/CLS
    suis/V
    (NPSS
      une/DET
      passionnée/ADJ
      de/P
      (NPS (NP la/DET science/NC) des/PetD (NP cosmétiques/NC))))
  (PHRASE
    et/CC
    aime/V
    (NPS
      également/ADV
      (NP l/DET 'animation/NC)
      et/CC
      (NP le/DET conseil/NC personnalisé/ADJ))))
    """
    tree = nltk.tree.Tree.fromstring(s)
    def traverse_tree(tree):
        print("tree:", tree)
        for subtree in tree:
            if type(subtree) == nltk.tree.Tree:
                traverse_tree(subtree)
    #~ traverse_tree(tree)
    #~ print(tree[0])
    #~ print(tree[0].label())
    #~ print(dir(tree[0]))
    def getAllPhrases(tree):
        print("DBG: getAllPhrases %s" % tree )
        o = []
        for subtree in tree:
            if type(subtree) != str and subtree.label() == "PHRASE":
                o.append(subtree)
            else:
                if type(subtree) == nltk.tree.Tree:
                    o.extend( getAllPhrases(subtree) )
        return o
                
    phrases = getAllPhrases(tree)
    print("Result of getAllPhrases:")
    for p in phrases:
        print(p)
        
    print(treesListToStr([tree]))
# exploreTrees - end

    
    

class FrenchAnalyser:
    def __init__( self ):
        self.parser = None
        
    def load(self):
        if self.parser != None:
            return # already loaded
            
        from transformers import AutoTokenizer, AutoModelForTokenClassification

        tokenizer = AutoTokenizer.from_pretrained("gilf/french-camembert-postag-model")
        model = AutoModelForTokenClassification.from_pretrained("gilf/french-camembert-postag-model")
        from transformers import pipeline
        self.nlp_token_class = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)

        
        #~ grammar = """
        #~ NP: {<PRP\$>*<DT|PP\$>?<JJ>*<NN><JJ>*}
        #~ NP:  {<NNP>+}

        #~ """
        #~ # was:
        #~ """
        #~ NP: {<DT>?<JJ>+<NN><JJ>+}
        #~ NP: {<DT>?<JJ>+<NN>}
        #~ NP: {<DT>?<NN>+<JJ>}
        #~ NP: {<DT>?<NN>}
        #~ """

        # ?: 0..1        
        # *: 0..n
        # +: 1..n
        # |: or
        # seems no line must refer to symbol coming after?
        
        # "NOUNS: {<N.*>{4,}}"
        
        grammar_french = ""
        
        # on commence par chopper la structure d'action
        grammar_french += "MODV: {<ADV>+<V><ADV>+}\n"
        grammar_french += "MODV: {<ADV>+<V>}\n"
        grammar_french += "MODV: {<V><ADV>+}\n"
        grammar_french += "MODV: {<V><P><VINF><VPP>}\n" # capture le décida de laisser détaché
        
        grammar_french += "NP: {<PRP\$>*<DET|PP\$>?<ADJ>*<NC|U|VINF><ADJ>*}\n"
        grammar_french += "NP:  {<NPP>+}\n" # usefull ? not working ?
        #~ grammar_french += "NPS:  {<NP><P>*<D>*<P+D>*<NP>}\n" # celle ci ne marche pas
        #~ grammar_french += "NPS:  {<NP><P+D>*<NP>}\n" # celle ci ne marche pas
        grammar_french += "NPS:  {<NP><PetD>*<NP>}\n" # patch P+D en PetD to help grammar
        grammar_french += "NPS:  {<ADV>*<NP><CC><ADV>*<NP>}\n"
        grammar_french += "NPS:  {<NP><CC><NPS>}\n"
        grammar_french += "NPS:  {<NPS><CC><NP>}\n"
        grammar_french += "NPSS:  {<DET>*<ADJ><P><NP|NPS>}\n"

        grammar_french += "PHRASE: {<CC>*<NP|NPS|NPSS|NPP|CLS>?<V|MODV><P>*<NP|NPS|NPSS|NPP>}\n"
        grammar_french += "PHRASE_ELID: {<CC><ADV>*<NP|NPS|NPSS|NPP>}\n"
        grammar_french += "COMBI: {<PHRASE><CC><PHRASE>}\n"
        
        self.parser = nltk.RegexpParser(grammar_french)
    
    def _preprocessText(self,s):
        s = s.replace(" n'", " ne " )
        sentences_pos = self.nlp_token_class(s)
        print("DBG: _preprocessText: 1: " + str(sentences_pos) )
        # convert to classical nltk postag
        sentences_pos_en = []
        for info in sentences_pos:
            #~ print(info)
            word = info['word']
            eg = info['entity_group']
            #~ eg=convertEG_fr_to_en(eg) # don't translate them anymore, just write the grammar directly in french !
            eg=eg.replace("P+D", "PetD") # patch P+D en PetD to help grammar
            sentences_pos_en.append((word,eg))
            
        print("DBG: _preprocessText: 1: " + str(sentences_pos_en) )
        return  sentences_pos_en
    
    def analyseText(self, txt):
        """
        receive a long text and return a list of analysed sentence as a list of trees
        """
        # bourrin:
        for i in range(4):
            txt = txt.replace("  ", " ")
            txt = txt.replace(" \n", "\n")
            txt = txt.strip()
            
        print("-"*40)
        print("DBG: analyseText: received:\n%s" % txt )
        print("-"*40)
        sentences = []
        i = 0
        start = 0
        while i < len(txt):
            if i == len(txt)-1 or  \
                ( txt[i] == '.' and (txt[i+1].isupper() or txt[i+1] == '\n' or (txt[i+1] == ' ' and txt[i+2].isupper() ) ) ) \
                :
                if i == len(txt)-1:
                    i += 1
                s = txt[start:i]
                start = i+1
                print("DBG: analyseText: sentence cut:\n%s" % s )
                sentences.append(s)
            i += 1
            
        listSentenceTrees = []
        for s in sentences:
            print("DBG: analyseText: sentence analysed:\n%s" % s )
            listPos = self._preprocessText(s)
            print("DBG: analyseSentence: listPos: " + str(listPos) )
            result = self.parser.parse(listPos)
            print("#"*20)
            print("DBG: analyseText: res:\n" + str(result) )
            print()
            listSentenceTrees.append(result)
        return listSentenceTrees
            
    def getAllPhrasesFromTree(self, tree):
        print("DBG: getAllPhrases %s" % tree )
        o = []
        for subtree in tree:
            if type(subtree) == str or type(subtree) == tuple:
                continue
            print("DBG: getAllPhrases subtrees: type: %s, %s" % (type(subtree),subtree ) )
            if type(subtree) == nltk.tree.Tree:
                if subtree.label() == "PHRASE" or subtree.label() == "PHRASE_ELID" :
                    o.append(subtree)
                else:
                    o.extend( self.getAllPhrasesFromTree(subtree) )
            else:
                print("DBG: getAllPhrases unhandled case!")
                assert(0)
        return o
        
    def getAllPhrasesFromListTrees(self, listTrees):
        o = []
        for tree in listTrees:
            o.extend(self.getAllPhrasesFromTree(tree))
        return o
        
# classFrenchAnalyser  - end

frenchAnalyser = FrenchAnalyser()
    
def testFrenchAnalysis():
    frenchAnalyser.load()
    
    listTxt = (txtDog1_fr, txtDog2_fr, txtCv1_fr, txtCv2_fr,txtCv2_fr_sorted,txtCv2_fr_sorted_ext,txtLike,txtLikeShort,txtLikeSimpleCompound, txtLikeSimple)
    listTxt = (txtDog1_fr, txtDog2_fr)
    interestingTreesAll = []
    for s in listTxt:
        listTrees = frenchAnalyser.analyseText(s)
        interestingTrees = frenchAnalyser.getAllPhrasesFromListTrees(listTrees)
        print("="*60)
        print("INF: testFrenchAnalysis: Interesting Trees:")
        for t in interestingTrees:
            print(t)
        interestingTreesAll.extend(interestingTrees)
        
    print("="*60)
    print("="*60)
    print("="*60)
    print("INF: testFrenchAnalysis: Interesting Trees:")
    for t in interestingTreesAll:
        print(t)
        

def autotest_FrenchAnalysis():
    frenchAnalyser.load()
    txt1_fr = "le petit chien jaune aboie sur la fille rieuse"
    txt2_fr = "Rapunzel décida de laisser détaché ses longs cheveux dorés"
    assert_equal(treesListToStr(frenchAnalyser.analyseText(txt1_fr)), treesListToStr([nltk.tree.Tree.fromstring("""(S
  (PHRASE
    (NP le/DET petit/ADJ chien/U jaune/ADJ)
    aboie/V
    sur/P
    (NP la/DET fille/NC rieuse/ADJ)))""")]))
    assert_equal(treesListToStr(frenchAnalyser.analyseText(txt2_fr)), treesListToStr([nltk.tree.Tree.fromstring("""(S
  (PHRASE
    (NP Rapunzel/NPP)
    (MODV décida/V de/P laisser/VINF détaché/VPP)
    (NP ses/DET longs/ADJ cheveux/NC dorés/ADJ)))""")])) # avant ca fonctionner, argh !
   
#~ explore2()
exploreTrees()
#~ testFrenchAnalysis()
autotest_FrenchAnalysis()



