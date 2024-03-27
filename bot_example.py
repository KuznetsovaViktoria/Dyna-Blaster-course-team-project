from random import randint
from pygame.locals import *

def get_bot_move(enemies_positions, bombs_positions,  blocks_layout, stones_layout):
    x = randint(0, 3)
    keys_to_move = [K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE]
    return keys_to_move[x]