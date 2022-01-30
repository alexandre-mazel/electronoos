from sklearn import datasets, svm, metrics
import numpy as np

## nos donnees
# poids/longueur/nbr_roues/moteur

features = [
                [14,1.8,2,0],
                [32,1.7,2,0],
                
                [800,3.4,4,1],
                [1500,4.5,4,1],
                
                [340,1.9,2,1],
                [200,1.8,2,1],

                [3,0.8,2,0],                
                [3,0.8,3,0],
                
                [150,2.,4,1],                
                [100,1.4,4,1],
            ]
            
dictClass = {0: "velo", 1: "voiture", 2: "moto", 3: "trottinette", 4: "quad"}
classes = [0,0,1,1,2,2, 3, 3, 4, 4]


classifier = svm.SVC(gamma="auto") # autre test: gamma=0.001
classifier.fit(features, classes)


new_comers = [9,1.8,2,0] # en dessous de 18 ca donne toujours un trotinette, sauf si gamma est auto
new_comers2 = [4,1.8,2,0]
new_comers3 = [800,3.8,4,1]
new_comers4 = [100,3.8,4,1]

predicted = classifier.predict([new_comers,new_comers2,new_comers3,new_comers4])

print("predicted: %s" % str(predicted) )
for c in predicted:
    print(" " + dictClass[c])

