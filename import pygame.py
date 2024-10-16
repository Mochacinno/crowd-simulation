import pygame
import sys
from random import randint

pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mvt de Foule")

screen.fill((0,0,0))

class Humain:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        vitesse = 10 

    def choisir_cible(self):
        pass

    def bouger(self):
        self.x = self.x + 10
        self.y = self.y + 5

    def afficher(self):
        pygame.draw.circle(screen, (200,200,200), (self.x, self.y), 2)

dict_personnes = {}
for i in range(5):
    humain = Humain(randint(0,40),randint(0,40))
    dict_personnes[f"humain_{i}"] = humain
    
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0,0,0))
    for humain in dict_personnes.values():
        humain.bouger()
        humain.afficher()
    pygame.display.update()