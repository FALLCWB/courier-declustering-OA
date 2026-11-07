"""sim/analysis_extension.py on synthetic episodes built from the runner's own job lists: family sizes, pairing by seed,
one planted effect that must come out established, the frozen-rerun check and the outputs."""
import json
import sys

import numpy as np
import pandas as pd

MAN = {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"], "levels": ["tight", "normal", "loose"]}
FROZEN = ["w1_rule_min", "w1_rule_first30_min", "w1_min", "w1_idle_weighted_min", "p90_c2d_min", "mean_c2d_min",
          "late_rate", "tv", "gini_idle", "uncovered", "extra_km_per_order", "idle_km_per_order", "earnings_gini",
          "food_wait_mean_min", "food_wait_p90_min", "unassigned_over_30min_share", "delivered", "undelivered", "orders"]


def rows(js, rng):
    out = []
    for j in js:
        base = 5.0 + 0.3 * (j["seed"] % 7)                         # shared by every model on a seed: pairing matters
        r = {**j, "blas_threads": 30}
        for k in FROZEN:
            r[k] = base + rng.normal(0, 0.01)
        r["delivered"], r["undelivered"], r["orders"] = 12000, 0, 12000
        if j["model"] == "xu":                                     # planted: Xu cuts W1 by 2 min everywhere
            r["w1_rule_min"] -= 2.0
        r["w1_rule_60min_after_min"] = base + rng.normal(0, 0.01)
        r["w1_rule_series"] = list(base + rng.normal(0, 0.01, 240))
        out.append(r)
    return out


def write(path, rs):
    path.mkdir(parents=True, exist_ok=True)
    (path / "episodes.jsonl").write_text("\n".join(json.dumps(r) for r in rs) + "\n")


def test_analysis_runs_the_five_families_and_finds_a_planted_effect(tmp_path, monkeypatch):
    from sim.run_extension import jobs
    import sim.analysis_extension as an
    rng = np.random.default_rng(1)
    full = rows(jobs("full:4", MAN), rng)
    write(tmp_path / "full", [r for r in full if r["set"] != "explore" or r["seed"] <= 1004])
    near = pd.DataFrame([r for r in full if r["model"] == "nearest"])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    f1 = [{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "hi": 0.3,
           "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]
          for mo in ("foodmatch", "forecast", "backpressure")]
    pd.DataFrame(f1).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": s, "level": "normal", "model": mo, "class": "does not decluster"}   # big_cluster is no Q1 cell
                  for s in ("scattered", "burst", "big_cluster")
                  for mo in ("foodmatch", "forecast", "backpressure")]).to_csv(tmp_path / "first" / "classes.csv", index=False)
    s8 = [{**{k: r[k] for k in FROZEN}, "family": "F1" if r["behavior"] == "fitted" else "F2", "scenario": r["scenario"],
           "level": r["level"], "behavior": r["behavior"], "model": r["model"], "seed": r["seed"]}
          for r in full if r["set"] == "frozen_rerun"]
    write(tmp_path / "s8", s8)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", str(out), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")), "--n", "4"])
    an.main()
    con = pd.read_csv(out / "contrasts.csv")
    assert con.groupby("family").size().to_dict() == {"E1": 60, "E2": 133, "E3": 240, "E4": 532, "E5": 192}
    xu = con[(con.family == "E1") & (con.model == "xu") & (con.metric == "w1_rule_min")]
    assert len(xu) == 6 and xu.established.all() and np.allclose(xu["mean"], -2.0, atol=0.05)
    others = con[(con.family == "E1") & (con.model != "xu")]
    assert not others.established.any()
    assert (con.n == 4).all()
    checks = json.loads((out / "checks.json").read_text())
    assert checks["frozen_vs_s8"]["compared"] == len(s8) and checks["frozen_vs_s8"]["differ"] == 0
    cl = pd.read_csv(out / "classes.csv")
    assert set(cl[(cl.question == "Q1") & (cl.model == "xu")]["class"]) == {"prevents at no delivery cost"}
    assert len(cl[cl.question == "Q2"]) == 80 and set(cl[cl.question == "Q2"].p90_source) == {"E2", "F1 (first round)"}
    pr = pd.read_csv(out / "profile.csv").set_index("model")
    assert json.loads(pr.loc["foodmatch", "q1_classes"]) == {"does not prevent": 2}      # scattered and burst only
    assert not (con.established & con.lower_at_least_sesoi & (con.model != "xu")).any()
    for f in ("class_counts.csv", "undo.csv", "costs.csv", "descriptive.csv", "profile.csv", "results.md"):
        assert (out / f).exists()


def test_analysis_runs_e1_and_e2_alone_while_the_other_cells_are_still_running(tmp_path, monkeypatch):
    """Filipe, 2026-11-04: G8 goes out with E1 and E2; here only phase 1 of the full runs is in the file."""
    from sim.run_extension import jobs, phase
    import sim.analysis_extension as an
    rng = np.random.default_rng(2)
    full = rows([j for j in jobs("full:4", MAN) if phase(j) == 1], rng)
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest"])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    pd.DataFrame([{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "hi": 0.3,
                   "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]
                  for mo in ("foodmatch", "forecast", "backpressure")]).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": "scattered", "level": "normal", "model": "foodmatch", "class": "does not decluster"}]).to_csv(
        tmp_path / "first" / "classes.csv", index=False)
    write(tmp_path / "s8", [{"family": "F1", "scenario": "x", "level": "x", "behavior": "x", "model": "x", "seed": 0}])
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", str(out), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")),
                                      "--n", "4", "--families", "E1,E2"])
    an.main()
    con = pd.read_csv(out / "contrasts.csv")
    assert con.groupby("family").size().to_dict() == {"E1": 60, "E2": 133}
    ds = pd.read_csv(out / "descriptive.csv")
    assert set(ds[ds.part.isin(["ride", "explore"])].status) == {"pending: runs not complete"}


def test_analysis_reads_the_frozen_three_on_q2_from_the_fresh_block_beside_the_frozen_seeds(tmp_path, monkeypatch):
    """R4: the frozen three's Q2 contrasts are computed again on seeds 5001 on, paired with nearest courier on the same
    seeds, with Holm over the 160 contrasts of E2 in which they replace the frozen-seed ones (their p90 on the starts
    included, which E2 takes from F1); a planted cut in the fresh block only must come out there and not in E2."""
    from sim.run_extension import jobs, phase
    import sim.analysis_extension as an
    rng = np.random.default_rng(3)
    full = rows([j for j in jobs("full:4", MAN) if phase(j) == 1], rng)
    for r in full:
        if r["set"] == "fresh_q2" and r["model"] == "foodmatch":
            r["w1_rule_60min_after_min"] -= 2.0
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest" and r["seed"] < 5001])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    pd.DataFrame([{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "hi": 0.3,
                   "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]
                  for mo in ("foodmatch", "forecast", "backpressure")]).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": "scattered", "level": "normal", "model": "foodmatch", "class": "does not decluster"}]).to_csv(
        tmp_path / "first" / "classes.csv", index=False)
    write(tmp_path / "s8", [{"family": "F1", "scenario": "x", "level": "x", "behavior": "x", "model": "x", "seed": 0}])
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", str(out), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")),
                                      "--n", "4", "--families", "E1,E2"])
    an.main()
    con = pd.read_csv(out / "contrasts.csv")
    fr = pd.read_csv(out / "contrasts_e2_fresh.csv")
    assert len(fr) == 160 and set(fr.family) == {"E2-fresh"}
    assert set(fr[fr.model.isin(an.FROZEN3)].seeds) == {"5001-5004"} and set(fr[~fr.model.isin(an.FROZEN3)].seeds) == {"1001-1004"}
    fm = fr[(fr.model == "foodmatch") & (fr.metric == an.W160)]
    assert len(fm) == 10 and (fm["mean"] < -1.9).all()
    old = con[(con.family == "E2") & (con.model == "foodmatch") & (con.metric == an.W160)]
    assert (old["mean"].abs() < 0.1).all()
    cl = pd.read_csv(out / "classes_e2_fresh.csv")
    assert set(cl.model) == set(an.FROZEN3) and len(cl) == 30 and set(cl.p90_source) == {"E2-fresh"}
    ud = pd.read_csv(out / "undo_e2_fresh.csv")
    assert set(ud.model) == {"nearest", *an.FROZEN3} and len(ud) == 40
    text = (out / "results.md").read_text()
    assert "fresh seed block" in text and "| E2-fresh (R4) | 160 |" in text


def test_short_sweep_families_hold_the_return_values_run(tmp_path, monkeypatch):
    """Filipe's 48-h rule (2026-11-04): past 48 h the sweep runs at return probability 0 and 1 only; E3 and E4 then hold
    E1's and E2's contrasts at those two values (120 and 266), with Holm within each family as run."""
    from sim.run_extension import jobs
    import sim.analysis_extension as an
    rng = np.random.default_rng(11)
    full = rows([j for j in jobs("full:4:short", MAN) if j["set"] != "explore"], rng)
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest" and r["seed"] < 5001])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    pd.DataFrame([{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "hi": 0.3,
                   "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]
                  for mo in ("foodmatch", "forecast", "backpressure")]).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": "scattered", "level": "normal", "model": "foodmatch", "class": "does not decluster"}]).to_csv(
        tmp_path / "first" / "classes.csv", index=False)
    write(tmp_path / "s8", [{"family": "F1", "scenario": "x", "level": "x", "behavior": "x", "model": "x", "seed": 0}])
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", str(out), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")),
                                      "--n", "4", "--families", "E1,E2,E3,E4,E5", "--sweep", "p0,p1"])
    an.main()
    con = pd.read_csv(out / "contrasts.csv")
    assert con.groupby("family").size().to_dict() == {"E1": 60, "E2": 133, "E3": 120, "E4": 266, "E5": 192}
    assert set(con[con.family.isin(["E3", "E4"])].behavior) == {"p0", "p1"}
