import numpy as np
import pyvista as pv

# Définir une surface gaussienne simple
n = 20
x = np.linspace(-200, 200, num=n) + np.random.uniform(-5, 5, size=n)
y = np.linspace(-200, 200, num=n) + np.random.uniform(-5, 5, size=n)
xx, yy = np.meshgrid(x, y)
A, b = 100, 100
zz = A * np.exp(-0.5 * ((xx / b) ** 2.0 + (yy / b) ** 2.0))

# Obtenir les points comme un tableau 2D NumPy (N x 3)
points = np.c_[xx.reshape(-1), yy.reshape(-1), zz.reshape(-1)]

# Créer un nuage de points pour la triangulation
cloud = pv.PolyData(points)

# Effectuer la triangulation
surf = cloud.delaunay_2d()

# Initialiser un plot interactif
plotter = pv.Plotter()
mesh = plotter.add_mesh(surf, scalars=zz.ravel(), cmap="ocean", show_edges=False)

# Fonction pour mettre à jour les hauteurs
def update_surface(t):
    """Met à jour les hauteurs pour simuler une animation."""
    new_zz = A * np.exp(-0.5 * ((xx / b) ** 2.0 + (yy / b) ** 2.0)) + 20 * np.sin(0.1 * xx + t)
    surf.points[:, 2] = new_zz.ravel()  # Mettre à jour les hauteurs des sommets
    surf.modified()  # Marquer comme modifié

# Animation dans une boucle
def animate():
    t = 0
    while True:
        update_surface(t)
        plotter.update()  # Forcer le rafraîchissement de l'affichage
        t += 0.1

# Lancer l'affichage
plotter.show(auto_close=False)
animate()
