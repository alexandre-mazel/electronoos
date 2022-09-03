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

print("INF: load allocine - begin")
dataset = pd.read_csv("allocine_review_polarity/train.csv")
dataset.head()

reviews = dataset['review'].values.tolist()
sentiments = dataset['polarity'].values.tolist()

print("INF: load allocine - end")

import sklearn
import sklearn.svm
import joblib # pip install joblib

testPola = [
        "c'est bien", 0.6,
        "c'est nul", -0.6,
        "c'est très bien", 0.8,
        "c'est pas bien", -0.2,
        "c'est très nul", -0.8,
        "c'est pas nul", 0.2,
    "c'est top", 1.,
    "c'est top", 1., # to check results and feats are identic
    "c'est super", 1.,
    "c'est très bien", 0.8,
    "c'est bien", 0.6,
    "c'est cool", 0.5,
    "c'est pas mal", 0.3,
    "c'est bof", 0.15,
    "c'est nul", -0.6,
    "c'est très nul", -0.8,
    "c'est trop nul", -0.8,
    "c'est exécrable", -0.9,
    "c'est de la daube", -0.9,
    "c'est de la bip", -0.9,
    "c'est de la merde", -0.9, # sorry for your eyes
    "c'est à chier", -0.9,
    "c'est moyen", 0.,
    "c'est pas bien", -0.6,
    "c'est pas top", -0.4,
    "c'est vraiment pas bien", -0.8,
    "c'est loin d'être nul", 0.6,
    "Mieux vaut ca que rien", -0.3,
    "c'est tout le contraire de bien", -0.6,
    "c'est tout sauf bien", -0.6,
    "pire y'a pas", -1.,
    "je n'ai jamais vu quelque chose d'aussi super que ca c'est la perfection",1.,
    "j'ai eu beaucoup de plaisir", 0.8,
    "je me suis ennuyé à mourir", -0.8,
    "si il s'agissait d'un concours du plus nul, il gagnerait", -1,
]

if 1:
    # simple and balanced
    testPola = testPola[:6]



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
    if bVerbose: print( "INF: txtToFeats: txt: '%s' " % txt )
    feats = []
    maxfeat = 20
    try:
        tokens = camembert.encode(txt)
        if bVerbose: print("tokens: " + str(tokens))

        if 0:
            # et si on envoyait juste les token des mots (pb, la phrase n'a pas toujours la meme longueur => pad avec des 0)
            # bien sur c'est bof
            feats = tokens.detach().numpy()
            while len(feats)<maxfeat:
                feats = np.concatenate((feats,[0]))
            if len(feats) > maxfeat:
                feats = feats[:maxfeat]
            if bVerbose: print( "feats: %s" % str(feats) )
            return feats
        last_layer_features = camembert.extract_features(tokens)    
        if bVerbose: print("last_layer_features: " + str(last_layer_features))
        if bVerbose: print("len[0][0]: %d" % len(last_layer_features[0][0]))
        if bVerbose: print("len[0][1]: %d" % len(last_layer_features[0][1]))
        # on a une last feature pour chaque mot, pas de chance!
        if bVerbose: print("len[0]: %d" % len(last_layer_features[0]))
        #~ feats = last_layer_features[0][0].detach().numpy()
        if 0:
            nNbrWordToUse = len(last_layer_features[0]) # pas possible car les phrases ont des longueurs differentes
            nNbrWordToUse = 1 # juste le premier mot, c'est idiot
            nNbrWordToUse = 6 # que faire des phrases trop courte ? on les vire? (attention il y a un token for start and end of sentence)
            for i in range(nNbrWordToUse):
                feats = np.concatenate((feats, last_layer_features[0][i].detach().numpy()))
                if bVerbose: print("shape feats: %s" % str(feats.shape))
        else:
            # add zero
            for i in range(min( len(last_layer_features[0]),maxfeat) ):
                feats = np.concatenate((feats, last_layer_features[0][i].detach().numpy() ))
                if bVerbose: print("shape feats: %s" % str(feats.shape))
                
            if len(last_layer_features[0])<maxfeat:
                for i in range(maxfeat-len(last_layer_features[0])):
                    feats = np.concatenate((feats, [0]*len(last_layer_features[0][0])))
                    
        if bVerbose: print( "end feats: %s" % str(feats) )
        return feats
    except ValueError as err:
        if bVerbose: print("DBG: txtToFeats: ValueError: %s" % str(err))
    return None

        
def train():
    listFeats = []
    listPolas = []
    
    if 1:
        # small base
        i = 0
        while i < len(testPola):
            txt = testPola[i]; i += 1
            pola = testPola[i]; i += 1
            pola = int((pola+1)*100)
            feats = txtToFeats(txt,True)
            listFeats.append(feats)
            listPolas.append(pola)
    else:
        # allocine
        print("INF: Allocine db: %s records" % len(reviews))
        i = 0
        while i < len(reviews):
            txt = reviews[i]
            pola = sentiments[i]
            feats = txtToFeats(txt,False)
            if not feats is None:
                listFeats.append(feats)
                listPolas.append(pola)
            i += 1
            if (i % 100)==0:
                print("%d/%d" % (i,len(reviews)) )
            if 1:
                if i > 5000:
                    break
        
    classifierPola = sklearn.svm.SVC(gamma='scale', kernel='rbf', C=17, class_weight='balanced', probability=False)
    print("INF: train: learning...")
    classifierPola.fit(listFeats, listPolas)
    joblib.dump(classifierPola, 'models/clf_pola.pkl')
    
def test():
    classifierPola = joblib.load('models/clf_pola.pkl')
    listTest = [
                ["c'est bien",0.6],
                ["c'est très bien",0.8],
                ["c'est pas bien",-0.2],
                ["c'est nul",-0.6],
                ["c'est très nul",-0.8],
                ["c'est pas nul",0.2],
                ["le cinéma c'est super",1.],
                ["le cinéma c'est top",1.],
                ["le cinéma c'est nul",-0.6],
                ["alexandre est super",1.],
                ["alexandre est nul",-0.6],
                ["jean-pierre est super",1.],
                ["jean-pierre est nul",-0.6],
                ["je suis pas content c'est trop nul",-1.],
                ["j'ai passé un super moment c'était top",1.],
            ]
    rSumDiff = 0
    nCpt = 0
    for txt, theo in listTest:
        feats = txtToFeats(txt)
        predicted = classifierPola.predict([feats])
        rNote = (predicted[0]/100.)-1
        rDiff = abs(rNote-theo)
        print("%s => %s, %.2f, diff:%.2f" % (txt,predicted,rNote,rDiff))
        rSumDiff += rDiff
        nCpt += 1
    print("rAvgDiff: %.3f" % (rSumDiff/nCpt) )
        
        
"""

### mini base

# token10
idem token20


# token20
c'est bien => [180], 0.80, diff:0.20
c'est pas bien => [180], 0.80, diff:1.40
le cinéma c'est super => [180], 0.80, diff:0.20
le cinéma c'est top => [40], -0.60, diff:1.60
le cinéma c'est nul => [40], -0.60, diff:0.00
alexandre est super => [9], -0.91, diff:1.91
alexandre est nul => [9], -0.91, diff:0.31
jean-pierre est super => [9], -0.91, diff:1.91
jean-pierre est nul => [9], -0.91, diff:0.31
rAvgDiff: 0.871


# last feature layer first word
c'est bien => [160], 0.60, diff:0.00
c'est pas bien => [40], -0.60, diff:0.00
le cinéma c'est super => [19], -0.81, diff:1.81
le cinéma c'est top => [19], -0.81, diff:1.81
le cinéma c'est nul => [19], -0.81, diff:0.21
alexandre est super => [0], -1.00, diff:2.00
alexandre est nul => [0], -1.00, diff:0.40
jean-pierre est super => [180], 0.80, diff:0.20
jean-pierre est nul => [0], -1.00, diff:0.40
rAvgDiff: 0.759

# last feature layer first 6 words
c'est bien => [160], 0.60, diff:0.00
c'est pas bien => [40], -0.60, diff:0.00
le cinéma c'est super => [0], -1.00, diff:2.00
le cinéma c'est top => [0], -1.00, diff:2.00
le cinéma c'est nul => [0], -1.00, diff:0.40
alexandre est super => [40], -0.60, diff:1.60
alexandre est nul => [40], -0.60, diff:0.00
jean-pierre est super => [40], -0.60, diff:1.60
jean-pierre est nul => [40], -0.60, diff:0.00
rAvgDiff: 0.844

# last feature layer 20 words padded
c'est bien => [160], 0.60, diff:0.00
c'est très bien => [180], 0.80, diff:0.00
c'est pas bien => [80], -0.20, diff:0.00
c'est nul => [40], -0.60, diff:0.00
c'est très nul => [19], -0.81, diff:0.01
c'est pas nul => [120], 0.20, diff:0.00
le cinéma c'est super => [19], -0.81, diff:1.81
le cinéma c'est top => [19], -0.81, diff:1.81
le cinéma c'est nul => [9], -0.91, diff:0.31
alexandre est super => [19], -0.81, diff:1.81
alexandre est nul => [40], -0.60, diff:0.00
jean-pierre est super => [180], 0.80, diff:0.20
jean-pierre est nul => [19], -0.81, diff:0.21
je suis pas content c'est trop nul => [40], -0.60, diff:0.40
j'ai passé un super moment c'était top => [40], -0.60, diff:1.60
rAvgDiff: 0.544

# last feature layer 20 words padded - simple learning
c'est bien => [160], 0.60, diff:0.00
c'est très bien => [180], 0.80, diff:0.00
c'est pas bien => [180], 0.80, diff:1.00
c'est nul => [40], -0.60, diff:0.00
c'est très nul => [180], 0.80, diff:1.60
c'est pas nul => [180], 0.80, diff:0.60
le cinéma c'est super => [180], 0.80, diff:0.20
le cinéma c'est top => [180], 0.80, diff:0.20
le cinéma c'est nul => [180], 0.80, diff:1.40
alexandre est super => [180], 0.80, diff:0.20
alexandre est nul => [40], -0.60, diff:0.00
jean-pierre est super => [180], 0.80, diff:0.20
jean-pierre est nul => [40], -0.60, diff:0.00
je suis pas content c'est trop nul => [180], 0.80, diff:1.80
j'ai passé un super moment c'était top => [180], 0.80, diff:0.20
rAvgDiff: 0.493




### allocine (old base)

# allocine 200
alexandre est super => [1], -0.99
alexandre est nul => [0], -1.00
jean-pierre est super => [1], -0.99
jean-pierre est nul => [1], -0.99
le cinéma c'est super => [0], -1.00
le cinéma c'est top => [0], -1.00
le cinéma c'est nul => [0], -1.00

# allocine 5000
alexandre est super => [1], -0.99
alexandre est nul => [0], -1.00
jean-pierre est super => [1], -0.99
jean-pierre est nul => [0], -1.00
le cinéma c'est super => [1], -0.99
le cinéma c'est top => [1], -0.99
le cinéma c'est nul => [0], -1.00

"""
    
#~ explore()
train()
test()