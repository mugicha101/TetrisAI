from model import *
import os
import time

display = [['?'] * BOARD_DIM[1] for i in range(BOARD_DIM[0])]

class render_controls:
    enabled: bool = True # if disabled, render function does nothing
    frame_time: bool = 0.05 # time in seconds between render frames

def frame_pause() -> None:
    if render_controls.frame_time > 0:
        time.sleep(render_controls.frame_time)

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

def move_playback(state: State, moves: str) -> None:
    for m in moves:
        match m:
            case 'L': state.active_piece.translate(0, -1)
            case 'R': state.active_piece.translate(0, 1)
            case 'D': state.active_piece.translate(1, 0)
            case 'E': state.active_piece.rotate(False)
            case 'Q': state.active_piece.rotate(True)
            case _: raise Exception("invalid move")
        render(state)