import pygame
from bot_example import get_bot_move, set_first_params
import socket
from pickle import loads, dumps
from time import time, sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
HOST = '127.0.0.1'  # localhost
PORT = 1093 # any above 1023

pygame.init()

TILE = 50
WIDTH = 650
HEIGHT = WIDTH + TILE
FPS = 8
GAME_STARTED = False
time_started = 0

window = pygame.display.set_mode((WIDTH, HEIGHT))

fontUI = pygame.font.Font(None, 35)
endgameFontUI = pygame.font.Font(None, 50)
timeFontUI = pygame.font.Font(None, 100)

imgBrick = pygame.transform.scale(pygame.image.load('images/block_brick.png'), (TILE, TILE))
imgBackground = pygame.transform.scale(pygame.image.load('images/background.png'), (WIDTH, HEIGHT))
imgBlockCantBroke = pygame.transform.scale(pygame.image.load('images/blockcantbroke.png'), (TILE, TILE))
imgGrass = pygame.transform.scale(pygame.image.load('images/grass.png'), (TILE, TILE))
imgBomb = pygame.transform.scale(pygame.image.load('images/bomb.png'), (TILE, TILE))
imgTanks = {
    'red': pygame.transform.scale(pygame.image.load('images/player_red.png'), (TILE * 8 // 10, TILE * 8 // 10)),
    'blue': pygame.transform.scale(pygame.image.load('images/player_blue.png'), (TILE * 8 // 10, TILE * 8 // 10)),
}
imgBangs = [
    pygame.transform.scale(pygame.image.load('images/bang1.png'), (TILE, TILE)),
    pygame.transform.scale(pygame.image.load('images/bang2.png'), (TILE, TILE)),
    pygame.transform.scale(pygame.image.load('images/bang3.png'), (TILE, TILE)),
]


DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]
BLOCKS_LAYOUT = []
BLOCKS_CANT_BROKE_LAYOUT = []


def make_grid():
    for (x, y) in BLOCKS_LAYOUT:
        Block(x, y, TILE)
    for (x, y) in BLOCKS_CANT_BROKE_LAYOUT:
        BlockCantBroke(x, y, TILE)

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
            option_rect = option.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * deltaY - 75))
            if i == self.currentOptionInd:
                pygame.draw.rect(surface, 'white', option_rect)
            # else:
                # pygame.draw.rect(surface, 'black', option_rect)
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
        pygame.draw.rect(window, 'white', (0, 0, WIDTH, TILE))
        for obj in objects:
            if obj.type == 'tank':
                tanks.append(obj)
                if obj.hp > 0:
                    tanksAlive.append(obj)

                text = fontUI.render(f'health: {obj.hp} - points: {obj.points}', 1, obj.color)
                if i == 0:
                    rect = text.get_rect(left=8, centery=TILE // 2)
                elif i == 1:
                    rect = text.get_rect(right=WIDTH - 8, centery=TILE // 2)
                else:
                    rect = text.get_rect()

                window.blit(text, rect)
                i += 1

        seconds = max(0, 180 - int(time() - time_started))

        if len(tanksAlive) <= 1 or seconds <= 0:
            possible_winners = tanks if len(tanksAlive) == 0 else tanksAlive
            window.blit(imgBackground, (0, 0))
            winnerPoints = max(possible_winners, key=lambda tank: tank.points).points
            winners = [tank.color for tank in possible_winners if tank.points == winnerPoints]
            color = 'purple' if len(winners) > 1 else winners[0]
            winnersText = 'Draw!' if len(winners) > 1 else f'{winners[0]} wins'
            gameOverText = endgameFontUI.render(f'Game over', 1, color)
            gameOverRect = gameOverText.get_rect(bottom=HEIGHT // 2, centerx=WIDTH // 2)
            winnerText = endgameFontUI.render(winnersText, 1, color)
            winnerRect = winnerText.get_rect(top=HEIGHT // 2, centerx=WIDTH // 2)
            window.blit(gameOverText, gameOverRect)
            window.blit(winnerText, winnerRect)
        else:
            self.seconds = seconds
        timerText = fontUI.render(f'{self.seconds // 60}:{(self.seconds % 60):02d}', 1, 'black')
        timerRect = timerText.get_rect(centerx=WIDTH // 2, centery=TILE // 2)
        window.blit(timerText, timerRect)


class MyTank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'
        self.server_name = ''

        self.color = color
        self.rect = pygame.Rect(px, py, TILE - 5, TILE - 5)
        self.direct = direct
        self.moveSpeed = TILE
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

    def update(self, key_pressed = None):
        if self.hp <= 0:
            return

        self.rect = self.image.get_rect(center=self.rect.center)

        oldX, oldY = self.rect.topleft
        if key_pressed == self.keyLEFT:
            self.rect.x = max(0, self.rect.x - self.moveSpeed)
            self.direct = 0
        elif key_pressed == self.keyRIGHT:
            self.rect.x = min(WIDTH - TILE, self.rect.x + self.moveSpeed)
            self.direct = 1
        elif key_pressed == self.keyUP:
            self.rect.y = max(TILE, self.rect.y - self.moveSpeed)
        elif key_pressed == self.keyDOWN:
            self.rect.y = min(HEIGHT - TILE, self.rect.y + self.moveSpeed)

        for obj in objects:
            if obj != self and obj.type in ['block', 'block_cant_broke'] and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if key_pressed == self.keySHOT and self.shotTimer == 0:
            Bomb(self, self.rect.centerx, self.rect.centery)
            self.shotTimer = self.shotDelay
            self.bombs_to_send.append([self.rect.centerx, self.rect.centery])

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
        return [['name', self.server_name], ['pos' , [self.rect.x, self.rect.y]], ['hp', self.hp], ['bombs', self.bombs_to_send]]

class EnemyTank:
    def __init__(self, server_name, pos, color, direct):
        self.server_name = server_name
        objects.append(self)
        self.type = 'tank'
        self.px = pos[0]
        self.py = pos[1]
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], TILE, TILE)
        self.hp = 1

        self.image = imgTanks[self.color]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.points = 0

    def update_position(self, pos): #[x, y]
        if self.hp <= 0:
            return

        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self, key):
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
            Bang(self.px, self.py)
            Bang(self.px + TILE, self.py)
            Bang(self.px - TILE, self.py)
            Bang(self.px, self.py + TILE)
            Bang(self.px, self.py - TILE)
            for obj in objects:
                if obj.type != 'bang' and obj.hp > 0 and (obj.rect.collidepoint(self.px, self.py) or
                                           obj.rect.collidepoint(self.px + TILE, self.py) or
                                           obj.rect.collidepoint(self.px - TILE, self.py) or
                                           obj.rect.collidepoint(self.px, self.py + TILE) or
                                           obj.rect.collidepoint(self.px, self.py - TILE)):
                    if obj.type == 'block':
                        self.parent.points += 1
                    if obj.type == 'tank':
                        if obj == self.parent:
                            self.parent.points -= 5
                        else:
                            self.parent.points += 20
                    obj.damage(self.damage)

    def draw(self):
        image = imgBomb
        rect = image.get_rect(center=(self.px, self.py))
        window.blit(image, rect)


class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.6
        if self.frame >= 3:
            objects.remove(self)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center=(self.px, self.py))
        window.blit(image, rect)

class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)
        
    def damage(self, value):
        global BLOCKS_LAYOUT
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            if (self.rect.x, self.rect.y) in BLOCKS_LAYOUT:
                BLOCKS_LAYOUT.remove((self.rect.x, self.rect.y))

    def get_data(self):
        return ['block']


class BlockCantBroke:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block_cant_broke'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

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
        data = loads(sock.recv(1024))
        sock.settimeout(0.5)
        if len(data) > 0 and len(data[0]) > 0 and data[0][1] == 'start':
            for t in range(3):
                window.blit(imgBackground, (0, 0))
                timeText = timeFontUI.render(f'{3 - t}', 1, 'purple')
                timeRect = timeText.get_rect(centerx=WIDTH//2, centery=HEIGHT//2)
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
                    set_first_params(pos[0], pos[1], TILE, WIDTH)
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
menu.append_option('Waiting for player', lambda: print('Welcome'), 'brown')
menu.append_option('Play', lambda: game_play_pressed())
# menu.append_option('Quit', lambda: pygame.quit())

bombs = []
objects = []
ui = UI()

play = True
all_players_names = []
enemies = {}
errors = 0
clock = pygame.time.Clock()
GAME_FINISHED = False
start_game_pressed = False
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
            break
        elif not GAME_STARTED:
            # if event.key == pygame.K_UP:
            #     menu.switch(-1)
            # elif event.key == pygame.K_DOWN:
            #     menu.switch(1)
            # elif event.key == pygame.K_RETURN:
            #     menu.select()
            if not start_game_pressed:
                window.blit(imgBackground, (0, 0))
                menu.draw(window, 100)
                start_game_pressed = True
            else:
                menu.select()
        if not GAME_STARTED and not GAME_FINISHED:
            window.blit(imgBackground, (0, 0))
            menu.draw(window, 100)
    if not play:
        break 
    if GAME_STARTED and not GAME_FINISHED:
        bot_move = get_bot_move([my_tank.rect.x, my_tank.rect.y - TILE], [[e.rect.x, e.rect.y - TILE] for e in enemies.values()], [e.points for e in enemies.values()], [[b.px, b.py - TILE] for b in bombs],  [[x, y - TILE] for (x, y) in BLOCKS_LAYOUT], [[x, y - TILE] for (x, y) in BLOCKS_CANT_BROKE_LAYOUT])
        for bomb in bombs:
            bomb.update()
        for obj in objects:
            if obj.type == 'tank':
                obj.update(bot_move)
            else:
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
            data = loads(sock.recv(1024))
            errors = 0
            if len(data) > 0 and len(data[0]) > 1:
                for i in range(len(data[0][1])): 
                    if data[0][1][i] == my_tank.server_name:
                        continue
                    enemies[data[0][1][i]].update_position(data[1][1][i]) #[x, y]
                    for j in data[3][1][i]:
                        Bomb(enemies[data[0][1][i]], j[0], j[1])
                if data[-1][0] == "removed_players" and len(data[-1][1]) > 0:
                    for p in data[-1][1]:
                        if p in enemies.keys():
                            enemies[p].hp = 0

        except:
            errors +=1
        for tileX in range(0, WIDTH, TILE):
            for tileY in range(TILE, HEIGHT, TILE):
                window.blit(imgGrass, (tileX, tileY))
        for bomb in bombs:
            bomb.draw()
        for obj in objects:
            obj.draw()
        ui.draw()
        clock.tick(FPS)

    pygame.display.update()

    if errors >= 100:
        play = False


pygame.quit()
sock.close()