import socket
import pickle
TILE = 50
WIDTH = 650
POINTS_HEIGHT = 4 * TILE
HEIGHT = WIDTH + POINTS_HEIGHT
BLOCKS = []
BLOCKS_CANT_BROKE = []
def fieldToArray():
    global BLOCKS, BLOCKS_CANT_BROKE
    FIELD = [
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "E", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "W", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "W", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "W", "B", "E"],
        ["E", "E", "E", "E", "E", "E", "E", "E", "E", "B", "B", "B", "E"]
    ]
    for i in range(13):
        for j in range(13):
            if FIELD[i][j] == "B":
                BLOCKS_CANT_BROKE.append((j * TILE, i* TILE + POINTS_HEIGHT))
            elif FIELD[i][j] == "W":
                BLOCKS.append((j * TILE, i* TILE + POINTS_HEIGHT))

fieldToArray()
# BLOCKS = [
#     (0, 100), (100, 100), (200, 100), (300, 100), (600, 100), (500, 100),
#     (50, 550), (300, 150), (300, 200), (300, 300), (300, 500),
#     (200, 150), (200, 50), (200, 350), (200, 400), (200, 550), (200, 600),
#     (400, 50), (400, 150), (400, 250), (400, 350), (400, 400), (400, 550),
#     (500, 50), (500, 150), (500, 200), (500, 250), (500, 450), (600, 50), (600, 150),
#     (600, 200), (600, 250), (600, 350), (600, 450), (600, 500), (150, 350), (150, 450),
#     (250, 50), (250, 450), (250, 350), (250, 550), (350, 450), (350, 150), (350, 550),
#     (450, 50), (450, 150), (450, 250), (450, 550), (550, 150), (550, 350), (550, 450),
#     (0, 150), (0, 450), (0, 400), (0, 550), (0, 600), (0, 650), (100, 650), (150, 650),
#     (350, 650), (300, 650), (500, 650), (400, 650), (450, 650)
# ]
# BLOCKS_CANT_BROKE = [
#     (50, 100), (150, 100), (250, 100), (350, 100), (450, 100), (550, 100),
#     (50, 200), (150, 200), (250, 200), (350, 200), (450, 200), (550, 200),
#     (50, 300), (150, 300), (250, 300), (350, 300), (450, 300), (550, 300),
#     (50, 400), (150, 400), (250, 400), (350, 400), (450, 400), (550, 400),
#     (50, 500), (150, 500), (250, 500), (350, 500), (450, 500), (550, 500),
#     (50, 600), (150, 600), (250, 600), (350, 600), (450, 600), (550, 600),
#     (50, 150), (50, 250), (50, 350), (50, 450)
# ]
class Player:
    def __init__(self, sock, name, color, pos):
        self.sock = sock
        self.name = name
        self.errors = 0
        self.pos = pos
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
positions = [[0, POINTS_HEIGHT], [WIDTH - TILE, HEIGHT - TILE], [WIDTH - TILE, POINTS_HEIGHT], [0, HEIGHT - TILE]]
while True:
    try:  # connect players
        new_socket, addr = main_socket.accept()
        print("Connected ", addr)
        new_socket.setblocking(0)
        new_socket.settimeout(6000) # установка таймаута
        players.append(Player(new_socket, addr, colors[len(players)], positions[len(players)]))
        names.append(addr)
        if len(players) == kExpectedPlayers:
            print("all payers connected")
            break
    except:
        pass

#ready to start the game
for player in players: # may have used sendall, but needed to count errors for each player
        try:
            player.sock.send(pickle.dumps([["message", "start"], ["all_players_names", names], ["field_layout", [BLOCKS, BLOCKS_CANT_BROKE]],
                                           ["your_name", player.name], ["your_color", player.color], ["your_position", player.pos],
                                           ["all_players_colors", colors], ["all_players_positions", positions]]))
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
            data = pickle.loads(player.sock.recv(1024))
            for [key, value] in data[1:]:
                if key == "pos":
                    player.pos = value
                    received_data_name_order += [data[0][1]]
                    positions.append(value)
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