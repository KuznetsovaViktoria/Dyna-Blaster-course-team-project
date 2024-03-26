import socket
import pickle

# BLOCKS = [(12, 12), (544, 512), (192, 480), (96, 448), (352, 320), (64, 256), (448, 320), (224, 288), (608, 416), (736, 96),
#           (224, 352), (448, 544), (736, 320), (384, 160), (288, 448), (32, 544), (544, 128), (320, 256), (320, 32),
#           (64, 96), (128, 64), (480, 128), (704, 448), (64, 416), (192, 288), (160, 448), (128, 448), (0, 256),
#           (0, 320), (288, 480), (0, 544), (768, 416), (384, 384), (416, 512), (0, 64), (480, 512), (640, 448),
#           (96, 64), (64, 64), (736, 224), (672, 224), (352, 416), (608, 448), (544, 32), (384, 128), (0, 480),
#           (288, 416), (192, 416), (608, 384), (448, 288), (512, 512), (736, 448), (160, 192), (704, 512), (160, 64),
#           (736, 512), (512, 320), (320, 96), (288, 544), (160, 416), (384, 32), (0, 192), (736, 160), (288, 160),
#           (512, 224), (352, 256), (320, 352), (32, 288), (224, 480), (192, 224), (128, 320), (608, 288), (64, 512),
#           (352, 384), (448, 512), (224, 544), (608, 320), (608, 128), (96, 32), (480, 288), (224, 384)]
TILE = 50
WIDTH = 650
HEIGHT = WIDTH + TILE
BLOCKS = [
    (0, 100), (50, 150), (100, 100), (200, 100), (300, 100), (600, 100), (500, 100),
    (50, 250), (50, 350), (50, 550), (300, 150), (300, 200), (300, 300), (300, 500),
    (200, 150), (200, 50), (200, 350), (200, 400), (200, 550), (200, 600), (400, 50),
    (400, 50), (400, 150), (400, 250), (400, 350), (400, 400), (400, 550), (500, 50),
    (500, 50), (500, 150), (500, 200), (500, 250), (500, 450), (600, 50), (600, 150),
    (600, 200), (600, 250), (600, 350), (600, 450), (600, 500), (150, 350), (150, 450),
    (250, 50), (250, 450), (250, 350), (250, 550), (350, 450), (350, 150), (350, 550),
    (450, 50), (450, 150), (450, 250), (450, 550), (550, 150), (550, 350), (550, 450),
    (0, 150), (0, 450), (0, 400), (0, 550), (0, 600), (0, 650), (100, 650), (150, 650),
    (350, 650), (300, 650), (500, 650), (40, 650), (450, 650)
]
BLOCKS_CANT_BROKE = [
    (50, 100), (150, 100), (250, 100), (350, 100), (450, 100), (550, 100),
    (50, 200), (150, 200), (250, 200), (350, 200), (450, 200), (550, 200),
    (50, 300), (150, 300), (250, 300), (350, 300), (450, 300), (550, 300),
    (50, 400), (150, 400), (250, 400), (350, 400), (450, 400), (550, 400),
    (50, 500), (150, 500), (250, 500), (350, 500), (450, 500), (550, 500),
    (50, 600), (150, 600), (250, 600), (350, 600), (450, 600), (550, 600),
]

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
    global players
    if player in players:
        players.remove(player)
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
HOST = "127.0.0.1"  # localhost
PORT = 1093 # any above 1023
main_socket.bind((HOST, PORT))
main_socket.setblocking(0)
main_socket.listen(2)   #change anytime
kExpectedPlayers = 2    #change anytime

# making connection with players
players = []
names = []
colors = ["red", "blue"]
positions = [[0, TILE], [WIDTH - TILE, HEIGHT - TILE]]
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
                # key, value = data[i][0], data[i][1]
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
    # print("received", positions, received_data_name_order)
    for player in players:
        try:
            player.sock.send(pickle.dumps([["names", received_data_name_order], ["positions", positions], ["hps", hps], ["bombs", bombs]]))
            # print("sent", received_data_name_order, positions)
            player.errors = 0
        except:
            player.errors += 1
            if player.errors >= 10:
                remove_from_game(player)
    if len(players) == 0:
        break

    # time.sleep(1)

main_socket.close()