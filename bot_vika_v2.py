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
bangs_positions = []
enemy_pos = []
my_pts = 0

def set_first_params(x, y, t, w):
    global my_pos, WIDTH, TILE, q
    q = queue.Queue()
    my_pos = [x, y]
    TILE = t
    WIDTH = w

def is_correct_coords(x, y):
    return 0 <= x <= WIDTH - TILE and 0 <= y < WIDTH
    
def update_my_points():
    global my_pts
    for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
        if (my_pos[0] + i * TILE, my_pos[1] + j * TILE) in blocks:
            my_pts += 1

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
                    all([x not in stones+blocks+enemy_pos+bombs_postitions+bangs_positions for x in [one, two, three]]) and 
                    all([abs(three[0] - b[0]) + abs(three[1] - b[1]) >= TILE * 2 for b in bombs_postitions])):
                    q.put(move_to_keys[(i, j)])
                    q.put(move_to_keys[(ii, jj)])
                    q.put(move_to_keys[(iii, jjj)])
                    # for _ in range(5):
                    #     q.put(move_to_keys[(0, 0)])
                    return
                    # q.put(move_to_keys[(-ii, -jj)])
                    # q.put(move_to_keys[(-i, -j)])

def restore_path(dist, a, b):
    global q
    path_rev = []
    while [a, b] != my_pos:
        for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
            if not is_correct_coords(a+i * TILE, b+j * TILE):
                continue
            if dist[(a, b)] - 1 == dist[(a+i * TILE, b+j * TILE)] and (a + i * TILE, b + j * TILE) not in blocks + stones + bombs_postitions + bangs_positions and dist[(a+i * TILE, b+j * TILE)] >= 0 and all([abs(a+i * TILE - c[0]) + abs(b+j * TILE - c[1]) >= TILE * 3 for c in bombs_postitions])and all([abs(a+i * TILE - c[0]) + abs(b+j * TILE - c[1]) > 0 for c in bangs_positions]):
                path_rev.append(move_to_keys[(-i, -j)])
                a, b = a+i * TILE, b+j * TILE
                break
    q.put(path_rev[-1])

                
def set_bomb_to_destroy_block():
    p = queue.Queue()
    p.put(my_pos)
    dist = {}
    for i in range(0, WIDTH, TILE):
        for j in range(0, WIDTH, TILE):
            dist[(i, j)] = -1
    dist[tuple(my_pos)] = 0
    fin = []
    while not p.empty():
        [x, y] = p.get()
        for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
            if not is_correct_coords(x + i * TILE, y + j * TILE) or dist[(x+i * TILE, y+j * TILE)] > 0 or [x+i * TILE, y+j * TILE] == my_pos:
                continue
            if fin == [] and (x + i * TILE, y + j * TILE) in blocks and (x + i * TILE, y + j * TILE) not in bombs_postitions + bangs_positions and  all([abs(x + i * TILE - b[0]) + abs(y + j * TILE - b[1]) >= TILE * 3 for b in bombs_postitions]):
                fin = [x + i * TILE, y + j * TILE]
                dist[(x+i * TILE, y+j * TILE)] = dist[(x, y)] + 1
            elif (x + i * TILE, y + j * TILE) in bombs_postitions:
                dist[(x + i * TILE, y + j * TILE)] = 100000
            elif (x + i * TILE, y + j * TILE) not in blocks + stones:
                dist[(x+i * TILE, y+j * TILE)] = dist[(x, y)] + 1
                p.put([x + i * TILE, y + j * TILE])
            else:
                dist[(x+i * TILE, y+j * TILE)] = 100000
    if fin == []:
        for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
            if (is_correct_coords(my_pos[0] + i * TILE, my_pos[1] + j * TILE) and all([abs(my_pos[0] - b[0]) + abs(my_pos[1] - b[1]) >= TILE * 3 for b in bombs_postitions]) and
                        all([abs(my_pos[0] - b[0]) + abs(my_pos[1] - b[1]) > 0 for b in bangs_positions]) and (my_pos[0] + i * TILE, my_pos[1] + j * TILE) not in stones+blocks):
                q.put(move_to_keys[(i, j)])
                return

    restore_path(dist, fin[0], fin[1])
        

def get_bot_move(p, enemies_positions, enemies_points, bombs_pos, bangs_pos, blocks_layout, stones_layout):
    global q, stones, blocks, time_escape_bomb, is_escaping_bombs, bombs_positions, my_pos, bombs_postitions, enemy_pos, bangs_positions
    bombs_postitions = bombs_pos
    bangs_positions = bangs_pos
    blocks = blocks_layout
    stones = stones_layout
    my_pos = list(p)
    enemy_pos = enemies_positions 
    if not q.empty():
        # t = q.get()
        return q.get()
    
    for b in bombs_pos:
        if abs(my_pos[0] - b[0]) + abs(my_pos[1] - b[1]) < TILE * 3:
            while not q.empty():
                q.get()
            escape_bombs() 
            time_escape_bomb = time()
            is_escaping_bombs = True
            return q.get()
        
    if is_escaping_bombs and time_escape_bomb + 1.5 > time():
        return K_1
    else:
        is_escaping_bombs = False
        
    for [i, j] in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
        # if (my_pos[0] + i * TILE, my_pos[1] + j * TILE) in blocks+enemy_pos and all([abs(my_pos[0] - b[0]) + abs(my_pos[1] - b[1]) >= TILE * 3 for b in bombs_postitions]):
        if (my_pos[0] + i * TILE, my_pos[1] + j * TILE) in blocks+enemy_pos:
            update_my_points()
            return move_to_keys['bomb']
    if any([my_pts <= p + 3 for p in enemies_points]):
        set_bomb_to_destroy_block()
        return q.get()
    dists = [abs(my_pos[0] - e[0]) + abs(my_pos[1] - e[1]) for e in enemies_positions]
    return move_to_enemy(enemies_positions[dists.index(min(dists))])
    

                

# def set_bomb_on_me(need_to_return = False):
#     global time_escape_bomb, is_escaping_bombs, bombs_postitions
#     bombs_postitions.append(my_pos)
#     escape_bombs(need_to_return) 
#     time_escape_bomb = round(time())
#     is_escaping_bombs = True
#     # print("set bomb on me")
#     return move_to_keys["bomb"]

def move_to_enemy(enemy_pos):
    if abs(my_pos[0] - enemy_pos[0]) < abs(my_pos[1] - enemy_pos[1]):
        # move along oy
        if is_correct_coords(my_pos[0], my_pos[1]+TILE):
            if my_pos[1] < enemy_pos[1] and (my_pos[0], my_pos[1]+TILE) not in stones + blocks:
                return K_DOWN
            # if my_pos[1] < enemy_pos[1] and (my_pos[0], my_pos[1]+TILE) not in stones:
            #     return set_bomb_on_me(True)
        if is_correct_coords(my_pos[0], my_pos[1]-TILE):
            if my_pos[1] > enemy_pos[1] and (my_pos[0], my_pos[1]-TILE) not in stones + blocks:
                return K_UP
            # if my_pos[1] > enemy_pos[1] and (my_pos[0], my_pos[1]-TILE) not in stones:
                # return set_bomb_on_me(True)
    # move along ox
    if is_correct_coords(my_pos[0]+TILE, my_pos[1]):
        if my_pos[0] < enemy_pos[0] and (my_pos[0]+TILE, my_pos[1]) not in stones + blocks:
            return K_RIGHT
        # if my_pos[0] < enemy_pos[0] and (my_pos[0]+TILE, my_pos[1]) not in stones:
        #     return set_bomb_on_me(True)
    if is_correct_coords(my_pos[0]-TILE, my_pos[1]):
        if my_pos[0] > enemy_pos[0] and (my_pos[0]-TILE, my_pos[1]) not in stones + blocks:
            return K_LEFT
        # if my_pos[0] < enemy_pos[0] and (my_pos[0]-TILE, my_pos[1]) not in stones:
        #     return set_bomb_on_me(True)
    h = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    shuffle(h)
    for [i, j] in h:
        if is_correct_coords(my_pos[0] + i * TILE, my_pos[1] + j * TILE) and (my_pos[0] + i * TILE, my_pos[1] + j * TILE) not in blocks + stones:
            return move_to_keys[(i, j)]
