from model import *
import os
import time

display = [['?'] * BOARD_DIM[1] for i in range(BOARD_DIM[0])]
FRAME_TIME = 0.05

def frame_pause() -> None:
    if FRAME_TIME > 0:
        time.sleep(FRAME_TIME)

class render_controls:
    enabled: bool = True # if disabled, render function does nothing

def render(state: State) -> None:
    if not render_controls.enabled: return
    os.system("cls")
    for r in range(BOARD_DIM[0]):
        for c in range(BOARD_DIM[1]):
            display[r][c] = '#' if state.grid[r][c] else '.'
    for r,c in state.active_piece.get_tiles():
        display[r][c] = '@'
    print("\n".join(" ".join(line) for line in display))
    frame_pause()