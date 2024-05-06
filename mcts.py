from model import *
from placement_search import *
from heuristic import *
from training import *
from multiprocessing import Pool

def mcts_sim(src):
    placement, depth, samples, heuristic = src
    sum_rating = 0
    for s in range(samples):
        state = placement.new_state.clone()
        for d in range(depth):
            if not state.valid():
                break
            placements = find_placements(state, Piece(PieceType(random.randint(0,6))), False)
            chosen, rating = chose_placement(placements, heuristic, False, True)
            state = chosen.new_state
            sum_rating += rating
    return sum_rating

def mcts_choose_placement(placements: list[Placement], heuristic: Callable[[Placement],float], max_candidates: int, depth: int, samples: int) -> Callable[[Placement],float]:
    if len(placements) > max_candidates:
        new_placements = [(heuristic(placement),i) for i,placement in enumerate(placements)]
        new_placements.sort(reverse=True)
        new_placements = new_placements[0:max_candidates]
        new_placements = [placements[i] for (score,i) in new_placements]
        placements = new_placements
    def gen_src(index, placement):
        return (placement, depth, samples, heuristic)
    ratings = [mcts_sim(gen_src(i,p)) for i, p in enumerate(placements)]
    return placements[ratings.index(max(ratings))]