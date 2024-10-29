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
    
    
# Reminder: use venv from ~/dev/llama_env
import ollama
import requests
import json
import time
import os
import numpy as np
    
url = "http://localhost:11434/api/chat"
strModel = "nomic-embed-text" # size: 274MB, running: 370MB

def llama3_embedding(text):
    print( "INF: llama3: using model: '%s'" % strModel )
    
    out  = ollama.embeddings( model=strModel, prompt=text )
    #~ print(out)
    return out['embedding']


def compare_two_texts(t1,t2):
    v1 = llama3_embedding(t1)
    v2 = llama3_embedding(t2)
    simi = np.dot(v1,v2)
    print("'%s'  and  '%s'  => %s" % (t1,t2,simi) )
    return simi
    
def compare_all(listText):
    allv = []
    for t in listText:
        v = llama3_embedding(t)
        allv.append(v)
    
    for j,t1 in enumerate(listText):
        simi_maxi = 0
        imaxi = 0
        simi_maxi2 = 0 # 2nd best
        imaxi2 = 0
        for i,t2 in enumerate(listText):
            if t1 == t2:
                continue
            simi = np.dot(allv[i],allv[j])
            #~ print("  simi: %.2f for %s and %s" % (simi,t1,t2) )
            if simi > simi_maxi:
                simi_maxi2 = simi_maxi
                imaxi2 = imaxi
                simi_maxi = simi
                imaxi = i
            elif simi > simi_maxi2:
                simi_maxi2 = simi
                imaxi2 = i
        print("Similar to '%s'  is  '%s'  with score %.2f" % (t1,listText[imaxi],simi_maxi) )
        print("   2nd: is '%s'  with score %.2f (%.1f%%)" % (listText[imaxi2],simi_maxi2,simi_maxi2*100/simi_maxi) )
        print("")

    
v1 = llama3_embedding("hi guys!")

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
texts.append("J'aimerais me sustenter")
texts.append("I'm hungry")
texts.append("Comment je pourrais calculer des sommes")
texts.append("2+2 = 4")
texts.append("Le président de la république est Macron")
texts.append("Qui est le dirigeant de la france")
texts.append("Qui est Obama?")
texts.append("Alexandre dumas a écrit les 3 mousquetaires")
texts.append("Connais tu des romanciers?")
    
compare_all(texts)
    




    