import socket
import pygame

def main():
    screen = pygame.display.set_mode((W, H))
    screen.fill((0, 0, 0))


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
HOST = "127.0.0.1"  # localhost
PORT = 1092 # any above 1023
sock.connect((HOST, PORT))

pygame.init()
W, H = 32 * 13 + 120, 32 * 13 + 120
clock = pygame.time.Clock()

while True:
    #sock.send("Some command".encode())

    data = sock.recv(2**20).decode()
    #data = data.decode()
    print(data)
    if data == "start":
        do = True
        break


while do:
    main()
pygame.quit()