import random
import time

# also look at:
https://blog.paperspace.com/speed-up-kmeans-numpy-vectorization-broadcasting-profiling/

if 1:
    numbers=[random.randint(1,10000) for i in range(10000)]
    timeBegin = time.time()
    mindiff = abs(numbers[1]-numbers[0])
    for i1,n1 in enumerate(numbers):
        for n2 in numbers[i1+1:]:
            diff = abs(n1-n2)
            if diff<mindiff:
                mindiff=diff
    print(mindiff)
    print("time: %.2f" % (time.time()-timeBegin)) # 6.08s

    timeBegin = time.time()
    numbers=sorted(numbers) # meme si on refait le parcours un coup pour rien, c'est quand meme plus efficace que d'etre dans le monde python
    mindiff = abs(numbers[1]-numbers[0])
    for i in range(len(numbers)-1):
        diff = abs(numbers[i+1]-numbers[i])
        if diff<mindiff:
            mindiff=diff
    print(mindiff)
    print("time: %.2f" % (time.time()-timeBegin)) # 0.01s
    
    exit(1)
    

from collections import namedtuple

Pixel = namedtuple('Pixel', 'frequency rgb') # Do not??????????????????????????????? change

    
pixels = [Pixel(2, [255,0,0]),
        Pixel(10, [200,0,0]),
		Pixel(30, [0,255,0]),
		Pixel(20, [0,0,255]),
		Pixel(25, [0,190,0]),
		Pixel(10, [0,0,128])]
        
        
import numpy as np
import sklearn.cluster

features = [ [pixel.rgb[0]/255,pixel.rgb[1]/255,pixel.rgb[2]/255] for pixel in pixels]
print(features)
features=np.array(features)
cluster_count = 2


if 0:
    from scipy.cluster.vq import vq, kmeans, whiten

    clusters,cores = kmeans(features,cluster_count)
    print("clusters:%s"%clusters)
    print("cores")
    print(cores)
else:
    km = sklearn.cluster.KMeans(n_clusters=cluster_count)

    estimator = km.fit(features)
    print("centroids: ", km.cluster_centers_)
    print("labels: ", km.labels_)
    
    ret = [[] for i in range(cluster_count)]
    print(ret)
    
    for i,k in enumerate(km.labels_):
        ret[k].append(pixels[i].rgb)
    print(ret)
    
def cluster_k_means(pixels, cluster_count, kmeans_random):
    features = [ [pixel.rgb[0]/255,pixel.rgb[1]/255,pixel.rgb[2]/255] for pixel in pixels]
    features=np.array(features)
    km = sklearn.cluster.KMeans(n_clusters=cluster_count)
    estimator = km.fit(features)
    ret = [[] for i in range(cluster_count)]
    for i,k in enumerate(km.labels_):
        ret[k].append(pixels[i].rgb)
    return ret
        
    