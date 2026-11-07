"""Order demand: Poisson arrivals with a time profile, customers by population, restaurants by gravity.

A demand model is a list of components. Each component has an arrival rate per minute over the episode
and a customer weight per cell; the restaurant of an order is drawn from the restaurants near the
customer with weight restaurants[r] * exp(-T[r, k] / gravity_s). Every model, policy and behavior
setting sees the same order stream for a given seed (common random numbers).
"""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Orders:
    placed: np.ndarray   # seconds from episode start, sorted
    rest: np.ndarray     # restaurant cell index
    cust: np.ndarray     # customer cell index
    ready: np.ndarray    # absolute time the food is ready, seconds
    due: np.ndarray      # promised door time, seconds
    approach_mult: np.ndarray = None   # factor on the courier's ride to the restaurant (mean 1); policies never see it
    ride_mult: np.ndarray = None       # factor on the pickup-to-door time, ride plus door overhead (mean 1)

    def __post_init__(self):
        if self.approach_mult is None:
            self.approach_mult = np.ones(len(self.placed))
        if self.ride_mult is None:
            self.ride_mult = np.ones(len(self.placed))

    def __len__(self):
        return len(self.placed)


@dataclass
class Component:
    rate_per_min: np.ndarray   # expected orders per minute, one value per minute of the episode
    cust_weight: np.ndarray    # customer weight per cell (need not sum to one)


@dataclass
class Demand:
    city: object
    components: list
    gravity_s: float = 600.0          # travel-time scale of restaurant choice; calibrated in step 5
    prep_s: np.ndarray = field(default_factory=lambda: np.array([720.0]))  # empirical sample of preparation times
    promise_s: float = 2400.0         # promised order-to-door time (Grubhub MDRP target: 40 min); intercept
    promise_per_km_s: float = 0.0     # added per straight-line km from restaurant to customer (calibrated in step 5)
    promise_floor_s: float = 0.0      # shortest promise
    ride_sigma: float = 0.0           # log-scale SD of the lognormal travel-time factors (mean 1); calibrated in S2

    def __post_init__(self):
        city = self.city
        self.rest_cells = np.flatnonzero(city.rest > 0)
        # choice[k] = probability of each restaurant cell for a customer in cell k
        w = city.rest[self.rest_cells][None, :] * np.exp(-city.T[np.ix_(self.rest_cells, np.arange(city.n))].T
                                                          / self.gravity_s)
        self.choice = w / w.sum(axis=1, keepdims=True)
        self.choice_cdf = np.cumsum(self.choice, axis=1)
        self.pickup_share = []        # expected share of pickups per cell for each component
        for comp in self.components:
            cw = comp.cust_weight / comp.cust_weight.sum()
            share = np.zeros(city.n)
            share[self.rest_cells] = cw @ self.choice
            self.pickup_share.append(share)

    def expected_pickups(self, t0, t1):
        """Expected number of orders picked up per cell for orders placed in [t0, t1) seconds."""
        out = np.zeros(self.city.n)
        for comp, share in zip(self.components, self.pickup_share):
            m0, m1 = int(t0 // 60), int(np.ceil(t1 / 60))
            out += comp.rate_per_min[m0:m1].sum() * share
        return out

    def expected_dropoffs(self, t0, t1):
        """Expected number of orders delivered per customer cell for orders placed in [t0, t1) seconds."""
        out = np.zeros(self.city.n)
        for comp in self.components:
            m0, m1 = int(t0 // 60), int(np.ceil(t1 / 60))
            out += comp.rate_per_min[m0:m1].sum() * comp.cust_weight / comp.cust_weight.sum()
        return out

    def sample(self, seed):
        rng = np.random.default_rng(np.random.SeedSequence([seed, 1]))
        placed, cust = [], []
        for comp in self.components:
            counts = rng.poisson(comp.rate_per_min)
            t = np.repeat(np.arange(len(counts)) * 60.0, counts) + rng.uniform(0, 60, counts.sum())
            cw = comp.cust_weight / comp.cust_weight.sum()
            placed.append(t)
            cust.append(rng.choice(self.city.n, size=len(t), p=cw))
        placed, cust = np.concatenate(placed), np.concatenate(cust)
        order = np.argsort(placed, kind="stable")
        placed, cust = placed[order], cust[order]
        u = rng.uniform(size=len(placed))
        j = np.minimum((self.choice_cdf[cust] < u[:, None]).sum(axis=1), len(self.rest_cells) - 1)
        rest = self.rest_cells[j]
        ready = placed + rng.choice(self.prep_s, size=len(placed))
        km = self.city.straight_m(rest, cust) / 1000.0
        promise = np.maximum(self.promise_floor_s, self.promise_s + self.promise_per_km_s * km)
        # Travel-time noise: two lognormal factors with mean 1 per order (approach leg, pickup to door), drawn last
        # from the order stream so every model sees the same factors for a seed and the draws above never shift.
        s = self.ride_sigma
        mult = np.exp(s * rng.standard_normal((2, len(placed))) - s * s / 2)
        return Orders(placed=placed, rest=rest.astype(np.int32), cust=cust.astype(np.int32),
                      ready=ready, due=placed + promise, approach_mult=mult[0], ride_mult=mult[1])
