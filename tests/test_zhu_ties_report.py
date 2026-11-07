"""scripts/zhu_ties_report.py on synthetic rows: pairing by seed, time to undo against the same variant's scattered start,
and the per-step owns-no-cell count."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def row(set_, scenario, model, seed, w1, events=None):
    series = [w1] * 240
    r = {"set": set_, "scenario": scenario, "level": "normal", "behavior": "fitted", "model": model,
         "obedience": 1.0 if model == "zhu" else None, "seed": seed, "w1_rule_min": w1, "w1_rule_60min_after_min": w1,
         "p90_c2d_min": 40.0, "unassigned_over_30min_share": 0.0, "w1_rule_series": series}
    if events:
        r.update(events)
    return r


def test_random_ties_report_pairs_by_seed_and_reads_its_own_scattered_reference(tmp_path):
    seeds = range(1001, 1031)
    ev = lambda nocell: {"events_steps": 600, "events_commands": 300000, "events_owns_no_cell": nocell}
    ties = [row("zhu_random_ties", s, "zhu", k, w, ev(0)) for k in seeds
            for s, w in (("big_cluster", 10.0), ("meetup", 6.0), ("scattered", 5.0))]
    full = [row("new", s, "zhu", k, w, ev(300000)) for k in seeds
            for s, w in (("big_cluster", 11.0), ("meetup", 7.0), ("scattered", 5.0))]
    full += [row("frozen_rerun" if s != "meetup" else "new", s, "nearest", k, w) for k in seeds
             for s, w in (("big_cluster", 12.0), ("meetup", 6.5), ("scattered", 4.0))]
    for d, rs in (("ties", ties), ("full", full)):
        (tmp_path / d).mkdir()
        (tmp_path / d / "episodes.jsonl").write_text("\n".join(json.dumps(r) for r in rs) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/zhu_ties_report.py"), str(ROOT), str(tmp_path / "ties"),
                    str(tmp_path / "full"), str(tmp_path / "out")], check=True, capture_output=True)
    pr = pd.read_csv(tmp_path / "out" / "zhu_ties_pairs.csv").set_index(["start", "metric"])
    assert np.isclose(pr.loc[("big_cluster", "W1"), "random_minus_frozen"], -1.0)
    assert np.isclose(pr.loc[("meetup", "couriers owning no cell per step"), "random_minus_frozen"], -500.0)
    tab = pd.read_csv(tmp_path / "out" / "zhu_ties.csv").set_index(["variant", "start"])
    # constant series: 10 against the variant's own scattered 5 never comes within 10%, so censored at 240
    assert tab.loc[("Zhu, random ties (sensitivity)", "big_cluster"), "time to undo, median"] == 240
    assert tab.loc[("Zhu, random ties (sensitivity)", "big_cluster"), "censored share"] == 1.0
