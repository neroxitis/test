import pygame as pg
from pygame.locals import *
from sys import exit

from elements import Board, IMAGE, NEIGHBOURS


def update_score(red_score, blue_score, red, new_calculation):
    if red and new_calculation:
        red_score = eval(str(red_score)+new_calculation)
    elif not red and new_calculation:
        blue_score = eval(str(blue_score)+new_calculation)
    print 'red score =', red_score, \
        'blue score =', blue_score
    return red_score, blue_score


def somebody_won(red_score, blue_score):
    if red_score == 100:
        print 'RED WON!'
    elif blue_score == 100:
        print 'BLUE WON!'
    if red_score == 100 or blue_score == 100:
        return True
    else:
        return False


def main():
    pg.init()
    screen = pg.display.set_mode((640, 640), 0, 32)
    pg.display.set_caption("CalcuLines")

    board = Board(screen)
    board.draw()
    board.populate_neighbours_dic()

    no_red_cells = 0
    no_blue_cells = 0
    red_score = 0
    blue_score = 0
    IMAGE['empty'].set_colorkey(IMAGE['empty'].get_at((0, 0)))
    left, top = pg.mouse.get_pos()
    pointer = pg.Rect(left, top, 1, 1)
    pointer_mask = pg.mask.Mask((1, 1))
    pointer_mask.set_at((0, 0), 1)

    red = True
    hold = False
    previous = None
    while True:
        for event in pg.event.get():
            new_calculation = None
            if event.type == QUIT:
                exit()

            if red:
                player = "red"
            else:
                player = "blue"

            if event.type == MOUSEBUTTONDOWN:
                pointer.x, pointer.y = pg.mouse.get_pos()
                for i in range(1, 50):
                    cell = board.cell[i]
                    if cell.rect.colliderect(pointer):
                        print cell.id
                        if no_red_cells == no_blue_cells == 5:
                            if not hold:
                                if cell.colour == 'empty':
                                    print 'There is no piece here!'
                                elif cell.colour != player:
                                    print 'Choose a piece you own!'
                                else:
                                    print "That's right!"
                                    previous = cell
                                    hold = True
                                    board.content(previous.id, 'green')
                                break
                            else:
                                if cell.colour == 'empty':
                                    previous.update('empty')
                                    board.screen.blit(previous.image,
                                                      previous.rect)
                                    board.content(previous.id)
                                    cell.update(player)
                                    board.screen.blit(cell.image, cell.rect)
                                    board.content(cell.id, player=player)
                                    if board.find_clusters(cell.id, player):
                                        print "Don't leave isolated cells!"
                                        previous.update(player)
                                        board.screen.blit(previous.image,
                                                          previous.rect)
                                        board.content(previous.id,
                                                      player=player)
                                        cell.update('empty')
                                        board.screen.blit(cell.image,
                                                          cell.rect)
                                        board.content(cell.id)
                                    else:
                                        previous.update('empty')
                                        board.screen.blit(previous.image,
                                                          previous.rect)
                                        board.content(previous.id)
                                        cell.update(player)
                                        board.screen.blit(cell.image,
                                                          cell.rect)
                                        board.content(cell.id, player=player)
                                        new_calculation = cell.operation

                                        red_score, blue_score = update_score(
                                            red_score, blue_score,
                                            red, new_calculation)

                                        red = not red
                                        hold = False

                                elif cell.id == previous.id:
                                    hold = False
                                    board.content(previous.id, player=player)
                                else:
                                    print "Occupied cell!"
                                break

                        else:
                            if cell.colour != 'empty':
                                print 'There is no piece here!'
                                break
                            own_neighbours = sum(
                                [1 for neighbour in NEIGHBOURS[cell.id]
                                 if board.cell[neighbour].colour == player])
                            if red:
                                if no_red_cells == 0 or own_neighbours >= 1:
                                    no_red_cells += 1
                                    new_calculation = cell.operation
                                else:
                                    print 'No isolated pieces!'
                                    break
                            else:
                                if no_blue_cells == 0 or own_neighbours >= 1:
                                    no_blue_cells += 1
                                    new_calculation = cell.operation
                                else:
                                    print 'No isolated pieces!'
                                    break
                            cell.update(player)
                            red_score, blue_score = update_score(
                                red_score, blue_score,
                                red, new_calculation)
                            red = not red
                            board.screen.blit(cell.image, cell.rect)
                            board.content(cell.id, player=player)

            pg.display.update()
            if somebody_won(red_score, blue_score):
                exit()
if __name__ == '__main__':
    main()
