from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
import sys


class ServerChannel(Channel):
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)


    def Close(self):
        self._server.DelPlayer(self)

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

    def Connected(self, channel, addr):
        print 'new connection:', channel
        channel.Send({"action": "helloc", "message": "hello client!"})

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

# Get command line argument of server, port
if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "host:port"
    print "e.g.", sys.argv[0], "localhost:31425"
else:
    host, port = sys.argv[1].split(":")
    server = CalcuLinesServer(localaddr=(host, int(port)))
    server.Launch()
