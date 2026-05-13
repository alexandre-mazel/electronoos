# draw a 3D interactive scatter (en fait l'interactivite est dans la rotation du graph et pas l'ajout de donnees)
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
 
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
 
x, y, z = np.random.rand(3, 100)
ax.scatter(x, y, z)
 
plt.show()