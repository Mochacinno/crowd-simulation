import pygame
import numpy as np
import sys
def isometrique(X,Y,Z):
    pass
    

pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Modélisation du banc de poisson")

screen.fill((0,0,0))

pos1 = (0,0,0)
pos2 = (0,1,1)

def isometrique(pos, a=2, b=3):
    return pos[0] * np.array(a,b) + pos[1] * np.array(-a,b)


x = True
while x:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()