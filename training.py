from model import *
from view import *
from placement_search import Placement
from placement_search import find_placements
from heuristic import *
from multiprocessing import Process, Pool
from time import sleep
import random
import os

GROUP_SIZE = 100 # size of remaining group per epoch
TRAINING_GROUP_SIZE = 200 # size of training group per epoch (crossbreed until this size reached)
RAND_PARENTS = 2 # number of completely random parents to add at start of each epoch
MUT_STD = 1 # standard deviation to mutate each param by when crossbreeding = MUT_STD * (diff between this param in parent)
NUM_CORES = 8 # number of cores to use
GEO_BASE = 0.98

# TODO: GET PROCESS RETURN VALUE

def load_group(gene_file_path: str) -> list[dict[str,float]]:
    group: list[dict[str,float]] = []
    with open(gene_file_path, 'r') as gene_file:
        data = gene_file.read()
    for model_data in data.split(';'):
        model_params: dict[str,float] = {}
        for param in model_data.split(','):
            comp = param.split('=')
            model_params[comp[0]] = float(comp[1])
        group.append(model_params)
    return group

def store_group(gene_file_path: str, group: list[dict[str,float]]) -> None:
    data = ";".join([",".join([f"{label}={value}" for label, value in model_params.items()]) for model_params in group])
    with open(gene_file_path, 'w') as gene_file:
        gene_file.write(data)

def write_data(data_path: str, avg_score: int, avg_moves: int, avg_line_clears: int):
    with open(data_path, 'a') as data_file:
        data_file.write(f"{avg_score}\t{avg_moves}\t{avg_line_clears}\n")

P_LINE_CLEAR_A1 = "line_clear_a1"
P_LINE_CLEAR_A2 = "line_clear_a2"
P_COL_SUM_A1 = "col_sum_a1"
P_COL_SUM_A2 = "col_sum_a2"
P_MAX_COL_A1 = "max_col_a1"
P_MAX_COL_A2 = "max_col_a2"
P_SCORE_CHANGE_A1 = "score_change_a1"
P_SCORE_CHANGE_A2 = "score_change_a2"
P_BUMPINESS_A1 = "bumpiness_a1"
P_BUMPINESS_A2 = "bumpiness_a2"
P_TARGET_SLOPE = "target_slope"
P_WELL_HEIGHT_A1 = "well_height_a1"
P_WELL_HEIGHT_A2 = "well_height_a2"
P_LIST = [P_LINE_CLEAR_A1, P_LINE_CLEAR_A2, P_COL_SUM_A1, P_COL_SUM_A2, P_MAX_COL_A1, P_MAX_COL_A2, P_SCORE_CHANGE_A1, P_SCORE_CHANGE_A2, P_BUMPINESS_A1, P_BUMPINESS_A2, P_TARGET_SLOPE, P_WELL_HEIGHT_A1, P_WELL_HEIGHT_A2]

rand = random.Random()

def rand_model() -> dict[str,float]:
    model_params: dict[str,float] = {}
    model_params[P_LINE_CLEAR_A1] = rand.uniform(0, 10)
    model_params[P_LINE_CLEAR_A2] = rand.uniform(0, 10)
    model_params[P_COL_SUM_A1] = rand.uniform(-10, 10)
    model_params[P_COL_SUM_A2] = rand.uniform(-10, 10)
    model_params[P_MAX_COL_A1] = rand.uniform(-10, 10)
    model_params[P_MAX_COL_A2] = rand.uniform(-10, 10)
    model_params[P_SCORE_CHANGE_A1] = rand.uniform(0, 10)
    model_params[P_SCORE_CHANGE_A2] = rand.uniform(0, 10)
    model_params[P_BUMPINESS_A1] = rand.uniform(-10, 0)
    model_params[P_BUMPINESS_A2] = rand.uniform(-10, 0)
    model_params[P_WELL_HEIGHT_A1] = rand.uniform(0, 10)
    model_params[P_WELL_HEIGHT_A2] = rand.uniform(0, 10)
    model_params[P_TARGET_SLOPE] = rand.uniform(-0.5, 0.5)
    return model_params

def gen_score_heuristic(model_params: dict[str,float]) -> Callable[[Placement],float]:
    def heuristic(placement: Placement) -> float:
        s = placement.new_state
        cols = column_heights(s)
        col_sum = sum(cols)
        max_col = max(cols)
        bumpiness = least_squares(s, model_params[P_TARGET_SLOPE])
        well = well_count(s)

        return \
            placement.line_clears * model_params[P_LINE_CLEAR_A1] + placement.line_clears ** 2 * model_params[P_LINE_CLEAR_A2] + \
            col_sum * model_params[P_COL_SUM_A1] + col_sum ** 2 * model_params[P_COL_SUM_A2] + \
            max_col * model_params[P_MAX_COL_A1] + max_col ** 2 * model_params[P_MAX_COL_A2] + \
            bumpiness * model_params[P_BUMPINESS_A1] + bumpiness ** 2 * model_params[P_BUMPINESS_A2] + \
            placement.score_gain * model_params[P_SCORE_CHANGE_A1] + placement.score_gain ** 2 * model_params[P_SCORE_CHANGE_A2] + \
            well * model_params[P_WELL_HEIGHT_A1] + well ** 2 * model_params[P_WELL_HEIGHT_A2]
    return heuristic

# simulate full game with model
def simulate(src, playback=False):
    model_params, rand_seed, epoch_num, cid = src
    heuristic = gen_score_heuristic(model_params)
    local_rand = random.Random()
    local_rand.seed(rand_seed)
    def gen_piece() -> Piece:
        return Piece(PieceType(local_rand.randint(0,6)))
    state = State(active_piece = gen_piece(), next_piece = gen_piece())
    score = 0
    line_clears = 0
    moves = 0
    while state.valid():
        placements: list[Placement] = find_placements(state, gen_piece(), False)
        chosen = chose_placement(placements, heuristic, False)
        score += chosen.score_gain
        line_clears += chosen.line_clears
        state = chosen.new_state
        if playback:
            render(chosen.new_state, score, line_clears)
            
        moves += 1
    if playback: return
    print(f"epoch: {epoch_num+1} child: {cid+1}, score: {score}, moves: {moves}, line clears: {line_clears}")
    return (score, moves, line_clears)

# evolutionary training
def train(source_path: str, data_path: str, epochs: int):
    # check if existing weight values exist and load if possible
    group: list[dict[str,float]] = []
    if os.path.isfile(source_path):
        group = load_group(source_path)
    
    # simulate evolution
    sim_pool = Pool(NUM_CORES)
    for epoch_num in range(epochs):
        # add random parents
        num_rand_parents = max(GROUP_SIZE + RAND_PARENTS - len(group), 0)
        for _ in range(num_rand_parents):
            group.append(rand_model())
        print(f"added {num_rand_parents} random parents")

        # generate children
        def gen_child(p1: dict[str,float], p2: dict[str,float]):
            c = p1.copy()
            for param_name in P_LIST:
                c[param_name] = rand.normalvariate(p1[param_name] * 0.5 + p2[param_name] * 0.5, MUT_STD * (abs(p1[param_name] - p2[param_name])))
            return c
        children = [model for model in group]
        weights = [pow(GEO_BASE, i) for i in range(len(group))]
        indices = [i for i in range(len(group))]
        while len(children) < TRAINING_GROUP_SIZE:
            p = rand.choices(indices, weights=weights, k=2)
            if p[0] == p[1]: continue
            children.append(gen_child(group[p[0]], group[p[1]]))
        print(f"{len(children)-len(group)} children created")

        # simulate games
        seed = random.randint(0, 10000000000)
        def gen_src(index: int, model_params: dict[str,float]):
            return (model_params, seed, epoch_num, index)
        try:
            async_res = sim_pool.map_async(simulate, [gen_src(i, c) for i, c in enumerate(children)])
            while not async_res.ready(): sleep(1)
            children = list(zip(children, async_res.get()))
        except KeyboardInterrupt:
            print("KILL")
            sim_pool.terminate()
            exit(-1)
        print(f"epoch {epoch_num+1} simulation finished")
        
        # keep best children
        children.sort(key=lambda x : -x[1][2]) # sort by line clears
        best = children[0][1][2]
        average_score = sum(c[1][0] for c in children) / len(children)
        average_moves = sum(c[1][1] for c in children) / len(children)
        average_line_clears = sum(c[1][2] for c in children) / len(children)

        group = [x[0] for x in children[0:min(len(children), GROUP_SIZE)]]

        # normalize group
        param_avg = sum(sum(abs(x[param]) for param in P_LIST) for x in group) / (len(P_LIST) * len(group))
        pdiv = 1 / param_avg
        for x in group:
            for param in P_LIST:
                x[param] *= pdiv

        # store results
        store_group(source_path, group)
        write_data(data_path, average_score, average_moves, average_line_clears)

        # playback best
        simulate(gen_src(0, group[0]), True)
        print(f"best: {best} line clears")
        print(f"average score: {average_score}")
        print(f"average moves: {average_moves}")
        print(f"average line clears: {average_line_clears}")
    
    # cleanup
    sim_pool.close()

def main():
    train("training_cache.txt", "training_data.txt", 1000)

if __name__ == "__main__":
    render_controls.enabled = True
    render_controls.frame_time = 0.01
    main()