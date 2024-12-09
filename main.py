import pygame
import sys
from random import randint
from config import *
import numpy as np
import math

pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Modélisation du banc de poisson")

screen.fill(BLACK)

def normaliser_vecteur(vecteur):
    norme = np.linalg.norm(vecteur)
    if norme == 0:
        return vecteur
    return vecteur / norme

def calculer_distance(pos1, pos2):
    return np.linalg.norm(pos1 - pos2)

class Poisson:
    def __init__(self, x, y, id, rayon_collision = 30):
        self.id = id
        self.pos = np.array([x, y], dtype=float)
        self.vitesse = 1
        self.tolerance = 2
        self.cible1 = None      # Instance de cible 1
        self.pos_percue_cible1 = (0,0) # Position percue par le poisson
        self.cible2 = None
        self.pos_percue_cible2 = (0,0)
        self.rayon_collision = rayon_collision  # Rayon de collision

    def choisir_cible(self, dict_poissons):
        target_ids = [key for key in dict_poissons if key != self.id]

        index_cible1, index_cible2 = np.random.choice(target_ids, 2, replace=False)
        self.cible1 = dict_poissons[index_cible1]
        self.cible2 = dict_poissons[index_cible2]

    def is_within_walls(self, destination, width=800, height=600):
        """
        Check if the destination point is within the bounds of a rectangular area.

        Parameters:
            destination (tuple or np.array): The point to check (x, y).
            width (int): The width of the boundary (default: 800).
            height (int): The height of the boundary (default: 600).

        Returns:
            bool: True if the point is within bounds, False otherwise.
        """
        x, y = destination
        return 0 <= x <= width and 0 <= y <= height


    def calculer_destination(self):
        mur_haut = [np.array([0, 0]), np.array([800, 0])]  # [start point, direction vector]
        mur_bas = [np.array([0, 600]), np.array([800, 0])]
        mur_gauche = [np.array([0, 0]), np.array([0, 600])]
        mur_droite = [np.array([800, 0]), np.array([0, 600])]
        liste_murs = [mur_haut, mur_bas, mur_gauche, mur_droite]

        # Perceived target positions
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2

        # Compute direction vectors
        vectdir = np.array([x1 - x2, y1 - y2])
        perp_vectdir = normaliser_vecteur(np.array([y1 - y2, x2 - x1]))
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2

        # Find the initial intersection point
        point = self.line_intersection((self.pos, vectdir), (midpoint, perp_vectdir))

        # If the point is outside walls, find the closest valid point
        if not self.is_within_walls(point):
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
                self.destination = closest_point
        else:
            self.destination = point  # Use the valid point

        return self.destination

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

    def calculer_prochaine_position(self, dict_poissons):
        
        repulsion = self.verifier_collisions(dict_poissons)
        vect_dir = self.calculer_destination() - self.pos
        prochaine_position = self.pos
        if np.linalg.norm(vect_dir) > self.tolerance : # Si on est loin de la destination
            prochaine_position = self.pos + normaliser_vecteur(vect_dir) * self.vitesse + repulsion
        else : # Si on est proche de la situation
            if np.linalg.norm(repulsion) > 0 :      
                prochaine_position = self.pos + repulsion
        dict_pos[self.id] = prochaine_position
        
    def verifier_collisions(self, dict_poissons):
        repulsion = 0
        for autre_poisson in dict_poissons.values():
            if autre_poisson != self:
                distance = calculer_distance(self.pos, autre_poisson.pos)
                if distance < self.rayon_collision:
                    # Calculer le vecteur de répulsion
                    vecteur_repulsion = self.pos - autre_poisson.pos
                    vecteur_repulsion_normalise = normaliser_vecteur(vecteur_repulsion)
                    # Appliquer une force de répulsion proportionnelle à l'inverse de la distance
                    force = (self.rayon_collision - distance) / self.rayon_collision * 4 # Entre 0 et 10
                    # Appliquer la force de répulsion
                    repulsion += vecteur_repulsion_normalise * force
        return repulsion

    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.calculer_destination(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible1.pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible2.pos))
            pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
        elif self.id in group_1_ids:
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

# La dictionnaire des poissons
dict_poissons = {}
dict_pos = {}
selected_fish = None  # This will store the ID of the selected fish

# Number of fish in each group
group_size = 40  # Total 80 fish, split into 2 groups
group_1_ids = set(range(group_size))  # IDs 0-39 for Group 1
group_2_ids = set(range(group_size, group_size * 2))  # IDs 40-79 for Group 2

group_1 = {}
group_2 = {}

# Création des gens
for i in range(80):

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

# creation de l'interface
interface = Interface()

# Boucle principale
x = True
while x:
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
    interface.display_fish_list()

    # Étape 1 : Calculer les prochaines positions
    
    for poisson in dict_poissons.values():
        poisson.calculer_prochaine_position(dict_poissons)

    # Étape 2 : Mettre à jour les positions
    
    for poisson in dict_poissons.values():
        poisson.pos = dict_pos[poisson.id]

    # Afficher les poissons
    for poisson in dict_poissons.values():
        if poisson.id == selected_fish:
            poisson.afficher(highlight=True)
        else:
            poisson.afficher()

    pygame.display.update()
