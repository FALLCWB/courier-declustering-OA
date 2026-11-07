"""C7 and the Ashkrof interval (instructions 2026-11-07, package C extra): grids widened beyond both explored ends, and
bands extended while an end still touches the grid."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _bf():
    sys.argv = ["behavior_fit.py", str(ROOT)]
    from sim import behavior_fit as bf
    return bf


def test_widen_adds_two_steps_beyond_the_explored_ends_within_bounds():
    bf = _bf()
    assert bf.widen("asc_stay", [-3.0, -2.5, -2.0], [-3.5, -1.5]) == [-4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5]
    assert bf.widen("p_return", [0.6, 0.675, 0.75, 0.825], [0.6, 0.825]) == [0.45, 0.525, 0.6, 0.675, 0.75, 0.825, 0.9, 0.975]
    assert bf.widen("p_return", [0.55, 0.95], [0.55, 0.95]) == [0.4, 0.475, 0.55, 0.95, 1.0]          # capped at 1
    assert bf.widen("epoch_s", [30.0, 42.0, 60.0], [29.4, 60.0]) == [15.0, 21.0, 29.4, 30.0, 42.0, 60.0, 84.0, 117.6]
    assert bf.widen("cruise_radius_m", [2000.0], [2000.0]) == [1020.408, 1428.571, 2000.0, 2800.0, 3920.0]


def test_band_points_extend_only_a_touching_end_across_the_other_keys_in_band_values():
    bf = _bf()
    pt = lambda p, a: {"p_return": p, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": a}
    seen = [pt(p, a) for p in (0.6, 0.675, 0.75, 0.825) for a in (-4.0, -3.5, -3.0, -2.5)]
    fixed = {"epoch_s", "cruise_radius_m"}
    # interior bands: nothing to add
    assert bf.band_points({"p_return": [0.675, 0.75], "asc_stay": [-3.5, -3.0]}, seen, fixed) == []
    # asc_stay band touches the highest explored value -2.5: one step up, across p_return's in-band values
    new = bf.band_points({"p_return": [0.675, 0.75], "asc_stay": [-3.0, -2.5]}, seen, fixed)
    assert sorted((p["p_return"], p["asc_stay"]) for p in new) == [(0.675, -2.0), (0.75, -2.0)]
    # a return probability of 1 is a bound
    seen1 = [pt(p, a) for p in (0.925, 1.0) for a in (-4.0, -3.5, -3.0)]
    assert bf.band_points({"p_return": [1.0, 1.0], "asc_stay": [-3.5, -3.5]}, seen1, fixed) == []


def test_local_points_are_keyed_by_name_whatever_the_order_of_the_grid():
    bf = _bf()
    best = {"asc_stay": -3.0, "p_return": 0.75, "cruise_radius_m": 2000.0, "epoch_s": 42.0}     # not local_grid's order
    pts = bf.local_points(best, {"epoch_s", "cruise_radius_m"}, seen=[dict(best)])
    assert all(list(p) == list(best) for p in pts) and dict(best) not in pts
    assert {p["asc_stay"] for p in pts} == {-3.5, -3.0, -2.5} and {p["p_return"] for p in pts} == {0.675, 0.75, 0.825}
    assert {p["epoch_s"] for p in pts} == {42.0} and {p["cruise_radius_m"] for p in pts} == {2000.0}
