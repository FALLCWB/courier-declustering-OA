"""Baseline dispatch policies. The published models of Part 1 are added in step 8 (models/)."""
import numpy as np
from scipy.optimize import linear_sum_assignment


class NearestIdle:
    """Oldest order first; each takes the available courier that reaches its restaurant soonest."""
    name = "nearest"

    def assign(self, v):
        eta_all = v.delay[None, :] + v.city.T[np.ix_(v.cell, v.rest)].T * v.sf   # [orders, couriers]
        free = np.ones(len(v.couriers), bool)
        pairs = []
        for i in np.argsort(v.placed, kind="stable"):
            if not free.any():
                break
            eta = np.where(free, eta_all[i], np.inf)
            j = int(np.argmin(eta))
            pairs.append((v.orders[i], v.couriers[j]))
            free[j] = False
        return pairs


class BatchMatching:
    """Minimum total time to the restaurants over the batch (Hungarian), older orders first when couriers are short."""
    name = "batch"

    def __init__(self, age_weight=1.0):
        self.age_weight = age_weight

    def assign(self, v):
        cost = v.delay[None, :] + v.city.T[np.ix_(v.cell, v.rest)].T * v.sf
        cost = cost - self.age_weight * (v.t - v.placed)[:, None]
        rows, cols = linear_sum_assignment(cost)
        return [(v.orders[i], v.couriers[j]) for i, j in zip(rows, cols)]
