# Modified version of inputbox.py, originally written by Timothy Downs

import string

import pygame as pg
from pygame.locals import *

from src.elements import COLOUR


def get_key():
    while True:
        event = pg.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass


class PopupBox:
    def __init__(self, screen):
        self.screen = screen

    def display_box(self, message):
        """Print a message in a box in the middle of the screen"""
        fontobject = pg.font.Font(None, 24)
        screen = self.screen

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        box_left = screen_width / 3
        box_top = screen_height / 3
        box_width = 300
        box_height = 30

        pg.draw.rect(screen,
                     COLOUR['black'],
                     (box_left, box_top,
                      box_width, box_height),
                     0)
        pg.draw.rect(screen,
                     COLOUR['white'],
                     (box_left, box_top,
                      box_width, box_height),
                     2)

        if len(message) != 0:
            screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                        (box_left+5,
                         box_top+5))
        pg.display.flip()

    def ask(self, question):
        """ask(screen, question) -> answer"""
        pg.font.init()

        current_string = []
        self.display_box(question + ": " + string.join(current_string, ""))

        while True:
            key = get_key()
            if key == K_BACKSPACE:
                current_string = current_string[0:-1]
            elif key == K_RETURN:
                break
            elif key == K_ESCAPE:
                return None
            elif key == K_MINUS:
                current_string.append("_")
            elif key <= 127:
                current_string.append(chr(key))
            self.display_box(question + ": " + string.join(current_string,""))

        return string.join(current_string, "")
