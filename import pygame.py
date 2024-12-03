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
        vitesse = 10 
        self.collision_radius = 10
        self.pos = np.array([x, y])

        self.cible1 = None      # Instance de cible 1
        self.pos_percue_cible1 = (0,0) # Position percue par l'humain
        self.cible2 = None
        self.pos_percue_cible2 = (0,0)
        

    def choisir_cible(self, dict_humains):
        target_ids = [key for key in dict_humains if key != self.id+1]

        index_cible1, index_cible2 = np.random.choice(target_ids, 2, replace=False)
        self.cible1 = dict_humains[index_cible1]
        self.cible2 = dict_humains[index_cible2]

    def calculer_destination(self):
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2
        vectdir = np.array([x1-x2, y1-y2])
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2
        perp_vectdir = normalize_vector(np.array([y1-y2, x2-x1]))
        res = np.linalg.solve([[perp_vectdir[0], vectdir[0]], [perp_vectdir[1], vectdir[1]]], self.pos - midpoint)
        self.destination = perp_vectdir * res[0] + midpoint

        return self.destination
    
    def detect_collision(self, dict_humains):
        for other in dict_humains.values():
            if other.id != self.id:
                distance = np.linalg.norm(self.pos - other.pos)
                if distance < self.collision_radius:  # Collision detected
                    return other  # Return the colliding Humain
        return None

    def bouger(self):
        # tous les gens bougent en meme temps au lieu que humain1 bouge, qui donc modifie la position pour qqn qui a le cible de humain1
        vect_dir = self.court_chemin_vect() - self.pos
        new_pos = self.pos + vect_dir / np.linalg.norm(vect_dir)

        # Check for collisions
        collision = self.detect_collision(dict_humains)
        if collision:
            # Push away from the colliding Humain
            direction_away = normalize_vector(self.pos - collision.pos)
            new_pos += direction_away * self.collision_radius  # Move out of collision radius

        self.pos = new_pos
        self.dict_humains[self.id] = self.pos

    def trouve_mur_limite(self):
        mur_haut = [np.array([0,0]), np.array([800,0])]     # [position d'1 point , vecteur directeur non normalisé]
        mur_bas = [np.array([0,600]), np.array([800,0])]
        mur_gauche = [np.array([0,0]), np.array([0,600])]
        mur_droite = [np.array([800,0]), np.array([0,600])]
        liste_murs = [mur_haut, mur_bas, mur_gauche, mur_droite]
        trouve = False
        i = 0
        while not trouve and i < 4 :
            a = np.array([[self.destination[0], - liste_murs[i][1][0]], [self.destination[1], - liste_murs[i][1][1]]])          
            b = np.array([self.pos[0]- liste_murs[i][0][0]])                      # Système matriciel
            alpha, beta = np.linalg.solve(a, b)
            
            if alpha >= 0 and alpha <= 1 and beta >= 0 and beta <= 1 :
                trouve = True
            else :
                i += 1
        return liste_murs[i]
        

    def calculer_etat_suivant(self):
        # tous les gens bougent en meme temps au lieu que humain1 bouge, qui donc modifie la position pour qqn qui a le cible de humain1
        vect_dir = self.calculer_destination() - self.pos
        self.pos = self.pos + vect_dir / np.linalg.norm(vect_dir)
        dict_pos_suiv[self.id] = self.pos
    
    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.calculer_destination(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible1.pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible2.pos))
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
        # Pente droite jusqu'à la cible
        cible = dict_humains[index_cible]
        a = self.calculer_pente(self, cible)

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
        #humain.bouger()
        humain.calculer_etat_suivant()
    t += 1
    dict_pos_prec = dict_pos_suiv

    pygame.display.update()
