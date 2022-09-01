# -*- coding: cp1252 -*-

import transformers # pip install transformers==2.8.0

import os
import json
import time
import torch
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from torch.utils.data import TensorDataset, random_split, \
                            DataLoader, RandomSampler, SequentialSampler
from transformers import CamembertForSequenceClassification, CamembertTokenizer, \
                         AdamW, get_linear_schedule_with_warmup

# Functions : preprocess() (create dataloaders from raw data) 
# load_models() (load tokenizers and models) training() (loop of one training step) evaluate()

dataset = pd.read_csv("allocine_review_polarity/train.csv")
dataset.head()

reviews = dataset['review'].values.tolist()
sentiments = dataset['polarity'].values.tolist()

import sklearn
import sklearn.svm
import joblib # pip install joblib

testPola = [
    "c'est top", 1.,
    "c'est super", 1.,
    "c'est très bien", 0.8,
    "c'est bien", 0.6,
    "c'est cool", 0.5,
    "c'est pas mal", 0.3,
    "c'est nul", -0.6,
    "c'est très nul", -0.8,
    "c'est exécrable", -0.9,
    "c'est de la daube", -0.9,
    "c'est de la bip", -0.9,
    "c'est de la merde", -0.9, # sorry for your eyes
    "c'est à chier", -0.9,
    "c'est moyen", 0.,
    "c'est pas bien", -0.6,
    "c'est vraiment pas bien", -0.8,
    "c'est loin d'être nul", 0.6,
    "Mieux vaut ca que rien", -0.3,
    "c'est tout le contraire de bien", -0.6,
    "c'est tout sauf bien", -0.6,
    "pire y'a pas", -1.,
    "si il s'agissait d'un concours du plus nul, il gagnerait", -1,
]


import torch
camembert = torch.hub.load('pytorch/fairseq', 'camembert')
camembert.eval()  # disable dropout (or leave in train mode to finetune)

def explore():
    aLine= [
                    "J'aime le camembert !",
                    "J'aime le nougat !",
                    "J'aime le nougat et le camembert !",
                    "J'aime le nougat et le camembert!",
                    ]
                    

    for line in aLine:
        tokens = camembert.encode(line)
        print("tokens:\n" + str(tokens))
        last_layer_features = camembert.extract_features(tokens)
        print(str(last_layer_features))
        print(len(last_layer_features[0][0]))
        #~ assert last_layer_features.size() == torch.Size([1, 10, 768]) # en tout cas pour le premier
    
    #~ print(dir(tokens))
    
def txtToFeats( txt, bVerbose=False ):
    tokens = camembert.encode(txt)
    if bVerbose: print("tokens:\n" + str(tokens))
    last_layer_features = camembert.extract_features(tokens)    
    if bVerbose: print("last_layer_features:\n" + str(last_layer_features))
    if bVerbose: print("len[0][0]: %d" % len(last_layer_features[0][0]))
    if bVerbose: print("len[0][1]: %d" % len(last_layer_features[0][1]))
    feats = last_layer_features[0][0].detach().numpy()
    return feats

        
def train():
    listFeats = []
    listPolas = []
    i = 0
    while i < len(testPola):
        txt = testPola[i]; i += 1
        pola = testPola[i]; i += 1
        feats = txtToFeats(txt,True)
        listFeats.append(feats)
        listPolas.append(int((pola+1)*100))
        
    classifierPola = sklearn.svm.SVC(gamma='scale', kernel='rbf', C=17, class_weight='balanced', probability=False)
    print("INF: train: learning...")
    classifierPola.fit(listFeats, listPolas)
    joblib.dump(classifierPola, 'models/clf_pola.pkl')
    
def test():
    classifierPola = joblib.load('models/clf_pola.pkl')
    listTest = [
            "alexandre est super",
            "alexandre est nul",
            "jean-pierre est super",
            "jean-pierre est nul",
            "le cinéma c'est super",
            "le cinéma c'est top",
            "le cinéma c'est nul",
            ]
    for txt in listTest:
        feats = txtToFeats(txt)
        predicted = classifierPola.predict([feats])
        print("%s => %s, %.2f" % (txt,predicted,(predicted[0]/100.)-1))
    
#~ explore()
train()
test()