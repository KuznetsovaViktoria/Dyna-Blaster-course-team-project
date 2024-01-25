import socket
import pygame


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('', 1092))

while True:
    sock.send("Some command".encode())

    data = sock.recv(2**20)
    data = data.decode()

    print(data)