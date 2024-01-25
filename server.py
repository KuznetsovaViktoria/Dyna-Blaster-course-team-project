import socket
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('', 1092))
main_socket.setblocking(0)
main_socket.listen(2)

players_sockets = []
while True:
    # connect players
    try:
        new_socket, addr = main_socket.accept()
        print("Connected ", addr)
        new_socket.setblocking(0)
        players_sockets.append(new_socket)
    except:
        print("nothing")

    # read players' commands
    for sock in players_sockets:
        try:
            data = sock.recv(1024)
            data = data.decode()
            print("Server got ", data)
        except:
            pass

    # parse commands

    # send new data to players
    for sock in players_sockets:
        try:
            sock.send("New data".encode())
        except:
            players_sockets.remove(sock)
            sock.close()
            print("Player disconnected")

    time.sleep(50)