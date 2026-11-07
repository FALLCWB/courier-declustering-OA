"""Package C part 3: the `ashkrof` variant of sim/behavior_fit.py (preregistration-addendum-C.md)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ashkrof_variant_zeroes_the_part_time_coefficient_and_fits_only_beta0_and_the_return_probability():
    sys.argv = ["behavior_fit.py", str(ROOT)]
    from sim import behavior_fit as bf
    flags, grid, over, fixed = bf.variant_setup("ashkrof")
    assert flags == {"single_decision": True} and over == {"part_time_stay": 0.0}
    assert grid["epoch_s"] == [42.0] and grid["cruise_radius_m"] == [2000.0]
    assert len(grid["p_return"]) > 2 and len(grid["asc_stay"]) > 2
    assert fixed == {"epoch_s", "cruise_radius_m"}
    best = {"p_return": 0.75, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": -3.0}
    loc = bf.local_grid(best, fixed)
    assert loc["epoch_s"] == [42.0] and loc["cruise_radius_m"] == [2000.0]
    assert len(loc["p_return"]) == 3 and len(loc["asc_stay"]) == 3
    bf._W["coef_over"] = over
    assert bf.coef({"asc_stay": -2.5})["part_time_stay"] == 0.0 and bf.coef({"asc_stay": -2.5})["asc_stay"] == -2.5
    bf._W.pop("coef_over")
    assert bf.coef({"asc_stay": -2.5})["part_time_stay"] != 0.0
    # the other variants keep their grids and refine every key
    f2, g2, o2, fx2 = bf.variant_setup("single")
    assert o2 == {} and fx2 == set() and g2 == bf.GRID_SINGLE


def test_refinement_goes_on_while_the_best_point_sits_on_an_edge_of_the_explored_values():
    sys.argv = ["behavior_fit.py", str(ROOT)]
    from sim import behavior_fit as bf
    fixed = {"epoch_s", "cruise_radius_m"}
    pt = lambda p, a: {"p_return": p, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": a}
    seen = [pt(p, a) for p in (0.55, 0.65, 0.75) for a in (-3.0, -2.5, -2.0)]
    # interior best: nothing more to run
    assert bf.edge_points(pt(0.65, -2.5), seen, fixed) == []
    # best on the asc_stay edge -2.0: the local grid around it, without the points already run
    new = bf.edge_points(pt(0.65, -2.0), seen, fixed)
    assert new and all(p not in seen for p in new) and max(p["asc_stay"] for p in new) == -1.5
    assert {p["epoch_s"] for p in new} == {42.0} and {p["cruise_radius_m"] for p in new} == {2000.0}
    # best on the p_return edge 0.75 extends p_return upward
    assert max(p["p_return"] for p in bf.edge_points(pt(0.75, -2.5), seen, fixed)) > 0.75
    # a probability of 1 is a hard bound, not an edge to extend past
    seen1 = [pt(p, a) for p in (0.9, 1.0) for a in (-3.0, -2.5, -2.0)]
    assert bf.edge_points(pt(1.0, -2.5), seen1, fixed) == []
