import numpy as np
import matplotlib.pyplot as plt
from main import *

def run_iteration_test(n_exec, n_poissons, r_group):
    n_liste = []
    for i in range(n_exec):
        #model = Model(n_poissons, r_group, display=False)
        #iterations = model.run_no_display()
        model = Model(n_poissons, r_group)
        iterations = model.run()
        n_liste.append(iterations)
        print(f"on iteration {i}")
    np.savetxt("run_test.txt", n_liste)

def run_npoissons(n_exec, r_group, n_poissons_min, n_poissons_max, step):
    n_liste = []
    n_poissons_liste = np.arange(n_poissons_min, n_poissons_max, step)
    for n_poissons in n_poissons_liste:
        for i in range(n_exec):
            model = Model(n_poissons, r_group, display=False)
            iterations = model.run_no_display()
            #model = Model(n_poissons, r_group)
            #iterations = model.run()
            n_liste.append([n_poissons, iterations])
    np.savetxt("npoissons4.txt", n_liste)

def run_separation_test(separation_c_group_min, separation_c_group_max, step, n_exec, n_poissons, r_group):
    res = []
    separation_c_group_liste = np.arange(separation_c_group_min, separation_c_group_max, step)
    for separation in separation_c_group_liste:
        for _ in range(n_exec):
            model = Model(n_poissons, r_group, separation)
            iterations = model.run()
            res.append([separation, iterations])
    np.savetxt("separation_stability.txt", res)

def run_separation_test_graphics(separation_c_group_min, separation_c_group_max, step, n_exec, n_poissons, r_group):
    res = []
    separation_c_group_liste = np.arange(separation_c_group_min, separation_c_group_max, step)
    for separation in separation_c_group_liste:
        for _ in range(n_exec):
            model = Model(n_poissons, r_group, separation)
            iterations = model.run()
            #res.append([separation, iterations])
    np.savetxt("separation_test_positions200.txt", iterations)

#run_iteration_test(10, 50, 100)
#run_npoissons(10, 100, 10, 50, 10)
#run_separation_test(50, 200, 50, 3, 40, 100)
run_separation_test_graphics(200, 250, 50, 1, 40, 100)
"""
STANDARD
TUNA school size of 30 to 100
spacing of 1 to 5 meters so if one tuna is 1 meter so rayon d'occultation = 5

10 ITERATIONS

DAns kla vrai vie, les poissons suivent les voisins pourqu'ils ne perdent pas dans la foule

"""

