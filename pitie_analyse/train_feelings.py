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

testPola = [
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