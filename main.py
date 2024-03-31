from model import *
from view import *
import random

def main():
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

main()