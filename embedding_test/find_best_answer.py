# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import socket
import pickle 
import argparse

    
"""
About usage of embedding:    
    Search (where results are ranked by relevance to a query string)
    Clustering (where text strings are grouped by similarity)
    Recommendations (where items with related text strings are recommended)
    Anomaly detection (where outliers with little relatedness are identified)
    Diversity measurement (where similarity distributions are analyzed)
    Classification (where text strings are classified by their most similar label)
"""
        

import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools


api_key = misctools.getEnv("OPENAI_KEY",None,0);
if api_key == None:
    print("ERR: please pour your api key in the .env file")
    exit(-1)
openai.api_key = api_key


import pandas as pd
import numpy as np

from openai.embeddings_utils import get_embedding

def generateEmbedding():
    # imports
    import pandas as pd
    import tiktoken


    # embedding model parameters
    embedding_model = "text-embedding-ada-002"
    embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
    max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191


    # load & inspect dataset
    input_datapath = "data/fine_food_reviews_1k.csv"  # to save space, we provide a pre-filtered dataset
    df = pd.read_csv(input_datapath, index_col=0)
    df = df[["Time", "ProductId", "UserId", "Score", "Summary", "Text"]]
    df = df.dropna()
    df["combined"] = (
        "Title: " + df.Summary.str.strip() + "; Content: " + df.Text.str.strip()
    )
    print(df.head(2))


    # subsample to 1k most recent reviews and remove samples that are too long
    top_n = 1000
    df = df.sort_values("Time").tail(top_n * 2)  # first cut to first 2k entries, assuming less than half will be filtered out
    df.drop("Time", axis=1, inplace=True)

    encoding = tiktoken.get_encoding(embedding_encoding)

    # omit reviews that are too long to embed
    df["n_tokens"] = df.combined.apply(lambda x: len(encoding.encode(x)))
    df = df[df.n_tokens <= max_tokens].tail(top_n)
    print(len(df))



    # Ensure you have your API key set in your environment per the README: https://github.com/openai/openai-python#usage

    # This may take a few minutes
    df["embedding"] = df.combined.apply(lambda x: get_embedding(x, engine=embedding_model))
    df.to_csv("data/fine_food_reviews_with_embeddings_1k.csv")


def loadFile():
    print("Loading file...")
    datafile_path = "data/fine_food_reviews_with_embeddings_1k.csv"

    df = pd.read_csv(datafile_path)
    df["embedding"] = df.embedding.apply(eval).apply(np.array)
    return df


# search through the reviews for a specific product
def search_reviews(df, product_description, n=3, pprint=True):
    from openai.embeddings_utils import get_embedding, cosine_similarity

    print("Searching review...")
    product_embedding = get_embedding(
        product_description,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)
        .combined.str.replace("Title: ", "")
        .str.replace("; Content:", ": ")
    )
    if pprint:
        for r in results:
            print(r[:200])
            print()
    return results


if 0:
    # load reviews and find some matching words 
    df = loadFile()
    results = search_reviews(df, "delicious beans", n=3)
    results = search_reviews(df, "pet food", n=3)
    
    
if 0:
    COMPLETIONS_MODEL = "text-davinci-003"
    # ask questions
    # prompt = """Answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, say "I don't know" """
    prompt = """Repond a la question le plus vraisemblablement possible en utilisant le texte donn�, et si la r�ponse n'est pas donn� dans le text ci dessous, dit "Je ne sais pas" """
    # this prompt work fine:
    #~ prompt += "Context: I have a son nammed Corto and a daughter nammed Gaia. I also have a cats nammed H'Batman and another one nammed Himalya"
    # this prompt doesn't work:
    #~ prompt += "Context: I have a son nammed Corto. I also have a cats nammed H'Batman and another one nammed Himalya. I also have a daughter named Gaia."
    
    prompt += "Context: J'ai un garcon, son nom est Corto et une fille nomm�e Gaia. J'ai aussi un chat nomm� H'Batman et un autre nomm� Himalya"
    
    if 0:
        prompt += "\nContext:"
        prompt += "\n* I have a son, his name is Corto"
        prompt += "\n* I also have a cats nammed H'Batman and another one nammed Himalya"
        prompt += "\n* I also have a daughter named Gaia." # forget the minuscul at gaia and you loose the info
        # with this prompt the answer become I have kids instead of YOU
    prompt += "\nQ: Do I have kids?"
    #~ prompt += "\nQ: Do I have a car?" # => I don't know.
    #~ prompt += "\nQ: Est ce que j'ai une voiture?" # => Je ne sais pas
    #~ prompt += "\nQ: Est ce que j'ai des enfants?" # => Je ne sais pas
    prompt += "\nA:"
    ret = openai.Completion.create(
        prompt=prompt,
        temperature=0, # variety of the answer: 0 always same, 1: more original answer (less probability of occurence)
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=COMPLETIONS_MODEL
    )
    print(ret["choices"][0]["text"].strip(" \n"))
    
    """
    Some answers:
    Yes, you have a son named Corto and a daughter named Gaia.
    
    Yes, you have two kids, a son named Corto and a daughter named Gaia.
    Yes, you have a son named Corto and a daughter named Gaia.
    
    #prompt en francais, mais question en anglais,fonctionne mieux que question en francais!
    Non, tu n'as pas d'enfants. Tu as un gar�on nomm� Corto et une fille nomm�e Gaia, mais pas d'enfants.
    Non, tu n'as pas d'enfants. Tu as un gar�on et une fille, mais aussi un chat et un autre chat.
    
    # en jouant avec la temperature:
    Non, vous n'avez pas d'enfants. Vous avez un gar�on nomm� Corto, une fille nomm�e Gaia, un chat nomm� H'Batman et un autre nomm� Himalya.
    """
    

"""

As seen in https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

creer une base de phrase avec embedding cf generateEmbedding
puis chercher parmi lesquelles celle qui contiennent des mot similaires a la question comme dans search_reviews
puis lancer une completion en donnant pour context les phrases.

Selected 2 document sections :
("Athletics at the 2020 Summer Olympics � Men's high jump", 'Summary')
("Athletics at the 2020 Summer Olympics � Men's long jump", 'Summary')
===
 Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."

Context:

* The men's high jump event at the 2020 Summer Olympics took place between 30 July and 1 August 2021 at the Olympic Stadium. 33 athletes from 24 nations competed; the total possible number depended on how many nations would use universality places to enter athletes in addition to the 32 qualifying through mark or ranking (no universality places were used in 2021). Italian athlete Gianmarco Tamberi along with Qatari athlete Mutaz Essa Barshim emerged as joint winners of the event following a tie between both of them as they cleared 2.37m. Both Tamberi and Barshim agreed to share the gold medal in a rare instance where the athletes of different nations had agreed to share the same medal in the history of Olympics. Barshim in particular was heard to ask a competition official "Can we have two golds?" in response to being offered a 'jump off'. Maksim Nedasekau of Belarus took bronze. The medals were the first ever in the men's high jump for Italy and Belarus, the first gold in the men's high jump for Italy and Qatar, and the third consecutive medal in the men's high jump for Qatar (all by Barshim). Barshim became only the second man to earn three medals in high jump, joining Patrik Sj�berg of Sweden (1984 to 1992).
* The men's long jump event at the 2020 Summer Olympics took place between 31 July and 2 August 2021 at the Japan National Stadium. Approximately 35 athletes were expected to compete; the exact number was dependent on how many nations use universality places to enter athletes in addition to the 32 qualifying through time or ranking (1 universality place was used in 2016). 31 athletes from 20 nations competed. Miltiadis Tentoglou won the gold medal, Greece's first medal in the men's long jump. Cuban athletes Juan Miguel Echevarr�a and Maykel Mass� earned silver and bronze, respectively, the nation's first medals in the event since 2008.

 Q: Who won the 2020 Summer Olympics men's high jump?
 A:

"""

def compute_num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

#~ compute_num_tokens_from_string("tiktoken is great!", "cl100k_base")


def getEmbeddingForLists( listSentences, engine ):
    listEmbed = []
    for s in listSentences:
        embed = get_embedding(s, engine=engine)
        listEmbed.append(embed)
    return listEmbed


def printEmbed(v):
    #~ print(len(v))
    for r in v[:8]:
        print("%.04f, " % r, end="" )
    print("...")
    
if 0:
    """
    info sur l'embedding:
    https://openai.com/blog/introducing-text-and-code-embeddings/
    
    An embedding is a vector (list) of floating point numbers.
    
    # comment evaluer un embedding
    https://github.com/facebookresearch/SentEval
    
    example above:
    """

    import openai, numpy as np
    
    #~ resp = openai.Embedding.create(
        #~ input=["feline friends go", "meow"],
        #~ engine="text-similarity-davinci-001")
    
    to_compare = [
                    ["feline friends go", "meow"],
                    ["feline friends go", "whouwhou"],
                    ["J'ai faim", "J'ai envie de manger"],
                    ["J'ai faim", "I'm hungry"],
                    ["J'ai faim", "I'm very hungry"],
                    ["J'ai tr�s faim", "I'm very hungry"],
                    ["J'ai faim", "J'ai envie de boire"],
                    ["J'ai faim", "J'ai envie de faire pipi"],
                    ["I need to pee", "J'ai envie de faire pipi"],
                    ["J'ai un garcon", "I have a kids"],
                    ["J'ai un garcon nomm� Corto", "Quel est le nom de ton garcon?"],
                    ["J'ai un garcon nom� Corto", "Quel est le nom de ton garcon?"],
                    ["Mon fils s'appelle Corto", "Quel est le nom de ton garcon?"],
                    ["Mon fils s'appelle Corto", "Quel est le nom de ton fils?"],
                    ["Ma fille s'appelle Gaia", "Quel est le nom de ton garcon?"],
                    ["Ma chat s'appelle H'Batman", "Quel est le nom de ton garcon?"],
                    ["my son is nammed Corto", "Quel est le nom de ton garcon?"],
                    ["my son is Corto", "What it the name of your son?"],
                    ["my son is Corto", "What it the name of your boy?"],
                    ["my son is Corto", "What it the name of your kids?"],
                    ["my son is Corto", "Quel sont les noms de tes enfants?"],
                    ["I have a boy", "Quel sont les noms de tes enfants?"],
                ]

    if 1:
        print("\n*** pair comparing:")
        for pair in to_compare:
            resp = openai.Embedding.create(
                input=pair,
                engine="text-similarity-davinci-001")

            embedding_a = resp['data'][0]['embedding']
            embedding_b = resp['data'][1]['embedding']
            printEmbed(embedding_a)
            printEmbed(embedding_b)
            
            similarity_score = np.dot(embedding_a, embedding_b)
            print("similarity_score %s: %.2f" % (str(pair),similarity_score ))
        
        
    print("\n*** answer findings:")
    strModelName = "text-similarity-davinci-001"
    strModelName = "text-search-davinci-query-001" # best result for this example
    #~ strModelName = "text-search-davinci-doc-001"
    strModelName = "text-embedding-ada-002" # peut etre vaguement mieux et prend up to 8191 tokens (use cl100k_base) cd compute_num_tokens_from_string pour savoir combien il y a de token dans une phrase
    
    # Limitation: Models lack knowledge of events that occurred after August 2020.
    
    #~ We recommend cosine similarity. The choice of distance function typically doesn�t matter much.

    #~ OpenAI embeddings are normalized to length 1, which means that:

    #~ Cosine similarity can be computed slightly faster using just a dot product
    #~ Cosine similarity and Euclidean distance will result in the identical rankings
    
    print("computing answer vectors...")
    listAns = []
    for pair2 in to_compare:
        listAns.append(pair2[0])
    listAns = list(set(listAns))
    
    bStandardCall = 1  # more limit with the standard ?
    bStandardCall = 0
    
    if bStandardCall:
        embedAns = openai.Embedding.create( input=listAns, engine=strModelName)
        o = []
        for d in embedAns['data']:
            o.append(d['embedding'])
        embedAns = o
    else:
        embedAns = getEmbeddingForLists( listAns, engine=strModelName )
    
    
    print("comparing using model %s:" % strModelName)
    listQ = []
    for pair2 in to_compare:
        listQ.append(pair2[1])
    listQ = sorted(list(set(listQ)))
    for q in listQ:
        if bStandardCall:
            resp = openai.Embedding.create( input=[q], engine=strModelName)
            vQ = resp['data'][0]['embedding']
        else:
            vQ = getEmbeddingForLists( [q], engine=strModelName )


        maxSimilarity = 0
        for numAns,vAns in enumerate(embedAns):
            simi = np.dot(vQ,vAns)
            if simi > maxSimilarity:
                maxSimilarity = simi
                ans = listAns[numAns]
        print("q: %s, a: %s, simi: %.2f" % (q,ans,maxSimilarity))
        
"""
*** pair comparing:
similarity_score ['feline friends go', 'meow']: 0.86
similarity_score ['feline friends go', 'whouwhou']: 0.77
similarity_score ["J'ai faim", "J'ai envie de manger"]: 0.93
similarity_score ["J'ai faim", "I'm hungry"]: 0.92
similarity_score ["J'ai faim", "I'm very hungry"]: 0.91
similarity_score ["J'ai tr�s faim", "I'm very hungry"]: 0.92
similarity_score ["J'ai faim", "J'ai envie de boire"]: 0.86
similarity_score ["J'ai faim", "J'ai envie de faire pipi"]: 0.83
similarity_score ['I need to pee', "J'ai envie de faire pipi"]: 0.88
similarity_score ["J'ai un garcon", 'I have a kids']: 0.82
similarity_score ["J'ai un garcon nomm� Corto", 'Quel est le nom de ton garcon?']: 0.83
similarity_score ["J'ai un garcon nom� Corto", 'Quel est le nom de ton garcon?']: 0.83
similarity_score ["Mon fils s'appelle Corto", 'Quel est le nom de ton garcon?']: 0.81
similarity_score ["Mon fils s'appelle Corto", 'Quel est le nom de ton fils?']: 0.81
similarity_score ["Ma fille s'appelle Gaia", 'Quel est le nom de ton garcon?']: 0.73
similarity_score ["Ma chat s'appelle H'Batman", 'Quel est le nom de ton garcon?']: 0.71
similarity_score ['my son is nammed Corto', 'Quel est le nom de ton garcon?']: 0.77
similarity_score ['my son is Corto', 'What it the name of your son?']: 0.78
similarity_score ['my son is Corto', 'What it the name of your boy?']: 0.76
similarity_score ['my son is Corto', 'What it the name of your kids?']: 0.71
similarity_score ['my son is Corto', 'Quel sont les noms de tes enfants?']: 0.72
similarity_score ['I have a boy', 'Quel sont les noms de tes enfants?']: 0.70

*** answer findings:
computing answer vectors...
comparing...
q: meow, a: feline friends go, simi: 0.86
q: whouwhou, a: I have a boy, simi: 0.79
q: J'ai envie de manger, a: J'ai faim, simi: 0.93
q: I'm hungry, a: J'ai faim, simi: 0.92
q: I'm very hungry, a: J'ai tr�s faim, simi: 0.92
q: I'm very hungry, a: J'ai tr�s faim, simi: 0.92
q: J'ai envie de boire, a: J'ai tr�s faim, simi: 0.86
q: J'ai envie de faire pipi, a: I need to pee, simi: 0.88
q: J'ai envie de faire pipi, a: I need to pee, simi: 0.88
q: I have a kids, a: I have a boy, simi: 0.89
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel est le nom de ton fils?, a: J'ai un garcon, simi: 0.82
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: What it the name of your son?, a: I have a boy, simi: 0.79
q: What it the name of your boy?, a: I have a boy, simi: 0.84
q: What it the name of your kids?, a: I have a boy, simi: 0.72
q: Quel sont les noms de tes enfants?, a: J'ai un garcon, simi: 0.76
q: Quel sont les noms de tes enfants?, a: J'ai un garcon, simi: 0.76

comparing using model text-similarity-davinci-001:
q: I have a kids, a: I have a boy, simi: 0.89
q: I'm hungry, a: J'ai faim, simi: 0.92
q: I'm very hungry, a: J'ai tr�s faim, simi: 0.92
q: J'ai envie de boire, a: J'ai tr�s faim, simi: 0.86
q: J'ai envie de faire pipi, a: I need to pee, simi: 0.88
q: J'ai envie de manger, a: J'ai faim, simi: 0.93
q: Quel est le nom de ton fils?, a: J'ai un garcon, simi: 0.82
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.86
q: Quel sont les noms de tes enfants?, a: J'ai un garcon, simi: 0.76
q: What it the name of your boy?, a: I have a boy, simi: 0.84
q: What it the name of your kids?, a: I have a boy, simi: 0.72
q: What it the name of your son?, a: I have a boy, simi: 0.79
q: meow, a: feline friends go, simi: 0.86
q: whouwhou, a: I have a boy, simi: 0.79

comparing using model text-search-davinci-query-001:
q: I have a kids, a: I have a boy, simi: 0.80
q: I'm hungry, a: J'ai faim, simi: 0.86
q: I'm very hungry, a: J'ai tr�s faim, simi: 0.86
q: J'ai envie de boire, a: J'ai faim, simi: 0.80
q: J'ai envie de faire pipi, a: I need to pee, simi: 0.80
q: J'ai envie de manger, a: J'ai tr�s faim, simi: 0.86
q: Quel est le nom de ton fils?, a: Mon fils s'appelle Corto, simi: 0.80
q: Quel est le nom de ton garcon?, a: J'ai un garcon nomm� Corto, simi: 0.80
q: Quel sont les noms de tes enfants?, a: Ma fille s'appelle Gaia, simi: 0.75
q: What it the name of your boy?, a: I have a boy, simi: 0.77
q: What it the name of your kids?, a: my son is nammed Corto, simi: 0.68
q: What it the name of your son?, a: my son is nammed Corto, simi: 0.74
q: meow, a: I need to pee, simi: 0.72
q: whouwhou, a: J'ai faim, simi: 0.65

comparing using model text-search-davinci-doc-001:
q: I have a kids, a: I have a boy, simi: 0.88
q: I'm hungry, a: J'ai faim, simi: 0.85
q: I'm very hungry, a: I need to pee, simi: 0.86
q: J'ai envie de boire, a: J'ai tr�s faim, simi: 0.87
q: J'ai envie de faire pipi, a: J'ai tr�s faim, simi: 0.84
q: J'ai envie de manger, a: J'ai tr�s faim, simi: 0.91
q: Quel est le nom de ton fils?, a: Mon fils s'appelle Corto, simi: 0.79
q: Quel est le nom de ton garcon?, a: J'ai un garcon nom� Corto, simi: 0.81
q: Quel sont les noms de tes enfants?, a: J'ai un garcon nomm� Corto, simi: 0.74
q: What it the name of your boy?, a: my son is nammed Corto, simi: 0.74
q: What it the name of your kids?, a: my son is nammed Corto, simi: 0.72
q: What it the name of your son?, a: my son is nammed Corto, simi: 0.75
q: meow, a: J'ai faim, simi: 0.74
q: whouwhou, a: J'ai faim, simi: 0.77

comparing using model text-embedding-ada-002:
q: I have a kids, a: I have a boy, simi: 0.90
q: I'm hungry, a: J'ai faim, simi: 0.91
q: I'm very hungry, a: J'ai tr�s faim, simi: 0.92
q: J'ai envie de boire, a: J'ai faim, simi: 0.89
q: J'ai envie de faire pipi, a: J'ai faim, simi: 0.88
q: J'ai envie de manger, a: J'ai faim, simi: 0.95
q: Quel est le nom de ton fils?, a: Mon fils s'appelle Corto, simi: 0.87
q: Quel est le nom de ton garcon?, a: J'ai un garcon, simi: 0.89
q: Quel sont les noms de tes enfants?, a: Mon fils s'appelle Corto, simi: 0.83
q: What it the name of your boy?, a: I have a boy, simi: 0.89
q: What it the name of your kids?, a: my son is nammed Corto, simi: 0.82
q: What it the name of your son?, a: my son is nammed Corto, simi: 0.86
q: meow, a: feline friends go, simi: 0.86
q: whouwhou, a: feline friends go, simi: 0.79


"""

if 0:
    # BPE encoding
    import tiktoken
    enc = tiktoken.get_encoding("gpt2")
    encoded = enc.encode("hello world")
    print("encoded gpt2: " + str(encoded))
    assert enc.decode(encoded) == "hello world"
    
    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = tiktoken.encoding_for_model("text-davinci-003")
    encoded = enc.encode("hello world")
    print("encoded d3: " + str(encoded))
    assert enc.decode(encoded) == "hello world"

    encoded = enc.encode("J'ai un fils")
    print("encoded sent0: " + str(encoded))
    
    encoded = enc.encode("J'ai un fils.")
    print("encoded sent0.: " + str(encoded))
    
    encoded = enc.encode("J'ai un fils qui aime jouer avec les voitures de courses")
    print("encoded sent1: " + str(encoded))

    encoded = enc.encode("J'ai un fils qui aime jouer avec les fils a coudre")
    print("encoded sent2: " + str(encoded))
    
    
if 0:
    import json
    
    print("test sur oia faq_informatique")
    
    bUseOpenAI = 1 # else it's camembert
    bUseOpenAI = 0
    
    if not bUseOpenAI:
        #~ sys.path.append("../../obo/camembert")
        #~ from bert_test_similarity import camEmbedList
        sys.path.append("../camembert")
        from sentence_embedding import camEmbedList

    
    def saveEmbed(fn,data):
        f = open(fn,"wt")
        f.write(json.dumps(data))
        f.close()
        
    def loadEmbed(fn):
        f = open(fn,"rt")
        buf = f.read()
        data = json.loads(buf)
        if 0:
            print("DBG: loadEmbed: converting...")
            # convert to numpy
            print("DBG: loadEmbed: len data: %s" % len(data))
            print("DBG: loadEmbed: len data[0]: %s" % len(data[0]))
            for i in range(3):
                print("DBG: loadEmbed: type data0: %s" % type(data[0][i]))
                print("DBG: loadEmbed: data0: %s" % str(data[0][i]))
            
            for j in range(len(data)):
                for i in range(len(data[j])):
                    data[j][i] = float(data[j][i])
        f.close()
        return data
        
    strModelName = "text-search-davinci-query-001"
        
        
    sys.path.append("../oia/")
    import chatbot_simple3
    faq = chatbot_simple3.loadFaqSimple("../oia/faq_informatique.txt")

    listq = [item[0] for item in faq]

    if bUseOpenAI: fn_embed = "faq_informatique_embed_openai.txt"
    else: fn_embed = "faq_informatique_embed_camembert.txt"
    if not os.path.isfile(fn_embed):
        print("generating embedding to %s..." % fn_embed)
        if bUseOpenAI: embedQ = getEmbeddingForLists( listq, engine = strModelName )
        else: embedQ = camEmbedList( listq )
        saveEmbed(fn_embed,embedQ)
    else:
       print("loading from %s..." % fn_embed)
       embedQ = loadEmbed(fn_embed)
       
       
    # result simi avec openai gpt3 / puis avec camembert (gpt2?)
    # camembert a seulement 512 float et gpt3 12k (24 fois plus)
    # Camembert: on remarque qu'on a une erreur et dans ce cas la la simi est < 0.2
    q = "parle moi de la m�moire vive" # => Qu'est ce que La m�moire morte 0.8 / 0.35
    q = "parle moi de la calculatrice" # => O� trouve-t-on la calculatrice?, simi: 0.85 / 0.26
    q = "J'ai besoin de faire des calculs" # => O� trouve-t-on la calculatrice?, simi: 0.78 / 0.32
    q = "J'ai besoin de faire des multiplication" # => O� trouve-t-on la calculatrice?, simi: 0.27
    q = "J'ai besoin de faire 16*16" # => O� trouve-t-on la calculatrice?, simi: 0.66 / Citez 4 raccourcis clavier, 0.14; O� trouve-t-on la calculatrice? est a 0.10
    q = "J'ai besoin d'envoyer un email" # => Que doit contenir obligatoirement une adresse mail ?, simi: 0.76 / 0.38
    q = "J'ai besoin d'envoyer un courrier electronique" # => Que doit contenir obligatoirement une adresse mail ?, simi: 0.76 / 0.37
    if bUseOpenAI: vQ = getEmbeddingForLists( [q], engine = strModelName )[0]
    else: vQ = camEmbedList( [q] )
    print(type(embedQ))
    print(type(vQ))
    print(type(embedQ[0]))
    print(type(vQ[0]))
    print(type(embedQ[0][0]))
    print(type(vQ[0][0]))
    
    print(len(embedQ))
    print(len(vQ))
    print(len(embedQ[0]))
    print(len(vQ[0]))
    
    #~ print(embedQ[0].shape)
    #~ print(vQ[0].shape)
    
    maxSimilarity = 0
    maxIdx = -1
    for num,v in enumerate(embedQ):
        simi = np.dot(vQ[0],v)
        ans = faq[num][0]
        print("simi: %.2f, %s" % (simi, ans))
        if simi > maxSimilarity:
            maxSimilarity = simi
            maxAns = ans
            maxIdx = num
    print("")
    print("q: %s\nqref: %s\nsimi: %.2f" % (q,maxAns,maxSimilarity))
    print("answer: %s" % faq[maxIdx][1])
    
    
if 1:
    print("\n\n Test sur faq en vrac\n\n")
    sys.path.append("../camembert")
    import sentence_embedding

    sys.path.append("../oia/")
    import chatbot_simple3
    faq1 = chatbot_simple3.loadFaqSimple("../oia/faq_informatique.txt")
    faq2 = chatbot_simple3.loadFaqSimple("./faq_drh.txt")
    faq3 = chatbot_simple3.loadFaqSimple("./faq_vrac.txt")
    faq = faq1+faq2+faq3
    faq = faq2

    listQ = [item[0] for item in faq]
    
    for n,qa in enumerate(listQ):
        print("%d: %s" % (n,qa))
    
    listQTest = [
                        "J'ai besoin d'envoyer un email",
                        "Je suis handicap�.",
                        "J'ai 50 ans",
                        "Je suis v�g�tarien.",
                        "Quelles sont les limitations sur la pose de cong�s?",
                        "Quelles sont les limitations sur la pose de vacances?",
                        "Quel sont les limitaton sur la pause de vacance?",
                        "J'aurai des responsabilit�es?"

                    ]
    
    listEmb = sentence_embedding.generateEmbedListCached(listQ,"faq_vrac_embed_camembert.txt")
    
    for q in listQTest:
        bests = sentence_embedding.getBests(q,listEmb)
        print("\nDBG: faqVrac: bests: %s" % bests)
        #~ print("DBG: faqVrac: refs: %s and %s" % (faq[bests[0][0]],faq[bests[1][0]]))
        imax = bests[0][0]
        simi = bests[0][1]
        conf = min(simi/0.36,1.)
        qref,aref = faq[imax]
        print("# 1: faqVrac: %s =>\n%d: %s\n%s\n(conf: %.2f)" % (q,imax,qref,aref,conf ) )
        imax2 = bests[1][0]
        simi2 = bests[1][1]
        conf2 = min(simi2/0.36,1.)
        qref2,aref2 = faq[imax2]
        print("# 2: faqVrac: %s =>\n%d: %s\n%s\n(conf: %.2f)" % (q,imax2,qref2,aref2,conf2 ) )
        

"""
DBG: faqVrac: bests: [(34, 0.3819858172588727), (35, 0.14339179273520386)]
# 1: faqVrac: J'ai besoin d'envoyer un email =>
34: Que doit contenir obligatoirement une adresse mail ?
une adresse email doit toujours contenir un arobase, c'est a dire le caractere special ou symbol: "@"
(conf: 1.00)
# 2: faqVrac: J'ai besoin d'envoyer un email =>
35: Puis je poser mes cong�s de mani�re r�troactive ?
Les cong�s doivent �tre pos� 3 jours � l'avance pour des raisons d'assurances.
(conf: 0.40)

DBG: faqVrac: bests: [(40, 0.17489819483113084), (37, 0.1489064417242786)]
# 1: faqVrac: Je suis handicap�. =>
40: Je suis en situation de handicap : un restaurateur peut-il me refuser l�acc�s � son �tablissement ?
Un restaurateur ne peut refuser l�acc�s � son �tablissement pour des motifs discriminatoires (religion, race, etc.), ni du fait de la pr�sence d�enfants.
(conf: 0.49)
# 2: faqVrac: Je suis handicap�. =>
37: Puis-je refus� un candidat car il est trop vieux.
En france il est interdit de juger de la qualit� d'un candidat uniquement en fonction de son age.
(conf: 0.41)

DBG: faqVrac: bests: [(6, 0.17427715375144598), (41, 0.15232267567338456)]
# 1: faqVrac: Je suis v�g�tarien. =>
6: Qu'est ce qu'une puce 
Symbole marquant le d�but d'une ligne dans le cadre entre autre d'une liste
(conf: 0.48)
# 2: faqVrac: Je suis v�g�tarien. =>
41: Je souhaite manger seul au restaurant. Puis-je me voir opposer un refus du restaurateur ?
Un restaurateur ne peut pas refuser de vous servir du fait que vous �tes seul. Cependant, vous serez contraint d�accepter la table propos�e.
(conf: 0.42)

DBG: faqVrac: bests: [(23, 0.246399040562425), (45, 0.24355220346289008)]
# 1: faqVrac: Quels sont les limitations sur la pose de cong�s? =>
23: A quoi reconna�t-t-on un raccourci ?
� la fl�che bleu en bas � gauche de l'icone
(conf: 0.68)
# 2: faqVrac: Quels sont les limitations sur la pose de cong�s? =>
45: Qu'est ce que le Management de Transition ?
Le Management de Transition : C�est un accompagnement temporaire et � temps plein d�un Directeur qui doit s�absenter pour de longs mois et dont l�absence p�nalise l�entreprise.
(conf: 0.68)

DBG: faqVrac: bests: [(46, 0.23275017776430346), (44, 0.2286323657259607)]
# 1: faqVrac: Quels sont les limitations sur la pose de vacances? =>
46: Qu'est ce que le Temps Partag� Augment� ?
Le Temps partag� Augment� : C�est une cr�ation du Groupe Reference. C�est un accompagnement � temps partiel ou temps plein qui peut se r�aliser sur quelques mois, le temps du d�veloppement complet de l�entreprise, � plusieurs ann�es. Certains de nos clients utilisent cette solution depuis la naissance du Groupe montrant que c�est aussi une solution p�renne ! Il est augment� de par la multiplicit� des services propos�s qu�un ind�pendant ne peut pas proposer.
(conf: 0.65)
# 2: faqVrac: Quels sont les limitations sur la pose de vacances? =>
44: Qu'est ce que le Temps Partag� ?
Le Temps partag� : Ce terme d�signe une organisation du travail d�une personne (salari�e ou non) entre diff�rentes entreprises. Un freelance qui travaille pour plusieurs entreprises en tant que DRH est de facto en temps partag�. Son temps est partag� entre les entreprises qui elles, l�utilisent � temps partiel.
(conf: 0.64)

"""

if 0:
    # generation de simi et de proximit� pour des presentations:
    sys.path.append("../camembert")
    import sentence_embedding
    listTxt = [
        "J'ai faim",
        "J'ai soif",
        "J'ai envie de faire pipi",
        "Quel est le nom du pr�sident de la r�publique francaise?",
        "2+2=4",
        "Etes vous fort en math?",
        "Les calculs c'est mon dada",
        "I'm hungry",
        "Gaston Deferre est un homme politique francais mort en 1953",
        "Barack Obama was the president of the united states",
        "I'm very thirsty",
        "J'ai tr�s faim",
        "Ich bin hungrig", # j'ai faim en allemand
        "ho fame", # j'ai faim en italien
    ]
    
    listEmb = sentence_embedding.generateEmbedListCached(listTxt,"tuto_embed_camembert.txt")
    
    for s1 in listTxt:
        # camembert: 512 floats
        #~ bests = sentence_embedding.getBests(q,listEmb)
        #~ print("\nDBG: tuto: bests: %s" % bests)
        #~ imax = bests[0][0]
        #~ simi = bests[0][1]
        #~ conf = min(simi/0.36,1.)
        #~ smax = listTxt[imax]
        #~ print("# 1: faqVrac: %s => %d: %s (conf: %.2f)" % (q,imax,smax, conf ) )
        #~ imax2 = bests[1][0]
        #~ simi2 = bests[1][1]
        #~ conf2 = min(simi2/0.36,1.)
        #~ smax2 = listTxt[imax2]
        #~ print("# 2: faqVrac: %s => %d: %s (conf: %.2f)" % (q,imax2,smax2, conf2 ) )
        for s2 in listTxt:
            if s1==s2: continue
            simi = sentence_embedding.getSimiSentences(s1,s2)
            #~ print("similarity '%s' and '%s': %.2f" % (s1,s2,simi) )
            print("'%s' / '%s'  =>  %.2f" % (s1,s2,simi) )

    

        
    
    
    