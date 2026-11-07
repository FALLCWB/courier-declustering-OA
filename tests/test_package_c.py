"""Package C (preregistration-addendum-C.md): the indep behavior setting (E6), the stay policy, noisy demand input, the
Ashkrof setting and the four run plans."""
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CITY = (ROOT / "sim/city/curitiba").exists()
MAN = {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"], "levels": ["tight", "normal", "loose"]}


def test_indep_homes_follow_the_share_from_each_couriers_own_stream():
    from sim.scenarios import indep_homes
    share = np.array([0.0, 1.0, 3.0, 0.0, 6.0])
    h = indep_homes(share, 4000, seed=1001)
    assert set(np.unique(h)) <= {1, 2, 4}
    f = np.bincount(h, minlength=5) / len(h)
    assert abs(f[4] - 0.6) < 0.03 and abs(f[1] - 0.1) < 0.02
    assert (indep_homes(share, 10, seed=1001) == h[:10]).all()          # keyed by courier, not by fleet size
    assert not (indep_homes(share, 4000, seed=1002) == h).all()


def test_stay_policy_assigns_like_nearest_courier_and_sends_no_command():
    from models import MODELS
    pol = MODELS["stay"](seed=1)
    assert hasattr(pol, "relocate") and pol.relocate(None) == []


def test_noisy_demand_has_mean_one_cv_point_two_per_zone_fixed_for_the_episode():
    from sim.noise import zone_factors
    f = zone_factors(5000, seed=1001, cv=0.2)
    assert abs(f.mean() - 1.0) < 0.01 and abs(f.std() / f.mean() - 0.2) < 0.01
    assert (zone_factors(5000, seed=1001, cv=0.2) == f).all() and not (zone_factors(5000, seed=1002, cv=0.2) == f).all()
    assert (zone_factors(10, seed=1001, cv=0.2) == f[:10]).all()        # keyed by (seed, zone)
    assert (zone_factors(10, seed=1001, cv=0.0) == 1.0).all()


def test_noisy_input_swaps_the_demand_only_inside_the_policy_call_and_keeps_its_arm():
    from sim.noise import NoisyDemand, noisy_input

    class Demand:
        def expected_pickups(self, t0, t1):
            return np.ones(4)

        def expected_dropoffs(self, t0, t1):
            return 2 * np.ones(4)
        other = "kept"

    class Sim:
        demand = Demand()

    class View:
        sim = Sim()

    class Assigner:
        def assign(self, v):
            return v.sim.demand.expected_pickups(0, 1), v.sim.demand.other

    class Mover(Assigner):
        def relocate(self, v):
            return list(v.sim.demand.expected_dropoffs(0, 1))

    zone = np.array([0, 0, 1, 1])
    noisy = NoisyDemand(View.sim.demand, zone, np.array([0.5, 2.0]))
    a = noisy_input(Assigner(), noisy)
    m = noisy_input(Mover(), noisy)
    assert not hasattr(a, "relocate") and hasattr(m, "relocate")
    got, other = a.assign(View())
    assert list(got) == [0.5, 0.5, 2.0, 2.0] and other == "kept"
    assert m.relocate(View()) == [1.0, 1.0, 4.0, 4.0]
    assert isinstance(View.sim.demand, Demand)                          # the true demand is back after the call


def test_package_c_plans():
    from sim.run_extension import jobs
    e6 = jobs("c_e6", MAN)
    assert len(e6) == 9 * 10 * 150 and {j["behavior"] for j in e6} == {"indep"} and {j["set"] for j in e6} == {"e6"}
    assert {j["scenario"] for j in e6} == {"big_cluster", "three_clusters", "mixed"}
    assert {j["obedience"] for j in e6 if j["model"] in ("zhu", "jusup")} == {1.0}
    st = jobs("c_stay", MAN)
    assert len(st) == 16 * 150 and {j["model"] for j in st} == {"stay"} and {j["obedience"] for j in st} == {1.0}
    no = jobs("c_noise", MAN)
    assert len(no) == 16 * 4 * 30 and {j["model"] for j in no} == {"forecast", "li", "zhu", "jusup"}
    assert {j["seed"] for j in no} == set(range(1001, 1031)) and {j["set"] for j in no} == {"noise"}
    ak = jobs("c_ashkrof", MAN)
    assert len(ak) == 16 * 10 * 30 and {j["behavior"] for j in ak} == {"ashkrof"}
    assert Counter(j["scenario"] for j in ak)["meetup"] == 10 * 30


@pytest.mark.skipif(not CITY, reason="needs the built city")
def test_indep_changes_only_the_homes():
    from sim.runner import Experiment
    ex = Experiment(ROOT)
    _, a = ex.episode("big_cluster", "tight", 1001, "nearest", setting="fitted", trace=True)
    _, b = ex.episode("big_cluster", "tight", 1001, "nearest", setting="indep", trace=True)
    assert (a.fleet.start == b.fleet.start).all() and (a.fleet.home == a.fleet.start).all()
    assert (b.fleet.home != b.fleet.start).mean() > 0.9
    assert (np.asarray(a.orders.placed) == np.asarray(b.orders.placed)).all()


@pytest.mark.skipif(not CITY, reason="needs the built city")
def test_stay_at_zero_obedience_equals_nearest_courier():
    from sim.runner import Experiment
    ex = Experiment(ROOT)
    a, _ = ex.episode("big_cluster", "tight", 1001, "nearest")
    b, _ = ex.episode("big_cluster", "tight", 1001, "stay", obedience=0.0)
    keys = [k for k in a if k not in ("model", "obedience", "seconds") and not k.startswith("events")]
    for k in keys:
        assert (a[k] == b[k]) or (a[k] != a[k] and b[k] != b[k]), k


# ---- C6 (instructions 2026-11-07, package C extra): homes where customers live, setting `resid`

def test_resid_homes_come_from_their_own_stream():
    from sim.scenarios import indep_homes
    share = np.array([0.0, 1.0, 3.0, 0.0, 6.0])
    a = indep_homes(share, 4000, seed=1001, tag=42)
    assert (indep_homes(share, 10, seed=1001, tag=42) == a[:10]).all()
    assert (a != indep_homes(share, 4000, seed=1001)).mean() > 0.3          # not the `indep` stream (tag 41)
    f = np.bincount(a, minlength=5) / len(a)
    assert abs(f[4] - 0.6) < 0.03 and f[0] == 0 and f[3] == 0


def test_resid_plan():
    from sim.run_extension import jobs
    rs = jobs("c_resid", MAN)
    assert len(rs) == 9 * 10 * 30 and {j["behavior"] for j in rs} == {"resid"} and {j["set"] for j in rs} == {"resid"}
    assert {j["seed"] for j in rs} == set(range(1001, 1031))
    assert {j["scenario"] for j in rs} == {"big_cluster", "three_clusters", "mixed"}
    assert {j["obedience"] for j in rs if j["model"] in ("zhu", "jusup")} == {1.0}
    assert "nearest" in {j["model"] for j in rs}


@pytest.mark.skipif(not CITY, reason="needs the built city")
def test_resid_draws_homes_where_drop_offs_are_expected_and_changes_only_the_homes():
    from sim.runner import Experiment
    ex = Experiment(ROOT)
    _, a = ex.episode("big_cluster", "tight", 1001, "nearest", setting="indep", trace=True)
    _, b = ex.episode("big_cluster", "tight", 1001, "nearest", setting="resid", trace=True)
    assert (a.fleet.start == b.fleet.start).all() and (b.fleet.home != a.fleet.home).mean() > 0.5
    assert (np.asarray(a.orders.placed) == np.asarray(b.orders.placed)).all()
    drop = ex.base.expected_dropoffs(0, 14400.0)
    assert (drop[b.fleet.home] > 0).all()
    assert ex.behavior_params("resid").p_return == ex.behavior_params("fitted").p_return


# ---- Part 3 at the wide-grid recalibration (DECISIONS.md, 2026-11-07): setting `ashkrofw`

def test_ashkrofw_reads_the_wide_grid_values_with_the_part_time_coefficient_at_zero(tmp_path):
    import json
    from types import SimpleNamespace
    from sim.runner import Experiment
    (tmp_path / "sim/params").mkdir(parents=True)
    (tmp_path / "sim/params/behavior_ashkrof_wide.json").write_text(json.dumps({"p_return": 0.7, "asc_stay": -4.5}))
    bp = Experiment.behavior_params(SimpleNamespace(root=tmp_path), "ashkrofw")
    assert bp.p_return == 0.7 and bp.coef["asc_stay"] == -4.5 and bp.coef["part_time_stay"] == 0.0


def test_ashkrof_wide_plan():
    from sim.run_extension import jobs
    a, w = jobs("c_ashkrof", MAN), jobs("c_ashkrof_wide", MAN)
    assert len(w) == len(a) == 16 * 10 * 30 and {j["behavior"] for j in w} == {"ashkrofw"} and {j["set"] for j in w} == {"ashkrof_wide"}
    assert sorted((j["scenario"], j["level"], j["model"], j["seed"]) for j in w) == sorted((j["scenario"], j["level"], j["model"], j["seed"]) for j in a)
