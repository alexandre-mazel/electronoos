# -*- coding: cp1252 -*-

def sq_dicho(x, rEpsilon = 0.0001 ):
    """
    Calcule la racine carrée de x par une méthode par dichotomie.
    Retourne la racine carrée estimée.
    - rEpsilon: precision de l'estimation
    """
    # on sait que y est compris entre 0 et x
    inf = 0
    sup = x
    
    while 1:
        y = ( inf + sup ) / 2 # on essaye a la moitie de l'intervalle
        if y*y < x:
            inf = y
        else:
            sup = y
        
        # condition de sortie:
        if abs(y*y-x) < rEpsilon:
            break
    
    return y
    
def measure(nNbrTimes = 100000):
    # pour ref: mac book air, puce m1: 0.52s, mstab7: 0.56s
    import time
    import math
    timeBegin = time.time()
    x = 1000000
    for i in range(nNbrTimes):
        sq_dicho(x)
        #~ math.sqrt(x)
    print("INF: measure: %5.2fs" % (time.time()-timeBegin))
        
    
print(sq_dicho(2))
print(sq_dicho(2,1e-8))
print(sq_dicho(3))
print(sq_dicho(5))
print(sq_dicho(9))
measure()
