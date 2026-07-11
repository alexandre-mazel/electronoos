def check_123456789(a,b,c):
    d={}
    for n in a,b,c:
        while n > 0:
            #~ print(n)
            c = n % 10
            if c == 0 or c in d:
                return False
            d[c] = 1
            n //= 10
    return len(d) == 9
    
assert check_123456789(12,345,6789) == True, "check1 error"
assert check_123456789(12,345,6) == False, "check2 error"
assert check_123456789(12,345,2) == False, "check3 error"

def trouve_mult():
    for a in range(1000):
        #~ print("j'en suis a:", a)
        for b in range(a,1000):
            c = a*b
            if check_123456789(a,b,c):
                print( a, "*" , b, "=", c )

trouve_mult()
