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
        self.vitesse = 2
        self.vitesse_reelle = None
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

    def calculer_destination(self):
        self.pos_percue_cible1 = self.cible1.pos
        self.pos_percue_cible2 = self.cible2.pos
        x1, y1 = self.pos_percue_cible1
        x2, y2 = self.pos_percue_cible2
        vectdir = np.array([x1-x2, y1-y2])
        midpoint = (self.pos_percue_cible1 + self.pos_percue_cible2) / 2
        perp_vectdir = normaliser_vecteur(np.array([y1-y2, x2-x1]))
        s,t = np.linalg.solve([[perp_vectdir[0], -vectdir[0]], [perp_vectdir[1], -vectdir[1]]], self.pos - midpoint)
        self.destination = midpoint + s * perp_vectdir

        return self.destination

    def trouve_mur_collision(self):
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
        if trouve == True :
            return liste_murs[i]
        else :
            return None 
        

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
        self.vitesse_reelle = np.linalg.norm((prochaine_position - self.pos) / (1/60))
        
        

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
                    force = (self.rayon_collision - distance) / self.rayon_collision * 10 # Entre 0 et 10
                    # Appliquer la force de répulsion
                    repulsion += vecteur_repulsion_normalise * force
        return repulsion

    def afficher(self, highlight=False):
        if highlight:
            pygame.draw.circle(screen, (255, 0, 0), self.calculer_destination(), 2)
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible1.pos))
            pygame.draw.line(screen, (0, 0, 255), (self.pos), (self.cible2.pos))
            pygame.draw.circle(screen, (0, 255, 0), self.pos, 2)
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



# La dictionnaire des gens
dict_poissons = {}
dict_pos = {}
selected_fish = None  # This will store the ID of the selected fish

# creation de l'interface
interface = Interface()

# Création des gens
for i in range(100):
    poisson = Poisson(randint(100,600),randint(100,500), i)
    dict_poissons[i] = poisson
    dict_pos[i] = poisson.pos

# Affecter les 2 cibles à chacun des gens
for poisson in dict_poissons.values() :
    dict_poissons_temp = dict_poissons.copy()
    poisson.choisir_cible(dict_poissons_temp)

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
