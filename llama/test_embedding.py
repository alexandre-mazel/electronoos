# -*- coding: cp1252 -*-


if 0:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_id = "meta-llama/Llama-2-7b-chat-hf"
    model_id = "llama3.2"

    t = AutoTokenizer.from_pretrained(model_id)
    t.pad_token = t.eos_token
    m = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto", device_map="auto" )
    m.eval()


    texts = [
        "this is a test",
        "this is another test case with a different length",
    ]
    t_input = t(texts, padding=True, return_tensors="pt")


    with torch.no_grad():
        last_hidden_state = m(**t_input, output_hidden_states=True).hidden_states[-1]


    weights_for_non_padding = t_input.attention_mask * torch.arange(start=1, end=last_hidden_state.shape[1] + 1).unsqueeze(0)

    sum_embeddings = torch.sum(last_hidden_state * weights_for_non_padding.unsqueeze(-1), dim=1)
    num_of_none_padding_tokens = torch.sum(weights_for_non_padding, dim=-1).unsqueeze(-1)
    sentence_embeddings = sum_embeddings / num_of_none_padding_tokens

    print(t_input.input_ids)
    print(weights_for_non_padding)
    print(num_of_none_padding_tokens)
    print(sentence_embeddings.shape)
    
    
# Reminder: use venv from ~/dev/llama_env + ollama server running internally
import requests
import json
import time
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
    
url = "http://localhost:11434/api/chat"
strModel = "nomic-embed-text" # size: 274MB, running: 370MB (output size: 768)
strModel = "mxbai-embed-large" # size: 669MB, running: 704MB (output size: 1024)
#~ strModel = "bge-large" # size: 670MB, running: 739MB (output size: 1024)

# a etudier a l'occasion: 
# https://github.com/meta-llama/llama-recipes/tree/main/recipes/use_cases
# eg:
# https://github.com/meta-llama/llama-recipes/tree/main/recipes/use_cases/end2end-recipes/RAFT-Chatbot


# function moved to embedtools
    
v1 = llama3_embedding("hi guys!")
print("len vector: %s" % len(v1)) # vector is 768

if 0:
    text1 = "Hello, j'ai faim"
    text2 = "Hello, j'ai soif"
    text3 = "Hi I'm hungry"

    r = compare_two_texts(text1,text2)
    r = compare_two_texts(text1,text3)
    r = compare_two_texts(text2,text3)
    
texts = []
texts.append("Hi, My name is Alexandre")
texts.append("Hi, My name is Pierre")
texts.append("Salut, je m'appelle Pierre")
texts.append("Salut, les gens ont tendance a me nommer Alexandre")
texts.append("J'ai la grosse dalle")
texts.append("J'ai faim")
texts.append("Ich habe Hunger")
texts.append("Ich habe Durst")
texts.append("J'aimerais me sustenter")
texts.append("I'm hungry")
texts.append("Comment je pourrais calculer des sommes")
texts.append("Es-tu bon en calcul mental?")
texts.append("I would like to compute addition")
texts.append("2+2 = 4")
texts.append("Le président de la république est Macron")
texts.append("Qui est le dirigeant de la france")
texts.append("Qui est Obama?")
texts.append("Qui est Zidane?")
texts.append("Qui est Michael jackson?")
texts.append("Tu aimes la musique?")
texts.append("Tu aimes le sport?")
texts.append("Alexandre dumas a écrit les 3 mousquetaires")
texts.append("Connais tu des romanciers?")
texts.append("Do you know writers?")
texts.append("I know a very well known noveller")
texts.append("My girlfriend tend a bookshop")
texts.append("I like politics")
texts.append("I have a harry potter's book")
texts.append("Do you like sorcery?")
texts.append("Es tu marié?")
texts.append("are you single?")
texts.append("do you have some the cure's disk?")
    
compare_all(texts)
    
    
"""
mxbai-embed-large + cosine_similarity results:

Similar to 'Hi, My name is Alexandre'  is  'Hi, My name is Pierre'  with score 0.81
   2nd: is 'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.78 (95.8%)

Similar to 'Hi, My name is Pierre'  is  'Salut, je m'appelle Pierre'  with score 0.83
   2nd: is 'Hi, My name is Alexandre'  with score 0.81 (97.8%)

Similar to 'Salut, je m'appelle Pierre'  is  'Hi, My name is Pierre'  with score 0.83
   2nd: is 'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.73 (88.4%)

Similar to 'Salut, les gens ont tendance a me nommer Alexandre'  is  'Hi, My name is Alexandre'  with score 0.78
   2nd: is 'Salut, je m'appelle Pierre'  with score 0.73 (94.4%)

Similar to 'J'ai la grosse dalle'  is  'J'aimerais me sustenter'  with score 0.69
   2nd: is 'Comment je pourrais calculer des sommes'  with score 0.68 (98.9%)

Similar to 'J'ai faim'  is  'J'aimerais me sustenter'  with score 0.71
   2nd: is 'J'ai la grosse dalle'  with score 0.67 (95.1%)

Similar to 'Ich habe Hunger'  is  'I'm hungry'  with score 0.81
   2nd: is 'Ich habe Durst'  with score 0.78 (96.1%)

Similar to 'Ich habe Durst'  is  'Ich habe Hunger'  with score 0.78
   2nd: is 'J'aimerais me sustenter'  with score 0.63 (80.0%)

Similar to 'J'aimerais me sustenter'  is  'Comment je pourrais calculer des sommes'  with score 0.71
   2nd: is 'J'ai faim'  with score 0.71 (100.0%)

Similar to 'I'm hungry'  is  'Ich habe Hunger'  with score 0.81
   2nd: is 'J'aimerais me sustenter'  with score 0.61 (74.8%)

Similar to 'Comment je pourrais calculer des sommes'  is  'J'aimerais me sustenter'  with score 0.71
   2nd: is 'J'ai la grosse dalle'  with score 0.68 (96.0%)

Similar to 'Es-tu bon en calcul mental?'  is  'Comment je pourrais calculer des sommes'  with score 0.67
   2nd: is 'J'ai la grosse dalle'  with score 0.62 (91.6%)

Similar to 'I would like to compute addition'  is  '2+2 = 4'  with score 0.71
   2nd: is 'Es-tu bon en calcul mental?'  with score 0.57 (79.7%)

Similar to '2+2 = 4'  is  'I would like to compute addition'  with score 0.71
   2nd: is 'Es-tu bon en calcul mental?'  with score 0.53 (74.7%)

Similar to 'Le président de la république est Macron'  is  'Qui est le dirigeant de la france'  with score 0.72
   2nd: is 'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.62 (86.6%)

Similar to 'Qui est le dirigeant de la france'  is  'Le président de la république est Macron'  with score 0.72
   2nd: is 'Qui est Zidane?'  with score 0.70 (97.9%)

Similar to 'Qui est Obama?'  is  'Qui est Zidane?'  with score 0.72
   2nd: is 'Es tu marié?'  with score 0.67 (93.0%)

Similar to 'Qui est Zidane?'  is  'Qui est Obama?'  with score 0.72
   2nd: is 'Qui est le dirigeant de la france'  with score 0.70 (98.0%)

Similar to 'Qui est Michael jackson?'  is  'Qui est Obama?'  with score 0.66
   2nd: is 'Qui est Zidane?'  with score 0.66 (99.2%)

Similar to 'Tu aimes la musique?'  is  'Tu aimes le sport?'  with score 0.76
   2nd: is 'J'aimerais me sustenter'  with score 0.66 (86.9%)

Similar to 'Tu aimes le sport?'  is  'Tu aimes la musique?'  with score 0.76
   2nd: is 'Qui est Zidane?'  with score 0.68 (90.0%)

Similar to 'Alexandre dumas a écrit les 3 mousquetaires'  is  'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.62
   2nd: is 'Connais tu des romanciers?'  with score 0.60 (97.0%)

Similar to 'Connais tu des romanciers?'  is  'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.69
   2nd: is 'Salut, je m'appelle Pierre'  with score 0.61 (88.1%)

Similar to 'Do you know writers?'  is  'I know a very well known noveller'  with score 0.65
   2nd: is 'Es tu marié?'  with score 0.49 (74.2%)

Similar to 'I know a very well known noveller'  is  'Do you know writers?'  with score 0.65
   2nd: is 'I have a harry potter's book'  with score 0.59 (89.6%)

Similar to 'My girlfriend tend a bookshop'  is  'I have a harry potter's book'  with score 0.61
   2nd: is 'I know a very well known noveller'  with score 0.56 (92.3%)

Similar to 'I like politics'  is  'Hi, My name is Alexandre'  with score 0.55
   2nd: is 'Hi, My name is Pierre'  with score 0.55 (99.3%)

Similar to 'I have a harry potter's book'  is  'My girlfriend tend a bookshop'  with score 0.61
   2nd: is 'I know a very well known noveller'  with score 0.59 (96.3%)

Similar to 'Do you like sorcery?'  is  'do you have some the cure's disk?'  with score 0.51
   2nd: is 'I have a harry potter's book'  with score 0.48 (95.3%)

Similar to 'Es tu marié?'  is  'Qui est Obama?'  with score 0.67
   2nd: is 'Salut, je m'appelle Pierre'  with score 0.65 (97.8%)

Similar to 'are you single?'  is  'Es tu marié?'  with score 0.62
   2nd: is 'Connais tu des romanciers?'  with score 0.54 (87.2%)

Similar to 'do you have some the cure's disk?'  is  'Tu aimes la musique?'  with score 0.52
   2nd: is 'Do you like sorcery?'  with score 0.51 (96.7%)



Camembert:
Similar to 'Hi, My name is Alexandre'  is  'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.81
   2nd: is 'Hi, My name is Pierre'  with score 0.75 (93.3%)

Similar to 'Hi, My name is Pierre'  is  'Salut, je m'appelle Pierre'  with score 0.96
   2nd: is 'Hi, My name is Alexandre'  with score 0.75 (79.0%)

Similar to 'Salut, je m'appelle Pierre'  is  'Hi, My name is Pierre'  with score 0.96
   2nd: is 'Hi, My name is Alexandre'  with score 0.71 (74.2%)

Similar to 'Salut, les gens ont tendance a me nommer Alexandre'  is  'Hi, My name is Alexandre'  with score 0.81
   2nd: is 'Salut, je m'appelle Pierre'  with score 0.52 (64.5%)

Similar to 'J'ai la grosse dalle'  is  'Ich habe Durst'  with score 0.70
   2nd: is 'J'ai faim'  with score 0.66 (94.6%)

Similar to 'J'ai faim'  is  'I'm hungry'  with score 0.97
   2nd: is 'Ich habe Hunger'  with score 0.95 (98.8%)

Similar to 'Ich habe Hunger'  is  'I'm hungry'  with score 0.97
   2nd: is 'J'ai faim'  with score 0.95 (98.8%)

Similar to 'Ich habe Durst'  is  'J'ai faim'  with score 0.83
   2nd: is 'I'm hungry'  with score 0.80 (96.1%)

Similar to 'J'aimerais me sustenter'  is  'I would like to compute addition'  with score 0.55
   2nd: is 'J'ai faim'  with score 0.54 (97.9%)

Similar to 'I'm hungry'  is  'Ich habe Hunger'  with score 0.97
   2nd: is 'J'ai faim'  with score 0.97 (100.0%)

Similar to 'Comment je pourrais calculer des sommes'  is  'I would like to compute addition'  with score 0.56
   2nd: is 'Es-tu bon en calcul mental?'  with score 0.33 (59.5%)

Similar to 'Es-tu bon en calcul mental?'  is  'Do you like sorcery?'  with score 0.42
   2nd: is 'do you have some the cure's disk?'  with score 0.40 (94.1%)

Similar to 'I would like to compute addition'  is  'Comment je pourrais calculer des sommes'  with score 0.56
   2nd: is 'J'aimerais me sustenter'  with score 0.55 (97.4%)

Similar to '2+2 = 4'  is  'I would like to compute addition'  with score 0.22
   2nd: is 'Comment je pourrais calculer des sommes'  with score 0.21 (97.9%)

Similar to 'Le président de la république est Macron'  is  'Qui est le dirigeant de la france'  with score 0.45
   2nd: is 'Qui est Obama?'  with score 0.41 (89.3%)

Similar to 'Qui est le dirigeant de la france'  is  'Qui est Obama?'  with score 0.56
   2nd: is 'Qui est Zidane?'  with score 0.47 (84.6%)

Similar to 'Qui est Obama?'  is  'Qui est Michael jackson?'  with score 0.63
   2nd: is 'Qui est le dirigeant de la france'  with score 0.56 (87.7%)

Similar to 'Qui est Zidane?'  is  'Qui est Obama?'  with score 0.55
   2nd: is 'Qui est Michael jackson?'  with score 0.49 (89.1%)

Similar to 'Qui est Michael jackson?'  is  'Qui est Obama?'  with score 0.63
   2nd: is 'Qui est Zidane?'  with score 0.49 (76.9%)

Similar to 'Tu aimes la musique?'  is  'Tu aimes le sport?'  with score 0.65
   2nd: is 'Do you like sorcery?'  with score 0.54 (83.0%)

Similar to 'Tu aimes le sport?'  is  'Tu aimes la musique?'  with score 0.65
   2nd: is 'Do you like sorcery?'  with score 0.52 (79.9%)

Similar to 'Alexandre dumas a écrit les 3 mousquetaires'  is  'Salut, les gens ont tendance a me nommer Alexandre'  with score 0.45
   2nd: is 'Hi, My name is Alexandre'  with score 0.40 (88.1%)

Similar to 'Connais tu des romanciers?'  is  'Do you know writers?'  with score 0.81
   2nd: is 'I know a very well known noveller'  with score 0.61 (75.6%)

Similar to 'Do you know writers?'  is  'Connais tu des romanciers?'  with score 0.81
   2nd: is 'I know a very well known noveller'  with score 0.59 (73.0%)

Similar to 'I know a very well known noveller'  is  'Connais tu des romanciers?'  with score 0.61
   2nd: is 'Do you know writers?'  with score 0.59 (96.6%)

Similar to 'My girlfriend tend a bookshop'  is  'I have a harry potter's book'  with score 0.54
   2nd: is 'I know a very well known noveller'  with score 0.37 (67.8%)

Similar to 'I like politics'  is  'J'aimerais me sustenter'  with score 0.41
   2nd: is 'Tu aimes la musique?'  with score 0.36 (88.0%)

Similar to 'I have a harry potter's book'  is  'My girlfriend tend a bookshop'  with score 0.54
   2nd: is 'I know a very well known noveller'  with score 0.46 (84.2%)

Similar to 'Do you like sorcery?'  is  'Tu aimes la musique?'  with score 0.54
   2nd: is 'Tu aimes le sport?'  with score 0.52 (96.2%)

Similar to 'Es tu marié?'  is  'are you single?'  with score 0.75
   2nd: is 'Connais tu des romanciers?'  with score 0.47 (62.7%)

Similar to 'are you single?'  is  'Es tu marié?'  with score 0.75
   2nd: is 'Connais tu des romanciers?'  with score 0.43 (57.5%)

Similar to 'do you have some the cure's disk?'  is  'Es-tu bon en calcul mental?'  with score 0.40
   2nd: is 'Connais tu des romanciers?'  with score 0.40 (99.5%)
"""




    