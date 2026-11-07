"""Noisy demand information (package C, part 4; preregistration-addendum-C.md, exploratory).

A policy that receives noisy input reads the expected demand multiplied, per zone (H3 resolution 8) and per episode, by
a lognormal factor with mean 1 and coefficient of variation `cv`, fixed for the episode and drawn from its own stream
keyed by (seed, 31, zone). The engine keeps the true demand: W1 and every metric use it. The swap happens only inside the
policy's own calls, and trained policies are not retrained.
"""
import numpy as np


def zone_factors(n_zones, seed, cv):
    """Lognormal factors with mean 1 and coefficient of variation cv, one per zone, keyed by (seed, 31, zone)."""
    if cv == 0:
        return np.ones(n_zones)
    sigma = np.sqrt(np.log(1.0 + cv ** 2))
    return np.array([np.random.default_rng(np.random.SeedSequence([seed, 31, z])).lognormal(-sigma ** 2 / 2, sigma)
                     for z in range(n_zones)])


class NoisyDemand:
    """The demand as a policy sees it: expected pickups and drop-offs of every cell times its zone's factor; every
    other attribute (the order-destination structure, restaurant cells) is the true demand's."""

    def __init__(self, demand, cell_zone, factors):
        self._true, self._f = demand, np.asarray(factors, float)[np.asarray(cell_zone)]

    def expected_pickups(self, t0, t1):
        return self._true.expected_pickups(t0, t1) * self._f

    def expected_dropoffs(self, t0, t1):
        return self._true.expected_dropoffs(t0, t1) * self._f

    def __getattr__(self, name):
        return getattr(self._true, name)


class _NoisyAssign:
    def __init__(self, inner, noisy):
        self._inner, self._noisy = inner, noisy

    def _call(self, fn, v):
        sim = v.sim
        true = sim.demand
        sim.demand = self._noisy
        try:
            return fn(v)
        finally:
            sim.demand = true

    def assign(self, v):
        return self._call(self._inner.assign, v)

    def __getattr__(self, name):
        return getattr(self._inner, name)


class _NoisyRelocate(_NoisyAssign):
    def relocate(self, v):
        return self._call(self._inner.relocate, v)


def noisy_input(policy, noisy):
    """Wrap a policy so it reads `noisy` instead of the true demand during its own calls; an arm C policy keeps its
    `relocate` (the engine reads the arm from it), an assignment policy gets none."""
    return (_NoisyRelocate if hasattr(policy, "relocate") else _NoisyAssign)(policy, noisy)
