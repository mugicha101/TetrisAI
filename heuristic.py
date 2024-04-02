from model import *
from placement_search import Placement
from typing import Callable
import time
import random

# MCTS next placement agent
# if weighted, does a weighted sample based on score, else chooses placement with highest score
# score of a placement based on heuristic
def chose_placement(placements: list[Placement], heuristic: Callable[[Placement],float], weighted: bool = True) -> Placement:
    weights = [heuristic(placement) for placement in placements]
    if not weighted:
        return placements[weights.index(max(weights))]
    print(weights)
    mult = 1.0 / sum(weights)
    weights = [w * mult for w in weights]
    time.sleep(1)
    return random.choices(placements, weights=weights, k=1)[0]

def score_heuristic(placement: Placement) -> float:
    return (BOARD_DIM[0] - max(column_heights((placement.new_state)))) ** 2

def column_heights(state: State) -> list[int]:
    return [BOARD_DIM[0] - next(r for r in range(BOARD_DIM[0]+1) if r == BOARD_DIM[0] or state.grid[r][c]) for c in range(BOARD_DIM[1])]