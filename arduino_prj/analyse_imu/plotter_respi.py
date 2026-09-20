import sys
import re
import serial
import matplotlib.pyplot as plt

from collections import deque
from matplotlib.collections import LineCollection

# ============================================================
# Configuration
# ============================================================

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
BAUDRATE = 115200

WINDOW = 10.0       # secondes affichées
ARDUINO_HZ = 100.0

# Rafraîchissement graphique
PLOT_HZ = 20.0

# Nombre de points conservés
MAX_POINTS = int(WINDOW * ARDUINO_HZ)

# ============================================================
# Série
# ============================================================

ser = serial.Serial(PORT, BAUDRATE, timeout=0)

print(f"Lecture de {PORT} à {BAUDRATE} bauds...")

# ============================================================
# Données
# ============================================================

x = deque(maxlen=MAX_POINTS)
y = deque(maxlen=MAX_POINTS)
colors = deque(maxlen=MAX_POINTS)

sample = 0

# ============================================================
# Regex
# ============================================================

ratio_re = re.compile(
    r"ratio_respi:\s*([-+]?\d*\.?\d+)"
)

# ============================================================
# Matplotlib
# ============================================================

plt.ion()

fig, ax = plt.subplots(figsize=(12, 5))

ax.set_title(f"Respiration - {PORT}")
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Ratio respiration")

ax.set_ylim(0, 1.05)
ax.set_xlim(0, WINDOW)

ax.grid(True, alpha=0.3)

# ============================================================
# Temps
# ============================================================

import time

start_time = time.perf_counter()

last_plot = 0.0

# ============================================================
# Boucle
# ============================================================

try:

    color = "green"

    while plt.fignum_exists(fig.number):

        # ----------------------------------------------------
        # Lire TOUT ce qui est disponible
        # ----------------------------------------------------

        while ser.in_waiting:

            raw = ser.readline()

            if not raw:
                break

            try:
                text = raw.decode("utf-8", errors="ignore").strip()
            except:
                continue

            if not text:
                continue

            # ------------------------------------------------
            # Extraction ratio
            # ------------------------------------------------

            match = ratio_re.search(text)

            if not match:
                continue

            ratio = float(match.group(1))

            # Sécurité
            ratio = max(0.0, min(1.0, ratio))

            # ------------------------------------------------
            # Détection UP / DOWN
            # ------------------------------------------------

            if re.search(r"\bUP\b", text, re.IGNORECASE):

                color = "green"

            elif re.search(r"\bDOWN\b", text, re.IGNORECASE):

                color = "red"

            # ------------------------------------------------
            # Ajout
            # ------------------------------------------------

            t = time.perf_counter() - start_time

            x.append(t)
            y.append(ratio)
            colors.append(color)

            sample += 1

        # ----------------------------------------------------
        # Rafraîchissement graphique
        # ----------------------------------------------------

        now = time.perf_counter()

        if now - last_plot >= 1.0 / PLOT_HZ:

            last_plot = now

            if len(x) >= 2:

                # --------------------------------------------
                # Conversion en listes
                # --------------------------------------------

                xx = list(x)
                yy = list(y)

                # --------------------------------------------
                # Construction des segments
                # --------------------------------------------

                segments = []

                for i in range(len(xx) - 1):

                    segments.append([
                        [xx[i], yy[i]],
                        [xx[i + 1], yy[i + 1]]
                    ])

                # --------------------------------------------
                # Supprime uniquement l'ancienne collection
                # --------------------------------------------

                for collection in ax.collections:
                    collection.remove()

                # --------------------------------------------
                # Couleurs
                # --------------------------------------------

                segment_colors = list(colors)[1:]

                lc = LineCollection(
                    segments,
                    colors=segment_colors,
                    linewidths=2
                )

                ax.add_collection(lc)

                # --------------------------------------------
                # Axe X : fenêtre glissante
                # --------------------------------------------

                xmax = xx[-1]

                xmin = max(0, xmax - WINDOW)

                ax.set_xlim(xmin, max(WINDOW, xmax))

                # --------------------------------------------
                # Redessine
                # --------------------------------------------

                fig.canvas.draw_idle()
                fig.canvas.flush_events()

        # ----------------------------------------------------
        # Petite pause pour laisser respirer GUI
        # ----------------------------------------------------

        plt.pause(0.001)

except KeyboardInterrupt:

    print("\nArrêt.")

finally:

    ser.close()

    plt.ioff()
    plt.show()