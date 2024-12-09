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
pygame.display.set_caption("test de collision")

screen.fill(BLACK)

class Humain:
    def __init__(self, x, y, id, cible_pos):
        self.id = id
        self.collision_radius = 10
        self.pos = np.array([x, y])
        self.priority = id
        self.cible_pos = cible_pos

    def calculer_destination(self):
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2
        vectdir = np.array([x1-x2, y1-y2])
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2
        perp_vectdir = np.array([y1-y2, x2-x1])
        res = np.linalg.solve([[perp_vectdir[0], vectdir[0]], [perp_vectdir[1], vectdir[1]]], self.pos - midpoint)
        self.destination = perp_vectdir * res[0] + midpoint

        return self.destination
    
    def detect_collision(self, dict_humains):
        for other in dict_humains.values():
            if other.id != self.id:
                distance = np.linalg.norm(self.pos - other.pos)
                if distance < self.collision_radius * 8:  # Collision detected
                    return other  # Return the colliding Humain
        return None
    
    def is_head_on_collision(self, colliding_object):
        # Calculate this object's direction
        vect_dir = self.cible - self.pos
        vect_dir /= np.linalg.norm(vect_dir) 

        # Future position
        future_pos = self.pos + vect_dir

        # Vector from the colliding object to the future position
        #to_future_pos = future_pos - colliding_object.pos

        # Colliding object's direction vector
        #colliding_dir = colliding_object.calculer_destination() - colliding_object.pos
        #colliding_dir /= np.linalg.norm(colliding_dir)  # Normalize direction

        # Calculate cross product (2D version)
        cross_product = colliding_dir[0] * to_future_pos[1] - colliding_dir[1] * to_future_pos[0]

        # Determine lateral direction based on cross product
        if cross_product > 0:
            return np.array([-vect_dir[1], vect_dir[0]])  # Future position is on the left
        elif cross_product <= 0:
            return np.array([vect_dir[1], -vect_dir[0]])  # Future position is on the right

    def calculer_etat_suivant(self):
        # tous les gens bougent en meme temps au lieu que humain1 bouge, qui donc modifie la position pour qqn qui a le cible de humain1
        vect_dir = self.cible_pos - self.pos
        vect_dir_normal = vect_dir / np.linalg.norm(vect_dir)

        # collisions
        colliding_object = self.detect_collision(dico_test)
        if colliding_object is not None:
            # celui avec une priorite plus bas va pas bouger
            if self.priority > colliding_object.priority:
                # si en plus le trajectoire de celui qui bouge est confondu avec l'autre point
                #lateral_movement = self.is_head_on_collision(colliding_object)
                self.pos = self.pos + np.array([-vect_dir_normal[1], vect_dir_normal[0]])
                #self.pos = (self.pos + vect_dir / np.linalg.norm(vect_dir))
        # else:
            #self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
                #self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
            else:
                self.pos = self.pos + np.array([-vect_dir_normal[1], vect_dir_normal[0]])
        else:
            self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
        dict_pos_suiv[self.id] = self.pos
    
    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.calculer_destination(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible1.pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible2.pos))
            pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
            pygame.draw.circle(screen, (255, 255, 0), self.pos, self.collision_radius * 2)
        else:

            pygame.draw.circle(screen, WHITE, self.pos, 2)
            pygame.draw.circle(screen, (255, 255, 0), self.pos, self.collision_radius * 4, 2)

font = pygame.font.Font(None, 24)

class Interface:
    def __init__(self):
        self.display_humain_list()

    def display_humain_list(self):
        """Display list of Humains"""
        y_offset = 10
        for humain in dico_test.values():
            text = font.render(f"Humain {humain.id}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 30

    def check_click_on_list(self, mouse_pos):
        """Check if humain in list is clicked"""
        y_offset = 10
        for humain in dico_test.values():
            text_rect = pygame.Rect(10, y_offset, 100, 30)
            if text_rect.collidepoint(mouse_pos):
                return humain.id 
            y_offset += 30
        return None


dict_pos_prec = {}
dict_pos_suiv = {}

#dico_test={0: Humain(300, 300, 0, [700, 300]), 1: Humain(500, 300, 1, [100, 300])}

dico_test={0: Humain(300, 200, 0, [700, 300]), 1: Humain(500, 300, 1, [100, 200])}

for i in range(len(dico_test)):
    dict_pos_prec[i] = dico_test[i].pos

selected_humain = None

# creation de l'interface
interface = Interface()

t = 0
# Boucle principale
x = True
y = False
while x and not y or x and y or not x and not y or not x and y:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_humain_id = interface.check_click_on_list(mouse_pos)
                if clicked_humain_id is not None:
                    selected_humain = clicked_humain_id

    screen.fill(BLACK)
    
    # Draw the Humain list
    interface.display_humain_list()

    for humain in dico_test.values():
        if humain.id == selected_humain:
            humain.afficher(highlight=True)
        else:
            humain.afficher()
        #humain.bouger()
        humain.calculer_etat_suivant()
    t += 1
    dict_pos_prec = dict_pos_suiv

    pygame.display.update()
