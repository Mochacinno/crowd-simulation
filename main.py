import pygame
import sys
from random import randint
from config import *
import numpy as np
import math


def define_model_zone():
    width_spacing = (screen_width - model_width) / 2
    height_spacing = (screen_height - model_height) / 2
    model_zone = np.array([[width_spacing, height_spacing], [width_spacing+model_width, height_spacing+model_height]])
    return model_zone

def define_walls():
    width_spacing = (screen_width - model_width) / 2
    height_spacing = (screen_height - model_height) / 2

    mur_haut = [np.array([width_spacing, height_spacing]), np.array([model_width, 0])]  # [start point, direction vector]
    mur_bas = [np.array([width_spacing, model_height + height_spacing]), np.array([model_width, 0])]
    mur_gauche = [np.array([width_spacing, height_spacing]), np.array([0, model_height])]
    mur_droite = [np.array([model_width + width_spacing, height_spacing]), np.array([0, model_height])]
    liste_murs = [mur_haut, mur_bas, mur_gauche, mur_droite]
    return liste_murs

def normaliser_vecteur(vecteur):
    norme = np.linalg.norm(vecteur)
    if norme == 0:
        return vecteur
    return vecteur / norme

def calculer_distance(pos1, pos2):
    return np.linalg.norm(pos1 - pos2)

def generate_groups_with_exact_centroid_distance(group_num, group_radius, separation_distance, zone_area):
    # we assume that the walls dont pose problem to the fish generation so we will generate the 2 imaginary centroids in the middle
    # the group radius must not make it that the point will be generated outside the border
    # Step 1: Initialize the first centroid within a space in the center
    midpoint = (zone_area[0] + zone_area[1]) / 2
    target_centroid_1 = (midpoint[0] - separation_distance / 2, midpoint[1])
    #print(f"target centroid for group1 {target_centroid_1}")
    # Step 2: Calculate the position of the second centroid with the desired separation
    #angle = np.random.uniform(np.pi, 2 * np.pi)  # Random angle for separation
    target_centroid_2 = (midpoint[0] + separation_distance / 2, midpoint[1])

    # Step 3: Generate points for each group around the theoretical centroid
    def generate_group(center):
        return [
            (
                np.random.normal(center[0], group_radius / 2),
                np.random.normal(center[1], group_radius / 2)
            )
            for _ in range(group_num)
        ]

    group_1 = generate_group(target_centroid_1)
    group_2 = generate_group(target_centroid_2)

    # Step 4: Adjust centroids to maintain exact separation
    def recalculate_centroid(points):
        return (
            sum(point[0] for point in points) / group_num,
            sum(point[1] for point in points) / group_num
        )

    centroid_1_actual = recalculate_centroid(group_1)
    #print(f"actual centroid for group1 {centroid_1_actual}")
    centroid_2_actual = recalculate_centroid(group_2)

    # Shift points to adjust centroids if necessary
    def shift_group(points, current_centroid, target_centroid):
        shift_vector = np.array(target_centroid) - np.array(current_centroid)
        return [(x + shift_vector[0], y + shift_vector[1]) for x, y in points]

    group_1 = shift_group(group_1, centroid_1_actual, target_centroid_1)
    #print(f"after shift, actual centroid for group1 {recalculate_centroid(group_1)}")
    group_2 = shift_group(group_2, centroid_2_actual, target_centroid_2)
    
    group_1_fish = {}
    for i, coordinate in enumerate(group_1):
        group_1_fish[i] = Poisson(coordinate[0], coordinate[1], i)

    group_2_fish = {}
    for i, coordinate in enumerate(group_2):
        group_2_fish[i + group_num] = Poisson(coordinate[0], coordinate[1], i + group_num)

    return group_1_fish, group_2_fish

# define zone area
zone_area = define_model_zone()
liste_murs = define_walls()

class Poisson:
    def __init__(self, x, y, id, rayon_collision = 10):
        self.id = id
        self.pos = np.array([x, y], dtype=float)
        self.vitesse = 1
        self.tolerance = 3
        self.rayon_collision = rayon_collision  # Rayon de collision
        self.rayon_de_vue = 0
        self.idle = False
        self.arrow = [0, 0] # juste pour visualiser

    def choisir_cible(self, dict_poissons):
        # Extract keys once, excluding the current fish
        target_ids = list(dict_poissons.keys())

        if self.id in target_ids:
            target_ids.remove(self.id)  # Avoid including self

        # Randomly select two distinct targets
        self.cible1, self.cible2 = np.random.choice([dict_poissons[id] for id in target_ids], 2, replace=False)

        # Directly assign perceived positions
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos

    def is_within_walls(self, point):
        """
        Check if the destination point is within the bounds of a rectangular area.

        Parameters:
            destination (tuple or np.array): The point to check (x, y).
            width (int): The width of the boundary (default: 800).
            height (int): The height of the boundary (default: 600).

        Returns:
            bool: True if the point is within bounds, False otherwise.
        """
        x, y = point
        return zone_area[0][0] <= x <= zone_area[1][0] and zone_area[0][1] <= y <= zone_area[1][1]
    
    def calculer_destination(self, dict_poissons):
        # Perceived target positions
        cibles_en_vue = self.cible_en_vue(dict_poissons)
        if cibles_en_vue[0]: # si on voit cible1
            self.pos_percue_cible1 = self.cible1.pos
        #else: 
            #print(f"poisson {self.id} cant see cible1")
        if cibles_en_vue[1]: # si on voit cible2
            self.pos_percue_cible2 = self.cible2.pos
        #else:
            #print(f"poisson {self.id} cant see cible2")
        
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2

        # Compute direction vectors
        vectdir = np.array([x1 - x2, y1 - y2])
        perp_vectdir = np.array([y1 - y2, x2 - x1]) / np.linalg.norm(vectdir)
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2

        # Find the initial intersection point
        destination = self.line_intersection((self.pos, vectdir), (midpoint, perp_vectdir))
        # Efficient collision check using spatial filtering
        poissons_positions = np.array([fish.pos for fish in dict_poissons.values() if fish != self])
        distances = np.linalg.norm(poissons_positions - destination, axis=1)
        collision_indices = np.where(distances < self.rayon_collision)[0]

        for idx in collision_indices:
            fish_pos = poissons_positions[idx]
            direction = (destination - fish_pos) / np.linalg.norm(destination - fish_pos)
            destination = fish_pos + direction * self.rayon_collision

        # If the point is outside walls, find the closest valid point
        if not self.is_within_walls(destination):
            closest_point = None
            closest_distance = float('inf')

            # Loop through walls to find valid intersections
            for mur in liste_murs:
                wall_start = mur[0]
                wall_end = wall_start + mur[1]

                # Find the intersection with the wall
                intersection = self.line_intersection((midpoint, perp_vectdir), mur)

                # Validate intersection within wall bounds
                if intersection is not None:
                    if (
                        min(wall_start[0], wall_end[0]) <= intersection[0] <= max(wall_start[0], wall_end[0])
                        and min(wall_start[1], wall_end[1]) <= intersection[1] <= max(wall_start[1], wall_end[1])
                    ):
                        # Calculate distance from current position
                        distance = np.linalg.norm(intersection - self.pos)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_point = intersection
                

            # Update destination to the closest valid point
            if closest_point is not None:
                destination = closest_point

        return destination

    def line_intersection(self, line1, line2):
        """
        Finds the intersection point of two line segments, if it exists.
        Parameters:
            line1, line2: Each line is defined as (point, direction_vector),
                          where point and direction_vector are numpy arrays.
        Returns:
            The point of intersection as a numpy array, or None if no intersection.
        """
        pos1, dir1 = line1
        pos2, dir2 = line2

        # Compute 2D cross product directly
        cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
        det = cross(dir1, dir2)

        if abs(det) < 1e-10:
            return None  # Lines are parallel or nearly parallel

        diff = pos2 - pos1
        t = cross(diff, dir2) / det

        return pos1 + t * dir1


    def calculer_prochaine_position(self, dict_poissons, dict_pos):
        
        repulsion = self.verifier_collisions(dict_poissons)
        self.arrow = repulsion
        vect_dir = self.calculer_destination(dict_poissons) - self.pos
        prochaine_position = self.pos + normaliser_vecteur(normaliser_vecteur(vect_dir) + repulsion) * self.vitesse
        self.idle = False
        
        if np.linalg.norm(vect_dir) < self.tolerance : # Si on est pas loin de la destination
            prochaine_position = self.pos + normaliser_vecteur(repulsion) * self.vitesse
            self.idle = True

        dict_pos[self.id] = prochaine_position
    
    def verifier_collisions(self, dict_poissons):
        # Extract positions and keys, ensuring consistent order
        poisson_keys = list(dict_poissons.keys())
        positions = np.array([dict_poissons[key].pos for key in poisson_keys])
        distances = np.linalg.norm(positions - self.pos, axis=1)
    
        # Mask to identify collisions (distances smaller than collision radius)
        collision_mask = distances < self.rayon_collision
        repulsion = np.zeros(2)
    
        # For each collision, calculate the repulsion
        for i, collides in enumerate(collision_mask):
            if collides and poisson_keys[i] != self.id:  # Skip self
                vecteur_repulsion = self.pos - positions[i]
                vecteur_repulsion_normalise = normaliser_vecteur(vecteur_repulsion)
                force = (self.rayon_collision - distances[i]) / distances[i]
                repulsion += vecteur_repulsion_normalise * force
    
        return repulsion


    def cible_en_vue2(self, dict_poissons):
        """
        Vérifie que la personne peut voir ses 2 cibles

        Args : dict_poissons

        Returns : 1 booléen pour chaque cible
        """
        cibles_en_vue = []
        for cible in [self.cible1, self.cible2]:
            # Pente droite jusqu'à la cible
            vectdir = self.pos-cible.pos
            cible_en_vue = True
            while cible_en_vue == True:
                for poisson in dict_poissons.values():
                    # Vérification pour cible 1
                    if poisson != self and poisson != cible :
                        min_pos = np.minimum(self.pos, cible.pos)
                        max_pos = np.maximum(self.pos, cible.pos)
                        if np.all((poisson.pos >= min_pos) & (poisson.pos <= max_pos)):
                            perpvectdir = np.array([-vectdir[1], vectdir[0]])
                            distance = np.linalg.norm(poisson.pos - self.line_intersection((self.pos, vectdir), (poisson.pos, perpvectdir)))
                            if distance < self.rayon_de_vue:
                                cible_en_vue = False
                                break
                else: 
                    break
            cibles_en_vue.append(cible_en_vue)
        return cibles_en_vue
    
    def cible_en_vue(self, dict_poissons):
        """
        Vérifie que la personne peut voir ses 2 cibles

        Args : dict_poissons

        Returns : 1 booléen pour chaque cible
        """
        cibles_en_vue = []

        for cible in [self.cible1, self.cible2]:
            # Pente droite jusqu'à la cible
            vectdir = self.pos-cible.pos
            perpvectdir = np.array([-vectdir[1], vectdir[0]])
            
            # Get bounds of the line segment
            min_pos = np.minimum(self.pos, cible.pos)
            max_pos = np.maximum(self.pos, cible.pos)

            # Check if any fish obstructs the line of sight
            obstructed = False
            for poisson in dict_poissons.values():
                if poisson != self and poisson != cible:
                    # Check if the fish is within the bounding box
                    if np.all((poisson.pos >= min_pos) & (poisson.pos <= max_pos)):
                        # Calculate perpendicular distance to the line
                        distance = np.abs(np.dot(poisson.pos - self.pos, perpvectdir)) / np.linalg.norm(vectdir)
                        if distance < self.rayon_de_vue:
                            obstructed = True
                            break

            cibles_en_vue.append(not obstructed)
        return cibles_en_vue

    def afficher(self, group_1_lim, screen, bebepoissoni=None):
        # Draw walls
        for mur in liste_murs:
            pygame.draw.line(screen, WHITE, mur[0], mur[0] + mur[1])  

        # Adjust color based on group_1_lim
        if self.id < group_1_lim:
            colour = (10, 200, 50)
        else:
            colour = WHITE

        # Adjust color if it matches bebepoissoni
        if self.id == bebepoissoni:
            colour = (200, 10, 10)

        # Draw the circle
        pygame.draw.circle(screen, colour, self.pos, 2)

class Model:
    """
    Class pour le modelisation
    Returns: data pour analyse
    """
    def __init__(self, n_poisson, r_group, separation_c_group, display = True):
        self.zone_area = define_model_zone()
        self.liste_murs = define_walls()

        self.dict_poissons = {}
        self.dict_pos = {}

        self.n_poisson = n_poisson
        self.r_group = r_group
        self.separation_c_group = separation_c_group
        self.clock = 0
        self.screen = 0
        self.font = 0
        self.display = display
    
    def init_program(self):
        if self.display: 
            pygame.init()
            self.clock = pygame.time.Clock()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Modélisation du banc de poisson")
            self.font = pygame.font.Font(None, 24)
        # WITH SEPARATION DISTANCE
        self.group_1, group_2 = generate_groups_with_exact_centroid_distance(self.n_poisson, self.r_group, self.separation_c_group, self.zone_area)

        self.dict_poissons = self.group_1.copy()
        self.group_1_lim = len(self.group_1) # with the group 1 lower bound being 0

        for id, poisson in self.group_1.items():
            self.dict_pos[id] = poisson.pos

        for id, poisson in group_2.items():
            self.dict_poissons[id] =  poisson
            self.dict_pos[id] = poisson.pos

        # Affecter les 2 cibles à chacun des gens
        for poisson in self.group_1.values() :
           dict_poissons_temp = self.group_1.copy()
           poisson.choisir_cible(dict_poissons_temp)

        for poisson in group_2.values() :
           dict_poissons_temp = group_2.copy()
           poisson.choisir_cible(dict_poissons_temp)

    def run(self, autorun = True, bebepoissoni = None):
        if self.dict_poissons == {}:
            self.init_program()
        # Boucle principale
        stable = False
        n = 0
        keypress = False
        while not keypress:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if not autorun and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if stable:
                            keypress = True
            if autorun and stable:
                keypress = True
            if not stable:
                n += 1
                stable = True
                self.screen.fill(BLACK)
                # Étape 1 : Calculer les prochaines positions
                for poisson in self.dict_poissons.values():
                    poisson.calculer_prochaine_position(self.dict_poissons, self.dict_pos)
                    # Étape 2 : Mettre à jour les positions
                    poisson.pos = self.dict_pos[poisson.id]
                    # afficher
                    if poisson.idle != True:
                        stable = False
                    poisson.afficher(self.group_1_lim, self.screen, bebepoissoni)
            pygame.display.update()
        return n # nombre d'iterations
    
    def run_no_display(self):
        if self.dict_poissons == {}:
            self.init_program()
        
        # Boucle principale
        stable = False
        n = 0
        while not stable:
            n += 1
            stable = True
            # Étape 1 : Calculer les prochaines positions
            for poisson in self.dict_poissons.values():
                poisson.calculer_prochaine_position(self.dict_poissons, self.dict_pos)
                # Étape 2 : Mettre à jour les positions
                poisson.pos = self.dict_pos[poisson.id]
                # afficher
                if poisson.idle != True:
                    stable = False
        return n # nombre d'iterations

    def run_and_save(self, autorun = True, bebepoissoni = None):
        if self.dict_poissons == {}:
            self.init_program()
        # Boucle principale
        stable = False
        n = 0
        keypress = False

        hist_pos = []
        while not keypress:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if not autorun and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if stable:
                            keypress = True
            if autorun and stable:
                keypress = True
            if not stable:
                n += 1
                stable = True

                self.screen.fill(BLACK)

                # Étape 1 : Calculer les prochaines positions
                for poisson in self.dict_poissons.values():
                    poisson.calculer_prochaine_position(self.dict_poissons, self.dict_pos)
                    # Étape 2 : Mettre à jour les positions
                    poisson.pos = self.dict_pos[poisson.id]
                    # afficher
                    if poisson.idle != True:
                        stable = False
                    poisson.afficher(self.group_1_lim, self.screen, bebepoissoni)
            
            if n == 1:
                hist_pos = list(self.dict_pos.values())
            else:
                hist_pos = np.column_stack((hist_pos, list(self.dict_pos.values())))

            pygame.display.update()
        np.savetxt("hist_pos.txt", hist_pos, fmt='%.2f')
    
    def run_bebepoisson(self, autorun=True):
        self.run(autorun)
        bebepoisson_i = np.random.randint(self.group_1_lim, len(self.dict_poissons))
        bebepoisson = self.dict_poissons[bebepoisson_i]
        bebepoisson.choisir_cible(self.group_1) # bebe poisson tjrs dans group 2 choisi 2 cibles dans group 1
        self.screen.fill(WHITE)
        self.run(bebepoissoni=bebepoisson_i, autorun=autorun)

if __name__ == "__main__":
    model = Model(10, 50, 10)
    #model.run_bebepoisson(autorun=False)
    model.run_and_save(autorun=False)