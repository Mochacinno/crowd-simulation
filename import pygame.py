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
        rand_index_1 = randint(0, len(dict_humains))
        cible_1 = dict_humains[f"humain_{randint(0, len(dict_humains))}"]

        cible_2 = dict_humains[f"humain_{randint(0, len(dict_humains))}"]

    def court_chemin_vect(self):
        vect_directeur = (1, ())

    def bouger(self):
        self.x = self.x + 10
        self.y = self.y + 5

    def afficher(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 2)

    def calculer_pente(self,humain1,humain2):
        a = (humain1.y - humain2.y)/(humain1.x - humain2.x)
        return a
    
    def cibles_en_vue(self, dict_humains):

        # Droite jusqu'à la cible 1
        a1 = self.calculer_pente(self, self.cible_1)
        b1 = self.y - a1 * self.x

        # Droite jusqu'à la cible 2
        a2 = self.calculer_pente(self, self.cible_2)
        b2 = self.y - a2 * self.x

        for humain in dict_humains.values():
            # Vérification pour cible 1
            if humain != self and humain != self.cible_1 :
                if ((humain.x >= self.x and humain.x <= self.cible_1.x) or (humain.x <= self.x and humain.x >= self.cible_1.x)) and ((humain.y >= self.y and humain.y <= self.cible_1.y) or (humain.y <= self.y and humain.y >= self.cible_1.y)):
                    # Humain est entre self et cible 1
                    a_humain = self.calculer_pente(self,humain)
                    if abs(a1 - a_humain) < 5 : 
                        cible1_en_vue = False
                else:
                    # Humain n'est pas entre self et cible 1
                    cible1_en_vue = True
            if humain != self and humain != self.cible_2 :
                if ((humain.x >= self.x and humain.x <= self.cible_2.x) or (humain.x <= self.x and humain.x >= self.cible_2.x)) and ((humain.y >= self.y and humain.y <= self.cible_2.y) or (humain.y <= self.y and humain.y >= self.cible_2.y)):
                    # Humain est entre self et cible 1
                    a_humain = self.calculer_pente(self,humain)
                    if abs(a2 - a_humain) < 5 : 
                        cible2_en_vue = False
                else:
                    # Humain n'est pas entre self et cible 1
                    cible2_en_vue = True
        return cible1_en_vue, cible2_en_vue


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
    
    