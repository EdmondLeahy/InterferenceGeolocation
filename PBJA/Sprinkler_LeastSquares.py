
from enum import Enum
import numpy as np


class ReturnCodes(Enum):
    SOL_COMPUTED = 1
    MAX_ITERATION_REACHED = 2
    INSUFFICIENT_OBS = -1
    NON_INVERTABLE_MATRIX = -2



def dist(p1, p2):
    d = np.sqrt(np.power(p2[0] - p1[0], 2) + np.power(p2[1] - p1[1], 2))
    return d


class SprinklerLS:

    def __init__(self, obs, rover_pos, x0=[0, 0], dimensions=2, max_iter=10, thresh=1e-5):
        self.pdoa_obs = obs
        self.rover_pos = rover_pos
        self.x0 = np.array(x0)
        self.dimensions = dimensions
        self.max_iter = max_iter
        self.deltas = []
        self.est_xs = [self.x0]
        self.thresh = thresh
        self.est_x = None

    def create_a_row(self, r1_ind, r2_ind):
        """
        A = (x-a/rB1 - x-d/rB2), (y-b/rB1 - x-3/rB2)
        """
        row = []
        for i in range(self.dimensions):
            row.append((self.x0[i] - self.rover_pos[r1_ind][i]) / dist(self.x0, self.rover_pos[r1_ind]) -
                       (self.x0[i] - self.rover_pos[r2_ind][i]) / dist(self.x0, self.rover_pos[r2_ind]))
        return row

    def create_fx(self, r1_ind, r2_ind):
        return dist(self.rover_pos[r1_ind], self.x0) - dist(self.rover_pos[r2_ind], self.x0)

    def iterate(self):
        self.est_x = self.x0
        if len(self.pdoa_obs) < 3:
            return ReturnCodes.INSUFFICIENT_OBS

        for i in range(self.max_iter):

            a_mat_list = []
            w_list = []
            for obs in self.pdoa_obs:
                a_mat_list.append(self.create_a_row(obs[0], obs[1]))
                fx = self.create_fx(obs[0], obs[1])
                w_list.append(fx - obs[2])

            A = np.array(a_mat_list)
            w = np.array(w_list)
            N = np.matmul(np.transpose(A), A)
            U = np.matmul(np.transpose(A), w)
            try:
                delta = np.matmul(np.linalg.inv(N), U)
            except np.linalg.LinAlgError:
                return ReturnCodes.NON_INVERTABLE_MATRIX

            self.est_x = self.est_x + delta

            self.deltas.append(delta)
            self.est_xs.append(self.est_x)
            if all([d < self.thresh for d in delta]):
                break

        if i == self.max_iter:
            return ReturnCodes.MAX_ITERATION_REACHED
