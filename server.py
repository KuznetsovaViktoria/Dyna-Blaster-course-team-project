import socket
import time

class Player:
    def __init__(self, sock):
        self.sock = sock
        self.errors = 0

def send_data_to_both_players(data):
    for player in players: # may have used sendall, but needed to count errors for each player
        try:
            player.sock.send(data.encode())
            player.errors = 0
        except:
            if player.errors >= 10:
                players.remove(player.sock)
                player.sock.close()
                print("Player disconnected")
                if players.empty():
                    end_game("all players disconnected")

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
while True:
    try:  # connect players
        new_socket, addr = main_socket.accept()
        print("Connected ", addr)
        new_socket.setblocking(0)
        players.append(Player(new_socket))
        if len(players) == kExpectedPlayers:
            break
    except:
        pass
        # print("nothing")
    time.sleep(0.1)

#ready to start the game
send_data_to_both_players("start")


while True:
    # read players' commands
    for player in players:
        try:
            data = player.setblocking.recv(1024)
            data = data.decode()
            print("Server got ", data)
        except:
            pass
    # parse commands

    # send new data to players
    for player in players:
        try:
            player.sock.send("New data".encode())
        except:
            players.remove(player.sock)
            player.sock.close()
            print("Player disconnected")

    time.sleep(50)