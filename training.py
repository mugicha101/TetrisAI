from model import *
from placement_search import Placement
from placement_search import find_placements
from heuristic import *
from threading import Thread
from time import sleep
import signal
import random
import os

GROUP_SIZE = 10 # size of remaining group per epoch
CHILD_COUNT = 3 # number of children produced by each pair of models in group per epoch
MUT_STD = 0.5 # standard deviation to mutate each param by when crossbreeding = MUT_STD * (diff between this param in parent)
NUM_THREADS = 8 # number of threads to use

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
P_LIST = [P_LINE_CLEAR_A1, P_LINE_CLEAR_A2, P_COL_SUM_A1, P_COL_SUM_A2, P_MAX_COL_A1, P_MAX_COL_A2, P_SCORE_CHANGE_A1, P_SCORE_CHANGE_A2, P_BUMPINESS_A1, P_BUMPINESS_A2, P_TARGET_SLOPE]

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
    model_params[P_TARGET_SLOPE] = rand.uniform(-0.5, 0.5)
    return model_params

def gen_score_heuristic(model_params: dict[str,float]) -> Callable[[Placement],float]:
    def heuristic(placement: Placement) -> float:
        s = placement.new_state
        cols = column_heights(s)
        col_sum = sum(cols)
        max_col = max(cols)
        bumpiness = least_squares(s, model_params[P_TARGET_SLOPE])

        return \
            placement.line_clears * model_params[P_LINE_CLEAR_A1] + placement.line_clears ** 2 * model_params[P_LINE_CLEAR_A2] + \
            col_sum * model_params[P_COL_SUM_A1] + col_sum ** 2 * model_params[P_COL_SUM_A2] + \
            max_col * model_params[P_MAX_COL_A1] + max_col ** 2 * model_params[P_MAX_COL_A2] + \
            bumpiness * model_params[P_BUMPINESS_A1] + bumpiness ** 2 * model_params[P_BUMPINESS_A2] + \
            placement.score_gain * model_params[P_SCORE_CHANGE_A1] + placement.score_gain ** 2 * model_params[P_SCORE_CHANGE_A2]
    return heuristic

# simulate full game with model
def simulate(src_list: list[list], rand_seed: int, epoch_num: int, tid: int):
    for sid, src in enumerate(src_list):
        model_params = src[0]
        heuristic = gen_score_heuristic(model_params)
        local_rand = random.Random()
        local_rand.seed(rand_seed)
        def gen_piece() -> Piece:
            return Piece(PieceType(local_rand.randint(0,6)))
        state = State(active_piece = gen_piece(), next_piece = gen_piece())
        score = 0
        while state.valid():
            placements: list[Placement] = find_placements(state, gen_piece(), False)
            chosen = chose_placement(placements, heuristic, False)
            score += chosen.score_gain
            state = chosen.new_state
        src.append(score)
        print(f"epoch {epoch_num+1} thread {tid+1} child {sid} score {score}")

# evolutionary training
def train(source_path: str, epochs: int):
    # check if existing weight values exist and load if possible
    group: list[dict[str,float]] = {}
    if os.path.isfile(source_path):
        group = load_group(source_path)
    else:
        # generate random group
        group = [rand_model() for _ in range(GROUP_SIZE)]
    
    # simulate evolution
    for epoch_num in range(epochs):
        # generate children
        def gen_child(p1: dict[str,float], p2: dict[str,float]):
            c = p1.copy()
            for param_name in P_LIST:
                c[param_name] = rand.normalvariate(p1[param_name] * 0.5 + p2[param_name] * 0.5, MUT_STD * (abs(p1[param_name] - p2[param_name])))
            return c
        children = []
        thread_srcs = [[] for _ in range(NUM_THREADS)]
        for i in range(len(group)):
            for j in range(i+1,len(group)):
                for k in range(CHILD_COUNT):
                    children.append([gen_child(group[i], group[j])])
                    thread_srcs[(len(children)-1) % NUM_THREADS].append(children[-1])
        print(f"{len(children)} children created")

        # simulate games
        seed = random.randint(0, 10000000000)
        threads = []
        try:
            for i in range(NUM_THREADS):
                src = thread_srcs[i]
                thread = Thread(target=simulate, args=(src, seed, epoch_num, i))
                thread.daemon = True
                threads.append(thread)
                thread.start()
            for i in range(NUM_THREADS):
                while threads[i].is_alive(): sleep(1)
                threads[i].join()
        except KeyboardInterrupt:
            print("KILL")
            for i in range(NUM_THREADS):
                threads[i].join(timeout=0)
        print(f"epoch {epoch_num+1} simulation finished")
        
        # keep best children
        children.sort(key=lambda x : -x[1])
        print(f"best score: {children[0][1]}")

        group = [x[0] for x in children[0:min(len(children), GROUP_SIZE)]]

        # store results
        store_group(source_path, group)

def main():
    train("training_cache.txt", 1000)

if __name__ == "__main__":
    main()