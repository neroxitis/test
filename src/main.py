import pygame as pg
from pygame.locals import *
import sys
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

from elements import Board, NEIGHBOURS

pg.init()
screen = pg.display.set_mode((900, 640), 0, 32)
pg.display.set_caption("CalcuLines")


class CalcuLinesGame(ConnectionListener):

    def __init__(self, host, port):

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
        self.board = Board(screen)
        self.player = None

        self.Connect((host, port))

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

    def events(self):
        while True:
            connection.Pump()
            self.Pump()

            for event in pg.event.get():
                if event.type == QUIT:
                    self.exit()

                if self.red:
                    self.player = "red"
                else:
                    self.player = "blue"

                if event.type == MOUSEBUTTONDOWN:
                    self.mouse_button_down()

                if self.somebody_won():
                    pg.display.update()
                    pg.time.delay(3000)
                    exit()
                pg.display.update()

    def Network_hello(self, data):
        print data['message']

    def Network_startgame(self, data):
        self.player = data["player"]
        if self.player == data['turn']:
            print("It's your turn!")
        else:
            print("Wait for your opponents turn!")

    def Network_bye(self, data):
        print data['message']

    def exit(self):
        connection.Send({"action": "exit"})
        sys.exit()

    def mouse_button_down(self):
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
                        elif cell.colour != self.player:
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
                            cell.update(self.player)
                            self.board.screen.blit(
                                cell.image, cell.rect)
                            self.board.content(cell.id,
                                               player=self.player)
                            if self.board.find_clusters(cell.id,
                                                        self.player):
                                self.board.update_info(
                                    message="Don't leave "
                                            "isolated cells!")
                                self.previous.update(self.player)
                                self.board.screen.blit(
                                    self.previous.image,
                                    self.previous.rect)
                                self.board.content(
                                    self.previous.id,
                                    player=self.player)
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
                                cell.update(self.player)
                                self.board.screen.blit(cell.image,
                                                       cell.rect)
                                self.board.content(cell.id,
                                                   player=self.player)
                                new_calculation = cell.operation

                                self.update_score(new_calculation)

                                self.red = not self.red
                                self.hold = False

                        elif cell.id == self.previous.id:
                            self.hold = False
                            self.board.content(
                                self.previous.id,
                                player=self.player)
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
                            neighbour].colour == self.player])
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
                    cell.update(self.player)
                    self.update_score(new_calculation)
                    self.red = not self.red
                    self.board.screen.blit(cell.image, cell.rect)
                    self.board.content(cell.id, player=self.player)

    def loop(self):
        self.Pump()
        connection.Pump()
        self.draw()
        self.events()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "host:port"
        print "e.g.", sys.argv[0], "localhost:12345"
    else:
        host, port = sys.argv[1].split(":")
        clgame = CalcuLinesGame(host, int(port))
        connection.Send({"action": "hello", "message": "Hello Server!!"})
        while True:
            clgame.loop()
            sleep(0.001)
