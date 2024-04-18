from model import *
from view import *
from placement_search import *
from heuristic import *
import random
import time

def manual_play():
    state = State(active_piece = Piece(PieceType(random.randint(0,6))), next_piece = Piece(PieceType(random.randint(0,6))))
    while state.valid():
        render(state)
        move = input().lower()
        p = state.active_piece
        if move == 's':
            p.translate(1,0)
            if not state.valid():
                p.translate(-1,0)
        elif move == 'a':
            p.translate(0,-1)
            if not state.valid():
                p.translate(0,1)
        elif move == 'd':
            p.translate(0,1)
            if not state.valid():
                p.translate(0,-1)
        elif move == 'e':
            p.rotate(False)
            if not state.valid():
                p.rotate(True)
        elif move == 'q':
            p.rotate(True)
            if not state.valid():
                p.rotate(False)
        elif move == 'z':
            while not state.placeable():
                p.translate(1,0)
            state.place_piece(Piece(PieceType(random.randint(0,6))))
    render(state)

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

def heuristic_placement(heuristic: Callable[[Placement],float], weighted_choice: bool = True, show_moves: bool = True) -> State:
    state = State(active_piece = Piece(PieceType(random.randint(0,6))), next_piece = Piece(PieceType(random.randint(0,6))))
    while state.valid():
        render(state)
        new_next_piece = Piece(PieceType(random.randint(0,6)))
        placements: list[Placement] = find_placements(state, new_next_piece, show_moves)
        chosen = chose_placement(placements, heuristic, weighted_choice)
        if show_moves: move_playback(state, chosen.moves)
        state = chosen.new_state
    render(state)
    return state

def main():
    end_state = heuristic_placement(test_heuristic, False, True)

if __name__ == "__main__":
    main()