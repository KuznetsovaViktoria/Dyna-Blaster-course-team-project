import random
from queue import Queue
from random import randint
from pygame.locals import *

my_pos =[0, 0]
TILE = 0
WIDTH = 0
INF = 1e10

def set_first_params(x, y, t, w):
    global my_pos, WIDTH, TILE
    my_pos = [x, y]
    TILE = t
    WIDTH = w

def is_correct_coords(x, y):
    return 0 <= x <= WIDTH - TILE and 0 < y <= WIDTH

def free(blocks_layout, stones_layout):
    free_positions = []
    for x in range(0, WIDTH, TILE):
        for y in range(0, WIDTH, TILE):
            if (x, y) in blocks_layout or (x, y) in stones_layout:
                continue
            free_positions.append((x, y))
    return free_positions

def without_bombs(free_positions, bombs_positions):
    free_positions_no_bombs = []
    for x,y in free_positions:
        if (x, y) in bombs_positions or (x + 1 * TILE, y) in bombs_positions or (x - 1 * TILE, y) in bombs_positions or (x, y + 1 * TILE) in bombs_positions or (x, y - 1 * TILE) in bombs_positions:
            continue
        free_positions_no_bombs.append((x, y))
    return free_positions_no_bombs

def pos_good_for_escape(x, y, free_positions):
    if (x - 1 * TILE, y) in free_positions:
        return True, K_LEFT
    if (x + 1 * TILE, y) in free_positions:
        return True, K_RIGHT
    if (x, y - 1 * TILE) in free_positions:
        return True, K_UP
    if (x, y + 1 * TILE) in free_positions:
        return True, K_DOWN
    return False, None

# cчитает для каждой клетки поля расстояние до ближайшего блока
def block_distance_finder(stones_layout, blocks_layout, bombs_positions, enemies_positions):
    layout = dict()
    for x in range(0, WIDTH, TILE):
        for y in range(0, WIDTH, TILE):
            layout[(x, y)] = -1
    for stone in stones_layout:
        layout[stone] = INF
    for bomb in bombs_positions:
        x, y = bomb
        layout[(x, y)] = INF
        layout[(x + 1 * TILE, y)] = INF
        layout[(x - 1 * TILE, y)] = INF
        layout[(x, y + 1 * TILE)] = INF
        layout[(x, y - 1 * TILE)] = INF
    for block in blocks_layout:
        layout[block] = 0
    for enemy in enemies_positions:
        layout[enemy] = 0
    q = Queue()
    for block in blocks_layout:
        q.put(block)
    for enemy in enemies_positions:
        q.put(enemy)
    while not q.empty():
        x, y = q.get()
        if x > 0 and layout[(x - TILE, y)] == -1:
            layout[(x - TILE, y)] = layout[(x, y)] + 1
            q.put((x - TILE, y))
        if x + TILE < WIDTH and layout[(x + TILE, y)] == -1:
            layout[(x + TILE, y)] = layout[(x, y)] + 1
            q.put((x + TILE, y))
        if y > 0 and layout[(x, y - TILE)] == -1:
            layout[(x, y - TILE)] = layout[(x, y)] + 1
            q.put((x, y - TILE))
        if y + TILE < WIDTH and layout[(x, y + TILE)] == -1:
            layout[(x, y + TILE)] = layout[(x, y)] + 1
            q.put((x, y + TILE))
    return layout

def get_bot_move(my_position, enemies_positions, enemies_points, bombs_positions,  blocks_layout, stones_layout):
    keys_to_move = []
    my_x, my_y = my_position
    free_positions = free(blocks_layout, stones_layout)
    free_positions_without_bombs = without_bombs(free_positions, bombs_positions)
    for bomb_x, bomb_y in bombs_positions:
        if bomb_x == my_x and bomb_y == my_y:
            if (my_x - 1 * TILE, my_y) in free_positions and pos_good_for_escape(my_x - 1 * TILE, my_y, free_positions_without_bombs)[0]:
                keys_to_move.append(K_LEFT)
            if (my_x + 1 * TILE, my_y) in free_positions and pos_good_for_escape(my_x + 1 * TILE, my_y, free_positions_without_bombs)[0]:
                keys_to_move.append(K_RIGHT)
            if (my_x, my_y - 1 * TILE) in free_positions and pos_good_for_escape(my_x, my_y - 1 * TILE, free_positions_without_bombs)[0]:
                keys_to_move.append(K_UP)
            if (my_x, my_y + 1 * TILE) in free_positions and pos_good_for_escape(my_x, my_y + 1 * TILE, free_positions_without_bombs)[0]:
                keys_to_move.append(K_DOWN)
            if len(keys_to_move) > 0:
                return random.choice(keys_to_move)
        if (bomb_x + 1 * TILE == my_x and bomb_y == my_y) or (bomb_x - 1 * TILE == my_x and bomb_y == my_y) or (bomb_x == my_x and bomb_y + 1 * TILE == my_y) or (bomb_x == my_x and bomb_y - 1 * TILE == my_y):
            is_good, key = pos_good_for_escape(my_x, my_y, free_positions_without_bombs)
            if is_good:
                return key
            else:
                # It is very very sad, -hp LOL
                if bomb_x + 1 * TILE == my_x and bomb_y == my_y:
                    return K_LEFT
                if bomb_x - 1 * TILE == my_x and bomb_y == my_y:
                    return K_RIGHT
                if bomb_x == my_x and bomb_y + 1 * TILE == my_y:
                    return K_UP
                if bomb_x == my_x and bomb_y - 1 * TILE == my_y:
                    return K_DOWN

    layout = block_distance_finder(stones_layout, blocks_layout, bombs_positions, enemies_positions)
    dist = layout[my_position]
    if dist != -1:
        if dist <= 1:
            return K_SPACE
        if layout.get((my_x - 1 * TILE, my_y), INF) < dist:
            keys_to_move.append(K_LEFT)
        if layout.get((my_x + 1 * TILE, my_y), INF) < dist:
            keys_to_move.append(K_RIGHT)
        if layout.get((my_x, my_y - 1 * TILE), INF) < dist:
            keys_to_move.append(K_UP)
        if layout.get((my_x, my_y + 1 * TILE), INF) < dist:
            keys_to_move.append(K_DOWN)
        if len(keys_to_move):
            return random.choice(keys_to_move)
    # return random.choice(keys_to_move)
    return None