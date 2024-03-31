from model import *
import os

display = [['?'] * BOARD_DIM[1] for i in range(BOARD_DIM[0])]
def render(state: State):
    os.system("cls")
    for r in range(BOARD_DIM[0]):
        for c in range(BOARD_DIM[1]):
            display[r][c] = '#' if state.grid[r][c] else '.'
    for r,c in state.active_piece.get_tiles():
        display[r][c] = '@'
    print("\n".join(" ".join(line) for line in display))