"""S5 end-to-end check: one shared start (big cluster, normal supply, fitted behavior), all four models, the metrics
table, and a 30-second video of nearest-courier that also tests the video pipeline.

Usage: python sim/e2e.py <project_root> <out_dir> [seed]
Seed 501 is outside the pilot (1 to 30), full-run (from 1001) and calibration seeds.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.runner import Experiment  # noqa: E402
from sim import video  # noqa: E402

MODELS = ["nearest", "foodmatch", "forecast", "backpressure"]
COLS = ["model", "w1_rule_min", "w1_rule_first30_min", "w1_min", "p90_c2d_min", "mean_c2d_min", "late_rate", "tv",
        "gini_idle", "uncovered", "extra_km_per_order", "idle_km_per_order", "earnings_gini", "food_wait_mean_min",
        "food_wait_p90_min", "delivered", "orders", "seconds"]


def main():
    out = Path(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 501
    out.mkdir(parents=True, exist_ok=True)
    ex = Experiment(ROOT)
    rows, sims = [], {}
    for m in MODELS:
        t0 = time.time()
        row, sim = ex.episode("big_cluster", "normal", seed, m, trace=(m == "nearest"))
        row["seconds"] = round(time.time() - t0, 1)
        rows.append(row)
        sims[m] = sim
        print(json.dumps({k: row[k] for k in COLS if k in row}, default=float), flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(out / "metrics.csv", index=False)
    t = table[COLS].round(3).astype(str)
    (out / "metrics.md").write_text("\n".join(["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
                                              + ["| " + " | ".join(r) + " |" for r in t.to_numpy()]) + "\n")

    sim = sims["nearest"]
    city = ex.city
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    demand = ex.demand["big_cluster"]

    def expected(t):
        return demand.expected_pickups(t, t + 1800.0)

    panel = {"name": "Nearest courier, big cluster", "legs": sim.legs, "start": sim.fleet.start, "snapshots": sim.snapshots}
    t0 = time.time()
    frames = video.render(out / "nearest_big_cluster_30s.mp4", city, seg, [panel], city.rest, expected,
                          start_s=0.0, end_s=30 * 160.0, title="Curitiba, simulated evening peak")
    stills = video.stills(out / "still_nearest_{minute:03d}min.png", city, seg, [panel], city.rest, expected,
                          minutes=(0, 30, 60))
    (out / "video.json").write_text(json.dumps({"frames": frames, "seconds": round(time.time() - t0, 1), "speed": 160,
                                                "fps": 30, "covers_min": 80, "stills": [Path(s).name for s in stills]}))
    print("video", frames, "frames", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
