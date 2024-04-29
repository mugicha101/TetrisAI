import numpy as np
import heuristic as hp
from model import *
import placement_search as ps

N_IN = BOARD_DIM[1] + 6
N_HIDDEN = 10

class NeuralNetwork:
    def __init__(self, weight_dict):
        self.weights1 , self.weights2 = self.parseInputs(weight_dict)
    
    def parseInputs(self, dict):
        w1 = [[dict[f"param{node}{feature}"] for feature in range(N_IN)] for node in range(N_HIDDEN)]
        w2 = [dict[f"output{node}"] for node in range(N_HIDDEN)]

        return w1, w2
        

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

        input_data = np.array(heights + [holes, max_heights, sum_heights, bumpiness, line_clears, score_gain], dtype=np.float32)

        return np.dot(self.weights2, np.dot(self.weights1, input_data))




    #array of input data -> we will have a node in the hidden layer for each one




