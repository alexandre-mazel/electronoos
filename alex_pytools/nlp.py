# -*- coding: utf-8 -*-
import nltk
if 0:
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('treebank')
    nltk.download('book_grammars')
    
    
"""
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

txtBiz = "The fourth Wells account moving to another agency is the packaged paper-products division of Georgia-Pacific Corp., which arrived at Wells only last fall. Like Hertz and the History Channel, it is also leaving for an Omnicom-owned agency, the BBDO South unit of BBDO Worldwide. BBDO South in Atlanta, which handles corporate advertising for Georgia-Pacific, will assume additional duties for brands like Angel Soft toilet tissue and Sparkle paper towels, said Ken Haldin, a spokesman for Georgia-Pacific in Atlanta."
txtDog = "We saw the yellow dog"
txtDog2 = "the little yellow dog barked at the cat"
txtDog2 = "the little yellow dog barked at the funny girl"
txtDog2_fr = "le petit chien jaune aboie sur la fille rieuse"

listEGFrEn = {
    "ADJ": "JJ",
    "DET": "DT",
    "V": "VBD",
    "U": "NN",
    "NC": "NN",
    "P": "IN",
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

# grammar try to match starting from beginning,
# NP: {<DT>?<JJ>*<NN>} will override later NP: {<DT>?<JJ>*<NN>} 
grammar = """
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
result = cp.parse(txtDogPosFr[0])
print(result)

def explore():
        
    s1 = """At eight o'clock on Thursday morning Arthur didn't feel very good."""
    s2 = "—Aucunement. Il les échange contre du millet. J' aime elsa et les haricots verts. Tu aimes les noix. Ils aiment les tableaux."

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
    print(nltk.boolean_ops())

        
    if 0:
        # need prover9 (linux only)
        read_expr = nltk.sem.Expression.fromstring
        SnF = read_expr('SnF')
        NotFnS = read_expr('-FnS')
        R = read_expr('SnF -> -FnS')
        prover = nltk.Prover9()
        prover.prove(NotFnS, [SnF, R])