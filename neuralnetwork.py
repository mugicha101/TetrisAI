import numpy as np
import heuristic as hp
import model
import placement_search as ps

class NeuralNetwork:
    def __init__(self, weight_dict):
        self.weights1 , self.weights2 = self.parseInputs(weight_dict)
    
    def parseInputs(self, dict):
        w1 = [[dict[f"param{node}{feature}"] for feature in range(6)] for node in range(5)]
        w2 = [dict[f"output{node}"] for node in range(5)]

        return w1, w2
        

    def forward(self, x: np.ndarray) -> np.array:
        return np.dot(x, self.weights)
    
    def evaluate(self, placement: ps.Placement):
        state = placement.new_state

        heights = hp.column_heights(state)
        holes = hp.hole_count(state)
        max_heights = max(heights)
        sum_heights = sum(heights)
        bumpiness = hp.least_squares(state, 0)
        line_clears = placement.line_clears
        score_gain = placement.score_gain

        input_data = np.ndarray([holes, max_heights, sum_heights, bumpiness, line_clears, score_gain])

        return list(np.dot(np.dot(self.input_data, self.weights1), self.weights2))




    #array of input data -> we will have a node in the hidden layer for each one




