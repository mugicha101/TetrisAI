from model import *
from view import *
from collections import deque

import sys

sys.setrecursionlimit(10**6)

# finds states after all possible placements
# returns placement state, placed piece, and optionally transcript of moves (if store_moves active)
def find_placement_states(state: State, new_next_piece: Piece, store_moves: bool = True) -> list[tuple[State,Piece,str]]:
    start_piece = state.active_piece.clone()
    state = state.clone()
    seen: dict[Piece,str] = {} # seen active piece state -> move performed
    placement_states: list[Piece] = [] # placed piece
    q: deque[Piece] = deque()
    q.append(state.active_piece.clone())
    while len(q) > 0:
        curr = q.popleft()
        state.active_piece = curr
        if state.placeable():
            placement_states.append(curr.clone())
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
    def f(piece: Piece) -> tuple[State,Piece,str]:
        cloned_state = state.clone()
        cloned_state.active_piece = piece
        cloned_state.place_piece(new_next_piece)
        if not store_moves:
            return (cloned_state, piece, "")
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
        return (cloned_state, piece, seq[::-1])
    return list(map(f, placement_states))