import numpy as np
import matplotlib.pyplot as plt
from main import *

def run_test(n_exec, n_poissons_min, n_poissons_max, step, r_group, separation_c_group):
    n_poissons_liste = np.arange(n_poissons_min, n_poissons_max, step)
    print(n_poissons_liste)
    for n_poissons in n_poissons_liste:
        n_liste = []
        for _ in range(n_exec):
            model = Model(n_poissons, r_group, separation_c_group, display=False)
            iterations = model.run_no_display()
            #model = Model(n_poissons, r_group, separation_c_group)
            #iterations = model.run()
            n_liste.append(iterations)
    np.savetxt("run_test.txt", n_liste)

def run_separation_test(separation_c_group_min, separation_c_group_max, step, n_exec, n_poissons, r_group):
    res = []
    separation_c_group_liste = np.arange(separation_c_group_min, separation_c_group_max, step)
    for separation in separation_c_group_liste:
        n_liste = []
        for _ in range(n_exec):
            print(n_exec)
            model = Model(n_poissons, r_group, separation)
            iterations = model.run()
            n_liste.append(iterations)
        res.append([separation, sum(n_liste)/n_exec])
    np.savetxt("separation_stability.txt", res)

run_test(100, 20, 30, 10, 100, 10)