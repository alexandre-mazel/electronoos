from collections import Counter
from sklearn.datasets import make_classification
from somlearn import SOM # pip install som-learn
X, _ = make_classification(random_state=0)
som = SOM(n_columns=2, n_rows=2, random_state=1)
labels = som.fit_predict(X)
print(sorted(Counter(labels).items()))

print(som.neighbors_.tolist())  

# fonctionne pas manqe des lib...