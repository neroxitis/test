import sys

import pygame as pg
from pygame.locals import *
 
pg.init()

background_image_filename = '/home/nikos/PycharmProjects/CalcuLines/images/' \
                            'menu_background.jpg'
menu_items = ('Start server', 'Configuration', 'Play', 'Quit')

class MenuItem(pg.sprite.Sprite):
    def __init__(self, name, label, pos):
        pg.sprite.Sprite.__init__(self)
        self.name = name
        self.label = label
        self.x_pos, self.y_pos = pos
        self.x, self.y = pos
        self.rect = self.label.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class GameMenu():
    def __init__(self, screen, bg_color=(255, 255, 255), font=None,
                 font_size=30, font_color=(255, 255, 255)):
        self.screen = screen
        self.scr_width = self.screen.get_rect().width
        self.scr_height = self.screen.get_rect().height
        self.background = pg.image.load(background_image_filename).convert()
        self.bg_color = bg_color
        self.clock = pg.time.Clock()
        left, top = pg.mouse.get_pos()
        self.pointer = pg.Rect(left, top, 1, 1)
 
        self.font = pg.font.SysFont(font, font_size)
        self.font_color = font_color
 
        self.items = []
        for index, name in enumerate(menu_items):
            label = self.font.render(name, 1, font_color)
 
            width = label.get_rect().width
            height = label.get_rect().height
 
            posx = (self.scr_width / 2) - (width / 2)

            # t_h: total height of text block
            t_h = len(menu_items) * height
            posy = (self.scr_height / 2) - (t_h / 2) + (index * height)
            menu_item = MenuItem(name, label, (posx, posy))
            self.items.append(menu_item)
        print(self.items)

    def mouse_button_down(self):
        self.pointer.x, self.pointer.y = pg.mouse.get_pos()
        print(self.pointer)
        for item in self.items:
            if item.rect.colliderect(self.pointer):
                if item.name == 'Play':
                    return False
                elif item.name == 'Quit':
                    pg.quit()
                    sys.exit()

        return True

    def run(self):
        pg.display.set_caption('Calculines')
        mainloop = True
        while mainloop:
            # Limit frame speed to 50 FPS
            self.clock.tick(50)
 
            for event in pg.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mainloop = self.mouse_button_down()

            # Redraw the background
            self.screen.blit(self.background, (0,0))
 
            for item in self.items:
                self.screen.blit(item.label, (item.x_pos, item.y_pos))
 
            pg.display.flip()
