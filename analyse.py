import numpy as np
import matplotlib.pyplot as plt
from main import *

def run_separation_test2(n_exec, n_poissons_min, n_poissons_max, step, r_group, separation_c_group):
    n_poissons_liste = np.arange(n_poissons_min, n_poissons_max, step)
    for n_poissons in n_poissons_liste:
        for _ in range(n_exec):
            model = Model(n_poissons, r_group, separation_c_group)
            model.run()

def run_separation_test(separation_c_group_min, separation_c_group_max, step, n_exec, n_poissons, r_group):
    res = []
    separation_c_group_liste = np.arange(separation_c_group_min, separation_c_group_max, step)
    for separation in separation_c_group_liste:
        n_liste = []
        for _ in range(n_exec):
            model = Model(n_poissons, r_group, separation)
            iterations = model.run()
            n_liste.append(iterations)
        res.append([separation, sum(n_liste)/n_exec])
    np.savetxt("separation_stability.txt", res)


#model = Model(20, 100, 100)
#model.run("group")

#run_separation_test(0, 500, 100, 15, 10, 150)
data = np.genfromtxt("separation_stability.txt")
print(data)
separation = data[:, 0]
iter = data[:, 1]

fig, ax = plt.subplots()
ax.plot(separation, iter)
plt.show()
