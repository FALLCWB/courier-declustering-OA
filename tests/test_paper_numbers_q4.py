"""scripts/paper_numbers_q4.py: the Q4 addendum (E5 now; E3 and E4 when phase 4 ends) and the Zhu mechanism check."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_extension import MAN, rows, write  # noqa: E402


def test_q4_addendum_reads_e5_both_directions_and_zhu_at_75_against_100(tmp_path, monkeypatch):
    from sim.run_extension import jobs, phase
    import sim.analysis_extension as an
    full = rows([j for j in jobs("full:4", MAN) if phase(j) in (1, 3)], np.random.default_rng(7))   # phase 2 needs n >= 30
    for r in full:
        if r["model"] == "zhu":
            r.update(events_steps=480, events_commands=900, events_whole_part_commands=40, events_no_demand_in_part=3,
                     events_owns_no_cell=200 if r["obedience"] == 0.75 else 150)
        if r["model"] == "jusup" and r["obedience"] == 0.25:
            r["w1_rule_min"] += 1.0                          # planted: Jusup at 25% raises W1 (the other direction)
    write(tmp_path / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest" and r["seed"] < 5001])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (tmp_path / "pilot").mkdir()
    m.reset_index().to_csv(tmp_path / "pilot" / "pilot_nearest_means.csv", index=False)
    (tmp_path / "first").mkdir()
    pd.DataFrame([{"family": "F1", "scenario": s, "level": lvl, "model": mo, "metric": "p90", "mean": 0.1, "lo": -0.1,
                   "hi": 0.3, "p_holm": 1.0} for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]
                  for mo in ("foodmatch", "forecast", "backpressure")]).to_csv(tmp_path / "first" / "contrasts.csv", index=False)
    pd.DataFrame([{"scenario": "scattered", "level": "normal", "model": "foodmatch", "class": "does not decluster"}]).to_csv(
        tmp_path / "first" / "classes.csv", index=False)
    write(tmp_path / "s8", [{"family": "F1", "scenario": "x", "level": "x", "behavior": "x", "model": "x", "seed": 0}])
    monkeypatch.setattr(sys, "argv", ["x", str(tmp_path / "out"), *(str(tmp_path / d) for d in ("full", "pilot", "first", "s8")),
                                      "--n", "4", "--families", "E1,E2,E5"])
    an.main()
    g = tmp_path / "g8"
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_q4.py"), str(tmp_path / "out"), str(tmp_path / "full"),
                    str(g), "--n", "4"], check=True, cwd=ROOT)
    e5 = pd.read_csv(g / "q4_e5.csv")
    assert len(e5) == 192 and {"obedience", "direction", "pct_of_nearest", "p_holm", "equivalence", "class",
                                "mean_at_100", "p_holm_at_100"} <= set(e5.columns)
    up = e5[(e5.model == "jusup") & (e5.obedience == 0.25) & (e5.metric == "w1_rule_min")]
    assert set(up.direction) == {"established increase"}
    zm = pd.read_csv(g / "zhu_mechanism_75_vs_100.csv")
    assert len(zm) == 16 and {"w1_diff", "w1_lo", "w1_hi", "owns_no_cell_per_step_75", "owns_no_cell_per_step_100",
                              "owns_no_cell_per_step_diff"} <= set(zm.columns)
    assert (zm.owns_no_cell_per_step_diff.round(9) == round(50 / 480, 9)).all()
    text = (g / "paper-numbers-addendum.md").read_text()
    assert "This research was supported by data provided by Meituan." in text and "E5" in text and "E3" in text
    # A3 at partial obedience (Filipe, 2026-11-06): W1 over 20:00 to 20:59, clustered starts, exploratory, no test
    a3 = pd.read_csv(g / "a3_evening_obedience.csv")
    assert len(a3) == 9 * 2 * 3 and set(a3.reading) == {"exploratory"} and "p" not in a3.columns
    assert set(a3.obedience) == {0.25, 0.5, 0.75} and set(a3.model) == {"zhu", "jusup"}
    assert "A3 at 25, 50 and 75% obedience" in text


def test_e4_classes_of_the_frozen_three_take_p90_on_the_starts_from_f2(tmp_path):
    """As E2 takes the frozen three's p90 on the Q2 starts from F1, E4 takes it from the first round's F2 at the same
    return value; on the meet-up it is in E4 itself."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from paper_numbers_q4 import family_table
    rows = []
    for s, lvl in (("big_cluster", "normal"), ("meetup", "normal")):
        rows.append({"family": "E4", "scenario": s, "level": lvl, "behavior": "p0", "model": "foodmatch",
                     "obedience": float("nan"), "metric": "w1_rule_60min_after_min", "delta": 1.0, "mean": -2.0,
                     "lo": -2.2, "hi": -1.8, "p": 1e-9, "p_holm": 1e-8, "established": True, "at_least_sesoi": True,
                     "lower_at_least_sesoi": True, "equivalence": "", "nearest_mean": 10.0})
    rows.append({**rows[1], "metric": "p90_c2d_min", "mean": 0.1, "lo": -0.1, "hi": 0.3, "p_holm": 0.5,
                 "established": False, "lower_at_least_sesoi": False})
    con = pd.DataFrame(rows)
    f2 = pd.DataFrame([{"family": "F2", "scenario": "big_cluster", "level": "normal", "behavior": "p0", "model": "foodmatch",
                        "metric": "p90", "mean": 2.0, "lo": 1.5, "hi": 2.5, "p_holm": 1e-6}])
    d = family_table(con, "E4", "behavior", "fitted", f2)
    cls = d.drop_duplicates(["scenario"]).set_index("scenario")["class"]
    assert cls["big_cluster"] == "undoes at a delivery cost" and cls["meetup"] == "undoes at no delivery cost"
    assert set(d.drop_duplicates(["scenario"]).set_index("scenario")["p90_source"]) == {"F2 (first round)", "E4"}
