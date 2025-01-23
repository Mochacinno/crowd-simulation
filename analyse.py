import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
import math

def convergence_time2():
    data = np.genfromtxt("run_test.txt")

    mean = np.mean(data)
    median = np.median(data)
    print(f"mean: {mean}, median: {median}")
    lquartile = np.quantile(data, 0.25)
    uquartile = np.quantile(data, 0.75)
    print(uquartile)
    filter = np.logical_and(data <= uquartile, data >= lquartile)
    data_filtered = data[filter]
    filtered_mean = np.mean(data_filtered)
    print(f"filtered mean: {filtered_mean}")

    iter = np.arange(1, len(data)+1, 1)
    sliced_mean_liste = []
    for n in iter:
        sliced_data = data[:n]
        sliced_mean = np.mean(sliced_data)
        sliced_mean_liste.append(sliced_mean)

    fig, ax = plt.subplots(2)
    ax[0].plot(data_filtered)
    ax[1].plot(iter, sliced_mean_liste)
    ax[1].plot(iter, np.linspace(mean, mean, num=len(data)))
    plt.show()

def convergence_time():
    data = np.genfromtxt("npoissons.txt")

    npoissons = data[:, 0]
    iters_list = data[:, 1]

    # fait un dictionairy pour organiser les iterations en fonction de nbr poissons
    stabilite = {}
    for i, npoisson in enumerate(npoissons):
        array = stabilite.get(npoisson, [])
        array.append(iters_list[i])
        stabilite[npoisson] = array

    mean_iters_filtered = []
    for iters in stabilite.values():
        mean = np.mean(iters)
        median = np.median(iters)
        lquartile = np.quantile(iters, 0.25)
        uquartile = np.quantile(iters, 0.75)
        filter = np.logical_and(iters <= uquartile, iters >= lquartile)
        iters_filtered = np.array(iters)[filter]
        filtered_mean = np.mean(iters_filtered)
        mean_iters_filtered.append(filtered_mean)

    fig, ax = plt.subplots(1,2, figsize=[12,5])
    ax[0].scatter(npoissons, iters_list, marker='o')
    ax[1].scatter(stabilite.keys(), mean_iters_filtered, marker='o')
    #ax.scatter(stabilite.keys(), median_iters, marker='o')
    #ax.scatter(stabilite.keys(), mean_iters, marker='o')
    #ax.scatter(stabilite.keys(), mean_iters_filtered, marker='o')
    ax[0].set_xlabel("Nombre de poissons")
    ax[0].set_ylabel("Nombre d'iterations")
    ax[0].set_title("Nombre d'iterations en fonction de nombre de poisson")
    ax[1].set_xlabel("Nombre de poissons")
    ax[1].set_ylabel("Nombre d'iterations")
    ax[1].set_title("Moyenne Pondérée d'iterations pour même nombre de poisson")
    plt.figtext(0.5, -0.2, "(a)", ha="center", va="center", fontsize=12, transform=ax[0].transAxes)
    plt.figtext(0.5, -0.2, "(b)", ha="center", va="center", fontsize=12, transform=ax[1].transAxes)
    plt.subplots_adjust(bottom=0.2)
    plt.show()

"""
from matplotlib.patches import Circle

# List of file names
file_names = [
    "separation_test_positions50.txt",
    "separation_test_positions100.txt",
    "separation_test_positions150.txt",
    "separation_test_positions200.txt"
]

# Create a figure with 4 subplots in a single row
fig, axs = plt.subplots(1, 4, figsize=(15, 5))

# Loop through each file and corresponding subplot
for i, file_name in enumerate(file_names):
    # Load data
    data = np.genfromtxt(file_name)

    # Split data into two groups
    group1 = data[:40]
    group1x = group1[:, 0]
    group1y = group1[:, 1]
    group2 = data[40:]
    group2x = group2[:, 0]
    group2y = group2[:, 1]

    # Function to calculate barycenter
    def calculate_barycenter(points):
        return (
            np.mean(points[:, 0]),
            np.mean(points[:, 1])
        )

    # Calculate barycenters
    barycenter1 = calculate_barycenter(group1)
    barycenter2 = calculate_barycenter(group2)

    # Create scatter plots
    axs[i].scatter(group1x, group1y, marker='o', s=3, label='Group 1')
    axs[i].scatter(group2x, group2y, marker='o', s=3, label='Group 2')

    # Create circles at the barycenters
    circle1 = Circle(barycenter1, 100, color='gray', alpha=0.2, fill=True)
    axs[i].add_patch(circle1)
    circle2 = Circle(barycenter2, 100, color='gray', alpha=0.2, fill=True)
    axs[i].add_patch(circle2)

    # Set limits and labels
    axs[i].set_xlim(200, 700)
    axs[i].set_ylim(100, 500)
    axs[i].set_aspect('equal', adjustable='box')
    #axs[i].set_title(f'Scatter Plot for {file_name}')
    axs[i].legend()

    # Hide axes
    axs[i].xaxis.set_visible(False)
    axs[i].yaxis.set_visible(False)

# Adjust layout
plt.tight_layout()
plt.show()
"""
def run_separation(data, n_poisson):
    #data = np.genfromtxt("separation_stable_positions.txt")
    # Split data into two groups
    group1 = data[:n_poisson]
    group2 = data[n_poisson:]

    # Fonction pour créer un polygone convexe à partir d'un nuage de points
    def create_polygon(points):
        hull = ConvexHull(points)
        return Polygon([points[v] for v in hull.vertices])

    # Création des polygones
    polygon1 = create_polygon(group1)
    polygon2 = create_polygon(group2)

    # Vérification de collision
    collision = polygon1.intersects(polygon2)

    # Affichage des résultats
    #print(f"Les polygones sont en collision : {collision}")

    """
    # Visualisation avec matplotlib
    plt.figure()
    plt.plot(*zip(*polygon1.exterior.coords), label="Polygone 1", color='blue')
    plt.plot(*zip(*polygon2.exterior.coords), label="Polygone 2", color='red')
    plt.scatter(*zip(*group1), color='blue')
    plt.scatter(*zip(*group2), color='red')
    plt.legend()
    plt.show()
    """
    return collision

#(50, [100.0])
#(60, [100.0])
#(100, [90.0])
#(120, [100.0])
#(130, [60.0])
#(120, [70.0])

#(150, [50.0])
#(170, [40.0])
#(190, [40.0])
#(200, [10.0])
#separation()
#pour 20 poisson
#(50, [90.0])
#(70, [90.0, 90.0])
#(90, [90.0, 90.0, 40.0])
#(110, [90.0, 90.0, 40.0, 40.0])
#(130, [90.0, 90.0, 40.0, 40.0, 20.0])

def plot_separation():
    data = np.genfromtxt("plotseparation.txt")
    separation = data[:, 0]
    probability = data[:, 1]/100
    k=0.055
    x = np.linspace(0, 250, 100)
    y = 1/(1+np.exp(-k*(x-100)))
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.scatter(separation, probability)

    ax.set_title("Probabilité de separation des groupes en fonction de chevauchement")
    ax.set_ylabel("Probability of separation")
    ax.set_xlabel("Separation distance")
    plt.legend()
    plt.show()

def plot_bebe():
    data = np.genfromtxt("bebepoisson.txt")

    clients = data[:, 0]
    iters = data[:, 1]
    fig, ax = plt.subplots()
    ax.scatter(clients, iters)

    ax.set_title("Probabilité de separation des groupes en fonction de chevauchement")
    ax.set_ylabel("Probability of separation")
    ax.set_xlabel("Separation distance")
    plt.legend()
    plt.show()
    
    client_dict = {}
    for i in range(len(data)):
        client = data[i][0]
        iter = data[i][1]
        value = client_dict.get(client, [])
        value.append(iter)
        client_dict[client] = value
    
    print(client_dict)

if __name__ == "__main__":
    #convergence_time()
    #plot_separation()
    plot_bebe()