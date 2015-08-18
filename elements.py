import pygame as pg
from random import randint

BOARD_SIZE = 7
CIRCLE_DIAM = 60
SEGMENT_TARGET = [3, 28]
GAME_HEIGHT = CIRCLE_DIAM*BOARD_SIZE
GAME_WIDTH = CIRCLE_DIAM*BOARD_SIZE
COLOUR = {'red': (255, 0, 0),
          'blue': (0, 0, 255),
          'white': (255, 255, 255),
          'green': (0, 255, 0),
          'black': (0, 0, 0)}
IMAGE = {'red': pg.image.load("images/red.png"),
         'blue': pg.image.load("images/blue.png"),
         'empty': pg.image.load("images/empty.png")}
OPERATORS = ['+', '-', '*', '//']
NEIGHBOURS = {}


class Cell(pg.sprite.Sprite):
    """ The ball """
    def __init__(self, colour, coord, pos):
        pg.sprite.Sprite.__init__(self)
        self.id = 0
        self.x_pos, self.y_pos = pos
        self.x, self.y = coord
        self.colour = colour
        self.update(colour)
        self.operation = OPERATORS[randint(0, 3)] + str(randint(1, 10))

    def update(self, colour):
        self.colour = colour
        self.image = IMAGE[colour]
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.x = self.x
        self.rect.y = self.y


class Board(pg.Surface):
    """ The Board """
    def __init__(self, screen):
        self.cell = {}
        self.cell_id = 1
        self.screen = screen
        self.font = pg.font.SysFont(None, 25)

    def content(self, cell_id, player=None):
        cell = self.cell[cell_id]
        if player:
            f_colour = COLOUR['white']
            b_colour = COLOUR[player]
        else:
            f_colour = COLOUR['black']
            b_colour = COLOUR['white']
        text = self.font.render(cell.operation, True, f_colour, b_colour)
        textrect = text.get_rect()
        textrect.centerx = cell.rect.centerx
        textrect.centery = cell.rect.centery

        self.screen.blit(text, textrect)

    def add_cell(self, cell, x_pos, y_pos):
        self.cell[self.cell_id] = cell
        cell.id = self.cell_id
        self.cell_id += 1
        cell.colour = 'empty'
        cell.x_pos = x_pos
        cell.y_pos = y_pos

    def get_cell(self, cell_id):
        return self.cell[cell_id]

    def change_cell(self, cell, colour):
        cell.colour = colour

    def draw(self):
        cell_image = IMAGE['empty']
        cell_image.set_colorkey(cell_image.get_at((0, 0)))
        radius = 30
        self.screen.fill((255, 255, 255))
        pos = [54, 54]
        for _ in range(7):
            pg.draw.line(self.screen,
                         COLOUR['black'],
                         (pos[0], pos[1]),
                         (pos[0], pos[1]+520),
                         2)
            pos[0] += 87

        pos = [54, 54]
        for _ in range(7):
            pg.draw.line(self.screen,
                         COLOUR['black'],
                         (pos[0], pos[1]),
                         (pos[0]+520, pos[1]),
                         2)
            pos[1] += 87

        pos = [30, 30]

        for x in range(7):
            for y in range(7):
                cell = Cell('empty', pos, (x, y))
                self.add_cell(cell, x, y)
                self.screen.blit(cell.image, cell.rect)
                self.content(cell.id)
                pos[0] += 2*radius+27

            pos[0] = 30
            pos[1] += 2*radius+27
        pg.display.update()
        pg.display.flip()

    def populate_neighbours_dic(self):
        for id in self.cell.keys():
            row = self.cell[id].x_pos + 1
            col = self.cell[id].y_pos + 1
            rows = range(max(1, row-1), min(row + 2, 8))
            cols = range(max(1, col-1), min(col + 2, 8))
            NEIGHBOURS[id] = {(row-1)*7+col
                              for row in rows
                              for col in cols} - {id}

    def neighbours(self, player, cell_id):
        return sum([n_id
                    for n_id in NEIGHBOURS[cell_id]
                    if self.cell[n_id].colour == player])

    def find_clusters(self, cell_id, player):
        found = []
        for neighbour in NEIGHBOURS[cell_id]:
            cluster(self, player, neighbour, found)
        if len(found) == 5:
            return False
        else:
            return True


def cluster(board, player, cell_id, found):
    cell = board.cell[cell_id]
    if cell.colour == player:
        if cell_id not in found:
            found.append(cell_id)
            neighbours = NEIGHBOURS[cell_id]
            if not neighbours:
                return
            else:
                for neighbour in neighbours:
                    cluster(board, player, neighbour, found)
    else:
        return
