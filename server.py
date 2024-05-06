import socket
import pickle
from fields import *
import random
TILE = 50
WIDTH = 650
POINTS_HEIGHT = 4 * TILE
HEIGHT = WIDTH + POINTS_HEIGHT
BLOCKS = []
BLOCKS_CANT_BROKE = []
fields = {"empty_field": empty_field, "random_field": random_field, "scull_field":scull_field, "busy_field": busy_field, "labyrinth_field": labyrinth_field}

def fieldToArray(field_name):
    global BLOCKS, BLOCKS_CANT_BROKE, FIELD, positions
    print(field_name)
    # keys = list(fields.keys())
    # random.shuffle(keys)
    FIELD = fields[field_name]
    for i in range(13):
        for j in range(13):
            if FIELD[i][j] == "B":
                BLOCKS_CANT_BROKE.append((j * TILE, i* TILE + POINTS_HEIGHT))
            elif FIELD[i][j] == "W":
                BLOCKS.append((j * TILE, i* TILE + POINTS_HEIGHT))
    # FIELD = keys[0]


    if field_name == "empty_field":
        positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [WIDTH - TILE, POINTS_HEIGHT], [0, HEIGHT - TILE],
                     [TILE * 6, POINTS_HEIGHT + TILE * 2], [TILE * 6, HEIGHT - TILE * 3], [TILE * 3, HEIGHT - TILE * 7], [WIDTH - TILE * 4, HEIGHT - TILE * 7]]
    elif field_name == "random_field":
        positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [WIDTH - 6 * TILE, POINTS_HEIGHT + 4 * TILE], [TILE * 2, HEIGHT - 2 * TILE],
                     [TILE * 2, HEIGHT - 7 * TILE], [TILE * 6, POINTS_HEIGHT + 6 * TILE], [8 * TILE, HEIGHT - 4 * TILE], [WIDTH - 3 * TILE, HEIGHT - 7 * TILE]]
    elif field_name == "scull_field":
        positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [WIDTH - TILE, POINTS_HEIGHT], [0, HEIGHT - TILE],
                     [TILE * 2, POINTS_HEIGHT + TILE * 6], [TILE * 6, HEIGHT - TILE], [TILE * 6, POINTS_HEIGHT], [WIDTH - TILE * 3, POINTS_HEIGHT + TILE * 6]]
    elif field_name == "busy_field":
        positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [WIDTH - TILE, POINTS_HEIGHT], [0, HEIGHT - TILE],
                     [TILE * 2, POINTS_HEIGHT + TILE * 6], [TILE * 6, HEIGHT - TILE], [TILE * 5, POINTS_HEIGHT + TILE], [WIDTH - TILE * 3, POINTS_HEIGHT + TILE * 5]]
    elif field_name == "labyrinth_field":
        positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [TILE * 7, POINTS_HEIGHT], [TILE * 5, HEIGHT - TILE],
                     [3 * TILE, POINTS_HEIGHT], [TILE * 9, HEIGHT - TILE], [TILE * 11, POINTS_HEIGHT], [TILE, HEIGHT - TILE]]

class Player:
    def __init__(self, sock, name, color):
        self.sock = sock
        self.name = name
        self.errors = 0
        self.pos = [0, 0]
        self.color = color
        self.hp = 5
        self.bombs = []
        self.received_data = []

def remove_from_game(player):
    global players, removed_players
    if player in players:
        players.remove(player)
        removed_players.append(player.name)
        player.sock.close()
        print("Player disconnected")
        if len(players) == 0:
            end_game("all players disconnected")


def end_game(msg):
    #sth to end the game
    print("GAME ENDED: ", msg)
    exit(0)

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
HOST = '127.0.0.1'  # localhost
# HOST = '192.168.1.72'
PORT = 1093 # any above 1023
main_socket.bind((HOST, PORT))
main_socket.setblocking(0)
kExpectedPlayers = 4    #change anytime
main_socket.listen(kExpectedPlayers)   #change anytime

# making connection with players
players = []
names = []
removed_players = []
colors = ["red", "blue", "gray", "white", "pink", "black", "orange", "yellow"]
positions = []
field_names = {field_name: 0 for field_name in fields.keys()}
while True:
    try:  # connect players
        new_socket, addr = main_socket.accept()
        print("Connected ", addr)
        new_socket.setblocking(0)
        new_socket.settimeout(6000) # установка таймаута
        while True:
            data = pickle.loads(new_socket.recv(1024 * 8))
            if len(data) > 0:
                field_names[data] += 1
                break
        players.append(Player(new_socket, addr, colors[len(players)]))
        names.append(addr)
        if len(players) == kExpectedPlayers:
            print("all payers connected")
            break
    except:
        pass

fieldToArray(sorted(field_names.items(), key=lambda p: -p[1])[0][0])
for i in range(kExpectedPlayers):
    players[i].pos = positions[i]

#ready to start the game
for player in players: # may have used sendall, but needed to count errors for each player
        try:
            player.sock.send(pickle.dumps([["message", "start"], ["all_players_names", names], ["field_layout", [BLOCKS, BLOCKS_CANT_BROKE]],
                                           ["your_name", player.name], ["your_color", player.color], ["your_position", player.pos],
                                           ["all_players_colors", colors[:kExpectedPlayers]], ["all_players_positions", positions[:kExpectedPlayers]]]))
            player.errors = 0
        except:
            if player.errors >= 10:
                remove_from_game(player)


while True:
    # read players" commands
    received_data_name_order = []
    positions = []
    hps = []
    bombs = []
    for player in players:
        try:
            data = pickle.loads(player.sock.recv(1024*8))
            for [key, value] in data[1:]:
                if key == "pos":
                    player.pos = value
                    if player.pos[0] % TILE < TILE - player.pos[0] % TILE:
                        player.pos[0] -= player.pos[0] % TILE
                    else:
                        player.pos[0] += TILE - player.pos[0] % TILE
                    if player.pos[1] % TILE < TILE - player.pos[1] % TILE:
                        player.pos[1] -= player.pos[1] % TILE
                    else:
                        player.pos[1] += TILE - player.pos[1] % TILE
                    received_data_name_order += [data[0][1]]
                    positions.append(player.pos)
                if key == "hp":
                    player.hp = value
                    hps.append(value)
                if key == "bombs":
                    player.bombs = value
                    bombs.append(value)

        except:
            player.errors += 1
            if player.errors >= 10:
                remove_from_game(player)
    # parse commands

    #sending new positions and hp_s to players
    if len(received_data_name_order) == 0:
        continue
    for player in players:
        try:
            player.sock.send(pickle.dumps([["names", received_data_name_order], ["positions", positions], ["hps", hps], ["bombs", bombs], ["removed_players", removed_players]]))
            player.errors = 0
        except:
            player.errors += 1
            if player.errors >= 10:
                remove_from_game(player)
    if len(players) == 0:
        break
    # time.sleep(1)

main_socket.close()