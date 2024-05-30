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
    
"""
methode de heron, pour calculer la racine carrée de a:
  elle peut etre approximée par la suite xn+1 = (xn + a/xn)/2
"""
    
def sq_heron_rec(a, xn=None, epsilon = 0.0001 ):
    if xn == None: xn = a/2
    if abs(a-xn*xn) < epsilon:
        return xn
    xn1 = (xn+a/xn)/2
    return sq_heron_rec(a,xn1)
    
def sq_heron_iter1(a, epsilon = 0.0001 ):
    """
    iterative version
    """
    x = a/2 # approximation grossière
    while abs(x*x-a)>epsilon:
        x = (x+a/x)/2
    return x
    
def sq_heron_iter2(a, epsilon = 0.0001 ):
    """
    iterative version
    """
    x = a/2 # approximation grossière
    while 1:
        x2 = (x+a/x)/2
        if abs(x2-x)<epsilon:
            break
        x = x2
    return x2
    
def measure(nNbrTimes = 100000):
    # pour ref: 
    # sq_dicho: mstab7: 0.56s (mac book air, puce m1: 0.52s)
    # sq_heron_rec: mstab7: 0.30s
    # sq_heron_iter1: mstab7: 0.16s
    # sq_heron_iter2: mstab7: 0.15s
    
    import time
    import math
    timeBegin = time.time()
    x = 1000000
    for i in range(nNbrTimes):
        #~ sq_dicho(x)
        #~ sq_heron_rec(x)
        sq_heron_iter1(x)
        #~ math.sqrt(x)
    print("INF: measure: %5.2fs" % (time.time()-timeBegin))
        
    
print(sq_dicho(2))
print(sq_dicho(2,1e-8))
print(sq_dicho(3))
print(sq_dicho(5))
print(sq_dicho(9))
print("heron:")
print(sq_heron_rec(2))
print(sq_heron_iter1(2))
print(sq_heron_iter2(2))
measure()
