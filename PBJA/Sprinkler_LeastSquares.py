

import numpy as np


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
        self.x0s = [self.x0]
        self.thresh = thresh

    def create_a_row(self, r1_ind, r2_ind):
        """
        A = (x-a/rB1 - x-d/rB2), (y-b/rB1 - x-3/rB2), (z-c/rB1 - x-f/rB2)
        """
        row = []
        for i in range(self.dimensions):
            row.append((self.x0[i] - self.rover_pos[r1_ind][i]) / dist(self.x0, self.rover_pos[r1_ind]) -
                       (self.x0[i] - self.rover_pos[r2_ind][i]) / dist(self.x0, self.rover_pos[r2_ind]))
        return row

    def create_fx(self, r1_ind, r2_ind):
        return dist(self.rover_pos[r1_ind], self.x0) - dist(self.rover_pos[r2_ind], self.x0)

    def iterate(self):

        for i in range(15):

            a_mat_list = []
            w_list = []
            for obs in self.pdoa_obs:
                a_mat_list.append(self.create_a_row(obs[0], obs[0]))
                fx = self.create_fx(obs[0], obs[1])
                w_list.append(fx - obs[2])

            A = np.array(a_mat_list)
            w = np.array(w_list)
            N = np.matmul(np.transpose(A), A)
            U = np.matmul(np.transpose(A), w)
            delta = np.matmul(np.linalg.inv(N), U)
            self.x0 = self.x0 + delta

            self.deltas.append(delta)
            self.x0s.append(self.x0)
            if all([d < self.thresh for d in delta]):
                break

