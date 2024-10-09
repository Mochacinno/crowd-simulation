import pygame
import sys

pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mvt de Foule")

screen.fill((0,0,0))

class Humain:
    def __init__(self) -> None:
        pass

    def appartient_qqn(self):
        pass

    def move(self):
        pass

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()