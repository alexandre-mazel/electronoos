# -*- coding: cp1252 -*-

import transformers # pip install transformers==2.8.0

import os
import json
import time
import torch # si erreur Numpy not available => pip install numpy --upgrade
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

if 0:
#~ if 1:
    # simple and balanced
    testPola = testPola[:6]



import torch
camembert = torch.hub.load('pytorch/fairseq', 'camembert')
camembert.eval()  # disable dropout (or leave in train mode to finetune)


bUseAllocine = 0
bUseAllocine = 1

strModelForTestAndInteractive = "d:/models/clf_pola_40000.pkl"
#~ strModelForTestAndInteractive = "models/clf_pola.pkl"

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
    
    if not bUseAllocine:
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
                #~ if i > 5000:
                #~ if i > 2000:
                #~ if i > 500:
                if i > 400:
                #~ if i > 100:
                    break
        
    classifierPola = sklearn.svm.SVC(gamma='scale', kernel='rbf', C=17, class_weight='balanced', probability=False)
    #~ classifierPola = sklearn.linear_model.Lasso(alpha=0.1)
    #~ classifierPola = sklearn.linear_model.MultiTaskLasso()
    #~ classifierPola = sklearn.linear_model.RidgeCV(alphas=np.logspace(-6, 6, 13))
    #~ classifierPola = sklearn.svm.SVR(kernel='rbf')
    
    print("INF: train: learning...")
    classifierPola.fit(listFeats, listPolas)
    joblib.dump(classifierPola, 'models/clf_pola.pkl')
    
def test():
    print("INF: test: start")
    print("INF: test: loading: " + strModelForTestAndInteractive)
    classifierPola = joblib.load(strModelForTestAndInteractive)
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
                ["ohlala cette chose est trop incroyable",0.7],
                ["c'est incroyable",0.7],
                ["c'est de la merde",-1.],
                ["c'est éclaté au sol",-1.],
                ["j'ai aimé",0.7],
                ["je n'ai pas aimé",-0.7],
                ["c'est ni bien ni mal",0.],
                ["c'est ni mal ni bien",0.],
                ["j'y met du mien",0.5],
                ["tu n'y met pas du tien",-0.5],
                ["j'aime",0.8],
                ["j'aime pas",-0.8],
                ["je n'aime pas",-0.8],
                ["je n'aime pas du tout",-1.],
                
            ]
    rSumDiff = 0
    nNbrPolaOk = 0
    nCpt = 0
    for txt, theo in listTest:
        feats = txtToFeats(txt)
        predicted = classifierPola.predict([feats])
        
        if bUseAllocine:
            nNote= predicted[0]
            rDiff = 2
            bPolaOk = 0
            if nNote == 1 and theo>=0:
                rDiff = 0
                bPolaOk = 1
            elif nNote == 0 and theo<0:
                rDiff = 0
                bPolaOk = 1
            rNote = nNote
        else:
            rNote = (predicted[0]/100.)-1
            rDiff = abs(rNote-theo)
            bPolaOk = ( rNote > 0 and theo>0) \
                            or ( rNote == 0 and theo==0) \
                            or ( rNote < 0 and theo<0)
        if bPolaOk:
            nNbrPolaOk += 1
        print("%s => %s, %.2f, diff:%.2f, bPolaOk:%d" % (txt,predicted,rNote,rDiff,int(bPolaOk)) )
        rSumDiff += rDiff
        nCpt += 1
    print("rAvgDiff: %.3f" % (rSumDiff/nCpt ) )
    print("pola_ok: %.3f" % (nNbrPolaOk/nCpt) )

        
        
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
c'est bien => [160], 0.60, diff:0.00, bPolaOk:1
c'est très bien => [180], 0.80, diff:0.00, bPolaOk:1
c'est pas bien => [80], -0.20, diff:0.00, bPolaOk:1
c'est nul => [40], -0.60, diff:0.00, bPolaOk:1
c'est très nul => [19], -0.81, diff:0.01, bPolaOk:1
c'est pas nul => [120], 0.20, diff:0.00, bPolaOk:1
le cinéma c'est super => [19], -0.81, diff:1.81, bPolaOk:0
le cinéma c'est top => [19], -0.81, diff:1.81, bPolaOk:0
le cinéma c'est nul => [9], -0.91, diff:0.31, bPolaOk:1
alexandre est super => [19], -0.81, diff:1.81, bPolaOk:0
alexandre est nul => [40], -0.60, diff:0.00, bPolaOk:1
jean-pierre est super => [180], 0.80, diff:0.20, bPolaOk:1
jean-pierre est nul => [19], -0.81, diff:0.21, bPolaOk:1
je suis pas content c'est trop nul => [40], -0.60, diff:0.40, bPolaOk:1
j'ai passé un super moment c'était top => [40], -0.60, diff:1.60, bPolaOk:0
ohlala cette chose est trop incroyable => [9], -0.91, diff:1.61, bPolaOk:0
c'est incroyable => [200], 1.00, diff:0.30, bPolaOk:1
c'est de la merde => [9], -0.91, diff:0.09, bPolaOk:1
c'est éclaté au sol => [9], -0.91, diff:0.09, bPolaOk:1
j'ai aimé => [40], -0.60, diff:1.30, bPolaOk:0
je n'ai pas aimé => [19], -0.81, diff:0.11, bPolaOk:1
c'est ni bien ni mal => [9], -0.91, diff:0.91, bPolaOk:0
c'est ni mal ni bien => [40], -0.60, diff:0.60, bPolaOk:0
j'y met du mien => [9], -0.91, diff:1.41, bPolaOk:0
tu n'y met pas du tien => [40], -0.60, diff:0.10, bPolaOk:1
j'aime => [100], 0.00, diff:0.80, bPolaOk:0
j'aime pas => [40], -0.60, diff:0.20, bPolaOk:1
je n'aime pas => [0], -1.00, diff:0.20, bPolaOk:1
je n'aime pas du tout => [40], -0.60, diff:0.40, bPolaOk:1
rAvgDiff: 0.561
pola_ok: 0.655

# last feature layer 20 words padded - simple learning
c'est bien => [160], 0.60, diff:0.00, bPolaOk:1
c'est très bien => [180], 0.80, diff:0.00, bPolaOk:1
c'est pas bien => [180], 0.80, diff:1.00, bPolaOk:0
c'est nul => [40], -0.60, diff:0.00, bPolaOk:1
c'est très nul => [180], 0.80, diff:1.60, bPolaOk:0
c'est pas nul => [180], 0.80, diff:0.60, bPolaOk:1
le cinéma c'est super => [180], 0.80, diff:0.20, bPolaOk:1
le cinéma c'est top => [180], 0.80, diff:0.20, bPolaOk:1
le cinéma c'est nul => [180], 0.80, diff:1.40, bPolaOk:0
alexandre est super => [180], 0.80, diff:0.20, bPolaOk:1
alexandre est nul => [40], -0.60, diff:0.00, bPolaOk:1
jean-pierre est super => [180], 0.80, diff:0.20, bPolaOk:1
jean-pierre est nul => [40], -0.60, diff:0.00, bPolaOk:1
je suis pas content c'est trop nul => [180], 0.80, diff:1.80, bPolaOk:0
j'ai passé un super moment c'était top => [180], 0.80, diff:0.20, bPolaOk:1
rAvgDiff: 0.493
pola_ok: 0.733

# last feature layer 20 words padded - SVR

c'est bien => [60.22860662], -0.40, diff:1.00, bPolaOk:0
c'est très bien => [60.24649683], -0.40, diff:1.20, bPolaOk:0
c'est pas bien => [59.16962068], -0.41, diff:0.21, bPolaOk:1
c'est nul => [59.18262478], -0.41, diff:0.19, bPolaOk:1
c'est très nul => [59.04874439], -0.41, diff:0.39, bPolaOk:1
c'est pas nul => [59.76281369], -0.40, diff:0.60, bPolaOk:0
le cinéma c'est super => [58.22129869], -0.42, diff:1.42, bPolaOk:0
le cinéma c'est top => [58.20454265], -0.42, diff:1.42, bPolaOk:0
le cinéma c'est nul => [58.21548349], -0.42, diff:0.18, bPolaOk:1
alexandre est super => [58.89106564], -0.41, diff:1.41, bPolaOk:0
alexandre est nul => [58.70206212], -0.41, diff:0.19, bPolaOk:1
jean-pierre est super => [59.58547654], -0.40, diff:1.40, bPolaOk:0
jean-pierre est nul => [58.67957146], -0.41, diff:0.19, bPolaOk:1
je suis pas content c'est trop nul => [59.14597673], -0.41, diff:0.59, bPolaOk:1
j'ai passé un super moment c'était top => [59.13188842], -0.41, diff:1.41, bPolaOk:0
ohlala cette chose est trop incroyable => [59.04052944], -0.41, diff:1.11, bPolaOk:0
c'est incroyable => [61.44778201], -0.39, diff:1.09, bPolaOk:0
c'est de la merde => [58.23149365], -0.42, diff:0.58, bPolaOk:1
c'est éclaté au sol => [59.13501132], -0.41, diff:0.59, bPolaOk:1
j'ai aimé => [59.58333237], -0.40, diff:1.10, bPolaOk:0
je n'ai pas aimé => [58.74738948], -0.41, diff:0.29, bPolaOk:1
c'est ni bien ni mal => [59.55836001], -0.40, diff:0.40, bPolaOk:0
c'est ni mal ni bien => [59.37246284], -0.41, diff:0.41, bPolaOk:0
j'y met du mien => [59.28236341], -0.41, diff:0.91, bPolaOk:0
tu n'y met pas du tien => [59.14185103], -0.41, diff:0.09, bPolaOk:1
j'aime => [60.8817587], -0.39, diff:1.19, bPolaOk:0
j'aime pas => [59.75157066], -0.40, diff:0.40, bPolaOk:1
je n'aime pas => [58.60361988], -0.41, diff:0.39, bPolaOk:1
je n'aime pas du tout => [59.23731524], -0.41, diff:0.59, bPolaOk:1
rAvgDiff: 0.722
pola_ok: 0.483





### allocine - last feature layer 20 words padded - simple learning

# allocine 500
400 C17
c'est bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est très bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est pas bien => [0], 0.00, diff:0.00, bPolaOk:1
c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
c'est très nul => [0], 0.00, diff:0.00, bPolaOk:1
c'est pas nul => [1], 1.00, diff:0.00, bPolaOk:1
le cinéma c'est super => [1], 1.00, diff:0.00, bPolaOk:1
le cinéma c'est top => [1], 1.00, diff:0.00, bPolaOk:1
le cinéma c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
alexandre est super => [1], 1.00, diff:0.00, bPolaOk:1
alexandre est nul => [0], 0.00, diff:0.00, bPolaOk:1
jean-pierre est super => [1], 1.00, diff:0.00, bPolaOk:1
jean-pierre est nul => [1], 1.00, diff:2.00, bPolaOk:0
je suis pas content c'est trop nul => [0], 0.00, diff:0.00, bPolaOk:1
j'ai passé un super moment c'était top => [1], 1.00, diff:0.00, bPolaOk:1
ohlala cette chose est trop incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est de la merde => [0], 0.00, diff:0.00, bPolaOk:1
c'est éclaté au sol => [1], 1.00, diff:2.00, bPolaOk:0
j'ai aimé => [1], 1.00, diff:0.00, bPolaOk:1
je n'ai pas aimé => [1], 1.00, diff:2.00, bPolaOk:0
c'est ni bien ni mal => [1], 1.00, diff:0.00, bPolaOk:1
c'est ni mal ni bien => [0], 0.00, diff:2.00, bPolaOk:0
j'y met du mien => [1], 1.00, diff:0.00, bPolaOk:1
tu n'y met pas du tien => [0], 0.00, diff:0.00, bPolaOk:1
j'aime => [1], 1.00, diff:0.00, bPolaOk:1
j'aime pas => [1], 1.00, diff:2.00, bPolaOk:0
je n'aime pas => [1], 1.00, diff:2.00, bPolaOk:0
je n'aime pas du tout => [0], 0.00, diff:0.00, bPolaOk:1
rAvgDiff: 0.414
pola_ok: 0.793

500 C17 (C10 meme resultat)
c'est bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est très bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est pas bien => [0], 0.00, diff:0.00, bPolaOk:1
c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
c'est très nul => [1], 1.00, diff:2.00, bPolaOk:0
c'est pas nul => [1], 1.00, diff:0.00, bPolaOk:1
le cinéma c'est super => [0], 0.00, diff:2.00, bPolaOk:0
le cinéma c'est top => [0], 0.00, diff:2.00, bPolaOk:0
le cinéma c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
alexandre est super => [1], 1.00, diff:0.00, bPolaOk:1
alexandre est nul => [0], 0.00, diff:0.00, bPolaOk:1
jean-pierre est super => [1], 1.00, diff:0.00, bPolaOk:1
jean-pierre est nul => [0], 0.00, diff:0.00, bPolaOk:1
je suis pas content c'est trop nul => [0], 0.00, diff:0.00, bPolaOk:1
j'ai passé un super moment c'était top => [1], 1.00, diff:0.00, bPolaOk:1
ohlala cette chose est trop incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est de la merde => [0], 0.00, diff:0.00, bPolaOk:1
c'est éclaté au sol => [1], 1.00, diff:2.00, bPolaOk:0
j'ai aimé => [1], 1.00, diff:0.00, bPolaOk:1
je n'ai pas aimé => [0], 0.00, diff:0.00, bPolaOk:1
rAvgDiff: 0.381
pola_ok: 0.810

2000 C17
c'est bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est très bien => [1], 1.00, diff:0.00, bPolaOk:1
c'est pas bien => [0], 0.00, diff:0.00, bPolaOk:1
c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
c'est très nul => [1], 1.00, diff:2.00, bPolaOk:0
c'est pas nul => [0], 0.00, diff:2.00, bPolaOk:0
le cinéma c'est super => [0], 0.00, diff:2.00, bPolaOk:0
le cinéma c'est top => [0], 0.00, diff:2.00, bPolaOk:0
le cinéma c'est nul => [0], 0.00, diff:0.00, bPolaOk:1
alexandre est super => [1], 1.00, diff:0.00, bPolaOk:1
alexandre est nul => [0], 0.00, diff:0.00, bPolaOk:1
jean-pierre est super => [1], 1.00, diff:0.00, bPolaOk:1
jean-pierre est nul => [0], 0.00, diff:0.00, bPolaOk:1
je suis pas content c'est trop nul => [0], 0.00, diff:0.00, bPolaOk:1
j'ai passé un super moment c'était top => [1], 1.00, diff:0.00, bPolaOk:1
ohlala cette chose est trop incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est incroyable => [1], 1.00, diff:0.00, bPolaOk:1
c'est de la merde => [0], 0.00, diff:0.00, bPolaOk:1
c'est éclaté au sol => [0], 0.00, diff:0.00, bPolaOk:1
j'ai aimé => [1], 1.00, diff:0.00, bPolaOk:1
je n'ai pas aimé => [0], 0.00, diff:0.00, bPolaOk:1
c'est ni bien ni mal => [1], 1.00, diff:0.00, bPolaOk:1
c'est ni mal ni bien => [1], 1.00, diff:0.00, bPolaOk:1
j'y met du mien => [1], 1.00, diff:0.00, bPolaOk:1
tu n'y met pas du tien => [0], 0.00, diff:0.00, bPolaOk:1
j'aime => [1], 1.00, diff:0.00, bPolaOk:1
j'aime pas => [0], 0.00, diff:0.00, bPolaOk:1
je n'aime pas => [0], 0.00, diff:0.00, bPolaOk:1
je n'aime pas du tout => [0], 0.00, diff:0.00, bPolaOk:1
rAvgDiff: 0.276
pola_ok: 0.862

5000 C17 (sur kakashi):
rAvgDiff: 0.414
pola_ok: 0.793 ?!?

40000 C17 (sur kakashi, ca a pris des jours!) 
(warning de version au rechargement sur ma tablette, mais resultat identique)
rAvgDiff: 0.207
pola_ok: 0.897

"""

def interactive():
    print("INF: Entering interactive word")
    classifierPola = joblib.load(strModelForTestAndInteractive)
    while 1:
        txt = input("your sentence:\n")
        feats = txtToFeats(txt)
        predicted = classifierPola.predict([feats])
        print("'%s' => %s" % (txt,predicted) ) 
    
#~ explore()
#~ train()
test()
#~ interactive()