from model import *
from view import *
from collections import deque

import sys

sys.setrecursionlimit(10**6)

# finds all placeable active piece states
def find_placement_positions(state: State, store_moves: bool = True) -> list[tuple[Piece,str]]:
    start_piece = state.active_piece.clone()
    state = state.clone()
    seen: dict[Piece,str] = {} # seen active piece state -> move performed
    placement_positions: list[Piece] = [] # placement states
    q: deque[Piece] = deque()
    q.append(state.active_piece.clone())
    while len(q) > 0:
        curr = q.popleft()
        state.active_piece = curr
        if state.placeable():
            placement_positions.append(curr.clone())
        def check(move: str):
            if not state.valid() or curr in seen:
                return
            seen[curr.clone()] = move
            q.append(curr.clone())
        # rot cw
        curr.rotate(False)
        check('E')
        curr.rotate(True)
        # rot ccw
        curr.rotate(True)
        check('Q')
        curr.rotate(False)
        # move left
        curr.translate(0, -1)
        check('L')
        curr.translate(0, 1)
        # move right
        curr.translate(0, 1)
        check('R')
        curr.translate(0, -1)
        # move down
        curr.translate(1, 0)
        check('D')
        curr.translate(-1, 0)
    def f(piece: Piece) -> tuple[Piece,str]:
        if not store_moves:
            return (piece, "")
        seq = ""
        curr = piece.clone()
        while curr != start_piece:
            seq += seen[curr]
            match seen[curr]:
                case 'L': curr.translate(0, 1)
                case 'R': curr.translate(0, -1)
                case 'D': curr.translate(-1, 0)
                case 'E': curr.rotate(True)
                case 'Q': curr.rotate(False)
                case _: raise Exception("invalid move")
        return (piece, seq[::-1])
    return list(map(f, placement_positions))