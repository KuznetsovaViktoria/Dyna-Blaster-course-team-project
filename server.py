import socket
import time
import pickle

BLOCKS = [(544, 512), (192, 480), (96, 448), (352, 320), (64, 256), (448, 320), (224, 288), (608, 416), (736, 96),
          (224, 352), (448, 544), (736, 320), (384, 160), (288, 448), (32, 544), (544, 128), (320, 256), (320, 32),
          (64, 96), (128, 64), (480, 128), (704, 448), (64, 416), (192, 288), (160, 448), (128, 448), (0, 256),
          (0, 320), (288, 480), (0, 544), (768, 416), (384, 384), (416, 512), (0, 64), (480, 512), (640, 448),
          (96, 64), (64, 64), (736, 224), (672, 224), (352, 416), (608, 448), (544, 32), (384, 128), (0, 480),
          (288, 416), (192, 416), (608, 384), (448, 288), (512, 512), (736, 448), (160, 192), (704, 512), (160, 64),
          (736, 512), (512, 320), (320, 96), (288, 544), (160, 416), (384, 32), (0, 192), (736, 160), (288, 160),
          (512, 224), (352, 256), (320, 352), (32, 288), (224, 480), (192, 224), (128, 320), (608, 288), (64, 512),
          (352, 384), (448, 512), (224, 544), (608, 320), (608, 128), (96, 32), (480, 288), (224, 384)]

class Player:
    def __init__(self, sock, name, color, pos):
        self.sock = sock
        self.name = name
        self.errors = 0
        self.pos = pos
        self.color = color
        self.hp = 5
        self.received_data = []

    def remove_from_game(self):
        if self.sock in players:
            players.remove(self.sock)
            self.sock.close()
            print("Player disconnected")
            if players.empty():
                end_game("all players disconnected")


def send_data_to_all_players(data):
    for player in players: # may have used sendall, but needed to count errors for each player
        try:
            player.sock.send(pickle.dumps([player.name] + data))
            player.errors = 0
        except:
            if player.errors >= 10:
                player.remove_from_game()

def end_game(msg):
    #sth to end the game
    print("GAME ENDED: ", msg)


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
positions = [[100, 275], [650, 275]]
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
# send_data_to_all_players(["start", ["all_players_names", names], ["field_layout", BLOCKS]])
for player in players: # may have used sendall, but needed to count errors for each player
        try:
            player.sock.send(pickle.dumps([["message", "start"], ["all_players_names", names], ["field_layout", BLOCKS],
                                           ["your_name", player.name], ["your_color", player.color], ["your_position", player.pos],
                                           ["all_players_colors", colors], ["all_players_positions", positions]]))
            player.errors = 0
        except:
            if player.errors >= 10:
                player.remove_from_game()


while True:
# for i in range(10):
    # read players" commands
    received_data_name_order = []
    positions = []
    hps = []
    for player in players:
        try:
            data = pickle.loads(player.sock.recv(1024))
            print(data)
            for [key, value] in data[1:]:
                # key, value = data[i][0], data[i][1]
                if key == "pos":
                    player.pos = value
                    received_data_name_order += [data[0][1]]
                    positions.append(value)
                if key == "hp":
                    player.hp = value
                    hps.append(value)
        except:
            player.errors += 1
            if player.errors >= 10:
                player.remove_from_game()
            # print("error")
    # parse commands

    #sending new positions and hp_s to players
    if len(received_data_name_order) == 0:
        continue
    print("received", positions, received_data_name_order)
    for player in players:
        try:
            player.sock.send(pickle.dumps([["names", received_data_name_order], ["positions", positions], ["hps", hps]]))
            # print("sent", received_data_name_order, positions)
            player.errors = 0
        except:
            player.errors += 1
            if player.errors >= 100:
                player.remove_from_game()
    if len(players) == 0:
        break

    # time.sleep(1)

main_socket.close()