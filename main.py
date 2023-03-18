import json
import os
from json import load, dump
from os import getcwd, path, chdir, remove
from random import choice
from shutil import copytree, rmtree, copyfile
from time import time
from tkinter import Tk, Label, Entry, Button as TkButton

import pygame
import pygame as pg

if getcwd() != path.dirname(path.realpath(__file__)):
    chdir(path.dirname(path.realpath(__file__)))


class Colors:
    Black = (0, 0, 0)
    White = (255, 255, 255)


BUTTONS = pg.sprite.Group()
TEXTBOXES = pg.sprite.Group()

pg.mixer.init()


class Button(pg.sprite.Sprite):
    def __init__(self, pos, scale, function, imagePath, clicked: bool = True):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load(imagePath + 'unclicked.png'), scale)
        self.clickedImage = pg.transform.smoothscale(
            pg.image.load(imagePath + 'clicked.png') if clicked else self.image,
            scale)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.funct = function

        self.clickSound = pg.mixer.Sound('assets\\audio\\buttonPress.mp3')

        self.pressed = False

    def press(self):
        self.pressed = True
        self.clickSound.play()
        self.image, self.clickedImage = self.clickedImage, self.image

    def unpress(self):
        self.pressed = False
        self.image, self.clickedImage = self.clickedImage, self.image
        self.funct()


class TextBox(pg.sprite.Sprite):
    def __init__(self, fontPath, pos, size, text='Null Value'):
        super().__init__()
        self.font = pg.font.Font(fontPath, size)
        self.image = self.font.render(text, True, Colors.White)
        self.rect = self.image.get_rect()
        self.rect.midtop = pos

    def updateText(self, text):
        self.image = self.font.render(text, True, Colors.White)
        self.tempRect = self.image.get_rect()
        self.tempRect.midtop = self.rect.midtop
        self.rect = self.tempRect


def game(world: str = 'maze', GRID: tuple = (20, 20)):
    snakeCollided = False

    GAMEDIR = f'assets\\worlds\\{world}\\'

    MAP = [l.strip('\n\r') for  l in open(GAMEDIR + 'MAP.txt', 'r').readlines()]

    textures = load(open(GAMEDIR + 'textures.json', 'r'))
    options = load(open(GAMEDIR + 'options.json', 'r'))

    gridWidth, gridHeight = GRID
    winWidth, winHeight = DIMS = (max(len(MAP[0]) * gridWidth, 400), max(len(MAP) * gridHeight, 400))

    pg.init()

    SCREEN = pg.display.set_mode((DIMS[0], DIMS[1] + 50))
    pg.display.set_caption('Snake')
    TIME = pg.time.Clock()
    SPEED = options['speed']

    COLOR = options['color']
    BUTTONS.empty()
    TEXTBOXES.empty()

    SNAKE = []
    PARTS = pg.sprite.Group()
    FOOD = pg.sprite.Group()
    WALLS = pg.sprite.Group()

    SCORE = 0
    newHigh = False
    scoreText = TextBox('assets\\fonts\\SuperLegendBoy.ttf', (winWidth // 2, winHeight + 20), 20, f'Score: {SCORE}')
    TEXTBOXES.add(scoreText)
    hiScore = TextBox('assets\\fonts\\SuperLegendBoy.ttf', (50, winHeight + 20), 20, f'HI: {options["highscore"]}')
    TEXTBOXES.add(hiScore)

    availPos = []

    class Position:
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def pos(self):
            return self.x, self.y

    class Part(pg.sprite.Sprite):

        def __init__(self, part, initpos: Position = Position()):
            super().__init__()

            self.spritesheet = {}

            for p in textures['snake']:
                self.spritesheet[p] = []
                for i in range(len(textures['snake'][p])):
                    img = pg.image.load(GAMEDIR + textures['snake'][p][i])
                    img = pg.transform.scale(img, GRID)
                    self.spritesheet[p].append(img)

            self.originalImage = choice(self.spritesheet[part])
            self.image = self.originalImage
            self.rect = self.image.get_rect()
            self.rect.topleft = initpos.pos()
            self.temprect = self.image.get_rect()
            self.temprect.topleft = initpos.pos()
            self.addPart = False
            self.collided = False

        def move(self):

            self.temprect.topleft, self.rect.topleft = self.rect.topleft, self.temprect.topleft

            if self.checkCollisions() and self == SNAKE[0]:
                pg.mixer.Sound('assets\\audio\\gameOver.mp3').play()
                nonlocal snakeCollided
                snakeCollided = True
                self.temprect.topleft, self.rect.topleft = self.rect.topleft, self.temprect.topleft
                SCREEN.blit(self.image, self.rect.topleft)

                return True
            self.temprect.topleft, self.rect.topleft = self.rect.topleft, self.temprect.topleft

            if SNAKE.index(self) + 1 < len(SNAKE):
                nextSnake = SNAKE[SNAKE.index(self) + 1]
                nextSnake.temprect.topleft = Position(self.rect.x, self.rect.y).pos()

            if self.addPart:
                addPart(Part('tail', Position(self.rect.x, self.rect.y)))
                self.originalImage = choice(self.spritesheet['body'])
                self.image = self.originalImage
                self.addPart = False

            self.image = pg.transform.rotate(self.originalImage, (
                0 if self.rect.x > self.temprect.x else -180)
                                             ) if self.rect.y == self.temprect.y else self.image

            self.image = pg.transform.rotate(self.originalImage, (
                -90 if self.rect.y > self.temprect.y else 90)
                                             ) if self.rect.x == self.temprect.x else self.image
            self.rect = self.image.get_rect(center=self.rect.center)
            availPos.append(self.rect.topleft)
            availPos.remove(self.temprect.topleft)
            if SNAKE.index(self) == len(SNAKE) - 1:
                SCREEN.fill(COLOR, self.rect)
                self.rect.topleft = self.temprect.topleft
                SCREEN.fill(COLOR, self.rect)
                SCREEN.blit(self.image, self.rect.topleft)
            else:
                self.rect.topleft = self.temprect.topleft
                SCREEN.blit(self.image, self.rect.topleft)

            return False

        def checkCollisions(self):
            for p in PARTS:
                if pg.sprite.collide_rect(self, p) and self != p:
                    return True
            if pg.sprite.spritecollideany(self, WALLS): return True
            return False

    class Food(pg.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pg.image.load(GAMEDIR + choice(textures['food']))
            self.image = pg.transform.scale(self.image, GRID)
            self.rect = self.image.get_rect()
            self.foodEaten = pg.mixer.Sound('assets\\audio\\foodEaten.mp3')

            self.reposition(False)

        def reposition(self, play=True):
            if play:
                self.foodEaten.stop()
                self.foodEaten.play()
            SCREEN.fill(COLOR, self.rect)
            self.rect.topleft = choice(availPos)
            SCREEN.blit(self.image, self.rect.topleft)

        def checkCollisions(self):
            if self.rect.colliderect(SNAKE[0].rect):
                nonlocal SCORE, scoreText, newHigh
                SCORE += 1

                if not newHigh and SCORE > options['highscore']:
                    newHigh = True
                self.reposition()
                scoreText.updateText(f'Score: {SCORE}')
                pg.draw.rect(SCREEN, Colors.Black, scoreText.rect)
                SCREEN.blit(scoreText.image, scoreText.rect)

                if newHigh:
                    hiScore.updateText(f'HI: {SCORE}')
                    pg.draw.rect(SCREEN, Colors.Black, hiScore.rect)
                    SCREEN.blit(hiScore.image, hiScore.rect)

                SNAKE[-1].addPart = True

    class Wall(pg.sprite.Sprite):
        def __init__(self, pos: tuple):
            super().__init__()
            self.image = pg.image.load(GAMEDIR + choice(textures['wall']))
            self.image = pg.transform.scale(self.image, GRID)
            self.rect = self.image.get_rect()

            self.rect.topleft = pos

    def addPart(part: Part = Part('body')):
        PARTS.add(part)
        SNAKE.append(part)

    for block in enumerate(''.join(MAP)):
        blockPos = gridWidth * (block[0] % len(MAP[0])), gridHeight * (
                block[0] // len(MAP[0])
        )
        if block[1] in '#':
            WALLS.add(Wall(blockPos))
        elif block[1] in '+':
            for i in range(4):
                addPart(Part(
                    'head' if i == 0 else ('tail' if i == 3 else 'body'),
                    Position(blockPos[0], blockPos[1])
                )
                )
        else:
            availPos.append(blockPos)
    FOOD.add(Food())
    FOOD.add(Food())

    BUTTONS.add(
        Button((winWidth - 37, winHeight + 12), (25, 25), (lambda: pg.mixer.music.fadeout(1000) or editor(world)),
               'assets\\buttons\\edit\\'))

    gameEnd = False
    direction = Position(1, 0)

    SCREEN.fill(COLOR)
    pg.draw.rect(SCREEN, Colors.Black, (0, winHeight, winWidth, winHeight + 50))
    BUTTONS.draw(SCREEN)
    WALLS.draw(SCREEN)
    TEXTBOXES.draw(SCREEN)
    FOOD.draw(SCREEN)

    timeSinceEnd = 0

    pg.mixer.music.load('assets\\audio\\game.mp3')
    pg.mixer.music.play(-1, 0, 5000)

    while not gameEnd:
        # Endgame
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    gameEnd = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        for b in BUTTONS:
                            if b.rect.collidepoint(pg.mouse.get_pos()):
                                b.press()
                if event.type == pg.MOUSEBUTTONUP:
                    for b in BUTTONS:
                        if b.pressed:
                            b.unpress()
                if event.type == pg.KEYDOWN:
                    if not direction.y:
                        if event.key == pg.K_DOWN:
                            direction = Position(0, 1)
                            break
                        elif event.key == pg.K_UP:
                            direction = Position(0, -1)
                            break
                    elif not direction.x:
                        if event.key == pg.K_LEFT:
                            direction = Position(-1, 0)
                            break
                        elif event.key == pg.K_RIGHT:
                            direction = Position(1, 0)
                            break
        except pygame.error:
            break

        if gameEnd: break

        if not snakeCollided:
            SNAKE[0].temprect.topleft = Position(SNAKE[0].rect.x + direction.x * gridWidth,
                                                 SNAKE[0].rect.y + direction.y * gridHeight).pos()
            if SNAKE[0].temprect.x < 0:
                SNAKE[0].temprect.x = gridWidth * (len(MAP[0]) - 1)
            if SNAKE[0].temprect.y < 0:
                SNAKE[0].temprect.y = gridHeight * (len(MAP) - 1)
            if SNAKE[0].temprect.x >= gridWidth * (len(MAP[0])):
                SNAKE[0].temprect.x = 0
            if SNAKE[0].temprect.y >= gridHeight * (len(MAP)):
                SNAKE[0].temprect.y = 0
            for f in FOOD:
                f.checkCollisions()
            for p in SNAKE:
                if p.move():
                    break
        else:
            if not timeSinceEnd:
                timeSinceEnd = time()
            if newHigh:
                options['highscore'] = SCORE
                with open(GAMEDIR + 'options.json', 'w') as opt:
                    dump(options, opt, indent=4)
                timeSinceEnd += 4
                newHigh = False
            if time() - timeSinceEnd >= 1:
                menu()

        pg.display.flip()
        TIME.tick(SPEED)
    pg.quit()


def editor(mapName: str = 'maze'):
    MAPDIR = f'assets\\worlds\\{mapName}\\'
    MAP = [l.strip('\n\r') for l in open(MAPDIR + 'map.txt', 'r').readlines()]

    textures = json.load(open(MAPDIR + 'textures.json', 'r'))
    options = json.load(open(MAPDIR + 'options.json', 'r'))

    legend = {
        'wall': '#',
        'snake': '+',
        'empty': '0'
    }
    GRID = gridWidth, gridHeight = 20, 20
    DIMS = winWidth, winHeight = max(gridWidth * len(MAP[0]), 580), max(gridHeight * len(MAP),
                                                                        580)

    pg.init()

    COLOR = options['color']
    SCREEN = pg.display.set_mode((winWidth + 100, winHeight))
    CLOCK = pg.time.Clock()
    BLOCKS = pg.sprite.Group()

    class MapBuilder:
        @staticmethod
        def saveMap():
            nonlocal editingDone
            open(MAPDIR + 'MAP.txt', 'w').write('\n'.join(MAP))
            editingDone = True
            pg.mixer.music.fadeout(1000)
            game(mapName)

        @staticmethod
        def setSnake(blockPos):
            blist = []
            for i in range(4):
                block = Block(
                    'head' if i == 0 else ('tail' if i == 3 else 'body'),
                    (blockPos[0] - i * gridWidth, blockPos[1])
                )
                blist.append(block)
                block.clearOthers()
            return blist

        @staticmethod
        def setBlock(name, blockPos):
            bl = Block(name, blockPos)
            for b in BLOCKS:
                if pg.sprite.collide_rect(bl, b) and b.name == 'snake':
                    bl.kill()
                    break
            else:
                return bl

        def draw(self, fill=None):
            BLOCKS.empty()
            for block in enumerate(''.join(MAP)):
                blockPos = gridWidth * (block[0] % len(MAP[0])), gridHeight * (
                        block[0] // len(MAP[0])
                )
                if block[1] in '#0':
                    BLOCKS.add(BUILDER.setBlock([k for k, v in legend.items() if v == block[1]][0], blockPos))
                elif block[1] in '+':
                    BLOCKS.add(BUILDER.setSnake(blockPos))
            if fill: SCREEN.fill(fill)
            BLOCKS.draw(SCREEN)
            self.UI()

        @staticmethod
        def UI():
            BUTTONS.empty()
            TEXTBOXES.empty()

            pg.draw.rect(SCREEN, Colors.Black, (winWidth, 0, winWidth + 100, winHeight))
            for i in range(len(legend.keys())):
                BUTTONS.add(
                    Button((winWidth + 25, 25 + i * 75), (50, 50),
                           (lambda x=list(legend.keys())[i]: MOUSE.updateImage(x)),
                           'assets\\buttons\\' + list(legend.keys())[i] + '\\'))
            BUTTONS.add(Button((winWidth + 25, winHeight - 75), (50, 50), (lambda: BUILDER.saveMap()),
                               'assets\\buttons\\done\\'))
            BUTTONS.add(Button((winWidth + 25, winHeight - 150), (50, 50), (lambda: BUILDER.clear()),
                               'assets\\buttons\\clear\\'))

            TEXTBOXES.add(TextBox('assets\\fonts\\SuperLegendBoy.ttf', (winWidth + 50, winHeight // 2), 20, 'Rows'))
            BUTTONS.add(Button((winWidth + 12, winHeight // 2 + 20), (25, 25), (lambda: BUILDER.removeRow()),
                               'assets\\buttons\\subtract\\', False))
            BUTTONS.add(Button((winWidth + 63, winHeight // 2 + 20), (25, 25), (lambda: BUILDER.addRow()),
                               'assets\\buttons\\add\\', False))

            TEXTBOXES.add(
                TextBox('assets\\fonts\\SuperLegendBoy.ttf', (winWidth + 50, winHeight // 2 + 70), 20, 'Cols.'))
            BUTTONS.add(Button((winWidth + 12, winHeight // 2 + 90), (25, 25), (lambda: BUILDER.removeColumn()),
                               'assets\\buttons\\subtract\\', False))
            BUTTONS.add(Button((winWidth + 63, winHeight // 2 + 90), (25, 25), (lambda: BUILDER.addColumn()),
                               'assets\\buttons\\add\\', False))

        def addColumn(self):
            nonlocal MAP, winWidth, SCREEN
            MAP = [row + '0' for row in MAP]
            winWidth += gridWidth if len(MAP[0]) * gridWidth >= winWidth + gridWidth else 0
            SCREEN = pg.display.set_mode((winWidth + 100, winHeight))
            self.draw(COLOR)

        def removeColumn(self):
            try:
                nonlocal MAP, winWidth, SCREEN
                if len(MAP[0]) <= 1: return
                MAP = [row[:-2] + legend['snake'] if row[-1] == legend['snake'] else row[:-1] for row in MAP]
                winWidth -= gridWidth if winWidth >= 580 else 0
                SCREEN = pg.display.set_mode((winWidth + 100, winHeight))
                self.draw(COLOR)
            except IndexError:
                pass

        def addRow(self):
            nonlocal MAP, winHeight, SCREEN
            MAP += ['0' * (len(MAP[0]) or 1)]
            winHeight += gridHeight if len(MAP) * gridHeight >= winHeight + gridHeight else 0
            SCREEN = pg.display.set_mode((winWidth + 100, winHeight))
            self.draw(COLOR)

        def removeRow(self):
            nonlocal MAP, winHeight, SCREEN
            if not len(MAP): return
            if legend['snake'] in MAP[-1]:
                index = MAP[-1].index(legend['snake'])
                MAP = MAP[:-2] + [
                    MAP[-2][:index] + legend['snake'] + MAP[-2][index + 1:]]
            else:
                MAP = MAP[:-1]
            winHeight -= gridHeight if winHeight > 600 else 0
            SCREEN = pg.display.set_mode((winWidth + 100, winHeight))
            self.draw(COLOR)

        def clear(self):
            nonlocal MAP
            MAP = [legend['snake'].join(['0' * len(bl) for bl in row.split(legend['snake'])]) if legend[
                                                                                                     'snake'] in row else '0' * len(
                row) for row in MAP]
            SCREEN.fill(COLOR)
            self.draw()

    BUILDER = MapBuilder()

    class Selector(pg.sprite.Sprite):
        def __init__(self, block: str = 'wall'):
            super().__init__()
            self.selectedBlock = block
            self.replacedBlock = None
            self.image = pg.transform.rotate(
                pg.transform.scale(
                    pg.image.load(
                        MAPDIR + choice(textures[self.selectedBlock] if
                                        self.selectedBlock != 'snake' else
                                        textures[self.selectedBlock]['head']
                                        )
                    ), GRID)
                , 180
            )
            self.rect = self.image.get_rect()
            self.active = False

        def updateImage(self, name):
            self.selectedBlock = name
            self.image = pg.transform.rotate(
                pg.transform.scale(
                    pg.image.load(
                        MAPDIR + choice(textures[self.selectedBlock] if
                                        self.selectedBlock != 'snake' else
                                        textures[self.selectedBlock]['head']
                                        )
                    ), GRID)
                , 180
            )

        def updatePos(self, pos):
            if self.replacedBlock:
                pg.draw.rect(SCREEN, COLOR, self.replacedBlock.rect)
                SCREEN.blit(self.replacedBlock.image, self.replacedBlock.rect)
            self.rect.topleft = pos
            self.replacedBlock = pg.sprite.spritecollide(self, BLOCKS, False)[0]
            pg.draw.rect(SCREEN, COLOR, self.rect)
            SCREEN.blit(self.image, self.rect)
            pg.display.flip()

        def updateMap(self):
            nonlocal MAP
            tempMap = [list(row) for row in MAP]
            if self.selectedBlock == 'snake':
                breaker = False
                for y in range(len(tempMap)):
                    for x in range(len(tempMap[y])):
                        if tempMap[y][x] in legend['snake']:
                            for i in range(4):
                                block = Block('empty', (gridWidth * (x - i), gridHeight * y))
                                pg.sprite.spritecollide(block, BLOCKS, False)[0].kill()
                                BLOCKS.add(block)
                                tempMap[y][x - i] = '0'
                                pg.draw.rect(SCREEN, COLOR, block.rect)
                                SCREEN.blit(block.image, block.rect)
                            breaker = True
                            break
                    if breaker:
                        break

            tempMap[self.rect.y // gridHeight][self.rect.x // gridWidth] = legend[self.selectedBlock]
            MAP = [''.join(l) for l in tempMap]
            if self.selectedBlock == 'snake':
                snake = BUILDER.setSnake(self.rect.topleft)
                for p in snake:
                    BLOCKS.add(p)
                    pg.draw.rect(SCREEN, COLOR, p.rect)
                    SCREEN.blit(p.image, p.rect)
            else:
                bl = BUILDER.setBlock(self.selectedBlock, self.rect.topleft)
                if not bl: return
                pg.sprite.spritecollide(bl, BLOCKS, False)[0].kill()
                BLOCKS.add(bl)
                pg.draw.rect(SCREEN, COLOR, bl.rect)
                SCREEN.blit(bl.image, bl.rect)

            self.updatePos(self.rect.topleft)

    class Block(pg.sprite.Sprite):
        def __init__(self, name, pos):
            super().__init__()
            self.name = name if name in legend else 'snake'
            self.image = pg.transform.rotate(pg.transform.scale(
                pg.image.load(MAPDIR + (textures[name][0] if name in legend else textures['snake'][name][0])), GRID),
                180)
            self.rect = self.image.get_rect()
            self.rect.topleft = pos

        def clearOthers(self):
            for block in BLOCKS:
                if pg.sprite.collide_rect(self, block) and block != self:
                    block.kill()

    MOUSE = Selector()

    BUILDER.draw(COLOR)
    BUILDER.UI()
    pg.display.flip()
    mousePos = (0, 0)
    editingDone = False

    pg.mixer.music.load('assets\\audio\\edit.mp3')
    pg.mixer.music.play(-1, 0, 5000)
    while not editingDone:
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    editingDone = True
                    break
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        if 0 < pg.mouse.get_pos()[0] < len(MAP[0]) * gridWidth and 0 < pg.mouse.get_pos()[
                            1] < len(MAP) * gridHeight:
                            MOUSE.active = True
                            MOUSE.updateMap()
                        else:
                            for b in BUTTONS:
                                if b.rect.collidepoint(pg.mouse.get_pos()):
                                    b.press()
                if event.type == pg.MOUSEBUTTONUP:
                    MOUSE.active = False
                    for b in BUTTONS:
                        if b.pressed:
                            b.unpress()
        except pygame.error:
            break

        if 0 < pg.mouse.get_pos()[0] < len(MAP[0]) * gridWidth and 0 < pg.mouse.get_pos()[1] < len(MAP) * gridHeight:
            newmousepos = (pg.mouse.get_pos()[0] // gridWidth) * gridWidth, (
                    pg.mouse.get_pos()[1] // gridHeight) * gridHeight
            if newmousepos != mousePos:
                mousePos = newmousepos
                MOUSE.updatePos(mousePos)
                if MOUSE.active:
                    MOUSE.updateMap()
        BUTTONS.draw(SCREEN)
        TEXTBOXES.draw(SCREEN)
        pg.display.flip()
        CLOCK.tick(24)


def menu():
    DIMS = winWidth, winHeight = 600, 600
    TEXTBOXES.empty()
    BUTTONS.empty()

    pg.init()

    SCREEN = pg.display.set_mode(DIMS)
    WORLDS = pg.sprite.Group()

    def newMap():

        def getWorldName():
            name = worldname.get()
            spd = speed.get()
            clr = color.get()

            def errorCheck():
                if not name.isalnum():
                    return 'name must include only \nletters and numbers'
                elif not spd.isnumeric():
                    return 'speed must be numeric'
                elif not ''.join([c for c in clr if c not in '[] ,']).isnumeric():
                    return 'color must be 3 integral values\nseparated by \',\' and syrrounded by \'[ ]\''
                else:
                    if not 0 < len(name) <= 10:
                        return 'name must be atleast 1 \nand atmost 10 characters long'
                    elif name in os.listdir('assets\\worlds'):
                        return 'world already exists'
                    elif not isinstance(eval(spd), int):
                        return 'speed must be an integer'
                    elif sum([i for i in eval(clr) if not (0 <= i <= 255)]):
                        return 'rgb values musn\'t exceed 255 or subceed 0'

                return None

            err = errorCheck()
            if err:
                nonlocal error
                error.configure(text=err)
                return

            copytree('assets\\worlds\\basic', f'assets\\worlds\\{name}')

            open(f'assets\\worlds\\{name}\\map.txt', 'w').write(
                (('0' * 21) + '\n') * 10 + ('0' * 10 + '+' + '0' * 10 + '\n') + (('0' * 21) + '\n') * 9 + ('0' * 21)
            )
            with open(f'assets\\worlds\\{name}\\options.json', 'r') as file:
                opts = load(file)
                opts['highscore'] = 0
                opts['color'] = eval(clr)
                opts['speed'] = int(spd)
            dump(opts, open(f'assets\\worlds\\{name}\\options.json', 'w'))

            remove(f'assets\\worlds\\{name}\\thumbnail.png')
            copyfile('assets\\defaultWorld.png', f'assets\\worlds\\{name}\\thumbnail.png')

            WORLDS.add(World(name, (25 + (len(WORLDS) % 2) * 300, 60 + (len(WORLDS) // 2) * 280 - scrolled)))

            addworld.rect.topleft = (25 + ((len(WORLDS)) % 2) * 300 + 100, 120 + ((len(WORLDS)) // 2) * 280 - scrolled)

            draw()

            window.destroy()

        window = Tk()
        window.geometry('300x170')
        window.title('NewName')
        window.configure(background='#212121')
        Label(text='Enter world name (only alphabets/numbers):', background='#212121', foreground='White',
              font=('Arial Bold', 10)).place(x=10, y=10)
        worldname = Entry(window, width=15, background='#383838', foreground='White', borderwidth=2)
        worldname.place(x=10, y=30)
        Label(text='Enter world speed (integer):', background='#212121', foreground='White',
              font=('Arial Bold', 10)).place(x=10, y=50)
        speed = Entry(window, width=15, background='#383838', foreground='White', borderwidth=2)
        speed.place(x=10, y=70)
        Label(text='Enter world color [r,g,b]:', background='#212121', foreground='White',
              font=('Arial Bold', 10)).place(x=10, y=90)
        color = Entry(window, width=15, background='#383838', foreground='White', borderwidth=2)
        color.place(x=10, y=110)
        error = Label(text='', font=('Arial Italic', 7), background='#212121', justify='left', foreground='Red')
        error.place(x=10, y=130)

        speed.insert(0, '15')
        worldname.insert(0, 'newWorld')
        color.insert(0, '[0, 0, 0]')

        TkButton(text='OK', borderwidth=3, background='#383838', foreground='White', activebackground='#383838',
                 activeforeground='White', command=lambda: getWorldName()).place(x=210, y=45, width=80, height=80)

        window.mainloop()

    class World(pg.sprite.Sprite):

        def __init__(self, worldName: str, pos):
            super().__init__()
            self.image = pg.transform.scale(pg.image.load(f'assets\\worlds\\{worldName}\\thumbnail.png'), (250, 175))
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.world = worldName
            self.editButton = Button((self.rect.x + self.rect.width // 10, self.rect.y + self.rect.height), (50, 50),
                                     lambda: self.edit(),
                                     'assets\\buttons\\edit\\')
            self.playButton = Button(
                (self.rect.x + self.rect.width - self.rect.width // 10 - 50, self.rect.y + self.rect.height), (50, 50),
                lambda: self.play(),
                'assets\\buttons\\play\\')
            self.deleteButton = Button(
                (self.rect.x + self.rect.width // 2 - 25, self.rect.y + self.rect.height), (50, 50),
                lambda: self.delete(),
                'assets\\buttons\\subtract\\',
                False
            )
            self.worldName = TextBox(r'assets\fonts\SuperLegendBoy.ttf',
                                     (self.rect.midtop[0], self.rect.midtop[1] + self.rect.height + 50), 20,
                                     worldName.title())
            BUTTONS.add([self.editButton, self.playButton, self.deleteButton])
            TEXTBOXES.add(self.worldName)

        def scroll(self, val):
            self.editButton.rect.y += val
            self.playButton.rect.y += val
            self.worldName.rect.y += val
            self.deleteButton.rect.y += val
            self.rect.y += val

        def edit(self):
            pg.mixer.music.fadeout(1000)
            editor(self.world)

        def play(self):
            pg.mixer.music.fadeout(1000)
            game(self.world)

        def delete(self):
            if self.world == 'basic' or self.world == 'maze': return

            def removeWorld():
                nonlocal scrolled
                rmtree(f'assets\\worlds\\{self.world}')
                for w in WORLDS:
                    for i in [w.playButton, w.editButton, w.deleteButton, w.worldName, w]:
                        i.kill()

                for world in enumerate(os.listdir('assets\\worlds\\')):
                    WORLDS.add(World(world[1], (25 + (world[0] % 2) * 300, 60 + (world[0] // 2) * 280)))

                if len(WORLDS) <= 4:
                    scrolled = 0

                addworld.rect.topleft = (
                    25 + ((len(WORLDS)) % 2) * 300 + 100, 120 + ((len(WORLDS)) // 2) * 280 + scrolled)

                draw()

                window.destroy()

            window = Tk()
            window.geometry('200x110')
            window.title('Confirm?')
            window.configure(background='#212121')

            Label(window, text=f'Are you SURE you want\nto delete {self.world}?', justify='left', background='#212121',
                  foreground='White', font=('Arial Bold', 10)).place(x=10, y=10)
            TkButton(window, text='YES', command=lambda: removeWorld(), background='#383838', foreground='White',
                     activebackground='#383838', activeforeground='White').place(x=110, y=60, width=80, height=40)
            TkButton(window, text='NO', command=lambda: window.destroy(), background='#383838', foreground='White',
                     activebackground='#383838', activeforeground='White').place(x=10, y=60, width=80, height=40)

            window.mainloop()

    def draw():
        SCREEN.fill(Colors.Black)

        WORLDS.draw(SCREEN)
        TEXTBOXES.draw(SCREEN)
        BUTTONS.draw(SCREEN)

        pg.draw.rect(SCREEN, Colors.Black, (0, 0, winWidth, 55))
        pg.draw.rect(SCREEN, Colors.White, (0, 55, winWidth, 2))

        SCREEN.blit(TITLE.image, TITLE.rect)

        pg.display.flip()

    TITLE = TextBox('assets\\fonts\\SuperLegendBoy.ttf', (winWidth // 2, 20), 20, 'Choose Level!')

    for world in enumerate(os.listdir('assets\\worlds\\')):
        WORLDS.add(World(world[1], (25 + (world[0] % 2) * 300, 60 + (world[0] // 2) * 280)))

    addworld = Button((25 + ((len(WORLDS)) % 2) * 300 + 100, 120 + ((len(WORLDS)) // 2) * 280), (50, 50),
                      lambda: newMap(),
                      'assets\\buttons\\add\\', False)
    BUTTONS.add(addworld)

    draw()

    scrolled = 0

    pg.mixer.music.load('assets\\audio\\menu.mp3')
    pg.mixer.music.play(-1, 0, 5000)

    while True:
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    break
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        for b in BUTTONS:
                            if b.rect.collidepoint(pg.mouse.get_pos()):
                                b.press()
                if event.type == pg.MOUSEBUTTONUP:
                    for b in BUTTONS:
                        if b.pressed:
                            b.unpress()
                if event.type == pg.MOUSEWHEEL:
                    if scrolled - event.y < 0 or (len(WORLDS) + 2) * 140 + 60 - (scrolled - 20 * event.y) <= 600:
                        break
                    scrolled -= 20 * event.y
                    for w in WORLDS:
                        w.scroll(20 * event.y)
                    addworld.rect.y += 20 * event.y

                    draw()
        except pygame.error:
            break


menu()
