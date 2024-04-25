from ctypes import CDLL, c_int, POINTER
from pygame.locals import * 

# Загружаем динамическую библиотеку C++
lib = CDLL('./bot.so')  # Путь к скомпилированной библиотеке .so

# Объявляем типы данных для функции
lib.get_bot_move.argtypes = (POINTER(c_int), c_int, POINTER(POINTER(c_int)), 
                                     c_int, POINTER(c_int), c_int, POINTER(POINTER(c_int)), c_int, 
                                     POINTER(POINTER(c_int)), c_int, POINTER(POINTER(c_int)), c_int)
lib.get_bot_move.restype = c_int

lib.set_first_params.argtypes = (c_int, c_int)


def set_first_params(t, w):
    lib.set_first_params(t, w)

def get_bot_move(my_pos, enemies_positions, enemies_points, bombs_positions,  blocks_layout, stones_layout):
    my_pos_arr = (c_int * 2)(*list(my_pos))
    enemies_positions_arr = (POINTER(c_int) * len(enemies_positions))(*[ (c_int * 2)( *v) for v in enemies_positions ])
    enemies_points_arr = (c_int * 2)(*list(enemies_points))
    bombs_positions_arr = (POINTER(c_int) * len(bombs_positions))(*[ (c_int * 2)( *v) for v in bombs_positions ])
    blocks_layout_arr = (POINTER(c_int) * len(blocks_layout))(*[ (c_int * 2)( *list(v)) for v in blocks_layout ])
    stones_layout_arr = (POINTER(c_int) * len(stones_layout))(*[ (c_int * 2)( *list(v)) for v in stones_layout ])

    result = lib.get_bot_move(my_pos_arr, 2, enemies_positions_arr, len(enemies_positions),
                                      enemies_points_arr, len(enemies_points),
                                      bombs_positions_arr, len(bombs_positions),
                                      blocks_layout_arr, len(blocks_layout),
                                      stones_layout_arr, len(stones_layout))
    keys_to_move = {'L': K_LEFT, 'R': K_RIGHT, 'U': K_UP, 'D': K_DOWN, 'S': K_SPACE}
    return keys_to_move[chr(result)]
