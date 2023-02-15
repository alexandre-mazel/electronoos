# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import socket
import pickle 
import argparse

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

def generateEmbedding():
    # imports
    import pandas as pd
    import tiktoken

    from openai.embeddings_utils import get_embedding

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
    
    
if 1:
    COMPLETIONS_MODEL = "text-davinci-003"
    # ask questions
    prompt = """Answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, say "I don't know" """
    # this prompt work fine:
    prompt += "Context: I have a son nammed Corto and a daughter nammed Gaia. I also have a cats nammed H'Batman and another one nammed Himalya"
    # this prompt doesn't work:
    #~ prompt += "Context: I have a son nammed Corto. I also have a cats nammed H'Batman and another one nammed Himalya. I also have a daughter named Gaia."
    
    if 0:
        prompt += "\nContext:"
        prompt += "\n* I have a son, his name is Corto"
        prompt += "\n* I also have a cats nammed H'Batman and another one nammed Himalya"
        prompt += "\n* I also have a daughter named Gaia." # forget the minuscul at gaia and you loose the info
        # with this prompt the answer become I have kids instead of YOU
    prompt += "\nQ: Do I have kids?"
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
    """
    
"""
As seen in https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

creer une base de phrase avec embedding cf generateEmbedding
puis chercher parmi lesquelles celle qui contiennent des mot similaires a la question comme dans search_reviews
puis lancer une completion en donnant pour context les phrases.

Selected 2 document sections :
("Athletics at the 2020 Summer Olympics – Men's high jump", 'Summary')
("Athletics at the 2020 Summer Olympics – Men's long jump", 'Summary')
===
 Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."

Context:

* The men's high jump event at the 2020 Summer Olympics took place between 30 July and 1 August 2021 at the Olympic Stadium. 33 athletes from 24 nations competed; the total possible number depended on how many nations would use universality places to enter athletes in addition to the 32 qualifying through mark or ranking (no universality places were used in 2021). Italian athlete Gianmarco Tamberi along with Qatari athlete Mutaz Essa Barshim emerged as joint winners of the event following a tie between both of them as they cleared 2.37m. Both Tamberi and Barshim agreed to share the gold medal in a rare instance where the athletes of different nations had agreed to share the same medal in the history of Olympics. Barshim in particular was heard to ask a competition official "Can we have two golds?" in response to being offered a 'jump off'. Maksim Nedasekau of Belarus took bronze. The medals were the first ever in the men's high jump for Italy and Belarus, the first gold in the men's high jump for Italy and Qatar, and the third consecutive medal in the men's high jump for Qatar (all by Barshim). Barshim became only the second man to earn three medals in high jump, joining Patrik Sjöberg of Sweden (1984 to 1992).
* The men's long jump event at the 2020 Summer Olympics took place between 31 July and 2 August 2021 at the Japan National Stadium. Approximately 35 athletes were expected to compete; the exact number was dependent on how many nations use universality places to enter athletes in addition to the 32 qualifying through time or ranking (1 universality place was used in 2016). 31 athletes from 20 nations competed. Miltiadis Tentoglou won the gold medal, Greece's first medal in the men's long jump. Cuban athletes Juan Miguel Echevarría and Maykel Massó earned silver and bronze, respectively, the nation's first medals in the event since 2008.

 Q: Who won the 2020 Summer Olympics men's high jump?
 A:

"""
