import numpy as np
import heuristic as hp
from model import *
import placement_search as ps

N_IN = 8
N_HIDDEN1 = 20
N_HIDDEN2 = 15
N_HIDDEN3 = 10

P_LIST = [f"w1{r}{c}" for c in range(N_IN) for r in range(N_HIDDEN1)] + [f"w2{r}{c}" for c in range(N_HIDDEN1) for r in range(N_HIDDEN2)] + [f"w3{r}{c}" for c in range(N_HIDDEN2) for r in range(N_HIDDEN3)] + [f"w4{c}" for c in range(N_HIDDEN3)]

class NeuralNetwork:
    def __init__(self, weight_dict):
        self.w1 , self.w2, self.w3, self.w4 = self.parseInputs(weight_dict)
    
    def parseInputs(self, dict):
        w1 = [[dict[f"w1{r}{c}"] for c in range(N_IN)] for r in range(N_HIDDEN1)]
        w2 = [[dict[f"w2{r}{c}"] for c in range(N_HIDDEN1)] for r in range(N_HIDDEN2)]
        w3 = [[dict[f"w3{r}{c}"] for c in range(N_HIDDEN2)] for r in range(N_HIDDEN3)]
        w4 = [dict[f"w4{c}"] for c in range(N_HIDDEN3)]

        return w1, w2, w3, w4
        

    def forward(self, x: np.ndarray) -> np.array:
        return np.dot(x, self.weights)
    
    def evaluate(self, placement: ps.Placement):
        state = placement.new_state

        heights = hp.column_heights(state)
        holes = float(hp.hole_count(state))
        max_heights = float(max(heights))
        sum_heights = float(sum(heights))
        bumpiness = float(hp.least_squares(state, 0))
        line_clears = float(placement.line_clears)
        score_gain = float(placement.score_gain)
        well_covering = float(hp.well_covering(state))
        num_wells = float(hp.num_wells(heights))

        input_data = np.array([holes, max_heights, sum_heights, bumpiness, line_clears, score_gain, well_covering, num_wells], dtype=np.float32)

        return np.dot(self.w4, np.dot(self.w3, np.dot(self.w2, np.dot(self.w1, input_data))))




    #array of input data -> we will have a node in the hidden layer for each one




