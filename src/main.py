import pygame as pg
from pygame.locals import *
import sys
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
from collections import OrderedDict

from elements import NEIGHBOURS, Board, screen

pg.display.set_caption("CalcuLines")


class CalcuLinesGame(ConnectionListener):

    def __init__(self, host, port):

        self.screen = pg.display.set_mode((900, 640), 0, 32)
        left, top = pg.mouse.get_pos()
        self.pointer = pg.Rect(left, top, 1, 1)
        self.pointer_mask = pg.mask.Mask((1, 1))
        self.pointer_mask.set_at((0, 0), 1)
        self.scores = OrderedDict()
        self.no_cells = {}
        self.players = []
        self.hold = False
        self.previous = None
        self.board = None
        self.player = None
        self.playing = False
        self.existing_board_content = None

        self.Connect((host, port))

        while not self.playing:
            self.Pump()
            connection.Pump()
            sleep(0.01)

        if self.turn:
            print("It's your turn!")
        else:
            print("Wait for your opponents turn!")

        self.board.update_info(isturn=self.turn, playertoplay=self.player)

    def draw_all(self, existing_board_content=None):
        existing_board_content = self.board.draw(
            existing_board_content=existing_board_content)
        self.board.populate_neighbours_dic()
        self.board.update_info(self.scores, players=self.players)
        return existing_board_content

    def update_score(self, score_info):
        player, calculation = score_info
        if player and calculation:
            player_recent_score = self.scores[player]
            self.scores[player] = eval(str(player_recent_score)+calculation)
        self.board.update_info(scores=self.scores,
                               message="",
                               isturn=self.turn,
                               playertoplay=player)

    def somebody_won(self):
        for colour, score in self.scores.items():
            if score == 100:
                self.board.update_info(message='%s WON!' % colour.upper())
                return True
        return False

    def events(self):
        while True:
            connection.Pump()
            self.Pump()

            for event in pg.event.get():
                if event.type == KEYUP:
                    if event.key == K_F1:
                        self.exit()

                if event.type == MOUSEBUTTONDOWN:
                    self.mouse_button_down()

                if self.somebody_won():
                    pg.display.update()
                    pg.time.delay(3000)
                    exit()
                pg.display.update()

    def Network_hello(self, data):
        restplayers = data['restplayers']
        if restplayers:
            self.players = restplayers
            print data['message'], 'The rest of the players are:', restplayers
            for player in restplayers:
                self.scores.update({player: 0})
                self.no_cells.update({player: 0})
        self.board = Board(screen)
        if data['board'] == "":
            self.existing_board_content = self.draw_all()
            connection.Send({"action": "hello",
                             "message": "Hello Server!!",
                             "board": self.existing_board_content})
        else:
            self.existing_board_content = data['board']
            self.draw_all(existing_board_content=self.existing_board_content)

    def Network_newplayer(self, data):
        new_player_colour = data['colour']
        print "New player is online with", new_player_colour, "colour !"
        self.players.append(new_player_colour)
        self.board.update_info(new_player=new_player_colour)
        self.scores.update({new_player_colour: 0})
        self.no_cells.update({new_player_colour: 0})

    def Network_startgame(self, data):
        self.playing = True
        self.player = data["player"]
        self.turn = True if self.player == data['whoplays'] else False
        self.board.update_info(scores=self.scores,
                               playertoplay=data['whoplays'],
                               isturn=self.turn)

    def Network_update(self, data):
        self.existing_board_content = data['board']
        self.turn = True if self.player == data['whoplays'] else False
        self.no_cells = data['no_cells']
        for id, value in self.existing_board_content.items():
            cell = self.board.cell[id]
            player = value[1]
            if player is None:
                cell.update('empty')
            else:
                cell.update(player)
            self.board.screen.blit(cell.image, cell.rect)
            self.board.content(cell.id, player=player)
        self.update_score(data['score_info'])

    def Network_bye(self, data):
        print data['message']

    def Network_close(self, data):
        pg.quit()
        sys.exit()

    def exit(self):
        connection.Send({"action": "exit"})

    def mouse_button_down(self):
        if not self.turn:
            return
        self.board.update_info(message="", playertoplay=self.player,
                               isturn=self.turn)
        self.pointer.x, self.pointer.y = pg.mouse.get_pos()
        for i in range(1, 50):
            cell = self.board.cell[i]
            if cell.rect.colliderect(self.pointer):
                if not bool([v for v in self.no_cells.values() if v != 5]):
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

                                self.hold = False

                                # Update the board map for server
                                self.existing_board_content[
                                    self.previous.id][1] = None
                                self.existing_board_content[cell.id][1] = \
                                    self.player
                                self.update_everything(cell)

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
                    if (self.no_cells[self.player] == 0 or
                            own_neighbours >= 1):
                        self.no_cells[self.player] += 1
                    else:
                        self.board.update_info(
                            message='No isolated pieces!')
                        break
                    # Update the board map for server
                    self.existing_board_content[cell.id][1] = self.player

                    self.update_everything(cell)

    def loop(self):
        connection.Pump()
        self.Pump()
        self.events()

    def update_everything(self, cell):
        cell.update(self.player)
        self.board.screen.blit(cell.image, cell.rect)
        self.board.content(cell.id, player=self.player)
        self.turn = False
        idx_next_player = (self.players.index(self.player)+1) % 4
        connection.Send({"action": "myaction",
                         "player": self.player,
                         "cell_id": cell.id,
                         "pointer_x": self.pointer.x,
                         "pointer_y": self.pointer.y,
                         "board": self.existing_board_content,
                         "whoplays": self.players[idx_next_player],
                         "score_info": (self.player, cell.operation),
                         "no_cells": self.no_cells})

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "host:port"
        print "e.g.", sys.argv[0], "localhost:12345"
    else:
        host, port = sys.argv[1].split(":")
        clgame = CalcuLinesGame(host, int(port))

        while True:
            clgame.loop()
            sleep(0.001)
