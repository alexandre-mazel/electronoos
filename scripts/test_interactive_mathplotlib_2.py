# interactivite: a chaque clique sur le bouton add, ca met a jour le graph
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import Button
 
fig, ax = plt.subplots()
scatter = ax.scatter(np.random.rand(10), np.random.rand(10))
 
button_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
button = Button(button_ax, 'Add')
 
def add_point(event):
    new_point = np.random.rand(2)
    scatter.set_offsets(np.concatenate([scatter.get_offsets(), [new_point]]))
    plt.draw()
 
button.on_clicked(add_point)
 
plt.show()