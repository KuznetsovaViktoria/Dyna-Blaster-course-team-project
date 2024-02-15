import socket
import time
import pickle

class Player:
    def __init__(self, sock, name):
        self.sock = sock
        self.name = name
        self.errors = 0
        self.pos = [0, 0, 0] # x, y, direction
        self.received_data = []

    def remove_from_game(self):
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
PORT = 1092 # any above 1023
main_socket.bind((HOST, PORT))
main_socket.setblocking(0)
main_socket.listen(8)
kExpectedPlayers = 1    #change anytime

# making connection with players
players = []
names = []
while True:
    try:  # connect players
        new_socket, addr = main_socket.accept()
        print("Connected ", addr)
        new_socket.setblocking(0)
        new_socket.settimeout(6000) # установка таймаута
        players.append(Player(new_socket, addr))
        names.append(addr)
        if len(players) == kExpectedPlayers:
            print("all payers connected")
            break
    except:
        pass
        # print("nothing")
    # time.sleep(0.1)

#ready to start the game
send_data_to_all_players(["start", names])
# maybe wait for the responce to draw the field
#send_data_to_all_players("draw the field")


# while True:
for i in range(10):
    # read players' commands
    received_data = []
    for player in players:
        try:
            data = player.sock.recv(1024)
            data = pickle.loads(data)
            received_data.append([player.name, data])
            print("Server got ", data)
            if data[0] == "tank":
                player.pos = data[1]["pos"]
        except:
            print("error")


    # parse commands
    positions = []
    for player in players:
        positions.append([player.name, player.pos]) # list of names and positions

    # send new data to players
            #sending new positions and directions
    for player in players:
        try:
            player.sock.send(pickle.dumps(positions))
            player.errors = 0
        except:
            if player.errors >= 10:
                player.remove_from_game()

    # time.sleep(50)

main_socket.close()