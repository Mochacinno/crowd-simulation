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
        self.cible_1=None
        self.cible_1_pos = (0, 0)
        self.cible_2=None
        self.cible_2_pos = (0, 0)

    def choisir_cible(self, dict_humains):
        #print(randint(0, len(dict_humains)-1))
        # faut qu'il ne choisit lui meme
        res = False
        index_cible_1 = 0
        index_cible_2 = 0
        while not res:
            index_cible_1 = randint(0, len(dict_humains)-1)
            if index_cible_1 != self.id:
                self.cible_1 = dict_humains[list(dict_humains.keys())[index_cible_1]]
                res = True
        res = False
        while not res: 
            index_cible_2 = randint(0, len(dict_humains)-1)
            if index_cible_2 not in (self.id, index_cible_1):
                self.cible_2 = dict_humains[list(dict_humains.keys())[index_cible_2]]
                res = True

        print(self.cible_1.id, self.cible_2.id)

    def court_chemin_vect(self):
        x1, y1 = self.cible_1.x, self.cible_1.y
        x2, y2 = self.cible_2.x, self.cible_2.y
        a = ( y2 - y1 ) / ( x2 - x1 ) # pente
        midpoint = (self.cible_1.pos + self.cible_2.pos) / 2
        # equation is midpoint y = (-1/a) * midpoint x + c1
        c1 = midpoint[1] + ( midpoint[0] / a )
        # other equation is self.y = a * self.x + c2
        c2 = self.y - ( a * self.y )
        # now the intersection between the two
        # -1 /a * interx+ c1 = a * interx + c2
        # -1 /a * interx - a* interx = c2- c1
        # interx(-1/a -a) = c2-c1
        # interx = a( c2 - c1) / (-1 - a**2)
        interx = (a * ( c2 - c1 ))/(-1-a**2)
        pygame.draw.circle(screen, (255, 0, 255), midpoint, 2)
        pygame.draw.circle(screen, (255, 0, 100), (interx, a * interx + c2), 2)
        #pygame.draw.line(screen, (255, 0, 255), midpoint, midpoint * 1 / - a)

        b = self.y - self.x * a
        self.vect_directeur = normalize_vector(np.array([1, a]))
        #pygame.draw.line(screen, WHITE, self.pos, self.pos+10*self.vect_directeur)

    def bouger(self):
        self.pos = self.pos 

    def afficher(self):
        #print((self.pos[0], self.pos[1]))
        pygame.draw.circle(screen, WHITE, self.pos, 2)
        #pygame.draw.line(screen, (self.id*20, self.id*50, self.id*60), self.pos, self.cible_1.pos)
        #pygame.draw.line(screen, (self.id*20, self.id*50, self.id*60), self.pos, self.cible_2.pos)
    
    def calculer_pente(self,humain1,humain2):
        a = (humain1.pos[1] - humain2.pos[1])/(humain1.pos[0] - humain2.pos[0])
        return a
    
    def cibles_en_vue(self, dict_humains):
        """
        Vérifie que la personne peut voir ses 2 cibles

        Args : dict_humains

        Returns : 1 booléen pour chaque cible
        """
        # Droite jusqu'à la cible 1
        a1 = self.calculer_pente(self, self.cible_1)

        # Droite jusqu'à la cible 2
        a2 = self.calculer_pente(self, self.cible_2)
        

        for humain in dict_humains.values():
            # Vérification pour cible 1
            if humain != self and humain != self.cible_1 :
                if ((humain.pos[0] >= self.pos[0] and humain.pos[0] <= self.cible_1.pos[0]) or (humain.pos[0] <= self.pos[0] and humain.pos[0] >= self.cible_1.pos[0])) and ((humain.pos[1] >= self.pos[1] and humain.pos[1] <= self.cible_1.pos[1]) or (humain.pos[1] <= self.pos[1] and humain.pos[1] >= self.cible_1.pos[1])):
                    # Humain est entre self et cible 1
                    a_humain = self.calculer_pente(self,humain)
                    if abs(a1 - a_humain) < 5 : 
                        cible1_en_vue = False
                else:
                    # Humain n'est pas entre self et cible 1
                    cible1_en_vue = True
            if humain != self and humain != self.cible_2 :
                if ((humain.x >= self.pos[0] and humain.pos[0] <= self.cible_2.pos[0]) or (humain.pos[0] <= self.pos[0] and humain.pos[0] >= self.cible_2.pos[0])) and ((humain.pos[1] >= self.pos[1] and humain.pos[1] <= self.cible_2.pos[1]) or (humain.pos[1] <= self.pos[1] and humain.pos[1] >= self.cible_2.pos[1])):
                    # Humain est entre self et cible 1
                    a_humain = self.calculer_pente(self,humain)
                    if abs(a2 - a_humain) < 5 : 
                        cible2_en_vue = False
                else:
                    # Humain n'est pas entre self et cible 1
                    cible2_en_vue = True
        return cible1_en_vue, cible2_en_vue

dico_test={"A": Humain(100,100,0),
           "B": Humain(200, 100,1),
           "C": Humain(300,300,2)}
for humain in dico_test.values():
    humain.choisir_cible(dico_test)

"""
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
"""
# Boucle principale

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)
    
    for humain in dico_test.values():
        #humain.bouger()
        humain.afficher()
        humain.court_chemin_vect() 
    pygame.display.update()
