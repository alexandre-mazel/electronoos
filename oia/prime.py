import math
import time

def isPrime(n):
    #~ end = n-1
    end = int(math.sqrt(n))+1
    if n == 1:
        return True
    for i in range(2,end):
        if (n % i) == 0:
            return False
    return True
    
def countPrime(n):
    cpt = 0
    for i in range(1,n):
        if isPrime(i):
            cpt += 1
    return cpt
    
        
def countPrimeSmart(n):
    cpt = 0
    listPrime = []
    listPrime.extend(range(1,min(n,3)+1))
    #~ print(listPrime)
    for i in range(4,n):
        end = int(math.sqrt(i))+1
        #~ print("testing %d" % i )
        bPrime = True
        for p in listPrime[1:]:
            if p > end:
                break
            #~ print("  div by %d" % p )
            if (i % p) == 0:
                bPrime = False
        if bPrime:
            # i is prime
            #~ print("=>found %d" % i)
            listPrime.append(i)
                
    return len(listPrime)

timeBegin = time.time()
if 0:
    for i in [1,2,3,5,7,9,10,20]:
        print("isPrime(%d): %s" % (i,isPrime(i)))

    

for i in [1000000]:
    #~ print("countPrime(%d):%d"%(i,countPrime(i)))
    print("countPrimeSmart(%d):%d"%(i,countPrimeSmart(i)))

print("duration: %.3f" % (time.time()-timeBegin))

# mstab7:
# countPrime(1000000):78499
# without sqrt: 1329s (22min9s)
# with sqrt: 2.35s
# countPrimeSmart: 103s