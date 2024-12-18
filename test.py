import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Paramètres de la mer
amplitude = 1  # Amplitude des vagues
frequency = 1  # Fréquence des vagues
speed = 1      # Vitesse des vagues

# Créer la figure et l'axe
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(-2, 2)
ax.set_title("Animation d'un bateau sur une mer agitée")

# Générer une mer
x = np.linspace(0, 10, 1000)
y = np.zeros_like(x)  # Initialisation des vagues
line, = ax.plot(x, y, label="Mer")

# Bateau (représenté par un triangle)
boat, = ax.plot([], [], 'r', marker="^", markersize=15, label="Bateau")
ax.legend()

# Initialiser les données du bateau
def init():
    line.set_ydata(np.sin(2 * np.pi * frequency * x))
    boat.set_data(5, 0)  # Position initiale du bateau au centre de l'axe
    return line, boat

# Mise à jour à chaque frame
def update(frame):
    global amplitude, frequency, speed
    y = amplitude * np.sin(2 * np.pi * frequency * (x - speed * frame / 30))
    line.set_ydata(y)

    # Position du bateau (on suppose qu'il est au centre)
    boat.set_data(5, np.interp(5, x, y))
    return line, boat

# Créer l'animation
anim = FuncAnimation(fig, update, frames=200, init_func=init, blit=True, interval=50)

# Ajouter des contrôles utilisateur (par exemple, modification de l'agitation)
def set_agitation(new_amplitude, new_frequency, new_speed):
    global amplitude, frequency, speed
    amplitude = new_amplitude
    frequency = new_frequency
    speed = new_speed

# Sauvegarder ou afficher
plt.show()

# Exemple : Ajustez les paramètres d'agitation par la suite en appelant la fonction `set_agitation`.