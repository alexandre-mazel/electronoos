    

def isSameFonction(f1,f2):
    """
    Methode empirique
    """
    x = -10000
    while x < 10000:
        #~ print(f1(x))
        if f1(x) != f2(x):
            print("Les fonctions sont differentes pour au moins %.1f" % x )
            break
        else:
            #~ print("DBG: pareil pour %.1f" % x )
            pass
        x += 0.5
    else:
        print("Les fonctions sont pareilles pour toutes les valeurs testees.")
    

def equ1(x):
    return (2*x-3)*(4*x-1)
    
def equ2(x):
    return (2*x-3)*(2*x-3) + (2*x-7)*(6*x-9)
    
def e3(x):
    return (4*x-5)*(4*x-5)-(4*x-5)*(7*x+8)

def e4(x):
    return -12*x*x-37*x+65
    
isSameFonction(equ1,equ2)
isSameFonction(e3,e4)