"""Idle-move moments with known answers: return, null, excess, stay share, bins, courier-weighted bootstrap."""
import math

import numpy as np
import pytest

from sim.core import idle_moments as im


def two_couriers(n=100):
    # courier "a": 10-min gaps from 3 km east of home straight back home; courier "b": 2-min gaps, never moves
    D = np.tile([3000.0, 0.0], (2 * n, 1))
    G = np.vstack([np.zeros((n, 2)), D[:n]])
    H = np.zeros((2 * n, 2))
    courier = np.array(["a"] * n + ["b"] * n)
    gap = np.array([10.0] * n + [2.0] * n)
    return im.prepare(courier, gap, D, G, H, np.random.default_rng(0))


def test_return_null_and_stay_have_their_known_values():
    m = im.moments(two_couriers())
    assert m["ret_2000_5-15"] == 1.0 and m["ret_2000_<5"] == 0.0
    # a 3 km move from 3 km out ends within 2 km of home when cos(theta) <= -7/9
    null = math.acos(7 / 9) / math.pi
    assert m["exc_2000_5-15"] == pytest.approx(1.0 - null, abs=0.03)
    assert m["exc_2000_<5"] == 0.0                     # a courier that never moves has a null of zero too
    assert m["stay_<5"] == 1.0 and m["stay_5-15"] == 0.0
    assert np.isnan(m["ret_2000_15-30"]) and np.isnan(m["stay_>=30"])
    assert m["move_q50"] == pytest.approx(1500.0)       # half the moves are 0 m, half 3,000 m
    assert m["move_mean"] == pytest.approx(1500.0)


def test_bootstrap_weights_resample_whole_couriers():
    p = two_couriers()
    only_a = im.moments(p, np.array([2, 0]))           # courier codes follow sorted labels: a = 0, b = 1
    assert only_a["ret_2000_5-15"] == 1.0 and np.isnan(only_a["stay_<5"]) and only_a["move_q50"] == 3000.0
    reps = im.bootstrap(p, ["ret_2000_5-15", "stay_<5"], 20, np.random.default_rng(1))
    assert reps.shape == (20, 2) and np.nanmax(reps) <= 1.0
