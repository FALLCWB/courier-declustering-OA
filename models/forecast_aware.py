"""Forecast-aware matching (Ozkan and Ward, Stochastic Systems 2020): LP-based Hybrid policy over zones.

Fidelity note: models/fidelity/forecast_aware.md; reading notes: literature/model-specs/ozkan-ward-2020.md.
Customer type j = restaurant zone (H3 resolution 8); driver type i = zone where the courier is available.
mu_j = forecast pickups per minute in zone j; lambda_i = forecast drop-offs per minute in zone i (couriers become
free where they deliver; all couriers stay online, so drop-offs are the only driver arrivals). LP (13) is solved at
the start of each 15-minute forecast bin and held as a step function (Sec 4.1, pp.38-39).
"""
import hashlib

import numpy as np
from scipy import sparse
from scipy.optimize import linprog

BIN_S = 900.0          # forecast bins of the arrival shape (15 min); x* is a step function over them
CUTOFF_S = 900.0       # F̄_ij = 1 if the zone-to-zone pickup time is at most 15 min, else 0 (no patience model)
EPS = 0.1              # w_ij = 1 - EPS t_ij / CUTOFF_S, the weighted objective (6)/(13a)

_CACHE = {}


def solve_lp(mu, lam, t_s, cutoff_s=CUTOFF_S, eps=EPS):
    """LP (13): max sum w_ij mu_j x_ij s.t. sum_j mu_j x_ij <= lambda_i (13b), sum_i x_ij <= 1 (13c), x >= 0 (13d).

    mu: [J] customer rates, lam: [I] driver rates, t_s: [I, J] pickup times. Returns dense x [I, J]."""
    I, J = t_s.shape
    ii, jj = np.nonzero((t_s <= cutoff_s) & (mu[None, :] > 0) & (lam[:, None] > 0))
    x = np.zeros((I, J))
    if not len(ii):
        return x
    w = 1.0 - eps * t_s[ii, jj] / cutoff_s
    c = -(w * mu[jj])                                                             # (13a), maximize
    k = np.arange(len(ii))
    A_drv = sparse.csr_matrix((mu[jj], (ii, k)), shape=(I, len(ii)))             # (13b)
    A_cus = sparse.csr_matrix((np.ones(len(ii)), (jj, k)), shape=(J, len(ii)))    # (13c)
    res = linprog(c, A_ub=sparse.vstack([A_drv, A_cus]).tocsr(), b_ub=np.concatenate([lam, np.ones(J)]),
                  bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(f"LP (13) failed: {res.message}")
    x[ii, jj] = np.clip(res.x, 0.0, 1.0)
    return x


def zone_rates(city, demand, t0, t1):
    """mu (pickups by restaurant zone) and lambda (drop-offs by customer zone), per minute, for orders placed in [t0, t1)."""
    minutes = (t1 - t0) / 60.0
    mu = np.bincount(city.zone, weights=demand.expected_pickups(t0, t1), minlength=city.n_zones) / minutes
    lam = np.bincount(city.zone, weights=demand.expected_dropoffs(t0, t1), minlength=city.n_zones) / minutes
    return mu, lam


class ForecastAware:
    """Hybrid policy (Sec 5.1.3): per order, draw the driver zone i with probability x*_ij (none with 1 - sum_i x*_ij);
    offer a courier from zone i if one is available, otherwise the closest courier (CD, eq. 3)."""
    name = "forecast"

    def __init__(self, seed=0, bin_s=BIN_S, cutoff_s=CUTOFF_S, eps=EPS):
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 10]))
        self.bin_s, self.cutoff_s, self.eps = bin_s, cutoff_s, eps
        self._bin, self._cx = None, None
        self.counts = {"orders": 0, "draw_none": 0, "zone_empty": 0}   # closest-courier fallbacks by cause (G3 C3)

    def x_star(self, city, demand, sf, b):
        """Cumulative x* over driver zones for forecast bin b; LPs are cached by their inputs across episodes."""
        mu, lam = zone_rates(city, demand, b * self.bin_s, (b + 1) * self.bin_s)
        key = (hashlib.sha1(mu.tobytes() + lam.tobytes()).hexdigest(), city.n, round(float(sf), 9), self.cutoff_s, self.eps)
        if key not in _CACHE:
            t = city.T[np.ix_(city.zone_rep, city.zone_rep)].astype(float) * sf
            np.fill_diagonal(t, 0.0)                                      # same zone: no zone-to-zone ride
            _CACHE[key] = np.cumsum(solve_lp(mu, lam, t, self.cutoff_s, self.eps), axis=0)
        return _CACHE[key]

    def assign(self, v):
        city, sim = v.city, v.sim
        horizon_bins = int(np.ceil(sim.params.horizon_s / self.bin_s)) - 1
        b = min(int(v.t // self.bin_s), horizon_bins)                                           # step function
        if b != self._bin:
            self._bin, self._cx = b, self.x_star(city, sim.demand, v.sf, b)
        cx = self._cx
        eta = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf                       # [orders, couriers]
        zone_c = city.zone[v.cell]
        free = np.ones(len(v.couriers), bool)
        pairs = []
        for o in np.argsort(v.placed, kind="stable"):                     # one customer at a time (Remark 5)
            if not free.any():
                break
            j = city.zone[v.rest[o]]
            i = int(np.searchsorted(cx[:, j], self.rng.uniform(), side="right"))   # Definition 2 draw; I = none
            cand = free & (zone_c == i) if i < city.n_zones else np.zeros_like(free)
            self.counts["orders"] += 1
            if not cand.any():                                            # outcome 0 or no type-i driver: CD
                self.counts["draw_none" if i >= city.n_zones else "zone_empty"] += 1
                cand = free
            c = int(np.argmin(np.where(cand, eta[o], np.inf)))            # within a zone: the courier that arrives first
            pairs.append((v.orders[o], v.couriers[c]))
            free[c] = False
        return pairs
