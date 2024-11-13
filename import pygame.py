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
        self.cible_1=None
        self.cible_1_pos = (0, 0)
        self.cible_2=None
        self.cible_2_pos = (0, 0)
        self.dict_humains = {}

    def choisir_cible(self, dict_humains):
        target_ids = [key for key in dict_humains if key != f"humain_{self.id+1}"]

        self.cible_1, self.cible_2 = np.random.choice(target_ids, 2, replace=False)

    def court_chemin_vect(self):
        cibles_en_vue = self.cible_en_vue(dict_humains)
        if not cibles_en_vue[0]:
            cible_1 = dict_humains[self.cible_1].pos
        # A FAIRE

        cible_2 = dict_humains[self.cible_2].pos
        x1, y1 = cible_1[0], cible_1[1]
        x2, y2 = cible_2[0], cible_2[1]
        vectdir = np.array([x1-x2, y1-y2])
        midpoint = (cible_1 + cible_2) / 2
        perp_vectdir = normalize_vector(np.array([y1-y2, x2-x1]))
        res = np.linalg.solve([[perp_vectdir[0], vectdir[0]], [perp_vectdir[1], vectdir[1]]], self.pos - midpoint)
        self.point = perp_vectdir * res[0] + midpoint
        
        return self.point
        
    def bouger(self):
        # tous les gens bougent en meme temps au lieu que humain1 bouge, qui donc modifie la position pour qqn qui a le cible de humain1
        vect_dir = self.court_chemin_vect() - self.pos
        self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
        self.dict_humains[self.id] = self.pos

    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.court_chemin_vect(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (dict_humains[self.cible_1].pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (dict_humains[self.cible_2].pos))
            pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
        else:
            pygame.draw.circle(screen, WHITE, self.pos, 2)

    def calculer_pente(self,humain1,humain2):
        a = (humain1.pos[1] - humain2.pos[1])/(humain1.pos[0] - humain2.pos[0])
        return a

    def cible_en_vue(self, dict_humains):
        """
        Vérifie que la personne peut voir ses 2 cibles

        Args : dict_humains

        Returns : 1 booléen pour chaque cible
        """
        cibles_en_vue = []
        for index_cible in [self.cible_1, self.cible_2]:
            # Pente droite jusqu'à la cible
            cible = dict_humains[index_cible]
            vectdir = np.array([self.pos[0]-cible.pos[0], self.pos[1]-cible.pos[1]])
            cible_en_vue = True

            for humain in dict_humains.values():
                # Vérification pour cible 1
                if humain != self and humain != cible :
                    if ((humain.pos[0] >= self.pos[0] and humain.pos[0] <= cible.pos[0]) or (humain.pos[0] <= self.pos[0] and humain.pos[0] >= cible.pos[0])) and ((humain.pos[1] >= self.pos[1] and humain.pos[1] <= cible.pos[1]) or (humain.pos[1] <= self.pos[1] and humain.pos[1] >= cible.pos[1])):

                        # definir un rayon autour de chaque personne. Sachant que notre rayon de humain vers cette cible passe par le rayon de qqn, donc iil ne peut pas voir.
                        d = np.linalg.norm(np.cross(vectdir, np.array([self.pos[0] - humain.pos[0], self.pos[1] - humain.pos[1]]))/ np.linalg.norm(vectdir))
                        #print(d)
                        if d <= 5:
                            cible_en_vue = False
            cibles_en_vue.append(cible_en_vue)
        return cibles_en_vue

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
selected_humain = None  # This will store the ID of the selected humain

# creation de l'interface
interface = Interface()

# Création des gens
for i in range(20):
    humain = Humain(randint(100,600),randint(100,500), i)
    dict_humains[f"humain_{i+1}"] = humain

# Affecter les 2 cibles à chacun des gens
for humain in dict_humains.values():
    dict_humains_temp = dict_humains.copy()
    humain.choisir_cible(dict_humains_temp)

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

    for humain in dict_humains.values():
        if humain.id == selected_humain:
            humain.afficher(highlight=True)
        else:
            humain.afficher()
        humain.bouger()
    t += 1
    pygame.display.update()
