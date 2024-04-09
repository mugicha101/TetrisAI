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
    col_heights = column_heights(placement.new_state)
    return -(hole_count(placement.new_state) ** 2) - least_squares(placement.new_state, 0) - (max(col_heights) - 4) ** 2 - min(col_heights) ** 2 + (placement.line_clears * 3) ** 2

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
        # if c > 0: check(r, c-1)
        # if c+1 < BOARD_DIM[1]: check(r, c+1)
        if r+1 < BOARD_DIM[0]: check(r+1, c)
    return sum(row.count(False) for row in visited)

def well_count(state: State) -> int:
    blocked = set()
    loc = 0
    height = 0
    for row in range(BOARD_DIM[0]):
        row_total = 0
        for col, val in enumerate(state.grid[row]):
            if val:
                blocked.add(col)
                row_total += 1
            else:
                loc = col
        if row_total == BOARD_DIM[1]:
            #everything will either be covered or we have reached the bottom of any potential well
            break
        if row_total != BOARD_DIM[1] - 1 or loc in blocked:
            #If there are not 9 filled columns or the unfilled column is blocked by something above it
            height = 0
        else:
            height += 1
    if height >= 1:
        return height
    return -100

def well_heuristic(state: State) -> int:
    return well_count(state)

def least_squares(state: State, target_gradient) -> list[int]:
    x_sum, y_sum, xy_sum, xsquare_sum = 0, 0, 0, 0

    heights = column_heights(state)
    for i in range(len(heights)):
        x_sum += i
        y_sum += heights[i]
        xy_sum += i * heights[i]
        xsquare_sum += i ** 2
    
    slope = (10 * xy_sum - (x_sum * y_sum)) / (10 * xsquare_sum - ((x_sum) ** 2))
    intercept = (y_sum - (slope * x_sum)) / 10

    ans = []
    for i in range(len(heights)):
         ans.append(abs(heights[i] - ((target_gradient * i) + intercept)))
    
    if(abs(.4 - slope) < 0.05):
        target_gradient = 0
    elif(abs(0 - slope) < 0.05):
        target_gradient = 0.4

    return sum(ans)
