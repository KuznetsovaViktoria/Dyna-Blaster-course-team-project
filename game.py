import pygame
from random import randint
import socket
from pickle import loads, dumps

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32
GAME_STARTED = False

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('images/block_brick.png')
imgTanks = {
    "red": pygame.transform.scale(pygame.image.load('images/player_red.png'), (27, 27)),
    "blue": pygame.transform.scale(pygame.image.load('images/player_blue.png'), (27, 27)),
}
imgBangs = [
    pygame.image.load('images/bang1.png'),
    pygame.image.load('images/bang2.png'),
    pygame.image.load('images/bang3.png'),
]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]
BLOCKS = [(544, 512), (192, 480), (96, 448), (352, 320), (64, 256), (448, 320), (224, 288), (608, 416), (736, 96),
          (224, 352), (448, 544), (736, 320), (384, 160), (288, 448), (32, 544), (544, 128), (320, 256), (320, 32),
          (64, 96), (128, 64), (480, 128), (704, 448), (64, 416), (192, 288), (160, 448), (128, 448), (0, 256),
          (0, 320), (288, 480), (0, 544), (768, 416), (384, 384), (416, 512), (0, 64), (480, 512), (640, 448),
          (96, 64), (64, 64), (736, 224), (672, 224), (352, 416), (608, 448), (544, 32), (384, 128), (0, 480),
          (288, 416), (192, 416), (608, 384), (448, 288), (512, 512), (736, 448), (160, 192), (704, 512), (160, 64),
          (736, 512), (512, 320), (320, 96), (288, 544), (160, 416), (384, 32), (0, 192), (736, 160), (288, 160),
          (512, 224), (352, 256), (320, 352), (32, 288), (224, 480), (192, 224), (128, 320), (608, 288), (64, 512),
          (352, 384), (448, 512), (224, 544), (608, 320), (608, 128), (96, 32), (480, 288), (224, 384)]


def make_grid():
    for (x, y) in BLOCKS:
        Block(x, y, TILE)

class Menu:
    def __init__(self):
        self.menuOptions = []
        self.callbacks = []
        self.currentOptionInd = 1

    def append_option(self, option, callback, color = 'purple'):

        self.menuOptions.append(fontUI.render(option, 1, color))
        self.callbacks.append(callback)

    def switch(self, direction):
        self.currentOptionInd = max(1, min(self.currentOptionInd + direction, len(self.menuOptions) - 1))
        # self.currentOptionInd = min(max(0, self.currentOptionInd + direction), len(self.menuOptions) - 1)
    def select(self):
        self.callbacks[self.currentOptionInd]()

    def draw(self, surface, x, y, deltaY):
        for i, option in enumerate(self.menuOptions):
            option_rect = option.get_rect(topleft=(x, y + i * deltaY))
            if i == self.currentOptionInd:
                pygame.draw.rect(surface, 'white', option_rect)
            else:
                pygame.draw.rect(surface, 'black', option_rect)
            surface.blit(option, option_rect)

class UI:
    def __init__(self):
        self.seconds = 180
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        tanksAlive = []
        for obj in objects:
            if obj.type == 'tank':
                if obj.hp > 0:
                    tanksAlive.append(obj)

                text = fontUI.render(f'health: {obj.hp} - points: {obj.points}', 1, obj.color)
                if i == 0:
                    rect = text.get_rect(left=8, top=6)
                elif i == 1:
                    rect = text.get_rect(right=WIDTH - 8, top=6)
                else:
                    rect = text.get_rect()

                pygame.draw.rect(window, 'white', (rect.left - 4, rect.top - 3, 8 + rect.width, 6 + rect.height))
                # rect = text.get_rect(center=(250 + i * 300 + 32, 5 + 11))

                window.blit(text, rect)
                i += 1

        seconds = max(0, 180 - pygame.time.get_ticks() // 1000)

        if len(tanksAlive) == 1 or seconds <= 0:
            winnerPoints = max(tanksAlive, key=lambda tank: tank.points).points
            winners = [tank.color for tank in tanksAlive if tank.points == winnerPoints]
            color = "purple" if len(winners) > 1 else winners[0]
            winnersText = "Draw!" if len(winners) > 1 else f'{winners[0]} wins'
            # pygame.draw.rect(window, 'brown', (200, 200, 300, 200))
            gameOverText = fontUI.render(f'Game over', 1, color)
            gameOverRect = gameOverText.get_rect(bottom=HEIGHT // 2, centerx=WIDTH // 2)
            winnerText = fontUI.render(winnersText, 1, color)
            winnerRect = winnerText.get_rect(top=HEIGHT // 2, centerx=WIDTH // 2)
            pygame.draw.rect(window, 'white', (min(gameOverRect.left, winnerRect.left) - 4, min(gameOverRect.top, winnerRect.top) - 3, 8 + max(gameOverRect.width, winnerRect.width), 6 + gameOverRect.height + winnerRect.height))
            window.blit(gameOverText, gameOverRect)
            window.blit(winnerText, winnerRect)
        else:
            self.seconds = seconds
        timerText = fontUI.render(f'{self.seconds // 60}:{(self.seconds % 60):02d}', 1, "white")
        timerRect = timerText.get_rect(centerx=WIDTH // 2, top=6)
        window.blit(timerText, timerRect)

class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'

        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.moveSpeed = 2
        self.hp = 5

        self.shotTimer = 0
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        # self.image = pygame.transform.rotate(imgTanks[self.color], -self.direct * 90)
        self.image = imgTanks[self.color]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.points = 0

    def update(self):
        if self.hp <= 0:
            return

        # self.image = pygame.transform.rotate(imgTanks[self.color], -self.direct * 90)
        # self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center=self.rect.center)

        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT]:
            self.rect.x = max(0, self.rect.x - self.moveSpeed)
            self.direct = 0
        elif keys[self.keyRIGHT]:
            self.rect.x = min(WIDTH - TILE, self.rect.x + self.moveSpeed)
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y = max(0, self.rect.y - self.moveSpeed)
        elif keys[self.keyDOWN]:
            self.rect.y = min(HEIGHT - TILE, self.rect.y + self.moveSpeed)

        for obj in objects:
            if obj != self and obj.type == 'block' and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            Bomb(self, self.rect.centerx, self.rect.centery)
            self.shotTimer = self.shotDelay

        if self.shotTimer > 0:
            self.shotTimer -= 1

    def draw(self):
        if self.hp > 0:
            window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            # objects.remove(self)
            print(self.color, 'dead')


class EnemyTank:
    def __init__(self, server_name):
        self.server_name = server_name
        self.px = 0
        self.py = 0
        self.direct = 0

    def update(self):
        pass

    def draw(self):
        pass


class Bomb:
    def __init__(self, parent, px, py, length=1):
        bombs.append(self)
        self.px, self.py = px, py
        self.length = length
        self.damage = 1
        self.timer = 3 * FPS
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
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 6)


class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
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
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)

def play1():
    print(keys[pygame.K_UP])
    # global GAME_STARTED
    # GAME_STARTED = True

    # keys = pygame.key.get_pressed()

    for bomb in bombs:
        bomb.update()
    for obj in objects:
        obj.update()
    ui.update()

    window.fill('black')
    for bomb in bombs:
        bomb.draw()
    for obj in objects:
        obj.draw()
    ui.draw()

    # pygame.display.update()
    # clock.tick(FPS)

def f():
    global GAME_STARTED
    GAME_STARTED = True

menu = Menu()
menu.append_option('Welcome to best game ever!', lambda: print('Welcome'), 'orange')
menu.append_option('Quit', lambda: pygame.quit())
menu.append_option('Play', lambda: f())

bombs = []
objects = []
Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_0))
ui = UI()
make_grid()

# blocks = []
# for _ in range(80):
#     while True:
#         x = randint(0, WIDTH // TILE - 1) * TILE
#         y = randint(1, HEIGHT // TILE - 1) * TILE
#         rect = pygame.Rect(x, y, TILE, TILE)
#         ok = True
#         for obj in objects:
#             if rect.colliderect(obj.rect):
#                 ok = False
#         if ok:
#             break
#     Block(x, y, TILE)
#     blocks.append((x, y))
# print(blocks)

play = True
while play:
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         play = False
    #     elif event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_UP:
    #             menu.switch(-1)
    #         elif event.key == pygame.K_DOWN:
    #             menu.switch(1)
    #         elif event.key == pygame.K_SPACE:
    #             menu.select()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
        elif not GAME_STARTED and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                menu.switch(-1)
            elif event.key == pygame.K_DOWN:
                menu.switch(1)
            elif event.key == pygame.K_RETURN:
                menu.select()
        if not GAME_STARTED:
            menu.draw(window, 100, 100, 75)
    keys = pygame.key.get_pressed()
    print(keys[pygame.K_UP])
    if GAME_STARTED:
        play1()
    # keys = pygame.key.get_pressed()

    # for bomb in bombs:
    #     bomb.update()
    # for obj in objects:
    #     obj.update()
    # ui.update()
    #
    # window.fill('black')
    # for bomb in bombs:
    #     bomb.draw()
    # for obj in objects:
    #     obj.draw()
    # ui.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
