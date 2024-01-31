# START WORKING
import pygame
import sys
from pygame.color import THECOLORS

pygame.init()  # prepare modules of pygame to work

screen = pygame.display.set_mode((1200, 800))  # create graphics window, (1200, 800) - resolution, -> Surface object for images
list_of_fonts = pygame.font.get_fonts()
# print(*list_of_fonts)
font = pygame.font.SysFont(list_of_fonts[10], 40)
text = font.render(str('Game by Erika and Vika'), True, THECOLORS['purple'])
screen.fill(THECOLORS['white'])  # make all screen white
screen.blit(text, (350, 50))
r = pygame.Rect(400, 300, 400, 300)  # coordinates: upper left corner, length of sides
                                 # coordinate (0, 0) - upper left corner of screen
pygame.draw.rect(screen, (255, 0, 255), r, 0)  # width = 0 -> full colored
# pygame.draw.line(screen, (0, 255, 0), (0, 0), (100, 100), width = 10)
# pygame.draw.line(screen, THECOLORS['orange'], (100, 100), (0, 200), width = 10)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # if escape
            pygame.quit()  # end work with pygame
            sys.exit()  # end programm
    pygame.display.flip()  # changes to be visable


# DRAW GEOM FIGURES
# Rect(left, top, width, height)  # make a rectangle, type Rect for such objects
# Rect((left, top), (width, height))
# rect(Surface, color, Rect, width = 0) -> Rect  # in pygame dict to draw geom. figures - module draw. rect() draws rectangle
