from doctest import testmod
from time import time

from upemtk import *

CELL_SIZE = 50
BOARD_WIDTH = 7
BOARD_HEIGHT = 6
WINDOW_WIDTH = 12 * CELL_SIZE
WINDOW_HEIGHT = 8 * CELL_SIZE
X_MARGIN = (WINDOW_WIDTH - BOARD_WIDTH * CELL_SIZE) // 2
Y_MARGIN = (WINDOW_HEIGHT - BOARD_HEIGHT * CELL_SIZE) // 2
FRAMERATE = 60
BAR_HEIGHT = -1
DIRECTIONS = [(1, 1), (1, -1), (1, 0), (0, 1)]

RUNNING = True
START = True


def pixel_to_cell(x: int, y: int):
    return (x - X_MARGIN) // CELL_SIZE, BOARD_HEIGHT - 1 - (y - Y_MARGIN) // CELL_SIZE


def cell_to_pixel(x: int, y: int):
    return X_MARGIN + (x + .5) * CELL_SIZE, WINDOW_HEIGHT - (y + 1 + .5) * CELL_SIZE


def format_time(time_to_format: int):
    minutes = ("" if time_to_format // 60 >= 10 else "0") + str(time_to_format // 60)
    seconds = ("" if time_to_format % 60 >= 10 else "0") + str(time_to_format % 60)
    return minutes + ":" + seconds


def set_start(start: bool):
    global START
    START = start


def set_running(running: bool):
    global RUNNING
    RUNNING = running


def allowed_moves(grid: list):
    result = dict()
    for x, column in enumerate(grid):
        for y, row in enumerate(column):
            if not row:
                result[x] = y
                break
    return result


def check_win(grid: list, player: int):
    for x, column in enumerate(grid):
        for y, row in enumerate(column):
            for (dx, dy) in DIRECTIONS:
                pawns = list()
                for i in range(4):
                    if not (0 <= x + i * dx < BOARD_WIDTH and 0 <= y + i * dy < BOARD_HEIGHT):
                        break
                    if grid[x + i * dx][y + i * dy] != player:
                        break
                    pawns.append((x + i * dx, y + i * dy))
                    if i == 3:
                        return True, pawns
    return False, None


def compute_text_size():
    global BAR_HEIGHT
    creer_fenetre(0, 0)
    BAR_HEIGHT = taille_texte('X')[1] + 19
    fermer_fenetre()


def left_click(ev: tuple):
    x, y = abscisse(ev), ordonnee(ev)
    for (xa, ya, xb, yb), f in buttons.items():
        if xa <= x <= xb and ya <= y <= yb:
            f()


def build_grid():
    grid = list()
    for _ in range(BOARD_WIDTH):
        grid.append([0] * BOARD_HEIGHT)
    return grid


def draw_board(grid: list):
    rectangle(X_MARGIN - 5, Y_MARGIN - 5, WINDOW_WIDTH - X_MARGIN + 5, WINDOW_HEIGHT - Y_MARGIN + 5, remplissage='blue')
    for i, column in enumerate(grid):
        for j, row in enumerate(column):
            x, y = cell_to_pixel(i, j)
            cercle(x, y, 7 / 16 * CELL_SIZE, remplissage='white')


def draw_grid(grid: list):
    for x, column in enumerate(grid):
        for y, row in enumerate(column):
            draw_pawn(x, y, row, False)


def draw_label(x: float, y: float, text: str, anchor: str = "center", outline: str = "black", bg: str = "white",
               fg: str = "black", size: int = 24, force_width: int = 0, force_height: int = 0, margin: int = 5):
    width = force_width or taille_texte(text, taille=size)[0]
    height = force_height or taille_texte(text, taille=size)[1]
    if anchor == "center":
        xa, ya, xb, yb = x - width / 2 - margin, y - height / 2 - margin, \
                         x + width / 2 + margin, y + height / 2 + margin
    elif anchor == "n":
        xa, ya, xb, yb = x - width / 2 - margin, y, \
                         x + width / 2 + margin, y + height + 2 * margin
    elif anchor == "s":
        xa, ya, xb, yb = x - width / 2 - margin, y - height - 2 * margin, \
                         x + width / 2 + margin, y
    elif anchor == "e":
        xa, ya, xb, yb = x - width - 2 * margin, y - height / 2 - margin, \
                         x, y + height / 2 + margin
    elif anchor == "w":
        xa, ya, xb, yb = x, y - height / 2 - margin, \
                         x + width + 2 * margin, y + height / 2 + margin
    elif anchor == "nw":
        xa, ya, xb, yb = x, y, \
                         x + width + 2 * margin, y + height + 2 * margin
    elif anchor == "ne":
        xa, ya, xb, yb = x - width - 2 * margin, y, \
                         x, y + height + 2 * margin
    elif anchor == "sw":
        xa, ya, xb, yb = x, y - height - 2 * margin, \
                         x + width + 2 * margin, y
    elif anchor == "se":
        xa, ya, xb, yb = x - width - 2 * margin, y - height - 2 * margin, \
                         x, y
    else:
        return
    rectangle(xa, ya, xb, yb, outline, bg)
    texte((xa + xb) / 2, (ya + yb) / 2, text, fg, ancrage="center",
          taille=size)
    return xa, ya, xb, yb


def draw_bottom_bar(playing: bool, winner: int):
    rectangle(0, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT + BAR_HEIGHT, remplissage='black')
    if not playing:
        offset = 0
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Quitter', 'se')
        offset += xb - xa + 5
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5 - offset, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Rejouer', 'se')
        buttons[(xa, ya, xb, yb)] = lambda: set_start(True)
        offset += xb - xa + 5
        if winner < 0:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT // 2, "Rouge a gagné !",
                  ancrage='e', couleur='red', taille=24)
        elif winner > 0:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT // 2, "Jaune a gagné !",
                  ancrage='e', couleur='gold', taille=24)
        else:
            texte(WINDOW_WIDTH - 10 - offset, WINDOW_HEIGHT + BAR_HEIGHT // 2, "Match nul !",
                  ancrage='e', couleur='green', taille=24)
    else:
        xa, ya, xb, yb = draw_label(WINDOW_WIDTH - 5, WINDOW_HEIGHT + BAR_HEIGHT - 5, 'Quitter', 'se')
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)


def draw_pawn(x: int, y: int, player: int, bold: bool):
    x, y = cell_to_pixel(x, y)
    if player < 0:
        cercle(x, y, 7 / 16 * CELL_SIZE, remplissage="red", epaisseur=5 if bold else 1)
    elif player > 0:
        cercle(x, y, 7 / 16 * CELL_SIZE, remplissage="gold", epaisseur=5 if bold else 1)


def draw_win_pawns(win_pawns: list, winner: int):
    for (x, y) in win_pawns:
        draw_pawn(x, y, winner, True)


def draw_turn_indicator(player: int):
    cercle(0, WINDOW_HEIGHT // 2, CELL_SIZE, remplissage='red' if player == -1 else 'gray')
    cercle(WINDOW_WIDTH, WINDOW_HEIGHT // 2, CELL_SIZE, remplissage='gold' if player == 1 else 'gray')
    texte(CELL_SIZE // 2, WINDOW_HEIGHT // 2, 'J1', ancrage='center', couleur='white')
    texte(WINDOW_WIDTH - CELL_SIZE // 2, WINDOW_HEIGHT // 2, 'J2', ancrage='center',
          couleur='white' if player < 1 else 'black')


def draw_time(ticks: float):
    effacer('time')
    current_time = format_time(int(ticks))
    texte(10, WINDOW_HEIGHT + BAR_HEIGHT // 2, current_time, ancrage='w', couleur='white', tag='time')


def draw_all(grid: list, player: int, playing: bool, ticks: float, winner: int):
    draw_board(grid)
    draw_grid(grid)
    draw_turn_indicator(player if playing else winner)
    draw_bottom_bar(playing, winner)
    draw_time(ticks)


def loop():
    creer_fenetre(WINDOW_WIDTH, WINDOW_HEIGHT + BAR_HEIGHT, nom="Puissance 4")

    grid = build_grid()
    playing = True
    winner = 0
    ticks = 0
    player = -1
    last_time = time()
    last_round_time = -1

    while RUNNING:
        if START:
            set_start(False)
            grid = build_grid()
            playing = True
            winner = 0
            ticks = 0
            player = -1
            last_time = time()
            last_round_time = -1

            draw_all(grid, player, playing, ticks, winner)

        ev = donner_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            break
        elif ty == 'ClicGauche':
            left_click(ev)

        if playing:
            if ty == 'ClicGauche' and ticks > 0:
                x, y = pixel_to_cell(abscisse(ev), ordonnee(ev))

                if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
                    continue

                moves = allowed_moves(grid)
                if x not in moves.keys():
                    continue

                grid[x][moves[x]] = player
                win = check_win(grid, player)

                if not allowed_moves(grid):
                    playing = False

                if playing and win[0]:
                    winner = player
                    playing = False
                else:
                    player *= -1

                buttons.clear()
                effacer_tout()
                draw_all(grid, player, playing, ticks, winner)
                if win[1]:
                    draw_win_pawns(win[1], winner)

            delta = (time() - last_time)
            ticks += delta
            last_time = time()

            if int(ticks) % 60 != last_round_time:
                last_round_time = int(ticks) % 60
                draw_time(ticks)

        attendre(1 / FRAMERATE)

    fermer_fenetre()


if __name__ == "__main__":
    testmod()
    buttons = dict()
    compute_text_size()
    loop()
