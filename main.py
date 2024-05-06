from model import *
from view import *
from placement_search import *
from heuristic import *
from training import *
from mcts import *
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

def heuristic_placement(heuristic: Callable[[Placement],float], weighted_choice: bool = False, show_moves: bool = True) -> State:
    state = State(active_piece = Piece(PieceType(random.randint(0,6))), next_piece = Piece(PieceType(random.randint(0,6))))
    score = 0
    line_clears = 0
    while state.valid():
        render(state, score, line_clears)
        new_next_piece = Piece(PieceType(random.randint(0,6)))
        placements: list[Placement] = find_placements(state, new_next_piece, show_moves)
        chosen = mcts_choose_placement(placements, heuristic, 5, 10, 10)
        if show_moves: move_playback(state, chosen.moves, score, line_clears)
        score += chosen.score_gain
        line_clears += chosen.line_clears
        state = chosen.new_state
    render(state, score, line_clears)
    return state

def main():
    # load best model
    heuristic = gen_nn_heuristic(load_group("training_cache.txt")[0])
    render_controls.frame_time = 0.01
    end_state = heuristic_placement(heuristic, False, True)

if __name__ == "__main__":
    main()