from random import *
from pygame.locals import *
import queue
from time import time
from pygame.key import *

my_pos =[-1, -1]
move_to_keys = {(-1, 0): K_LEFT, (1, 0): K_RIGHT, (0, -1): K_UP, (0, 1): K_DOWN, (0, 0):K_1, "bomb": K_SPACE}
stones = []
blocks = []
TILE = 0
WIDTH = 0
time_escape_bomb = time() - 5
is_escaping_bombs = False
bombs_postitions = []
my_pts = 0

def set_first_params(x, y, t, w):
    global my_pos, WIDTH, TILE, q
    q = queue.Queue()
    my_pos = [x, y]
    TILE = t
    WIDTH = w

def is_correct_coords(x, y):
    return 0 <= x <= WIDTH - TILE and 0 <= y < WIDTH
    
def escape_bombs(need_to_return = False):
    global q
    h = [[1, 0], [0, 1], [-1, 0], [0, -1], [0, 0]]
    shuffle(h)
    for [i, j] in h:
        for [ii, jj] in h:
            for [iii, jjj] in h[::-1]:
                one = (my_pos[0] + i * TILE, my_pos[1] + j * TILE)
                two = (my_pos[0] + (i+ii) * TILE, my_pos[1] + (j + jj) * TILE)
                three = (my_pos[0] + (i + ii + iii) * TILE, my_pos[1] + (j + jj + jjj) * TILE)
                if (is_correct_coords(one[0], one[1]) and is_correct_coords(two[0], two[1]) and is_correct_coords(three[0], three[1]) and
                    all([x not in stones+blocks for x in [one, two, three]]) and all([abs(three[0] - b[0]) + abs(three[1] - b[1]) >= TILE * 2 for b in bombs_postitions])):
                    q.put(move_to_keys[(i, j)])
                    q.put(move_to_keys[(ii, jj)])
                    q.put(move_to_keys[(iii, jjj)])
                    if not need_to_return:
                        return
                    # for _ in range(3):
                    #     q.put(move_to_keys[(0, 0)])
                    # q.put(move_to_keys[(-ii, -jj)])
                    # q.put(move_to_keys[(-i, -j)])
                
def update_my_points(b):
    global my_pts
    for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
        if (b[0] + i * TILE, b[1] + j * TILE) in blocks:
            my_pts += 1

def set_bomb_on_me(need_to_return = False):
    global time_escape_bomb, is_escaping_bombs, bombs_postitions
    bombs_postitions.append(my_pos)
    escape_bombs(need_to_return) 
    time_escape_bomb = round(time())
    is_escaping_bombs = True
    # print("set bomb on me")
    return move_to_keys["bomb"]
                
def set_bomb_to_destroy_block():
    global time_escape_bomb, is_escaping_bombs
    for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
        if (my_pos[0] + i * TILE, my_pos[1] + j * TILE) in blocks and not is_escaping_bombs:
            return set_bomb_on_me()
        
def move_to_enemy(enemy_pos):
    # print("from move_to_enemy")
    if abs(my_pos[0] - enemy_pos[0]) < abs(my_pos[1] - enemy_pos[1]):
        # move along oy
        if is_correct_coords(my_pos[0], my_pos[1]+TILE):
            if my_pos[1] < enemy_pos[1] and (my_pos[0], my_pos[1]+TILE) not in stones + blocks:
                return K_DOWN
            if my_pos[1] < enemy_pos[1] and (my_pos[0], my_pos[1]+TILE) not in stones:
                return set_bomb_on_me(True)
        if is_correct_coords(my_pos[0], my_pos[1]-TILE):
            if my_pos[1] > enemy_pos[1] and (my_pos[0], my_pos[1]-TILE) not in stones + blocks:
                return K_UP
            if my_pos[1] > enemy_pos[1] and (my_pos[0], my_pos[1]-TILE) not in stones:
                return set_bomb_on_me(True)
    # move along ox
    if is_correct_coords(my_pos[0]+TILE, my_pos[1]):
        if my_pos[0] < enemy_pos[0] and (my_pos[0]+TILE, my_pos[1]) not in stones + blocks:
            return K_RIGHT
        if my_pos[0] < enemy_pos[0] and (my_pos[0]+TILE, my_pos[1]) not in stones:
            return set_bomb_on_me(True)
    if is_correct_coords(my_pos[0]-TILE, my_pos[1]):
        if my_pos[0] > enemy_pos[0] and (my_pos[0]-TILE, my_pos[1]) not in stones + blocks:
            return K_LEFT
        if my_pos[0] < enemy_pos[0] and (my_pos[0]-TILE, my_pos[1]) not in stones:
            return set_bomb_on_me(True)
    h = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    shuffle(h)
    for [i, j] in h:
        if is_correct_coords(my_pos[0] + i * TILE, my_pos[1] + j * TILE) and (my_pos[0] + i * TILE, my_pos[1] + j * TILE) not in blocks + stones:
            return move_to_keys[(i, j)]

def get_bot_move(p, enemies_positions, enemies_points, bombs_pos,  blocks_layout, stones_layout):
    global q, stones, blocks, time_escape_bomb, is_escaping_bombs, bombs_positions, my_pos, bombs_postitions
    bombs_postitions = bombs_pos
    blocks = blocks_layout
    stones = stones_layout
    my_pos = list(p)
    enemy_pos = enemies_positions[0]   
    enemy_pts = enemies_points[0]
    if not q.empty():
        return q.get()
    for b in bombs_pos:
        if abs(my_pos[0] - b[0]) <= TILE and abs(my_pos[1] - b[1]) <= TILE:
            while not q.empty():
                q.get()
            escape_bombs() 
            time_escape_bomb = round(time())
            is_escaping_bombs = True
            return q.get()
    if is_escaping_bombs and time_escape_bomb + 2 > time():
        return K_1
    else:
        is_escaping_bombs = False
    if my_pts <= enemy_pts + 2:
        btn = set_bomb_to_destroy_block()
        if btn == K_SPACE:
            return btn
    if abs(my_pos[0] - enemy_pos[0]) + abs(my_pos[1] - enemy_pos[1]) <= TILE:
        return set_bomb_on_me()
    return move_to_enemy(enemy_pos)
