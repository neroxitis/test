from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
import sys


class ServerChannel(Channel):
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)


    def Close(self):
        self._server.DeletePlayer(self)

    # Callbacks #########################################

    def Network_myaction(self, data):
        print "myaction:", data

    def Network_hello(self, data):
        print 'message=', data['message']

    def Network_nickname(self, data):
        print 'nickname=', data['nickname']

    def Network_mousedown(self, data):
        print 'action:', data['action']

    # ###################################################


class CalcuLinesServer(Server):
    channelClass = ServerChannel

    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.players = {}
        print 'CalcuLines Server launched!'
        self.game = None

    def Connected(self, channel, addr):
        print 'new connection:', channel
        self.players[channel] = True
        channel.Send({"action": "hello", "message": "Hello client!"})
        if self.game is None:
            self.game = Game(channel)
        else:
            self.game.blueplayer = channel
            self.game.redplayer.Send({"action": "hello",
                                      "message": "You are the red player."})
            self.game.blueplayer.Send({"action": "hello",
                                      "message": "You are the blue player."})
            self.game.redplayer.Send({"action": "startgame", "player": "red",
                                      "turn": "red"})
            self.game.blueplayer.Send({"action": "startgame",
                                        "player": "blue", "turn": "red"})

    def DeletePlayer(self, player):
        print 'player with id', str(player.address), 'has left the game.'
        player.Send({"action": "bye", "message": "Bye client!"})
        del self.players[player]

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)


class Game:
    def __init__(self, redplayer):
        # 'red' or 'blue'
        self.turn = 'red'
        self.redplayer = redplayer
        self.blueplayer = None

# Get command line argument of server, port
if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "host:port"
    print "e.g.", sys.argv[0], "localhost:12345"
else:
    host, port = sys.argv[1].split(":")
    server = CalcuLinesServer(localaddr=(host, int(port)))
    server.Launch()
