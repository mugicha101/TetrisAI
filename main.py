from model import *
from view import *
import random

def main():
    repr = grid_repr()
    print(repr)
    grid = load_repr(repr)
    print(grid)
    state = State(active_piece = Piece(PieceType(random.randint(0,6))), next_piece = Piece(PieceType(random.randint(0,6))))
    while state.valid():
        while (not state.placeable()):
            state.active_piece.translate(1,0)
        state.place_piece(Piece(PieceType(random.randint(0,6))))
    render(state)

main()