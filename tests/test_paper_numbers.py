"""scripts/paper_numbers.py (instructions of 2026-11-05, section 3) on the synthetic analysis of tests/test_analysis_extension."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_extension import MAN, rows, write  # noqa: E402


def analysed(tmp_path, monkeypatch, plant=None):
    from sim.run_extension import jobs, phase
    import sim.analysis_extension as an
    full = rows([j for j in jobs("full:4", MAN) if phase(j) == 1], np.random.default_rng(5))
    for r in full if plant else ():
        plant(r)
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest" and r["seed"] < 5001])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    pd.DataFrame([{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "lo": -0.1,
                   "hi": 0.3, "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed", "scattered", "burst")
                  for lvl in MAN["levels"] for mo in ("foodmatch", "forecast", "backpressure")]
                 ).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": s, "level": lvl, "model": mo, "class": "does not decluster"} for s in ("scattered", "burst")
                  for lvl in MAN["levels"] for mo in ("foodmatch", "forecast", "backpressure")]
                 ).to_csv(tmp_path / "first" / "classes.csv", index=False)
    write(tmp_path / "s8", [{"family": "F1", "scenario": "x", "level": "x", "behavior": "x", "model": "x", "seed": 0}])
    monkeypatch.setattr(sys, "argv", ["x", str(tmp_path / "out"), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")),
                                      "--n", "4", "--families", "E1,E2"])
    an.main()
    (tmp_path / "ties").mkdir()
    pd.DataFrame([{"scenario": "big_cluster", "metric": "w1_rule_min", "lower_mean": 9.0, "random_mean": 8.5,
                   "diff_mean": -0.5, "lo": -0.7, "hi": -0.3}]).to_csv(tmp_path / "ties" / "zhu_ties.csv", index=False)
    return tmp_path


def test_undo_reports_the_interquartile_range_and_the_censored_count(tmp_path, monkeypatch):
    d = analysed(tmp_path, monkeypatch)
    ud = pd.read_csv(d / "out" / "undo.csv")
    assert {"time_to_undo_q25", "time_to_undo_q75", "censored_count"} <= set(ud.columns)
    assert (ud.time_to_undo_q25 <= ud.time_to_undo_median).all() and (ud.time_to_undo_median <= ud.time_to_undo_q75).all()


def test_paper_numbers_write_every_table_with_its_csv(tmp_path, monkeypatch):
    d = analysed(tmp_path, monkeypatch)
    g = d / "g8"
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers.py"), str(d / "out"), str(d / "full"),
                    str(d / "ties"), str(g), "--n", "4", "--first", str(d / "first")], check=True, cwd=ROOT)
    for f in ("q1_e1", "q2_e2", "q2_e2_fresh", "q2_undo", "q2_descriptive", "q3_costs", "secondary_agreement",
              "profile_counts", "zhu_ties", "training_budgets", "learning_curves"):
        assert (g / f"{f}.csv").exists(), f
    q1 = pd.read_csv(g / "q1_e1.csv")
    assert {"mean", "lo", "hi", "p_holm", "pct_of_nearest", "n", "class", "equivalence"} <= set(q1.columns)
    assert set(q1[q1.model == "jahanshahi"].p_holm.astype(str)) == {"descriptive"}
    assert len(q1[q1.model != "jahanshahi"]) == 60
    q2 = pd.read_csv(g / "q2_e2.csv")
    assert len(q2) == 133 + 20 and "class" in q2
    assert set(q2[q2.model == "jahanshahi"].p_holm.astype(str)) == {"descriptive"}
    assert len(pd.read_csv(g / "q2_e2_fresh.csv")) == 60
    q3 = pd.read_csv(g / "q3_costs.csv")
    assert set(q3.metric) == {"p90_c2d_min", "mean_c2d_min", "late_rate", "idle_km_per_order", "extra_km_per_order"}
    pc = pd.read_csv(g / "profile_counts.csv")
    assert set(pc.question) == {"Q1", "Q2", "Q3", "Q2 fresh block (R4)", "Q3 fresh block (R4)"}
    tb = pd.read_csv(g / "training_budgets.csv")
    assert set(tb.model) == {"xu", "li", "jahanshahi", "auad", "jusup", "forecast"}
    lc = pd.read_csv(g / "learning_curves.csv")
    assert "seed" not in lc.columns and {"model", "training_seed", "scenario", "w1_rule_min_mean"} <= set(lc.columns)
    text = (g / "paper-numbers-G8.md").read_text()
    assert "This research was supported by data provided by Meituan." in text and "fresh seed block" in text


def test_sign_agreement_keeps_a_zero_secondary_difference_apart():
    sys.path.insert(0, str(ROOT / "scripts"))
    from paper_numbers import sign_agreement
    assert sign_agreement(-0.3, -1.0) == "agrees" and sign_agreement(0.2, -1.0) == "disagrees"
    assert sign_agreement(0.0, -1.0) == "no sign"


def test_review_fixes_fresh_profile_r3_counts_training_scope_and_jusup_epochs(tmp_path, monkeypatch):
    d = analysed(tmp_path, monkeypatch)
    g = d / "g8"
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers.py"), str(d / "out"), str(d / "full"),
                    str(d / "ties"), str(g), "--n", "4", "--first", str(d / "first")], check=True, cwd=ROOT)
    pc = pd.read_csv(g / "profile_counts.csv")
    fresh = pc[pc.question.isin(["Q2 fresh block (R4)", "Q3 fresh block (R4)"])]
    assert set(fresh.model) == {"foodmatch", "forecast", "backpressure"}
    assert fresh[fresh.question == "Q2 fresh block (R4)"].cells.sum() == 30
    text = (g / "paper-numbers-G8.md").read_text()
    assert "| E2-fresh, frozen three only (R4) |" in text
    tb = pd.read_csv(g / "training_budgets.csv")
    assert set(tb[tb.model != "forecast"].wall_hours_scope) == {"final run only"}
    assert "5.26 h" in tb[tb.model == "auad"].other_runs.iloc[0]
    ep = pd.read_csv(g / "learning_curves_jusup_epochs.csv")
    assert {"training_seed", "epoch", "valid_objective"} <= set(ep.columns) and ep.epoch.max() > 300
    sa = pd.read_csv(g / "secondary_agreement.csv")
    assert set(sa.sign_agreement) <= {"agrees", "disagrees", "no sign"}


def jusup_undoes(r):
    """Planted: Jusup cuts W1 over the first 60 min by 2 min on the Q2 starts, and its second hour stays high."""
    if r["model"] == "jusup" and r["scenario"] in ("big_cluster", "three_clusters", "mixed") and r["set"] == "new":
        r["w1_rule_60min_after_min"] -= 2.0


def test_g8_verdict_d1_and_a1_to_a3(tmp_path, monkeypatch):
    d = analysed(tmp_path, monkeypatch, plant=jusup_undoes)
    g = d / "g8"
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers.py"), str(d / "out"), str(d / "full"),
                    str(d / "ties"), str(g), "--n", "4", "--first", str(d / "first")], check=True, cwd=ROOT)
    text = (g / "paper-numbers-G8.md").read_text()
    # D1: every model and metric in the Q3 summary, with the largest unassigned share; the DQN's W1 over 60 min
    q3s = pd.read_csv(g / "q3_summary.csv")
    assert len(q3s) == 9 and "largest_unassigned_over_30min_share" in q3s
    assert all(f"{m} mean" in q3s.columns for m in ("p90_c2d_min", "mean_c2d_min", "late_rate", "idle_km_per_order",
                                                    "extra_km_per_order"))
    ds = pd.read_csv(d / "out" / "descriptive.csv")
    dq = ds[(ds.part == "jahanshahi")]
    assert dq.w1_60_minus_nearest.notna().all() and dq.p90_minus_nearest.notna().all()
    # A1: the second-hour split on every undoing cell
    a1 = pd.read_csv(g / "a1_second_hour_split.csv")
    cl = pd.read_csv(d / "out" / "classes.csv")
    undo = cl[(cl.question == "Q2") & cl["class"].str.startswith("undoes")]
    assert len(a1) == len(undo) > 0
    for k in ("model", "nearest", "model_scattered", "nearest_scattered", "excess_cell", "excess_scattered",
              "excess_beyond_scattered"):
        assert {f"{k}_mean", f"{k}_lo", f"{k}_hi"} <= set(a1.columns)
    r = a1.iloc[0]
    assert abs(r.excess_cell_mean - (r.model_mean - r.nearest_mean)) < 1e-9
    # A2: ride to the restaurant and idle riding, per model and primary cell
    a2 = pd.read_csv(g / "a2_km_split.csv")
    assert len(a2) == 9 * 16 and {"pickup_km_per_order_diff", "idle_km_per_order_diff"} <= set(a2.columns)
    # A3: W1 over 20:00 to 20:59 on the clustered starts, exploratory, no test
    a3 = pd.read_csv(g / "a3_evening_2000_2059.csv")
    assert len(a3) == 9 * 9 and set(a3.reading) == {"exploratory"} and "p" not in a3.columns
    assert "A3" in text and "exploratory" in text and "A1" in text and "A2" in text
