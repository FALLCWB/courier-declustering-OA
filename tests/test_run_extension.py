"""The extension's job lists match preregistration-extension.md section 3 (frozen at 8e082e3)."""
from collections import Counter

MAN = {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"], "levels": ["tight", "normal", "loose"]}


def cells(js):
    return {(j["set"], j["scenario"], j["level"], j["behavior"], j["model"], j["obedience"]) for j in js}


def test_pilot_runs_every_new_cell_at_seeds_1_to_30_with_arm_c_at_zero_and_the_frozen_fitted_cells():
    from sim.run_extension import jobs
    js = jobs("pilot", MAN)
    c = cells(js)
    # new: rows 5 to 8 in 16 start-supply combinations x 5 settings (320), the frozen four on the meet-up (20), arm C at
    # 25 to 100% fitted and 100% in the sweep (256); the ride variant (10); arm C at 0% (32); the frozen four in the 15
    # fitted start cells and nearest courier in the 60 sweep start cells, rerun for the Q2 fields their S7 rows lack,
    # so that every cell's smallest effect comes from the pilot (section 6) (60 + 60)
    assert Counter(x[0] for x in c) == {"new": 596, "ride": 10, "identity": 32, "frozen_rerun": 120}
    sweep = {(x[1], x[2], x[3]) for x in c if x[0] == "frozen_rerun" and x[3] != "fitted"}
    assert len(sweep) == 60 and {x[4] for x in c if x[0] == "frozen_rerun" and x[3] != "fitted"} == {"nearest"}
    assert {j["seed"] for j in js} == set(range(1, 31)) and len(js) == 30 * len(c)
    assert {x[4] for x in c if x[0] == "identity"} == {"zhu", "jusup"} and {x[5] for x in c if x[0] == "identity"} == {0.0}
    assert {x[1] for x in c if x[0] == "ride"} == {"meetup_ride"} and len({x[4] for x in c if x[0] == "ride"}) == 10
    assert {(x[1], x[2]) for x in c if x[1] == "meetup"} == {("meetup", "normal")}


def test_full_runs_rerun_every_frozen_cell_and_drop_arm_c_at_zero():
    from sim.run_extension import jobs
    js = jobs("full:40", MAN)
    c = cells(js)
    assert Counter(x[0] for x in c) == {"new": 596, "ride": 10, "frozen_rerun": 300, "explore": 10, "fresh_q2": 52}
    assert {j["seed"] for j in js if j["set"] != "fresh_q2"} == set(range(1001, 1041))
    assert {j["seed"] for j in js if j["set"] == "explore"} == set(range(1001, 1031))


def test_head_start_runs_the_e1_e2_cells_at_seeds_1001_to_1030_that_every_full_plan_holds():
    """While the pilot runs, idle cores start the phase-1 jobs at seeds 1001 to 1030: n is at least 30 (section 6), so
    every full plan, short or not, holds them in the same order, and the full run resumes past them."""
    from sim.run_extension import jobs, phase, key
    head = jobs("head", MAN)
    assert head and {phase(j) for j in head} == {1} and {j["seed"] for j in head} == set(range(1001, 1031))
    for plan in ("full:30", "full:40", "full:30:short"):
        first = [j for j in jobs(plan, MAN) if phase(j) == 1 and j["seed"] <= 1030]
        assert [key(j) for j in head] == [key(j) for j in first]


def test_full_runs_rerun_the_frozen_four_q2_cells_on_a_fresh_seed_block_right_after_phase_1():
    """R4 (Filipe, 2026-11-05): nearest courier and the frozen three in the ten Q2 cells, with the scattered start as the
    time-to-undo reference, on seeds 5001 to 5000 + n, which no pilot, training, evaluation or check has used; they run
    right after the other phase-1 jobs, before the meet-ups."""
    from sim.run_extension import FRESH0, jobs, phase
    js = jobs("full:40", MAN)
    fr = [j for j in js if j["set"] == "fresh_q2"]
    assert FRESH0 == 5001 and {j["seed"] for j in fr} == set(range(5001, 5041))
    c = cells(fr)
    assert {x[4] for x in c} == {"nearest", "foodmatch", "forecast", "backpressure"} and {x[3] for x in c} == {"fitted"}
    q2 = {(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]} | {("meetup", "normal")}
    assert {(x[1], x[2]) for x in c} == q2 | {("scattered", lvl) for lvl in MAN["levels"]}
    assert len(c) == 52 and len(fr) == 52 * 40
    other = {j["seed"] for p in ("pilot", "explore", "zhu_ties") for j in jobs(p, MAN)}
    other |= {j["seed"] for j in js if j["set"] != "fresh_q2"}
    assert not other & {j["seed"] for j in fr}
    i = [k for k, j in enumerate(js) if j["set"] == "fresh_q2"]
    assert i == list(range(i[0], i[-1] + 1))
    assert all(phase(j) == 1 for j in js[:i[-1] + 1]) and phase(js[i[-1] + 1]) == 2


def test_full_runs_go_in_filipes_order_e1_e2_then_meetups_then_e5_then_the_sweep():
    """Filipe, 2026-11-04: E1 and E2 first, then the exploratory meet-up, then E5, then E3 and E4."""
    from sim.run_extension import jobs, phase
    js = jobs("full:30", MAN)
    ph = [phase(j) for j in js]
    assert ph == sorted(ph) and set(ph) == {1, 2, 3, 4}
    assert all(j["behavior"] == "fitted" and j["obedience"] in (None, 1.0) for j in js if phase(j) == 1)
    assert {j["set"] for j in js if phase(j) == 2} == {"explore", "ride"}
    assert {j["obedience"] for j in js if phase(j) == 3} == {0.25, 0.5, 0.75}
    assert {j["behavior"] for j in js if phase(j) == 4} == {"p0", "p0.25", "p0.5", "p1"}


def test_short_sweep_keeps_return_probabilities_0_and_1_only():
    from sim.run_extension import jobs
    c = cells(jobs("full:30:short", MAN))
    assert {x[3] for x in c} == {"fitted", "p0", "p1"}
    assert Counter(x[0] for x in c) == {"new": 396, "ride": 10, "frozen_rerun": 180, "explore": 10, "fresh_q2": 52}


def test_explore_runs_the_ten_models_on_the_median_meetup_at_seeds_1001_to_1030():
    from sim.run_extension import jobs
    js = jobs("explore", MAN)
    c = cells(js)
    assert len(c) == 10 and {x[1] for x in c} == {"meetup_median"} and {x[5] for x in c} - {None} == {1.0}
    assert {j["seed"] for j in js} == set(range(1001, 1031))


def test_learned_models_run_the_policy_of_training_seed_s_minus_1_mod_5_plus_1():
    from sim.run_extension import policy_kw
    assert policy_kw("xu", 1001, None)["value_path"].name == "xu_value_seed1.npz"
    assert policy_kw("auad", 1007, None)["theta_path"].name == "auad_seed2.npz"
    assert policy_kw("jusup", 30, 0.5) == {"weights_path": policy_kw("jusup", 30, 0.5)["weights_path"], "q": 0.5}
    assert policy_kw("jusup", 30, 0.5)["weights_path"].name == "jusup_seed5.pt"
    assert policy_kw("nearest", 5, None) == {} and policy_kw("zhu", 5, 1.0) == {}


def test_zhu_ties_plan_runs_zhu_with_random_partition_ties_on_three_starts_at_seeds_1001_to_1030():
    from sim.run_extension import job_kw, jobs
    js = jobs("zhu_ties", MAN)
    c = cells(js)
    assert c == {("zhu_random_ties", s, "normal", "fitted", "zhu", 1.0) for s in ("big_cluster", "meetup", "scattered")}
    assert {j["seed"] for j in js} == set(range(1001, 1031)) and len(js) == 90
    assert job_kw(js[0]) == {"tie": "random"}
    assert job_kw({**js[0], "set": "new"}) == {}


def test_a_part_splits_the_jobs_by_seed_so_two_machines_never_run_the_same_job():
    """Two machines share the remaining jobs (Filipe, 2026-11-05): each takes the seeds whose remainder mod m is in its
    set; together they cover every job exactly once, in the run order."""
    from sim.run_extension import in_part, jobs, key
    js = jobs("full:30:short", MAN)
    a = [j for j in js if in_part(j, "3:0")]
    b = [j for j in js if in_part(j, "3:1,2")]
    assert sorted(map(key, a + b)) == sorted(map(key, js)) and not set(map(key, a)) & set(map(key, b))
    assert {j["seed"] % 3 for j in a} == {0} and a == [j for j in js if j["seed"] % 3 == 0]
    assert all(in_part(j, None) for j in js)
