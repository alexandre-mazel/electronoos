import random
import sys
import time

sys.path.append("../alex_pytools")
import score_table


def pick(choice):
    i = random.randint(0, len(choice)-1)
    return choice[i]
    
def game(nbr_question):
    n = 0
    while n < nbr_question:
        n1 = pick(range(2,10))
        n2 = pick(range(5,10))
        print("")
        bCorrect = False
        while not bCorrect:
            if random.random()>0.5: 
                c = n1
                n1 = n2
                n2 = c
            res = input("%d x %d ? " % (n1,n2))
            res_correct = n1*n2
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
st = score_table.ScoreTable("multiplication",True)
def get_best():
    return st.get_best()[:]
    
def store_best(score,name):
    st.add_score(score,name)
    st.save()
    
def print_best_table():
    print(st.get_results(15))
        
def get_rank(score):
    return st.get_rank(score)
        
input("appuie sur entree pour commencer...")
print("")

nbr_question = 8
print("C'est parti pour %d questions !" % nbr_question )

time_begin = time.time()

game(nbr_question)
duration = time.time() - time_begin
rTime = duration/nbr_question
print("\nTemps par multiplication: %.3fs" % ( rTime ) )

best_time, best_name = get_best()
if best_time > rTime:
    print("Bravo!\ntu as battu le record de %.3fs fait par %s." % (best_time,best_name) )
    name = input("Quel est ton nom ? ")
    store_best(rTime, name)
else:
    print("Dommage, tu n'as pas battu le record de %.3fs fait par %s." % (best_time,best_name) )
    if get_rank(rTime)<10:
        print("Mais tu as quand meme fait un bon score..." )
        name = input("Quel est ton nom ? ")
        store_best(rTime, name)

print("\nLegend table:\n")
print_best_table()    