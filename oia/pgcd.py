def pgcd(a,b):
    if b == 0:
        return 0 # ERROR
    if a%b == 0:
        return b
    return pgcd(b,a%b)

print(pgcd(10,3))
print(pgcd(100,50))
print(pgcd(17,33))
print(pgcd(25,125))
print(pgcd(125,25))
print(pgcd(10,25))
print(pgcd(25,10))
print(pgcd(0,3)) # weird
print(pgcd(3,0))