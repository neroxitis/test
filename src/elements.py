import pygame as pg
from random import randint

BOARD_SIZE = 7
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 640
CIRCLE_DIAM = 60
SEGMENT_TARGET = [3, 28]
GAME_HEIGHT = CIRCLE_DIAM*BOARD_SIZE
GAME_WIDTH = CIRCLE_DIAM*BOARD_SIZE
SCORE_DISTANCE = 100
COLOUR = {'red': (255, 0, 0),
          'blue': (0, 0, 255),
          'green': (0, 255, 0),
          'yellow': (255, 255, 0),
          'white': (255, 255, 255),
          'black': (0, 0, 0),
          'grey': (180, 180, 180)}
IMAGE = {
    'red': pg.image.load(
        "/home/nikos/PycharmProjects/CalcuLines/images/red.png"),
    'blue': pg.image.load(
        "/home/nikos/PycharmProjects/CalcuLines/images/blue.png"),
    'green': pg.image.load(
        "/home/nikos/PycharmProjects/CalcuLines/images/green.png"),
    'yellow': pg.image.load(
        "/home/nikos/PycharmProjects/CalcuLines/images/yellow.png"),
    'empty': pg.image.load(
        "/home/nikos/PycharmProjects/CalcuLines/images/empty.png")}
OPERATORS = ['+', '-', '*', '//']
NEIGHBOURS = {}
BLANKER = pg.Surface((280, 30))
PLAYER = pg.Surface((25, 25))

pg.init()
pg.font.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)


class PlayerStatus:
    def __init__(self, colour, idx):
        self.colour = colour
        self.idx = idx
        self.top_distance = None

    def calculate_top_distance(self, no_players):
        vertical_margin = (SCREEN_HEIGHT-(no_players+1)*SCORE_DISTANCE)/2
        self.top_distance = vertical_margin+self.idx*SCORE_DISTANCE


class Cell(pg.sprite.Sprite):
    """ The Cell """
    def __init__(self, colour, coord, pos, operation=None):
        pg.sprite.Sprite.__init__(self)
        self.id = 0
        self.x_pos, self.y_pos = pos
        self.x, self.y = coord
        self.colour = colour
        self.update(colour)
        self.operation = operation or \
            OPERATORS[randint(0, 3)] + str(randint(1, 10))

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
        self.info_font = pg.font.SysFont(None, 40)
        BLANKER.fill(COLOUR['white'])
        self.board_content = {}
        self.no_players = 0
        self.players = []

    def get_vertical_top_distance(self):
        vertical_margin = (SCREEN_HEIGHT-(self.no_players+1)*SCORE_DISTANCE)/2
        return vertical_margin + self.no_players*SCORE_DISTANCE

    def update_info(self, scores=None, message=None,
                    isturn=None, playertoplay=None, players=None,
                    new_player=None):
        if players is not None:
            self.no_players = len(players)
            for idx, colour in enumerate(players):
                player = PlayerStatus(colour, idx)
                player.calculate_top_distance(self.no_players)
                self.players.append(player)


        if new_player is not None:
            idx = len(self.players)
            player = PlayerStatus(new_player, idx)
            player.calculate_top_distance(idx)
            self.players.append(player)

        if scores is not None:
            for player in self.players:
                score = scores[player.colour]
                score_text = self.info_font.render(
                    str(score),
                    True,
                    COLOUR[player.colour],
                    COLOUR['white'])
                score_rect = score_text.get_rect(
                    left=660, top=player.top_distance
                )
                self.screen.blit(BLANKER, (660, player.top_distance))
                self.screen.blit(score_text, score_rect)
        if message is not None:
            message_text = self.font.render(message, True, COLOUR['black'])
            max_top_distance = self.get_vertical_top_distance()
            message_rect = message_text.get_rect(
                left=660, top=max_top_distance
            )
            self.screen.blit(BLANKER, (660, max_top_distance))
            self.screen.blit(message_text, message_rect)
        if isturn is not None:
            for player in self.players:
                if player.colour != playertoplay:
                    PLAYER.fill(COLOUR['white'])
                else:
                    PLAYER.fill(COLOUR['black'])
                self.screen.blit(PLAYER,
                                 (620, player.top_distance))


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

    def draw(self, existing_board_content=None):
        cell_image = IMAGE['empty']
        cell_image.set_colorkey(cell_image.get_at((0, 0)))
        radius = 30
        self.screen.fill((255, 255, 255))

        # Draw vertical lines
        pos = [54, 54]
        for _ in range(7):
            pg.draw.line(self.screen,
                         COLOUR['grey'],
                         (pos[0], pos[1]),
                         (pos[0], pos[1]+520),
                         2)
            pos[0] += 87

        # Draw horizontal lines
        pos = [54, 54]
        for _ in range(7):
            pg.draw.line(self.screen,
                         COLOUR['grey'],
                         (pos[0], pos[1]),
                         (pos[0]+520, pos[1]),
                         2)
            pos[1] += 87

        # Draw back slashes
        pos = [54, 487]
        diag_len = 87
        for _ in range(6):
            pg.draw.line(
                self.screen,
                COLOUR['grey'],
                (pos[0], pos[1]),
                (pos[0]+diag_len, pos[1]+diag_len),
                2)
            pos[0] = 54
            pos[1] -= 87
            diag_len += 87

        pos = [141, 54]
        diag_len = 433
        for _ in range(6):
            pg.draw.line(
                self.screen,
                COLOUR['grey'],
                (pos[0], pos[1]),
                (pos[0]+diag_len, pos[1]+diag_len),
                2)
            pos[0] += 87
            pos[1] = 54
            diag_len -= 87

        # Draw slashes
        pos = [54, 574]
        diag_len = 520
        for _ in range(6):
            pg.draw.line(
                self.screen,
                COLOUR['grey'],
                (pos[0], pos[1]),
                (pos[0]+diag_len, pos[1]-diag_len),
                2)
            pos[0] = 54
            pos[1] -= 87
            diag_len -= 87

        pos = [574, 141]
        diag_len = 433
        for _ in range(6):
            pg.draw.line(
                self.screen,
                COLOUR['grey'],
                (pos[0], pos[1]),
                (pos[0]-diag_len, pos[1]+diag_len),
                2)
            pos[0] = 574
            pos[1] += 84
            diag_len -= 87

        # Draw cells
        if existing_board_content is None:
            board_content = {}

        pos = [30, 30]
        for x in range(7):
            for y in range(7):
                if existing_board_content is None:
                    cell = Cell('empty', pos, (x, y))
                    self.add_cell(cell, x, y)
                    board_content.update({cell.id: [cell.operation, None]})
                else:
                    id = x*7+y+1
                    cell = Cell('empty', pos, (x, y),
                                operation=existing_board_content[id][0])
                    self.add_cell(cell, x, y)
                self.screen.blit(cell.image, cell.rect)
                self.content(cell.id)
                pos[0] += 2*radius+27
            pos[0] = 30
            pos[1] += 2*radius+27
        pg.display.update()
        pg.display.flip()
        return board_content if existing_board_content is None else None

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
