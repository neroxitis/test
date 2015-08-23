import pygame as pg
from pygame.locals import *
from sys import exit
from PodSixNet.Connection import ConnectionListener, connection
from time import time

from elements import Board, NEIGHBOURS


class CalcuLinesGame(ConnectionListener):

    def __init__(self):
        self.Connect()
        pg.init()
        screen = pg.display.set_mode((900, 640), 0, 32)
        pg.display.set_caption("CalcuLines")

        self.board = Board(screen)
        self.board.draw()
        self.board.populate_neighbours_dic()

    def update_score(self, red_score, blue_score, red, new_calculation):
        if red and new_calculation:
            red_score = eval(str(red_score)+new_calculation)
        elif not red and new_calculation:
            blue_score = eval(str(blue_score)+new_calculation)
        self.board.update_info(red_score=red_score, blue_score=blue_score,
                          message="", player='red' if red else 'blue')
        return red_score, blue_score

    def somebody_won(self, red_score, blue_score):
        if red_score == 100:
            self.board.update_info(message='RED WON!')
        elif blue_score == 100:
            self.board.update_info(message='BLUE WON!')
        if red_score == 100 or blue_score == 100:
            return True
        else:
            return False

    def main(self):
        connection.Pump()
        self.Pump()

        no_red_cells = 0
        no_blue_cells = 0
        red_score = 0
        blue_score = 0
        self.board.update_info(red_score=red_score, blue_score=blue_score,
                          player='')
        left, top = pg.mouse.get_pos()
        pointer = pg.Rect(left, top, 1, 1)
        pointer_mask = pg.mask.Mask((1, 1))
        pointer_mask.set_at((0, 0), 1)

        red = True
        hold = False
        previous = None
        while True:
            for event in pg.event.get():
                if event.type == QUIT:
                    exit()

                if red:
                    player = "red"
                else:
                    player = "blue"

                if event.type == MOUSEBUTTONDOWN:
                    self.board.update_info(message="")
                    pointer.x, pointer.y = pg.mouse.get_pos()
                    for i in range(1, 50):
                        cell = self.board.cell[i]
                        if cell.rect.colliderect(pointer):
                            if no_red_cells == no_blue_cells == 5:
                                if not hold:
                                    if cell.colour == 'empty':
                                        self.board.update_info(
                                            message='There is no piece here!')
                                    elif cell.colour != player:
                                        self.board.update_info(
                                            message='Choose a piece you own!')
                                    else:
                                        self.board.update_info(
                                            message="That's right!")
                                        previous = cell
                                        hold = True
                                        self.board.content(previous.id, 'green')
                                    break
                                else:
                                    if cell.colour == 'empty':
                                        previous.update('empty')
                                        self.board.screen.blit(previous.image,
                                                          previous.rect)
                                        self.board.content(previous.id)
                                        cell.update(player)
                                        self.board.screen.blit(
                                            cell.image, cell.rect)
                                        self.board.content(cell.id, player=player)
                                        if self.board.find_clusters(cell.id,
                                                               player):
                                            self.board.update_info(
                                                message="Don't leave "
                                                        "isolated cells!")
                                            previous.update(player)
                                            self.board.screen.blit(previous.image,
                                                              previous.rect)
                                            self.board.content(previous.id,
                                                          player=player)
                                            cell.update('empty')
                                            self.board.screen.blit(cell.image,
                                                              cell.rect)
                                            self.board.content(cell.id)
                                        else:
                                            previous.update('empty')
                                            self.board.screen.blit(previous.image,
                                                              previous.rect)
                                            self.board.content(previous.id)
                                            cell.update(player)
                                            self.board.screen.blit(cell.image,
                                                              cell.rect)
                                            self.board.content(cell.id,
                                                          player=player)
                                            new_calculation = cell.operation

                                            red_score, blue_score = \
                                                self.update_score(
                                                    red_score, blue_score,
                                                    red, new_calculation)

                                            red = not red
                                            hold = False

                                    elif cell.id == previous.id:
                                        hold = False
                                        self.board.content(previous.id,
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
                                if red:
                                    if (no_red_cells == 0 or
                                            own_neighbours >= 1):
                                        no_red_cells += 1
                                        new_calculation = cell.operation
                                    else:
                                        self.board.update_info(
                                            message='No isolated pieces!')
                                        break
                                else:
                                    if (no_blue_cells == 0 or
                                            own_neighbours >= 1):
                                        no_blue_cells += 1
                                        new_calculation = cell.operation
                                    else:
                                        self.board.update_info(
                                            message='No isolated pieces!')
                                        break
                                cell.update(player)
                                red_score, blue_score = self.update_score(
                                    red_score, blue_score,
                                    red, new_calculation)
                                red = not red
                                self.board.screen.blit(cell.image, cell.rect)
                                self.board.content(cell.id, player=player)

                if self.somebody_won(red_score, blue_score):
                    pg.display.update()
                    pg.time.delay(3000)
                    exit()
                pg.display.update()

if __name__ == '__main__':
    clgame = CalcuLinesGame()
    clgame.main()
