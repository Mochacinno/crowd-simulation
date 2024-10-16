import pygame
import sys
from random import randint
from config import *

pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mvt de Foule")

screen.fill(BLACK)

class Humain:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        vitesse = 10 
        cible_1 = ()
        cible_2 = ()

    def choisir_cible(self, dict_humains):
        rand_index_1 = randint(0, len(dict_humains)
        cible_1 = dict_humains[f"humain_{randint(0, len(dict_humains))}"]

        cible_2 = dict_humains[f"humain_{randint(0, len(dict_humains))}"]

    def court_chemin_vect(self):
        vect_directeur = (1, ())

    def bouger(self):
        self.x = self.x + 10
        self.y = self.y + 5

    def afficher(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 2)

dict_humains = {}
for i in range(5):
    humain = Humain(randint(0,40),randint(0,40))
    dict_humains[f"humain_{i}"] = humain
    
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
    pygame.display.update()