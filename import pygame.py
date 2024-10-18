import pygame
import sys
from random import randint
from config import *
import numpy as np

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

    def choisir_cible(self, dict_humains):
        #print(randint(0, len(dict_humains)-1))
        # faut qu'il ne choisit lui meme
        if randint(0, len(dict_humains)-1) != id:
            self.cible_1 = dict_humains.pop(list(dict_humains.keys())[randint(0, len(dict_humains)-1)])
        if randint(0, len(dict_humains)-1) != id:
            self.cible_2 = dict_humains.pop(list(dict_humains.keys())[randint(0, len(dict_humains)-1)])

    def court_chemin_vect(self):
        x1, y1 = self.cible_1.x, self.cible_1.y
        x2, y2 = self.cible_2.x, self.cible_2.y
        a = ( y2 - y1 ) / ( x2 - x1 ) # pente
        pygame.draw.line(screen, WHITE, self.cible_1.pos, self.cible_2.pos)

        b = self.y - self.x * a
        self.vect_directeur = normalize_vector(np.array([1, a]))
        #pygame.draw.line(screen, WHITE, self.pos, self.pos+10*self.vect_directeur)

    def bouger(self):
        self.pos = self.pos 

    def afficher(self):
        print((self.pos[0], self.pos[1]))
        pygame.draw.circle(screen, WHITE, self.pos, 2)
        #pygame.draw.line(screen, (self.id*20, self.id*50, self.id*60), self.pos, self.cible_1.pos)
        #pygame.draw.line(screen, (self.id*20, self.id*50, self.id*60), self.pos, self.cible_2.pos)


# La dictionnaire des gens
dict_humains = {}

# Création des gens
for i in range(3):
    humain = Humain(randint(200,500),randint(100,400), i)
    dict_humains[f"humain_{i+1}"] = humain

# Affecter les 2 cibles à chacun des gens
for humain in dict_humains.values():
    dict_humains_temp = dict_humains.copy()
    humain.choisir_cible(dict_humains_temp)

# Boucle principale
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)
    
    for humain in dict_humains.values():
        humain.bouger()
        humain.afficher()
        humain.court_chemin_vect()
    pygame.display.update()
    
    