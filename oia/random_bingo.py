# -*- coding: cp1252 -*-

#~ a = [1,2,3]
#~ a.append([1,"banane"])
#~ a = [1,2,3,[1,"banane"]]
#~ a[0] => 1
#~ a[1] => 2
#~ a[2] => 3
#~ a[3] => [1,"banane"]
#~ a[3][0] => 1
#~ a[3][1] => "banane"
#~ a[-1][1] => "banane"


# simulateur de bingo
import random
numero = random.randint(1,100)

#Structure de données recommandée car la plus simple pour cette exercice:
"""
soit tab = [x,y,z,t,...]
x: nombre de fois que j'ai eu 0
y: nombre de fois que j'ai eu 1
z: nombre de fois que j'ai eu 2
t: nombre de fois que j'ai eu 3
...
"""

occ = [0]*100 # occurence de chaque numero de boule
nbr_tirage = 1000*1000*100

num_tirage = 0
while num_tirage < nbr_tirage:
    numero = random.randint(0,99)
    occ[numero] += 1
    num_tirage += 1
    
print("occ:", occ)

iminocc = 0
for i in range(1,len(occ)):
    if occ[i]<occ[iminocc]:
        iminocc = i
print("boule la moins tirée: %d, occ: %d" % (iminocc,occ[iminocc]))

imaxocc = 0
for i in range(1,len(occ)):
    if occ[i]>occ[imaxocc]:
        imaxocc = i
print("boule la plus tirée: %d, occ: %d" % (imaxocc,occ[imaxocc]))
       