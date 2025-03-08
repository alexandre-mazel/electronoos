import numpy as np
import random

import matplotlib.pyplot as plt

from scipy import stats
if 0:
    rng = np.random.default_rng()

    x = rng.random(10000)
    y = 1.6*x + rng.random(10000)
    # should be a=1.6 and b=0.5
    print("x: " + str(x))
    print("y: " + str(y))
else:
    x = []
    y = []
    for i in range( 1,10000 ):
        xi = i * 100
        x.append( xi )
        y.append( xi*14.5+139+(2*random.random()-1) )
        # should be a=14.5 and b=139
res = stats.linregress(x, y)
print(res)
print("a=",res.slope)
print("b=",res.intercept)