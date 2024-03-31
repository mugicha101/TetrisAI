from model import *
from view import *
import random

def main():
    state = State(active_piece = Piece(PieceType(random.randint(0,6))), next_piece = Piece(PieceType(random.randint(0,6))))
    while state.valid():
        while (not state.placeable()):
            state.active_piece.translate(1,0)
        state.place_piece(Piece(PieceType(random.randint(0,6))))
    repr = grid_repr(state.grid)
    print(repr)
    state.grid = load_repr(repr)
    print(state.grid)
    render(state)

main()