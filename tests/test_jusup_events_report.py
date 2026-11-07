"""scripts/jusup_events_report.py: G8 item 1, couriers reached per policy step by Jusup's adaptation 10."""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_report_counts_couriers_whose_mass_zone_differs_per_step_and_their_share(tmp_path):
    rows = []
    for seed in (1001, 1002):
        rows.append({"set": "new", "scenario": "big_cluster", "level": "normal", "behavior": "fitted", "model": "jusup",
                     "obedience": 1.0, "seed": seed, "events_steps": 10, "events_couriers": 200,
                     "events_zone_mismatch": 20 if seed == 1001 else 40, "events_max_zone_mismatch_in_step": 3 + seed % 2})
    rows.append({**rows[0], "model": "nearest", "obedience": None})
    rows.append({**rows[0], "seed": 1003})                                  # outside n = 2: ignored
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "episodes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/jusup_events_report.py"), str(tmp_path / "full"),
                    str(tmp_path / "out"), "--n", "2"], check=True, cwd=ROOT)
    t = pd.read_csv(tmp_path / "out" / "jusup_events.csv")
    assert len(t) == 1
    r = t.iloc[0]
    assert r.episodes == 2 and r.policy_steps_taken_per_episode == 10
    assert r.couriers_per_step == 20 and r.mismatched_per_step == 3.0 and abs(r.mismatched_share - 0.15) < 1e-12
    assert r.max_mismatched_in_one_step == 4
    text = (tmp_path / "out" / "jusup_events.md").read_text()
    assert "adaptation 10" in text and "Policy steps taken per episode" in text and "Steps per episode" not in text
    assert "big_cluster normal fitted 1.00: 1 of 2 seeds" not in text


def test_report_lists_cells_left_out_for_missing_seeds(tmp_path):
    rows = [{"set": "new", "scenario": "burst", "level": "tight", "behavior": "fitted", "model": "jusup", "obedience": 0.5,
             "seed": 1001, "events_steps": 10, "events_couriers": 100, "events_zone_mismatch": 1,
             "events_max_zone_mismatch_in_step": 1}]
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "episodes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/jusup_events_report.py"), str(tmp_path / "full"),
                    str(tmp_path / "out"), "--n", "2"], check=True, cwd=ROOT)
    assert "burst tight fitted 0.50: 1 of 2 seeds" in (tmp_path / "out" / "jusup_events.md").read_text()
