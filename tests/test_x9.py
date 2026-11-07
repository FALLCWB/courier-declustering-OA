"""X9 scripts: the nine videos and their panels, and the W1-over-time CSV on synthetic rows."""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_nine_videos_one_per_arm_and_start_with_their_panels():
    from sim.x9_videos import videos
    v = videos()
    assert len(v) == 9 and len({x[0] for x in v}) == 9
    assert {(x[0].split("_")[1], x[1]) for x in v} == {(a, s) for a in "ABC" for s in ("big_cluster", "meetup", "scattered")}
    assert all(x[2][0] == ("nearest", None) and len(x[2]) <= 4 for x in v)
    assert [x[3:5] for x in v if x[1] == "meetup"][0] == (6600.0, 12600.0)          # 18:50 to 20:30


def test_w1_over_time_csv_has_every_model_and_start_and_the_scattered_reference(tmp_path):
    ten = ["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"]
    rows = [{"set": "new", "scenario": s, "level": "normal", "behavior": "fitted", "model": m,
             "obedience": 1.0 if m in ("zhu", "jusup") else None, "seed": k, "w1_rule_series": [float(k - 1000)] * 240}
            for s in ("big_cluster", "meetup", "scattered") for m in ten for k in (1001, 1002, 1003)]
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "episodes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/x9_w1_over_time.py"), str(tmp_path / "full"), str(tmp_path / "out"),
                    "--n", "3"], check=True, capture_output=True)
    t = pd.read_csv(tmp_path / "out" / "w1_over_time_extension.csv")
    assert set(t.start) == {"big_cluster", "meetup", "scattered", "reference_scattered"}
    assert len(t) == (3 * 10 + 1) * 240 and (t["mean"] == 2.0).all()            # mean of 1, 2 and 3
    assert set(t[t.start == "reference_scattered"].model) == {"nearest"}


def test_stills_cover_the_ten_models_on_the_big_cluster_at_17_and_18():
    """Instructions of 2026-11-05, section 4: stills at 17:00 and 18:00 for all ten models, big cluster, seed 1001,
    normal supply, fitted behavior (arm C at 100%), named panel_<model>_000.png and panel_<model>_060.png."""
    from sim.x9_videos import STILL_MINUTES, still_panels, videos
    sp = still_panels()
    assert STILL_MINUTES == (0, 60) and len(sp) == 10
    assert {m for m, _ in sp} == {"nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad",
                                  "zhu", "jusup"}
    assert dict(sp)["zhu"] == 1.0 and dict(sp)["jusup"] == 1.0 and dict(sp)["xu"] is None
