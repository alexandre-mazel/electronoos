import sys

from math import * # pour sin, factorial...

def evalue(s):
    """
    eg: 
        "2+2" => 4
        2**8 => 128
        factorial(5) => 120  (utilisation implicite du module math)
        sin(3.14159) => 2.6 E-6  (utilisation implicite du module math)
    """
    print("evaluating: '%s'" % s )
    res = eval(s)
    return res
    
    
expression = ""
for s in sys.argv[1:]:
    expression += s + " "
expression = expression.strip()
    
out = evalue(expression)
print(out)