import pygame as pg
from pygame.locals import *
from sys import exit
from PodSixNet.Connection import ConnectionListener, connection
from time import time

from elements import Board, NEIGHBOURS


class CalcuLinesGame(ConnectionListener):

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((900, 640), 0, 32)
        pg.display.set_caption("CalcuLines")

        left, top = pg.mouse.get_pos()
        self.pointer = pg.Rect(left, top, 1, 1)
        self.pointer_mask = pg.mask.Mask((1, 1))
        self.pointer_mask.set_at((0, 0), 1)
        self.no_red_cells = 0
        self.no_blue_cells = 0
        self.red_score = 0
        self.blue_score = 0
        self.red = True
        self.hold = False
        self.previous = None
        self.board = Board(self.screen)

        self.Connect()

    def draw(self):
        self.board.draw()
        self.board.populate_neighbours_dic()
        self.board.update_info(red_score=self.red_score,
                               blue_score=self.blue_score,
                               player='')

    def update_score(self, new_calculation):
        if self.red and new_calculation:
            self.red_score = eval(str(self.red_score)+new_calculation)
        elif not self.red and new_calculation:
            self.blue_score = eval(str(self.blue_score)+new_calculation)
        self.board.update_info(red_score=self.red_score,
                               blue_score=self.blue_score,
                               message="",
                               player='red' if self.red else 'blue')

    def somebody_won(self):
        if self.red_score == 100:
            self.board.update_info(message='RED WON!')
        elif self.blue_score == 100:
            self.board.update_info(message='BLUE WON!')
        if self.red_score == 100 or self.blue_score == 100:
            return True
        else:
            return False

    def Events(self):
        while True:
            for event in pg.event.get():
                if event.type == QUIT:
                    exit()

                if self.red:
                    player = "red"
                else:
                    player = "blue"

                if event.type == MOUSEBUTTONDOWN:
                    self.board.update_info(message="")
                    self.pointer.x, self.pointer.y = pg.mouse.get_pos()
                    for i in range(1, 50):
                        cell = self.board.cell[i]
                        if cell.rect.colliderect(self.pointer):
                            connection.Send({"action": "myaction",
                                       "cell_id": cell.id,
                                       "pointer_x": self.pointer.x,
                                       "pointer_y": self.pointer.y})
                            if self.no_red_cells == self.no_blue_cells == 5:
                                if not self.hold:
                                    if cell.colour == 'empty':
                                        self.board.update_info(
                                            message='There is no piece here!')
                                    elif cell.colour != player:
                                        self.board.update_info(
                                            message='Choose a piece you own!')
                                    else:
                                        self.board.update_info(
                                            message="That's right!")
                                        self.previous = cell
                                        self.hold = True
                                        self.board.content(self.previous.id,
                                                           'green')
                                    break
                                else:
                                    if cell.colour == 'empty':
                                        self.previous.update('empty')
                                        self.board.screen.blit(
                                            self.previous.image,
                                            self.previous.rect)
                                        self.board.content(self.previous.id)
                                        cell.update(player)
                                        self.board.screen.blit(
                                            cell.image, cell.rect)
                                        self.board.content(cell.id,
                                                           player=player)
                                        if self.board.find_clusters(cell.id,
                                                                    player):
                                            self.board.update_info(
                                                message="Don't leave "
                                                        "isolated cells!")
                                            self.previous.update(player)
                                            self.board.screen.blit(
                                                self.previous.image,
                                                self.previous.rect)
                                            self.board.content(
                                                self.previous.id,
                                                player=player)
                                            cell.update('empty')
                                            self.board.screen.blit(
                                                cell.image,
                                                cell.rect)
                                            self.board.content(cell.id)
                                        else:
                                            self.previous.update('empty')
                                            self.board.screen.blit(
                                                self.previous.image,
                                                self.previous.rect)
                                            self.board.content(
                                                self.previous.id)
                                            cell.update(player)
                                            self.board.screen.blit(cell.image,
                                                                   cell.rect)
                                            self.board.content(cell.id,
                                                               player=player)
                                            new_calculation = cell.operation

                                            self.update_score(new_calculation)

                                            self.red = not self.red
                                            self.hold = False

                                    elif cell.id == self.previous.id:
                                        self.hold = False
                                        self.board.content(
                                            self.previous.id,
                                            player=player)
                                    else:
                                        self.board.update_info(
                                            message="Occupied cell!")
                                    break

                            else:
                                if cell.colour != 'empty':
                                    self.board.update_info(
                                        message='There is no piece here!')
                                    break
                                own_neighbours = sum(
                                    [1 for neighbour in NEIGHBOURS[cell.id]
                                     if self.board.cell[
                                        neighbour].colour == player])
                                if self.red:
                                    if (self.no_red_cells == 0 or
                                            own_neighbours >= 1):
                                        self.no_red_cells += 1
                                        new_calculation = cell.operation
                                    else:
                                        self.board.update_info(
                                            message='No isolated pieces!')
                                        break
                                else:
                                    if (self.no_blue_cells == 0 or
                                            own_neighbours >= 1):
                                        self.no_blue_cells += 1
                                        new_calculation = cell.operation
                                    else:
                                        self.board.update_info(
                                            message='No isolated pieces!')
                                        break
                                cell.update(player)
                                self.update_score(new_calculation)
                                self.red = not self.red
                                self.board.screen.blit(cell.image, cell.rect)
                                self.board.content(cell.id, player=player)

                if self.somebody_won():
                    pg.display.update()
                    pg.time.delay(3000)
                    exit()
                pg.display.update()

if __name__ == '__main__':
    clgame = CalcuLinesGame()
    clgame.draw()
    clgame.Events()
