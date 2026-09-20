import sys
import re
import serial
import matplotlib.pyplot as plt
from collections import deque

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
BAUDRATE = 115200

WINDOW = 10          # secondes affichées
MAX_POINTS = 300

# ------------------------------------------------------------
# Série
# ------------------------------------------------------------

ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)

print(f"Lecture de {PORT} à {BAUDRATE} bauds...")

# ------------------------------------------------------------
# Données
# ------------------------------------------------------------

x = deque(maxlen=MAX_POINTS)
y = deque(maxlen=MAX_POINTS)

# Couleur associée à chaque point
colors = deque(maxlen=MAX_POINTS)

sample = 0

# ------------------------------------------------------------
# Matplotlib
# ------------------------------------------------------------

plt.ion()

fig, ax = plt.subplots(figsize=(12, 5))

line, = ax.plot([], [], color="blue", linewidth=2)

ax.set_title("Respiration")
ax.set_xlabel("Échantillons")
ax.set_ylabel("Ratio respiration")
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.3)

# ------------------------------------------------------------
# Regex
# ------------------------------------------------------------

ratio_re = re.compile(r"ratio_respi:\s*([-+]?\d*\.?\d+)")

# ------------------------------------------------------------
# Boucle
# ------------------------------------------------------------

try:
    
    color = "green"

    while True:

        raw = ser.readline()

        if not raw:
            plt.pause(0.01)
            continue

        try:
            text = raw.decode("utf-8", errors="ignore").strip()
        except:
            continue

        if not text:
            continue
            
        print( "text: '%s'" % text )

        # Cherche ratio_respi
        match = ratio_re.search(text)

        if not match:
            continue

        ratio = float(match.group(1))

        # Sécurité
        ratio = max(0.0, min(1.0, ratio))
        
        print( "ratio:%.2f" % ratio )

        # Détermine la couleur
        if re.search(r"\bUP\b", text, re.IGNORECASE):
            color = "green"

        elif re.search(r"\bDOWN\b", text, re.IGNORECASE):
            color = "red"

        #~ else:
            #~ color = "blue"

        # Ajout
        x.append(sample)
        y.append(ratio)
        colors.append(color)

        sample += 1

        # ----------------------------------------------------
        # Redessine
        # ----------------------------------------------------

        if len(x) > 1:

            # Ligne bleue de base
            ax.clear()

            ax.set_title(f"Respiration - {PORT}")
            ax.set_xlabel("Échantillons")
            ax.set_ylabel("Ratio respiration")

            ax.set_ylim(0, 1.05)
            ax.grid(True, alpha=0.3)

            # Dessine chaque segment avec sa couleur
            for i in range(1, len(x)):

                ax.plot(
                    [x[i - 1], x[i]],
                    [y[i - 1], y[i]],
                    color=colors[i],
                    linewidth=2
                )

            # Fenêtre glissante
            if len(x) > 2:

                xmin = max(0, x[-1] - MAX_POINTS)

                ax.set_xlim(xmin, x[-1] + 1)

            plt.pause(0.001)

except KeyboardInterrupt:

    print("\nArrêt.")

finally:

    ser.close()
    plt.ioff()
    plt.show()