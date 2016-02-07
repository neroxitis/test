import sys
import subprocess
from time import sleep

from menu import GameMenu
from game import CalcuLinesGame
from elements import screen


if __name__ == '__main__':

    host = None
    port = None
    no_players = None
    gm = GameMenu(screen, port, no_players)
    menu = True
    server = None
    while menu:
        option, args = gm.run()
        if option == 1:
            host = 'localhost'
            port, no_players = args
            server = subprocess.Popen(['python',
                                       'server.py',
                                       '{}:{}'.format (host, port),
                                       'players:{}'.format(no_players)])
        elif option == 2:
            server.kill()
            print('Calculines Server stopped!')
        elif option == 3:
            host = 'localhost'
            port = args
            clgame = CalcuLinesGame(host, int(port))
            while True:
                clgame.loop_events()
                sleep(0.001)

        elif option == 4:
            menu = False
    sys.exit()