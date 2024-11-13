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
pygame.display.set_caption("Mvt de Foule")

screen.fill(BLACK)

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

class Humain:
    def __init__(self, x, y, id):
        self.id = id
        self.x = x
        self.y = y
        self.pos = np.array([self.x, self.y])
        vitesse = 10 
        self.vect_directeur = np.array([0,0])
        self.cible1 = None      # Instance de cible 1
        self.pos_percue_cible1 = (0,0) # Position percue par l'humain
        self.cible2 = None
        self.pos_percue_cible2 = (0,0)
        

    def choisir_cible(self, dict_humains):
        target_ids = [key for key in dict_humains if key != self.id+1]

        index_cible1, index_cible2 = np.random.choice(target_ids, 2, replace=False)
        self.cible1 = dict_humains[index_cible1]
        self.cible2 = dict_humains[index_cible2]
    def court_chemin_vect(self):
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2
        vectdir = np.array([x1-x2, y1-y2])
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2
        perp_vectdir = normalize_vector(np.array([y1-y2, x2-x1]))
        res = np.linalg.solve([[perp_vectdir[0], vectdir[0]], [perp_vectdir[1], vectdir[1]]], self.pos - midpoint)
        self.point = perp_vectdir * res[0] + midpoint
        
        return self.point
        
    def calculer_etat_suivant(self):
        # tous les gens bougent en meme temps au lieu que humain1 bouge, qui donc modifie la position pour qqn qui a le cible de humain1
        vect_dir = self.court_chemin_vect() - self.pos
        self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
        dict_pos_suiv[self.id] = self.pos
    
    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.court_chemin_vect(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible1.pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible2.pos))
            pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
        else:
            pygame.draw.circle(screen, WHITE, self.pos, 2)

    def calculer_pente(self,humain1,humain2):
        a = (humain1.pos[1] - humain2.pos[1])/(humain1.pos[0] - humain2.pos[0])
        return a
    
    def cible_en_vue(self, dict_humains, index_cible):
        """
        Vérifie que la personne peut voir ses 2 cibles

        Args : dict_humains

        Returns : 1 booléen pour chaque cible
        """
        # Pente droite jusqu'à la cible
        cible = dict_humains[index_cible]
        a = self.calculer_pente(self, cible)

        
        for humain in dict_humains.values():
            # Vérification pour cible 1
            if humain != self and humain != cible :
                if ((humain.pos[0] >= self.pos[0] and humain.pos[0] <= cible.pos[0]) or (humain.pos[0] <= self.pos[0] and humain.pos[0] >= cible.pos[0])) and ((humain.pos[1] >= self.pos[1] and humain.pos[1] <= cible.pos[1]) or (humain.pos[1] <= self.pos[1] and humain.pos[1] >= cible.pos[1])):
                    
                    # definir un rayon autour de chaque personne. Sachant que notre rayon de humain vers cette cible passe par le rayon de qqn, donc iil ne peut pas voir.

                    a_humain = self.calculer_pente(self,humain)
                    if abs(a - a_humain) < 5 : 
                        cible_en_vue = False
                else:
                    # Humain n'est pas entre self et cible 1
                    cible_en_vue = True
        
        return cible_en_vue


font = pygame.font.Font(None, 24)

class Interface:
    def __init__(self):
        self.display_humain_list()

    def display_humain_list(self):
        """Display list of Humains"""
        y_offset = 10
        for humain in dict_humains.values():
            text = font.render(f"Humain {humain.id}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 30

    def check_click_on_list(self, mouse_pos):
        """Check if humain in list is clicked"""
        y_offset = 10
        for humain in dict_humains.values():
            text_rect = pygame.Rect(10, y_offset, 100, 30)
            if text_rect.collidepoint(mouse_pos):
                return humain.id 
            y_offset += 30
        return None

"""
dico_test={"A": Humain(100,100,0),
           "B": Humain(200, 100,1),
           "C": Humain(300,300,2)}
for humain in dico_test.values():
    humain.choisir_cible(dico_test)

dico_test["B"].court_chemin_vect() 
"""

# La dictionnaire des gens
dict_humains = {}
dict_pos = {}
dict_pos_suiv = {}
selected_humain = None  # This will store the ID of the selected humain

# creation de l'interface
interface = Interface()

# Création des gens
for i in range(20):
    humain = Humain(randint(100,600),randint(100,500), i)
    dict_humains[i] = humain
    dict_pos[i] = humain.pos

# Affecter les 2 cibles à chacun des gens
for humain in dict_humains.values() :
    dict_humains_temp = dict_humains.copy()
    humain.choisir_cible(dict_humains_temp)

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
                clicked_humain_id = interface.check_click_on_list(mouse_pos)
                if clicked_humain_id is not None:
                    selected_humain = clicked_humain_id

    screen.fill(BLACK)
    
    # Draw the Humain list
    interface.display_humain_list()

    for humain in dict_humains.values():
        if humain.id == selected_humain:
            humain.afficher(highlight=True)
        else:
            humain.afficher()
        humain.calculer_etat_suivant()
    dict_pos_prec = dict_pos_suiv

    pygame.display.update()
