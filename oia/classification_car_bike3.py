from sklearn import datasets, svm, metrics, tree
import numpy as np
import matplotlib.pyplot as plt


## nos donnees
libelle_features = ["poids", "longueur", "nbr_roues", "moteur"]

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
            
libelle_class = ["velo", "voiture", "moto", "trottinette", "quad"]
classes = [0,0,1,1,2,2, 3, 3, 4, 4]


classifier = tree.DecisionTreeClassifier() #try with criterion = 'entropy' or  max_depth = 2,
classifier.fit(features, classes)


new_comers = [9,1.8,2,0] # en dessous de 18 ca donne toujours un trotinette, sauf si gamma est auto
new_comers2 = [4,1.8,2,0]
new_comers3 = [800,3.8,4,1]
new_comers4 = [100,3.8,4,1]

predicted = classifier.predict([new_comers,new_comers2,new_comers3,new_comers4])

print("predicted: %s" % str(predicted) )
for c in predicted:
    print( "    " + libelle_class[c])
    
if 0:
    tree.plot_tree(classifier,impurity=False,fontsize=5)
    plt.show()
else:
    import graphviz
    import cv2
    dot_data = tree.export_graphviz(classifier, out_file=None, 
                feature_names=libelle_features,  
                class_names=libelle_class,  
                filled=True, rounded=True,  
                special_characters=True)  
    graph = graphviz.Source(dot_data) 
    import os
    os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Graphviz\bin"
    graph.view()
    