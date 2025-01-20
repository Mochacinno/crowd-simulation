import numpy as np
import matplotlib.pyplot as plt

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

#lower and upper quartiles



fig, ax = plt.subplots()
ax.plot(data_filtered)
plt.show()
