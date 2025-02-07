def check_123456789(a,b,c):
    d=set()
    for n in a,b,c:
        while n > 0:
            #~ print(n)
            c = n % 10
            if c == 0 or c in d:
                return False
            d.add(c)
            n //= 10
    return len(d) == 9
    
assert check_123456789(12,345,6789) == True, "check1 error"
assert check_123456789(12,345,6) == False, "check2 error"
assert check_123456789(12,345,2) == False, "check3 error"

def trouve_mult():
    nbtry=0
    nbfound=0
    for a in range(1000):
        #~ print("j'en suis a:", a)
        for b in range(a,10000): # was 1000 # a: from 10M to 9.5M (and remove duplicate)
            c = a*b
            nbtry += 1
            if check_123456789(a,b,c):
                print( a, "*" , b, "=", c )
                nbfound +=1
            if c > 9876: # from 9.5M to 57k
                break
    print("try:",nbtry)
    print("found:",nbfound)

import time
time_begin = time.time()
trouve_mult()
print("duration: %.3fs" % (time.time()-time_begin))
