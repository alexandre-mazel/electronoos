import random
import sys
import time

sys.append("../alex_pytools")
import score_table


def pick(choice):
    i = random.randint(0, len(choice)-1)
    return choice[i]
    
def game(nbr_question):
    n = 0
    while n < nbr_question:
        n1 = pick(range(2,9))
        n2 = pick(range(5,9))
        print("")
        bCorrect = False
        while not bCorrect:
            res = input("%d x %d ? " % (n1,n2))
            try:
                res = int(res)
                bCorrect = res == n1*n2
            except:
                pass
                
            if bCorrect:
                print("ok!")
            else:
                print("essaye encore!")
        n += 1
        
        
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
        
        
time_begin = time.time()
nbr_question = 8
print("C'est parti pour %d questions !" % nbr_question )
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