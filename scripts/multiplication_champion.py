# -*- coding: cp1252 -*-
import random
import sys
import time

sys.path.append("../alex_pytools")
import score_table


def pick(choice):
    i = random.randint(0, len(choice)-1)
    return choice[i]
    
def game(nMode,nbr_question):
    """
    mode:
    0: mult
    1: add
    2: mix
    3: mult hard
    """
    nModeMaxForMix = 1
    n = 0
    while n < nbr_question:
        print("")
        
        n1 = pick(range(2,10))
        n2 = pick(range(5,10))
        
        nChoice = nMode
        if nMode == 2:
            nChoice = random.randint(0,nModeMaxForMix)
            
        if nChoice == 1:
            n1 = random.randint(1,40)
            n2 = random.randint(20,50)

        if nChoice == 3:
            n1 = random.randint(6,15)
            n2 = random.randint(2,15)      
        
        if random.random()>0.5: 
            c = n1
            n1 = n2
            n2 = c

        bCorrect = False
        while not bCorrect:

            if nChoice == 0 or nChoice == 3:
                res = input("%d x %d ? " % (n1,n2))
                res_correct = n1*n2
            else:
                res = input("%d + %d ? " % (n1,n2))
                res_correct = n1+n2                
            try:
                res = int(res)
                bCorrect = res == res_correct
            except:
                res = -100 # for the presque case when typing a letter
                
            if bCorrect:
                print("ok!")
            else:
                if abs(res - res_correct) <= 2:
                    print("presque...")
                else:
                    print("essaye encore!")
        n += 1
        
"""
def get_best():
    try:
        f = open("multiplication_best.dat", "rt")
        s = f.read()
        r,name = eval(s)
        r = float(r)
        f.close()
    except:
        r,name = 20, "inconnu"
    return r,name
    
def store_best(score,name):
    f = open("multiplication_best.dat", "wt")
    f.write(str((score,name)))
    f.close()
    
"""

def get_best():
    return st.get_best()[:]
    
def store_best(score,name):
    st.add_score(score,name)
    st.save()
    
def print_best_table(nbr_best):
    print(st.get_results(nbr_best))
        
def get_rank(score):
    return st.get_rank(score)
        
if 1:
    print("")
    print("Choix du mode de jeu:")
    print("  1: multiplication")
    print("  2: additition")
    print("  3: mix")
    print("  4: multiplication_hard")
    print("")
    strMode = input( "Ton choix: ")
    nMode = int(strMode)-1
    


tabGameName = [
    "multiplication",
    "addition",
    "mix",
    "multiplication_hard"
]
strGameName = tabGameName[nMode]

print("Enclenchment du mode %s" % strGameName)
print("")
input("appuie sur entree pour commencer...")
print("")

st = score_table.ScoreTable(strGameName,True)

nbr_question = 8
nbr_best = 20
print("C'est parti pour %d questions !" % nbr_question )

time_begin = time.time()

game(nMode,nbr_question)
duration = time.time() - time_begin
rTime = duration/nbr_question
print("\nTemps par opération: %.3fs" % ( rTime ) )

best_time, best_name = get_best()[:2]
if best_time > rTime:
    print("Bravo!\ntu as battu le record de %.3fs fait par %s." % (best_time,best_name) )
    name = input("Quel est ton nom ? ")
    store_best(rTime, name)
else:
    print("Dommage, tu n'as pas battu le record de %.3fs fait par %s." % (best_time,best_name) )
    if get_rank(rTime)<nbr_best:
        print("Mais tu as quand meme fait un bon score..." )
        name = input("Quel est ton nom ? ")
        store_best(rTime, name)

print("\nLegend table:\n")
print_best_table(nbr_best)    