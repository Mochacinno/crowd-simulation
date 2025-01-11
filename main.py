import pygame
import sys
from random import randint
from config import *
import numpy as np
import math

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Modélisation du banc de poisson")

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

class Poisson:
    def __init__(self, x, y, id, rayon_collision = 10):
        self.id = id
        self.pos = np.array([x, y], dtype=float)
        self.vitesse = 1
        self.tolerance = 3
        self.rayon_collision = rayon_collision  # Rayon de collision
        self.rayon_de_vue = 10
        self.idle = False
        self.arrow = [0, 0] # juste pour visualiser

    def choisir_cible(self, dict_poissons):
        # Extract keys once, excluding the current fish
        target_ids = list(dict_poissons.keys())
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
        Parameters: 2 lines of format (point of the line, direction vector of the line)
        Returns: The point of intersection, None if no intersection
        """
        pos1, vect_dir1 = line1
        pos2, vect_dir2 = line2

        line_cross_product = np.cross(vect_dir1, vect_dir2)

        # Check if lines are parallel or almost parallel
        if abs(line_cross_product) < 1e-10:
            return None  # Lines are parallel or nearly so

        pos_diff = pos2 - pos1
        t = np.cross(pos_diff, vect_dir2) / line_cross_product

        # Calculate intersection point
        intersection = pos1 + t * vect_dir1
        return intersection

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
    
    def debug_afficher(self, highlight=False):

        # TODO: procedural generated fish
        #body_size = [10, 10, 10]
        # distance constraint
        # one point that moves, all the other points follow
        # draw walls 
        for mur in liste_murs:
            pygame.draw.line(screen, WHITE, mur[0], mur[0]+mur[1])
        if highlight:
             pygame.draw.circle(screen, (255, 0, 0), self.calculer_destination(), 2)
             pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.pos_percue_cible1))
             pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.pos_percue_cible2))
             pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
        pygame.draw.circle(screen, (0, 200, 100), self.pos, self.rayon_collision, 1)       
        if self.id in group_1_ids:
            pygame.draw.circle(screen, (0, 200, 100), self.pos, 2)
        else:
            pygame.draw.circle(screen, WHITE, self.pos, 2)
        pygame.draw.line(screen, (10, 50, 155), (self.pos), (self.pos + self.arrow*50))

    def afficher(self, group_1_ids):
        for mur in liste_murs:
            pygame.draw.line(screen, WHITE, mur[0], mur[0]+mur[1])  

        if self.id in group_1_ids:
            pygame.draw.circle(screen, (0, 200, 100), self.pos, 2)
        else:
            pygame.draw.circle(screen, WHITE, self.pos, 2)



font = pygame.font.Font(None, 24)


class Interface:
    def __init__(self):
        self.display_fish_list()

    def display_fish_list(self):
        """Display list of fish"""
        y_offset = 10
        for poisson in dict_poissons.values():
            text = font.render(f"Poisson {poisson.id}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 30

    def check_click_on_list(self, mouse_pos):
        """Check if fish in list is clicked"""
        y_offset = 10
        for poisson in dict_poissons.values():
            text_rect = pygame.Rect(10, y_offset, 100, 30)
            if text_rect.collidepoint(mouse_pos):
                return poisson.id 
            y_offset += 30
        return None

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

# La dictionnaire des poissons
dict_poissons = {}
dict_pos = {}
selected_fish = None  # This will store the ID of the selected fish

### GROUP TESTING
# Random points
"""
# Number of fish in each group
group_size = int(group_num)  # Total 80 fish, split into 2 groups

group_1_ids = set(range(group_size))  # IDs 0-39 for Group 1
group_2_ids = set(range(group_size, group_size * 2))  # IDs 40-79 for Group 2

# Création des gens
for i in range(group_num*2):

   # Assign fish to their respective group
   if i in group_1_ids:
       poisson = Poisson(randint(0,300),randint(0,600), i)
       group_1[i] = poisson
   elif i in group_2_ids:
       poisson = Poisson(randint(400,800),randint(0,600), i)
       group_2[i] = poisson

   # Adding to dictionairy
   dict_poissons[i] = poisson
   dict_pos[i] = poisson.pos

# Affecter les 2 cibles à chacun des gens
for poisson in group_1.values() :
   dict_poissons_temp = group_1.copy()
   poisson.choisir_cible(dict_poissons_temp)

for poisson in group_2.values() :
   dict_poissons_temp = group_2.copy()
   poisson.choisir_cible(dict_poissons_temp)
"""
# WITH SEPARATION DISTANCE
group_1, group_2 = generate_groups_with_exact_centroid_distance(group_num, group_radius, init_group_separation, zone_area)

dict_poissons = group_1.copy()
group_1_ids = list(group_1.keys())

for id, poisson in group_2.items():
    dict_poissons[id] =  poisson

# Affecter les 2 cibles à chacun des gens
for poisson in group_1.values() :
   dict_poissons_temp = group_1.copy()
   poisson.choisir_cible(dict_poissons_temp)

for poisson in group_2.values() :
   dict_poissons_temp = group_2.copy()
   poisson.choisir_cible(dict_poissons_temp)
"""
### SIMPLE CASES

# La dictionnaire des poissons
dict_poissons = {}
dict_pos = {}
selected_fish = None  # This will store the ID of the selected fish

# Création des gens
for i in range(10):
    poisson = Poisson(randint(100,700),randint(100,400), i)
    dict_poissons[i] = poisson
    dict_pos[i] = poisson.pos

# Affecter les 2 cibles à chacun des gens
for poisson in dict_poissons.values() :
   dict_poissons_temp = dict_poissons.copy()
   poisson.choisir_cible(dict_poissons_temp)
"""

### END OF CASES
DEBUG = False

# creation de l'interface
interface = Interface()

# Boucle principale
stable = True
n = 0
while not stable:
    n += 1
    stable = True
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_fish_id = interface.check_click_on_list(mouse_pos)
                if clicked_fish_id is not None:
                    selected_fish = clicked_fish_id

    screen.fill(BLACK)
    
    # Draw the fish list
    if DEBUG:
        interface.display_fish_list()

    # Étape 1 : Calculer les prochaines positions
    
    for poisson in dict_poissons.values():
        poisson.calculer_prochaine_position(dict_poissons)

    # Étape 2 : Mettre à jour les positions
    for poisson in dict_poissons.values():
        poisson.pos = dict_pos[poisson.id]

    # Afficher les poissons
    for poisson in dict_poissons.values():
        if poisson.idle != True:
            stable = False
        if DEBUG:
            if poisson.id == selected_fish:
                poisson.debug_afficher(highlight=True)
            else:
                poisson.debug_afficher()
        else:
            poisson.afficher()

    pygame.display.update()
print(f"took {n} iterations")


class Model:
    """
    Class pour le modelisation
    Returns: data pour analyse
    """
    def __init__(self, n_poisson, r_group, separation_c_group):
        self.zone_area = define_model_zone()
        self.liste_murs = define_walls()

        self.dict_poissons = {}
        self.dict_pos = {}
        self.group_1_ids = {}


        self.n_poisson = n_poisson
        self.r_group = r_group
        self.separation_c_group = separation_c_group
    
    def init_program(self):
        # WITH SEPARATION DISTANCE
        group_1, group_2 = generate_groups_with_exact_centroid_distance(self.n_poisson, self.r_group, self.separation_c_group, self.zone_area)

        self.dict_poissons = group_1.copy()
        self.group_1_ids = list(group_1.keys())

        for id, poisson in group_1.items():
            self.dict_pos[id] = poisson.pos

        for id, poisson in group_2.items():
            self.dict_poissons[id] =  poisson
            self.dict_pos[id] = poisson.pos

        # Affecter les 2 cibles à chacun des gens
        for poisson in group_1.values() :
           dict_poissons_temp = group_1.copy()
           poisson.choisir_cible(dict_poissons_temp)

        for poisson in group_2.values() :
           dict_poissons_temp = group_2.copy()
           poisson.choisir_cible(dict_poissons_temp)

    def run(self):
        self.init_program()
        # Boucle principale
        stable = False
        n = 0
        while not stable:
            n += 1
            stable = True
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BLACK)

            # Étape 1 : Calculer les prochaines positions
            for poisson in self.dict_poissons.values():
                poisson.calculer_prochaine_position(self.dict_poissons, self.dict_pos)
                # Étape 2 : Mettre à jour les positions
                poisson.pos = self.dict_pos[poisson.id]
                # afficher
                if poisson.idle != True:
                    stable = False
                poisson.afficher(self.group_1_ids)

            pygame.display.update()

model = Model(50, 100, 100)
model.run()