import sys
from time import sleep

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server


class ServerChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        print 'Bye bye server!'
        self._server.DeletePlayer(self)

    # Callbacks #########################################

    def Network_myaction(self, data):
        print "myaction:", data
        self._server.SetBoard(data, update=True)

    def Network_hello(self, data):
        print 'message=', data['message']
        if data['board'] != '':
            self._server.SetBoard(data)

    def Network_leave(self, data):
        self._server.LeaveGame(self)

    # ###################################################


class CalcuLinesServer(Server):
    channelClass = ServerChannel
    player_colours = ["yellow", "green", "blue", "red"]

    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.no_players = kwargs['listeners']
        print 'CalcuLines Server launched!'
        self.game = None
        self.board = None
        self.players = []
        self.Launch()

    def Connected(self, channel, addr):
        if self.game is None:
            self.game = Game()
        if len(self.game.players) <= self.no_players:
            print 'new connection:', channel
            player_colour = self.player_colours.pop()
            self.game.players[channel] = {'online': True,
                                          'colour': player_colour}
            if len(self.game.players) == 1:
                board = ""
            else:
                board = self.board
            channel.Send({"action": "hello",
                          "colour": player_colour,
                          "message": "Welcome to CalcuLines! "
                                     "You will be the " + player_colour +
                                     " player.",
                          "restplayers": self.players,
                          "board": board})
            self.players.append(player_colour)
            for player in self.game.players:
                player.Send({"action": "newplayer",
                             "colour": player_colour})
        else:
            # Need to dismiss more clients.
            return
        if len(self.game.players) == self.no_players:
            for player, status in self.game.players.items():
                if status['online']:
                    player.Send({"action": "startgame",
                                 "whoplays": "red"})

    def LeaveGame(self, leaver):
        leaver_colour = self.game.players[leaver]['colour']
        print 'player with id {} has left the game'.format(str(leaver.addr))
        player_message = '{} player left the game'.format(leaver_colour)
        leaver.Send({"action": "forcequit"})
        for player in [pl for pl in self.game.players if pl != leaver]:
            player.Send({"action": "message",
                         "message": player_message})

    def DeletePlayer(self, quitter):
        quitter_colour = self.game.players[quitter]['colour']
        print 'player with id {} has quit the game'.format(str(quitter.addr))
        player_message = '{} player has quit the game'.format(quitter_colour)
        self.player_colours.append(quitter_colour)
        self.players.pop()
        del self.game.players[quitter]
        for player in [pl for pl in self.game.players if pl != quitter]:
            player.Send({"action": "message",
                         "message": player_message})
            player.Send({"action": "forcequit"})

    def SetBoard(self, data, update=False):
        self.board = data['board']
        if update:
            print(data['whoplays'], data['score_info'])
            for player in self.game.players:
                player.Send({"action": "update",
                             "board": data['board'],
                             "whoplays": data['whoplays'],
                             "score_info": data['score_info'],
                             "no_cells": data['no_cells']})

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)


class Game:
    def __init__(self):
        # 'red' or 'blue'
        self.turn = 'red'
        self.players = {}

if __name__ == '__main__':
    # Get command line argument of server, port
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "host:port players:number"
        print "e.g.", sys.argv[0], "localhost:12345 players:3"
        print ""
    else:
        host, port = sys.argv[1].split(":")
        no_players = int(sys.argv[2].split(":")[1])
        server = CalcuLinesServer(localaddr=(host, int(port)),
                                  listeners=no_players)
        server.Launch()
