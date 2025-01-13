import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Poisson Mobile")

# Couleurs
white = (255, 255, 255)
black = (0, 0, 0)

# Position et angle du poisson
fish_pos = [400, 300]  # Position initiale du poisson
fish_angle = 0         # Angle initial du poisson

# Vitesse de déplacement
speed = 5

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Gestion des touches pour le mouvement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        fish_angle += 5  # Tourner à gauche
    if keys[pygame.K_RIGHT]:
        fish_angle -= 5  # Tourner à droite
    if keys[pygame.K_UP]:
        # Calculer le déplacement en fonction de l'angle
        fish_pos[0] += speed * math.cos(math.radians(fish_angle))
        fish_pos[1] += speed * math.sin(math.radians(fish_angle))

    # Remplir l'écran avec une couleur (noir ici)
    screen.fill(black)

    # Dessiner le poisson
    # Corps du poisson (cercle)
    circle_radius = 20
    pygame.draw.circle(screen, (255,0,0), (int(fish_pos[0]), int(fish_pos[1])), circle_radius)

    # Calculer les points du triangle (queue du poisson)
    triangle_length = 50  # Longueur de la queue
    
    # Largeur de la queue

    # Points du triangle
    point1 = (fish_pos[0], fish_pos[1]+circle_radius*1.02)  # Point gauche (attaché au corps)
    point2 = (fish_pos[0], fish_pos[1] - circle_radius*1.02)  # Point haut
    point3 = (fish_pos[0]-triangle_length, fish_pos[1])  # Point bas

    
    # Dessiner le triangle
    pygame.draw.polygon(screen, (255,0,0), [point1, point2, point3])

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Limiter la vitesse de la boucle
    clock.tick(60)