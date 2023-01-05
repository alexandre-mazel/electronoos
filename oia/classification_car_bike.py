from sklearn import svm
import numpy as np

## nos donnees
# poids/longueur/nbr_roues/moteur

features = [
                    [14,1.8,2,0],
                    [800,3.4,4,1],
                    [32,1.7,2,1],
                    [340,1.9,2,1],
]

dictClass = {0: 'velo', 1: 'voiture', 2: 'moto'} # a la fois un helper et un commentaire
classes = [0,1,0,2]


## apprentissage

classifier = svm.SVC()
classifier.fit(features, classes)


## testons 

new_comers = [16,1.8,2,0]

predicted = classifier.predict([new_comers])

print("predicted: %s (%s)" % (str(predicted),dictClass[predicted[0]] ) )

## explorons des classifications de nouveaux objets:
# une voiture de 300kg
# et si on mettez 3 roues?

# A votre avis, pourquoi est ce souvent des velos qui sortent ?



