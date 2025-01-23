import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

# Exemple de nuages de points
points1 = [(1, 1), (2, 3), (3, 1), (2, 2),(5,4),(3,2.5)]
points2 = [(2.5, 2.5), (3.5, 4), (5, 3), (4, 2)]

# Fonction pour créer un polygone convexe à partir d'un nuage de points
def create_polygon(points):
    hull = ConvexHull(points)
    return Polygon([points[v] for v in hull.vertices])

# Création des polygones
polygon1 = create_polygon(points1)
polygon2 = create_polygon(points2)

# Vérification de collision
collision = polygon1.intersects(polygon2)

# Affichage des résultats
print(f"Les polygones sont en collision : {collision}")

# Visualisation avec matplotlib
plt.figure()
plt.plot(*zip(*polygon1.exterior.coords), label="Polygone 1", color='blue')
plt.plot(*zip(*polygon2.exterior.coords), label="Polygone 2", color='red')
plt.scatter(*zip(*points1), color='blue')
plt.scatter(*zip(*points2), color='red')
plt.legend()
plt.show()