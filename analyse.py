import numpy as np
import matplotlib.pyplot as plt

"""
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
"""

"""
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