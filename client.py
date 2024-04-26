import pygame
import socket
from pickle import loads, dumps
from time import time, sleep
from math import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
HOST = '127.0.0.1'  # localhost
# HOST = '192.168.1.72'
PORT = 1093 # any above 1023

pygame.init()

TILE = 50
WIDTH = 650
POINTS_HEIGHT = 4 * TILE
HEIGHT = WIDTH + POINTS_HEIGHT
new_tile = 50
new_width = 650
new_points_height = POINTS_HEIGHT
new_height = HEIGHT
old_tile = 50
old_width = 650
old_points_height = POINTS_HEIGHT
old_height = HEIGHT
FPS = 8
GAME_STARTED = False
time_started = 0
fontUISize = 35
endgameFontUISize = 50
timeFontUISize = 100

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

fontUI = pygame.font.Font(None, fontUISize)
endgameFontUI = pygame.font.Font(None, endgameFontUISize)
timeFontUI = pygame.font.Font(None, timeFontUISize)


def resize_all_images():
    global imgBackground, imgBangs, imgBlockCantBroke, imgBomb, imgBrick, imgGrass, imgTanks
    imgBrick = pygame.transform.scale(pygame.image.load('images/block_brick.png'), (new_tile, new_tile))
    imgBackground = pygame.transform.scale(pygame.image.load('images/background.png'), (new_width, new_height))
    imgBlockCantBroke = pygame.transform.scale(pygame.image.load('images/blockcantbroke.png'), (new_tile, new_tile))
    imgGrass = pygame.transform.scale(pygame.image.load('images/grass.png'), (new_tile, new_tile))
    imgBomb = pygame.transform.scale(pygame.image.load('images/bomb.png'), (new_tile, new_tile))
    imgTanks = {
        'red': pygame.transform.scale(pygame.image.load('images/bird_red.png'), (new_tile, new_tile)),
        'blue': pygame.transform.scale(pygame.image.load('images/bird_blue.png'), (new_tile, new_tile)),
        'black': pygame.transform.scale(pygame.image.load('images/bird_black.png'), (new_tile, new_tile)),
        'yellow': pygame.transform.scale(pygame.image.load('images/bird_yellow.png'), (new_tile, new_tile)),
        'gray': pygame.transform.scale(pygame.image.load('images/bird_gray.png'), (new_tile, new_tile)),
        'orange': pygame.transform.scale(pygame.image.load('images/bird_orange.png'), (new_tile, new_tile)),
        'pink': pygame.transform.scale(pygame.image.load('images/bird_pink.png'), (new_tile, new_tile)),
        'white': pygame.transform.scale(pygame.image.load('images/bird_white.png'), (new_tile, new_tile)),
    }
    imgBangs = [
        pygame.transform.scale(pygame.image.load('images/bang1.png'), (new_tile, new_tile)),
        pygame.transform.scale(pygame.image.load('images/bang2.png'), (new_tile, new_tile)),
        pygame.transform.scale(pygame.image.load('images/bang3.png'), (new_tile, new_tile)),
    ]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]
BLOCKS_LAYOUT = []
BLOCKS_CANT_BROKE_LAYOUT = []
resize_all_images()


def make_grid():
    for (x, y) in BLOCKS_LAYOUT:
        Block(x, y)
    for (x, y) in BLOCKS_CANT_BROKE_LAYOUT:
        BlockCantBroke(x, y)

class Menu:
    def __init__(self):
        self.menuOptions = []
        self.callbacks = []
        self.currentOptionInd = 1

    def append_option(self, option, callback, color='purple'):

        self.menuOptions.append(fontUI.render(option, 1, color))
        self.callbacks.append(callback)

    def switch(self, direction):
        self.currentOptionInd = max(1, min(self.currentOptionInd + direction, len(self.menuOptions) - 1))
    def select(self):
        self.callbacks[self.currentOptionInd]()

    def draw(self, surface, deltaY):
        for i, option in enumerate(self.menuOptions):
            option_rect = option.get_rect(center=(new_width // 2, new_height // 2 + i * deltaY - 75))
            if i == self.currentOptionInd:
                pygame.draw.rect(surface, 'white', option_rect)
            surface.blit(option, option_rect)

class UI:
    def __init__(self):
        self.seconds = 180
        pass

    def update(self):
        pass

    def draw(self):
        global GAME_FINISHED
        i = 0
        tanksAlive = []
        tanks = []
        for obj in objects:
            if obj.type == 'tank':
                tanks.append(obj)
                if obj.hp > 0:
                    tanksAlive.append(obj)

        seconds = max(0, 180 - int(time() - time_started))


        if len(tanksAlive) <= 1 or seconds <= 0:
            possible_winners = tanks if len(tanksAlive) == 0 else tanksAlive
            GAME_FINISHED = True
            window.blit(imgBackground, (0, 0))
            winnerPoints = max(possible_winners, key=lambda tank: tank.points).points
            winners = [tank.color for tank in possible_winners if tank.points == winnerPoints]
            color = 'purple' if len(winners) > 1 else winners[0]
            winnersText = 'Draw!' if len(winners) > 1 else f'{winners[0]} wins'
            gameOverText = endgameFontUI.render(f'Game over', 1, color)
            gameOverRect = gameOverText.get_rect(bottom=new_height // 2, centerx=new_width // 2)
            winnerText = endgameFontUI.render(winnersText, 1, color)
            winnerRect = winnerText.get_rect(top=new_height // 2, centerx=new_width // 2)
            window.blit(gameOverText, gameOverRect)
            window.blit(winnerText, winnerRect)
        else:
            self.seconds = seconds
        pygame.draw.rect(window, 'green', (0, 0, new_width, new_points_height))
        for obj in objects:
            if obj.type == 'tank':
                text = fontUI.render(f'health: {obj.hp} - points: {obj.points}', 1, obj.color)
                if i == 0:
                    rect = text.get_rect(left=8, centery=new_tile // 2 + 0 * new_tile)
                elif i == 1:
                    rect = text.get_rect(right=new_width - 8, centery=new_tile // 2 + 0 * new_tile)
                elif i == 2:
                    rect = text.get_rect(left=8, centery=new_tile // 2 + 1 * new_tile)
                elif i == 3:
                    rect = text.get_rect(right=new_width - 8, centery=new_tile // 2 + 1 * new_tile)
                elif i == 4:
                    rect = text.get_rect(left=8, centery=new_tile // 2 + 2 * new_tile)
                elif i == 5:
                    rect = text.get_rect(right=new_width - 8, centery=new_tile // 2 + 2 * new_tile)
                elif i == 6:
                    rect = text.get_rect(left=8, centery=new_tile // 2 + 3 * new_tile)
                elif i == 7:
                    rect = text.get_rect(right=new_width - 8, centery=new_tile // 2 + 3 * new_tile)
                else:
                    rect = text.get_rect()

                window.blit(text, rect)
                i += 1
        timerText = fontUI.render(f'{self.seconds // 60}:{(self.seconds % 60):02d}', 1, 'black')
        timerRect = timerText.get_rect(centerx=new_width // 2, centery=new_tile // 2)
        window.blit(timerText, timerRect)


class MyTank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'
        self.server_name = ''

        self.color = color
        px = min(new_width - new_tile, max(0, floor(px * new_width / WIDTH / new_tile) * new_tile))
        py = min(new_height - new_tile, max(new_points_height, floor(py * new_height / HEIGHT / new_tile) * new_tile))
        self.rect = pygame.Rect(px, py, new_tile, new_tile)
        self.direct = direct
        self.moveSpeed = new_tile
        self.hp = 1

        self.shotTimer = 0
        self.shotDelay = 15

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        self.image = imgTanks[self.color]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.points = 0
        self.bombs_to_send = []

    def update(self):
        if RESIZE_FLAG:
            self.rect.width = new_tile
            self.rect.height = new_tile
            self.moveSpeed = new_tile
            self.rect.left = floor(self.rect.left * new_width / old_width / new_tile) * new_tile
            self.rect.top = floor(self.rect.top * new_height / old_height  / new_tile) * new_tile
            self.image = imgTanks[self.color]
            self.rect = self.image.get_rect(center=self.rect.center)
        if self.hp <= 0:
            return

        self.rect = self.image.get_rect(center=self.rect.center)

        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT]:
            self.rect.x = max(0, self.rect.x - self.moveSpeed)
            self.direct = 0
        elif keys[self.keyRIGHT]:
            self.rect.x = min(new_width - new_tile, self.rect.x + self.moveSpeed)
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y = max(new_points_height, self.rect.y - self.moveSpeed)
        elif keys[self.keyDOWN]:
            self.rect.y = min(new_height - new_tile, self.rect.y + self.moveSpeed)

        for obj in objects:
            if obj != self and obj.type in ['block', 'block_cant_broke', 'tank', 'bomb'] and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            Bomb(self, self.rect.centerx, self.rect.centery)
            self.shotTimer = self.shotDelay
            self.bombs_to_send.append([floor(self.rect.x * WIDTH / new_width) + TILE//2, floor(self.rect.y * HEIGHT / new_height) + TILE//2])

        if self.shotTimer > 0:
            self.shotTimer -= 1

    def draw(self):
        if self.hp > 0:
            window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            print(self.color, 'dead')

    def get_data(self):
        return [['name', self.server_name], ['pos' , [floor(self.rect.x * WIDTH / new_width), floor(self.rect.y * HEIGHT / new_height)]], ['hp', self.hp], ['bombs', self.bombs_to_send]]

class EnemyTank:
    def __init__(self, server_name, pos, color, direct):
        self.server_name = server_name
        objects.append(self)
        self.type = 'tank'
        # self.px = floor(pos[0] * new_width / WIDTH / new_tile) * new_tile
        # self.py = floor(pos[1] * new_height / HEIGHT / new_tile) * new_tile
        px = min(new_width, max(0, floor(pos[0] * new_width / WIDTH / new_tile) * new_tile))
        py = min(new_height - new_tile, max(new_points_height, floor(pos[1] * new_height / HEIGHT / new_tile) * new_tile))
        self.color = color
        self.rect = pygame.Rect(px, py, new_tile, new_tile)
        self.hp = 1

        self.image = imgTanks[self.color]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.points = 0

    def update_position(self, pos): #[x, y]
        self.rect.width = new_tile
        self.rect.height = new_tile
        if self.hp <= 0:
            return

        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.x = floor(pos[0] * new_width / WIDTH / new_tile) * new_tile
        self.rect.y = floor(pos[1] * new_height / HEIGHT / new_tile) * new_tile
        self.image = imgTanks[self.color]
        self.rect = self.image.get_rect(center=self.rect.center)


    def update(self):
        pass

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            print(self.color, 'dead')
    
    def draw(self):
        if self.hp > 0:
            window.blit(self.image, self.rect)


class Bomb:
    def __init__(self, parent, px, py, length=1):
        bombs.append(self)
        self.px, self.py = px, py
        self.length = length
        self.damage = 1
        self.timer = FPS
        self.parent = parent

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            bombs.remove(self)
            Bang(self.px, self.py, self.parent)
            Bang(self.px + new_tile, self.py, self.parent)
            Bang(self.px - new_tile, self.py, self.parent)
            Bang(self.px, self.py + new_tile, self.parent)
            Bang(self.px, self.py - new_tile, self.parent)

    def draw(self):
        image = imgBomb
        rect = image.get_rect(center=(self.px, self.py))
        window.blit(image, rect)


class Bang:
    def __init__(self, px, py, parent):
        objects.append(self)
        self.type = 'bang'

        self.parent = parent
        self.damage = 1
        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.6
        if self.frame >= 3:
            objects.remove(self)
            return
        for obj in objects:
            if obj.type != 'bang' and obj.hp > 0 and obj.rect.collidepoint(self.px, self.py):
                if obj.type == 'block':
                    self.parent.points += 1
                if obj.type == 'tank':
                    if obj == self.parent:
                        self.parent.points -= 5
                    else:
                        self.parent.points += 20
                obj.damage(self.damage)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center=(self.px, self.py))
        window.blit(image, rect)

class Block:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'block'
        px = floor(px * new_width / old_width / new_tile) * new_tile
        py = floor(py  * new_height / old_height / new_tile) * new_tile
        self.rect = pygame.Rect(px, py, new_tile, new_tile)
        self.hp = 1

    def update(self):
        if RESIZE_FLAG:
            self.rect.x = floor(self.rect.x * new_width / old_width / new_tile) * new_tile
            self.rect.y = floor(self.rect.y  * new_height / old_height / new_tile) * new_tile
            self.rect.width = new_tile
            self.rect.height = new_tile

    def draw(self):
        window.blit(imgBrick, self.rect)
        
    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)

    def get_data(self):
        return ['block']


class BlockCantBroke:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'block_cant_broke'
        px = floor(px * new_width / old_width / new_tile) * new_tile
        py = floor(py  * new_height / old_height / new_tile) * new_tile
        self.rect = pygame.Rect(px, py, new_tile, new_tile)
        self.hp = 1

    def update(self):
        if RESIZE_FLAG:
            self.rect.x = floor(self.rect.x * new_width / old_width / new_tile) * new_tile
            self.rect.y = floor(self.rect.y  * new_height / old_height / new_tile) * new_tile
            self.rect.width = new_tile
            self.rect.height = new_tile

    def draw(self):
        window.blit(imgBlockCantBroke, self.rect)

    def damage(self, value):
        pass

    def get_data(self):
        return ['block_cant_broke']


def game_play_pressed():
    global GAME_STARTED, all_players_names, BLOCKS_LAYOUT, BLOCKS_CANT_BROKE_LAYOUT, my_tank, enemies, objects, sock, time_started
    sock.connect((HOST, PORT))
    name, color, pos = 0, 0, 0
    enemies_colors, enemies_positions = [], []
    while True:
        data = loads(sock.recv(1024 * 8))
        sock.settimeout(0.5)
        if len(data) > 0 and len(data[0]) > 0 and data[0][1] == 'start':
            for t in range(3):
                window.blit(imgBackground, (0, 0))
                timeText = timeFontUI.render(f'{3 - t}', 1, 'purple')
                timeRect = timeText.get_rect(centerx=new_width//2, centery=new_height//2)
                window.blit(timeText, timeRect)
                pygame.display.update()
                sleep(1)

            GAME_STARTED = True
            for [key, value] in data[1:]:
                if key == 'all_players_names':
                    all_players_names = value
                elif key == 'field_layout':
                    [BLOCKS_LAYOUT, BLOCKS_CANT_BROKE_LAYOUT] = value
                elif key == 'your_name':
                    name = value
                elif key == 'your_color':
                    color = value
                elif key == 'your_position':
                    pos = value
                elif key == 'all_players_colors':
                    enemies_colors = value
                elif key == 'all_players_positions':
                    enemies_positions = value
            break
    my_tank = MyTank(color, pos[0], pos[1], 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE))
    my_tank.server_name = name
    for i in range (len(all_players_names)):
        name = all_players_names[i]
        if name == my_tank.server_name:
            continue
        enemies[name] = EnemyTank(name, enemies_positions[i], enemies_colors[i], 0)
    make_grid()
    time_started = time()


menu = Menu()
menu.append_option('Welcome to the best game ever!', lambda: print('Welcome'), 'brown')
menu.append_option('Play', lambda: game_play_pressed())
menu.append_option('Quit', lambda: pygame.quit())

bombs = []
objects = []
ui = UI()

play = True
all_players_names = []
enemies = {}
errors = 0
clock = pygame.time.Clock()
GAME_FINISHED = False
RESIZE_FLAG = False

while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
        if event.type == pygame.VIDEORESIZE:
            old_height = new_height
            old_width = new_width
            old_tile = new_tile
            old_points_height = new_points_height
            new_width = event.w - event.w % 13
            new_tile = new_width // 13
            new_points_height = 4 * new_tile
            new_height = new_width + new_points_height
            fontUISize = fontUISize * new_width // old_width
            endgameFontUISize = endgameFontUISize * new_width // old_width
            timeFontUISize = timeFontUISize * new_width // old_width
            fontUI = pygame.font.Font(None, fontUISize)
            endgameFontUI = pygame.font.Font(None, endgameFontUISize)
            timeFontUI = pygame.font.Font(None, timeFontUISize)
            window = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            RESIZE_FLAG = True
            resize_all_images()
        elif not GAME_STARTED and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                menu.switch(-1)
            elif event.key == pygame.K_DOWN:
                menu.switch(1)
            elif event.key == pygame.K_RETURN:
                menu.select()
        if not GAME_STARTED and not GAME_FINISHED:
            window.blit(imgBackground, (0, 0))
            menu.draw(window, 100)
    keys = pygame.key.get_pressed()
    if GAME_STARTED and not GAME_FINISHED:
        for bomb in bombs:
            bomb.update()
        for obj in objects:
            obj.update()
        ui.update()
        data = []
        try:
            sock.send(dumps(my_tank.get_data()))
            my_tank.bombs_to_send.clear()
            errors = 0
        except:
            errors +=1
        try:
            data = loads(sock.recv(4096 * 4))
            errors = 0
            if len(data) > 0 and len(data[0]) > 1:
                for i in range(len(data[0][1])): 
                    if data[0][1][i] == my_tank.server_name:
                        continue
                    enemies[data[0][1][i]].update_position(data[1][1][i]) #[x, y]
                    for j in data[3][1][i]:
                        Bomb(enemies[data[0][1][i]], floor(j[0] * new_width / WIDTH / (new_tile // 2)) * (new_tile // 2), floor(j[1] * new_height / HEIGHT / (new_tile // 2)) * (new_tile // 2))
                if data[-1][0] == "removed_players" and len(data[-1][1]) > 0:
                    for p in data[-1][1]:
                        if p in enemies.keys():
                            enemies[p].hp = 0

        except:
            errors +=1
        for tileX in range(0, new_width, new_tile):
            for tileY in range(new_points_height, new_height, new_tile):
                window.blit(imgGrass, (tileX, tileY))
        for bomb in bombs:
            bomb.draw()
        for obj in objects:
            obj.draw()
        ui.draw()
        clock.tick(FPS)

    pygame.display.update()
    RESIZE_FLAG = False
    if errors >= 1000:
        play = False


pygame.quit()
sock.close()