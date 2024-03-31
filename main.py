from model import *
from view import *
import random

def main():
    repr = grid_repr()
    print(repr)
    grid = load_repr(repr)
    print(grid)
    state = State(active_piece = Piece(PieceType.J))
    while state.valid():
        while (not state.placeable()):
            state.active_piece.translate(1,0)
        state.place_piece(Piece(PieceType(random.randint(0,7))))
    render(state)

main()