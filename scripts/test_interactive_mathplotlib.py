import matplotlib.pyplot as plt
import numpy as np

# On active le mode interactif
plt.ion()   # ion => interactive on / ioff => interactive off

# Créer des données de test et la figure associée
x = np.linspace(0, 10, 100)
y1 = np.cos(x)
y2 = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y1, label="Cosinus")
sinplot, = ax.plot(x, y2, label="Sinus")

# Afficher la figure de manière non bloquante
plt.show(block=False)
#~ plt.pause(2)

# Récupérer la liste des objets Line2D
lines = ax.get_lines()

# Trouver l'objet Line2D correspondant à la courbe 'Sinus'
for line in lines:
    if line.get_label() == "Sinus":
        # Changer la couleur de la ligne en rouge
        line.set_color("Red")
        plt.draw()
        break

plt.legend()
#~ plt.pause(2)

# faire bouger les sinus
for i in range(100):
    #~ y2 = np.sin(x+i)
    #~ ax.plot(x, y2, label="Sinus")
    new_point = np.sin(x+i)
    #~ sinplot.set_offsets(np.concatenate([sinplot.get_offsets(), [new_point]]))
    sinplot.set_ydata(new_point)
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)

plt.ioff()
plt.show()