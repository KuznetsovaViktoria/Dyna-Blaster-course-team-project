from random import randint
from pygame.locals import *

my_pos =[0, 0]
TILE = 0
WIDTH = 0

def set_first_params(t, w):
    global WIDTH, TILE
    TILE = t
    WIDTH = w

def is_correct_coords(x, y):
    return 0 <= x <= WIDTH - TILE and 0 < y <= WIDTH


def get_bot_move(my_pos, enemies_positions, enemies_points, bombs_positions,  blocks_layout, stones_layout):
    x = randint(0, 3)
    keys_to_move = [K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE]
    return keys_to_move[x]