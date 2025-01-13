import numpy as np
import pyvista as pv

# Dimensions de la grille
nx, ny = 50, 50  # Nombre de points en x et y
x = np.linspace(-10, 10, nx)  # Coordonnées x
y = np.linspace(-10, 10, ny)  # Coordonnées y
x, y = np.meshgrid(x, y)
z = np.zeros_like(x)  # Initialement, la surface est plate

# Créer une grille PyVista
grid = pv.StructuredGrid(x, y, z)

# Fonction pour mettre à jour les vagues
def wave_animation(t):
    """Met à jour la surface pour simuler des vagues."""
    z = np.sin(1000000*np.sqrt(x**2 + y**2) - t)  # Formule des vagues
    grid.points[:, 2] = z.ravel()  # Mettre à jour les hauteurs
    grid.modified()  # Indique que les données ont changé

# Créer un plot interactif
plotter = pv.Plotter()
plotter.add_mesh(grid, scalars=z.ravel(), cmap="viridis", show_edges=False)

# Fonction de callback pour animer
def update(frame):
    wave_animation(frame * 0.1)  # Met à jour les vagues avec le temps
    return

# Lancer l'animation
plotter.show(auto_close=False)
plotter.add_callback(update, interval=50)  # Appelle `update` toutes les 50 ms
plotter.start_xvfb()  # Démarre l'animation