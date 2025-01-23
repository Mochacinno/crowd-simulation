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

    # Create a dictionary to organize iterations based on the number of poissons
    stabilite = {}
    for i, npoisson in enumerate(npoissons):
        array = stabilite.get(npoisson, [])
        array.append(iters_list[i])
        stabilite[npoisson] = array

    # Prepare lists for plotting
    filtered_npoissons = []
    filtered_iters = []
    means = []
    unique_npoissons = []

    for npoisson in sorted(stabilite.keys()):
        iters = stabilite[npoisson]
        sorted_iters = np.sort(iters)
        n = len(sorted_iters)
        trim_count = int(np.round(0.1 * n))

        # Trim the data
        trimmed_data = sorted_iters[trim_count:n-trim_count]

        # Store the filtered npoissons and their corresponding trimmed data
        filtered_npoissons.extend([npoisson] * len(trimmed_data))  # Repeat npoisson for each trimmed value
        filtered_iters.extend(trimmed_data)  # Add the trimmed data

        # Calculate the mean of the trimmed data
        if len(trimmed_data) > 0:  # Ensure there's data to calculate mean
            mean_value = np.mean(trimmed_data)
            means.append(mean_value)
            unique_npoissons.append(npoisson)

    # Convert to numpy arrays for easier plotting
    filtered_npoissons = np.array(filtered_npoissons)
    filtered_iters = np.array(filtered_iters)
    means = np.array(means)
    unique_npoissons = np.array(unique_npoissons)

    # Plotting
    fig, ax = plt.subplots(1, 2, figsize=[12, 5])
    
    # First plot
    ax[0].scatter(npoissons, iters_list, marker='o', label='Data Points')
    ax[0].set_xlabel(r"Nombre de poissons $(N)$", fontsize=12)
    ax[0].set_ylabel(r"Nombre d'iterations $(n)$", fontsize=12)
    ax[0].set_title(r"Nombre d'iterations $(N)$ en fonction de nombre de poissons $(n)$", fontsize=12)
    
    # Second plot with filtered data
    ax[1].scatter(filtered_npoissons, filtered_iters, marker='o', label='Iterations tronqués')
    ax[1].set_xlabel(r"Nombre de poissons $(N)$", fontsize=12, fontstyle='italic')
    ax[1].set_ylabel(r"Nombre d'iterations $(n)$", fontsize=12)
    ax[1].set_title("Après suppression des valeurs extrêmes", fontsize=12)

    # Plot the mean for each unique N
    ax[1].plot(unique_npoissons, means, color='orange', marker='o', label='Moyenne des valeurs tronquées')

    # Add legends
    ax[0].legend()
    ax[1].legend()

    # Adjust layout and show
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
    ax.plot(x, y, color="orange", label=r"Fonction logistique")
    ax.scatter(separation, probability)

    ax.set_title(r"Probabilité de separation des groupes en fonction de chevauchement")
    ax.set_ylabel(r"Probabilité de separation $P(S)$")
    ax.set_xlabel(r"Distance de chevauchement $d$")
    ax.axvline(200, label=r"$d = 2R_b$", linestyle='dashed', color="red")
    plt.legend()
    plt.show()

def plot_bebe():
    data = np.genfromtxt("bebepoisson.txt")

    clients = data[:, 0]
    iters = data[:, 1]
    
    # Create a scatter plot
    fig, ax = plt.subplots()
    #ax[0].scatter(clients, iters, label='Data Points')

    # Remove outlier
    data = np.delete(data, 19, axis=0)

    clients = data[:, 0]
    iters = data[:, 1]
    ax.scatter(clients, iters)

    # Create a dictionary to store iterations for each client
    client_dict = {}
    for i in range(len(data)):
        client = data[i][0]
        iter_value = data[i][1]
        value = client_dict.get(client, [])
        value.append(iter_value)
        client_dict[client] = value
    
    client_dict = dict(sorted(client_dict.items()))

    # Calculate min and max for each client
    min_values = []
    max_values = []
    mean_values = []
    unique_clients = list(client_dict.keys())

    for client in unique_clients:
        iterations = client_dict[client]
        min_values.append(np.min(iterations))
        max_values.append(np.max(iterations))
        mean_values.append(np.mean(iterations))

    # Plot min and max lines
    ax.plot(unique_clients, mean_values, color='orange', marker='o', label='Moyenne')

    # Fill between min and max
    ax.fill_between(unique_clients, min_values, max_values, color='gray', alpha=0.5, label='Intervalle de résultats')

    # Set titles and labels
    ax.set_title(r"Nombre d'itérations $n$ en fonction du nombre de poissons qui y sont liés $Z$")
    ax.set_ylabel(r"Nombre d'itérations $(n)$")
    ax.set_xlabel(r"Poissons liés $(Z)$")


    
    plt.legend()
    #plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()

if __name__ == "__main__":
    #convergence_time()
    #plot_separation()
    plot_bebe()