from model import *
from placement_search import Placement
from typing import Callable
from collections import deque
import time
import random

# MCTS next placement agent
# if weighted, does a weighted sample based on score, else chooses placement with highest score
# score of a placement based on heuristic
def chose_placement(placements: list[Placement], heuristic: Callable[[Placement],float], weighted: bool = True) -> Placement:
    weights = [heuristic(placement) for placement in placements]
    if not weighted:
        return placements[weights.index(max(weights))]
    offset = min(weights)
    weights = [w - offset for w in weights]
    mult = 1.0 / sum(weights)
    weights = [w * mult for w in weights]
    return random.choices(placements, weights=weights, k=1)[0]

def score_heuristic(placement: Placement) -> float:
    return -max(column_heights((placement.new_state))) * 5 - hole_count(placement.new_state) + placement.line_clears * 10

def column_heights(state: State) -> list[int]:
    return [BOARD_DIM[0] - next(r for r in range(BOARD_DIM[0]+1) if r == BOARD_DIM[0] or state.grid[r][c]) for c in range(BOARD_DIM[1])]

def hole_count(state: State) -> int:
    q: deque[tuple[int,int]] = deque()
    visited = [row[:] for row in state.grid]
    for c in range(BOARD_DIM[1]):
        if not visited[0][c]:
            visited[0][c] = True
            q.append((0,c))
    while len(q) > 0:
        (r, c) = q.popleft()
        def check(r, c):
            if visited[r][c]: return
            visited[r][c] = True
            q.append((r, c))
        if r > 0: check(r-1, c)
        if c > 0: check(r, c-1)
        if r+1 < BOARD_DIM[0]: check(r+1, c)
        if c+1 < BOARD_DIM[1]: check(r, c+1)
    return sum(row.count(False) for row in visited)

def well_count(state: State):
    blocked = set()
    prior = -1
    loc = 0
    ans = 0
    height = 0
    for row in range(BOARD_DIM[0]):
        row_total = 0
        for col, val in enumerate(state.grid[row]):
            if val:
                blocked.add(col)
                row_total += 1
            else:
                loc = col
        if row_total != BOARD_DIM[1] - 1 or (loc != prior and prior != -1) or loc in blocked:
            height = 0
            prior = -1
        else:
            prior = loc
            height += 1
    if height >= 4:
        return height
    return 0

    
        

