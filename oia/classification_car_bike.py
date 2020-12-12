from sklearn import datasets, svm, metrics
import numpy as np

features = [
                [14,1.8,2,0],
                [800,3.4,4,1],
                [32,1.7,2,1],
                [340,1.9,2,1],
            ]
            
classes = [0,1,0,2]


classifier = svm.SVC()
classifier.fit(features, classes)


new_comers = [14,1.8,3,0]
new_comers2 = [800,3.8,4,1]

predicted = classifier.predict([new_comers,new_comers2])

print("predicted: %s" % str(predicted) )

