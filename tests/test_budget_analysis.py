"""scripts/budget_analysis.py: the training-budget check's tables (preregistration-addendum-budget.md)."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_extension import MAN, rows, write  # noqa: E402

SEEDS = [1001, 1006, 1011]
Q1 = [(s, lvl) for s in ("scattered", "burst") for lvl in MAN["levels"]]


def test_budget_analysis(tmp_path):
    from sim.run_extension import jobs
    rng = np.random.default_rng(9)
    keep = {"nearest", "xu", "li", "auad", "jusup", "jahanshahi"}
    full = rows([j for j in jobs("full:15:short", MAN) if j["set"] in ("new", "frozen_rerun") and j["seed"] in SEEDS
                 and j["model"] in keep and j["behavior"] == "fitted" and j["obedience"] in (None, 1.0)], rng)
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest"])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    bud = rows([j for j in jobs("c_budget", MAN) if j["seed"] in SEEDS], rng)
    for r in bud:                                       # planted: the retrained Li prevents on Q1
        if r["model"] == "li" and (r["scenario"], r["level"]) in Q1:
            r["w1_rule_min"] -= 2.0
    write(tmp_path / "budget", bud)
    g8 = tmp_path / "g8"
    g8.mkdir()
    pd.DataFrame([{"question": "Q1", "scenario": s, "level": lvl, "model": "li", "class": "prevents at no delivery cost"}
                  for s, lvl in Q1[:2]] + [{"question": "Q2", "scenario": "mixed", "level": "tight", "model": "jusup",
                                           "class": "undoes at no delivery cost"}]).to_csv(g8 / "classes.csv", index=False)
    pp = []
    for (s, lvl), mo, fam, met in [(Q1[0], "li", "E1", "w1_rule_min"), (Q1[1], "li", "E1", "w1_rule_min"),
                                   (("mixed", "tight"), "jusup", "E2", "w1_rule_60min_after_min")]:
        for k in range(1, 6):
            pp.append({"family": fam, "scenario": s, "level": lvl, "metric": met, "model": mo, "policy": k, "seeds": 30,
                       "mean": -5.0 if k != 3 else 0.0, "lo": -6.0, "hi": 1.0})
    pd.DataFrame(pp).to_csv(tmp_path / "c5_per_policy.csv", index=False)
    ag = tmp_path / "auad_grid"
    ag.mkdir()
    pd.DataFrame([{"alpha": a, "mem": 3000, "n_step": n, "diverged": False, "theta_best_is_theta0": False,
                   "valid_cost": 100.0 + a * 1e6 + n / 1000, "gate_best_cost": 90.0, "peaks": 200, "theta_best": "[]"}
                  for a in (1e-7, 1e-6, 1e-5) for n in (2, 1000)]).to_csv(ag / "grid.csv", index=False)
    (ag / "run.json").write_text(json.dumps({"chosen": {"alpha": 1e-7, "mem": 3000, "n_step": 1000}}))
    af = tmp_path / "auad_final"
    af.mkdir()
    pd.DataFrame([{"training_seed": k, "episodes": n, "scenario": "scattered", "seed": 95001, "cost": 120.0 - n / 10}
                  for k in range(1, 6) for n in range(25, 201, 25)]).to_csv(af / "curve.csv", index=False)
    tr = tmp_path / "train"                             # retraining outputs: Li present, the others still pending
    (tr / "li").mkdir(parents=True)
    pd.DataFrame([{"training_seed": 1, "episode": i, "critic_loss": 1.0 / i, "actor_loss": 0.5 / i, "episode_reward": float(i)}
                  for i in range(1, 51)]).to_csv(tr / "li" / "training.csv", index=False)
    pd.DataFrame([{"training_seed": 1, "episodes": n, "scenario": "scattered", "seed": 95001, "w1_rule_min": 5.0 - n / 100,
                   "p90_c2d_min": 40.0} for n in (0, 25, 50)]).to_csv(tr / "li" / "curve.csv", index=False)
    (tr / "li" / "run.json").write_text(json.dumps({"model": "li", "episodes": 600}))
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/budget_analysis.py"), str(out), "--full", str(tmp_path / "full"),
                        "--budget-runs", str(tmp_path / "budget"), "--train", str(tr), "--pilot", str(tmp_path / "pilot"),
                        "--g8", str(g8), "--per-policy", str(tmp_path / "c5_per_policy.csv"), "--auad-grid", str(ag),
                        "--auad-final", str(af), "--n", "3"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    cl = pd.read_csv(out / "b2_classes.csv")
    assert len(cl) == 4 * 16 and {"class_retrained", "class_current", "changed"} <= set(cl.columns)
    ch = cl[cl.changed]
    assert set(ch.model) == {"li"} and set(ch.class_retrained) == {"prevents at no delivery cost"} and len(ch) == 6
    con = pd.read_csv(out / "b2_contrasts.csv")
    assert con.groupby(["input", "holm_set"]).size().to_dict() == {("current", "E1-shaped"): 48, ("current", "E2-shaped"): 80,
                                                                   ("retrained", "E1-shaped"): 48, ("retrained", "E2-shaped"): 80}
    assert len(pd.read_csv(out / "b2_dqn.csv")) == 2 * 16
    pp = pd.read_csv(out / "b3_per_policy.csv")
    assert len(pp) == 3 and set(pp.policies_beyond_minus_delta) == {4}
    g = pd.read_csv(out / "b4_auad_grid.csv")
    assert len(g) == 6 and g.chosen.sum() == 1
    v = pd.read_csv(out / "b4_auad_validation.csv")
    assert abs(v[v.checkpoint == 200].mean_cost.iloc[0] - 100.0) < 1e-9
    cu = pd.read_csv(out / "b1_curves.csv")
    assert {"li"} == set(cu.model) and {"actor_loss", "critic_loss", "episode_reward", "w1_valid", "p90_valid"} <= set(cu.measure)
    t = (out / "paper-numbers-budget.md").read_text()
    assert "pending" in t and "c217ca4" in t and "This research was supported by data provided by Meituan." in t
    assert "Classes that change: 6 of 64" in t
    assert "| 1e-07 |" in t
    assert "| model | class | retrained | current |" in t
    assert "| nan |" not in t.split("## Training")[1].split("## Per-policy")[0]
    assert "(the frozen code saves the actor after the last peak) | done | 600 |" in t


def test_curves_leave_capped_gate_runs_out_of_the_mean_and_report_their_share(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import budget_analysis as ba
    (tmp_path / "auad").mkdir()
    pd.DataFrame({"episode": [1, 2, 3, 4], "gate_cost": [np.inf, 100.0, np.inf, 50.0], "best_cost": [np.inf, 100.0, 100.0, 50.0],
                  "train_cost": [1.0, 2.0, 3.0, 4.0]}).to_csv(tmp_path / "auad" / "training.csv", index=False)
    cu = ba.curves(tmp_path)
    v = cu[cu.checkpoint == 25].set_index("measure").value
    assert v["gate_cost"] == 75.0 and v["gate_capped_share"] == 0.5 and abs(v["best_cost"] - 250 / 3) < 1e-12
