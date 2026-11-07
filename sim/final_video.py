"""S9: final video, stills and the W1-over-time data for the MATLAB figures.

Usage: python sim/final_video.py <project_root> <out_dir> <results_dir> [workers]

Best model = the published model with the largest mean W1 reduction against nearest-courier over the F1 contrasts
(`<results_dir>/contrasts.csv`). Video: nearest-courier and the best model side by side from the same start and seed
(big cluster, normal supply, fitted behavior, seed 1001), the whole 17:00 to 21:00 at 160x and 30 fps (90 s,
1920x1080), with the W1 strip; stills at 0, 30, 60, 120 and 240 min. W1 over time: the soon-free W1 of every snapshot
for the four models on that cell, seeds 1001 to 1030, mean and 95% percentile bootstrap interval per minute.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim import video  # noqa: E402
from sim.runner import Experiment  # noqa: E402

CELL = dict(scenario="big_cluster", level="normal", setting="fitted")
SEED = 1001
SEEDS_CURVE = list(range(1001, 1031))
MODELS = ["nearest", "foodmatch", "forecast", "backpressure"]
NAMES = {"nearest": "Nearest courier", "foodmatch": "FoodMatch (bundling off)", "forecast": "Forecast-aware matching",
         "backpressure": "Mirror backpressure"}
_EX = {}


def curve(args):
    model, seed = args
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    ex = _EX["ex"]
    _, sim = ex.episode(CELL["scenario"], CELL["level"], seed, model, setting=CELL["setting"])
    key = "w1_soon_min" if ex.man["few_idle_rule"] == "soon_free" else "w1_min"
    return [(model, seed, s["t"] / 60, s.get(key, np.nan)) for s in sim.snapshots]


def best_model(results_dir):
    c = pd.read_csv(Path(results_dir) / "contrasts.csv")
    f1 = c[(c.family == "F1") & (c.metric == "W1")]
    return f1.groupby("model")["mean"].mean().idxmin()


def main():
    out = Path(sys.argv[2])
    best = best_model(sys.argv[3])
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(workers) as pool:
        rows = [r for part in pool.map(curve, [(m, s) for m in MODELS for s in SEEDS_CURVE]) for r in part]
    d = pd.DataFrame(rows, columns=["model", "seed", "minute", "w1"])
    rng = np.random.default_rng(20261103)
    agg = []
    for (m, minute), g in d.groupby(["model", "minute"]):
        x = g.w1.dropna().to_numpy()
        boot = x[rng.integers(0, len(x), (2000, len(x)))].mean(axis=1)
        agg.append({"model": m, "minute": minute, "mean": x.mean(), "lo": np.percentile(boot, 2.5),
                    "hi": np.percentile(boot, 97.5), "seeds": len(x)})
    pd.DataFrame(agg).to_csv(out / "w1_over_time.csv", index=False)

    ex = Experiment(ROOT)
    panels = []
    for m in ["nearest", best]:
        _, sim = ex.episode(CELL["scenario"], CELL["level"], SEED, m, setting=CELL["setting"], trace=True)
        panels.append({"name": NAMES[m], "legs": sim.legs, "start": sim.fleet.start,
                       "snapshots": [{"t": s["t"], "w1_min": s.get("w1_soon_min", s["w1_min"])} for s in sim.snapshots]})
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    demand = ex.demand[CELL["scenario"]]

    def expected(t):
        return demand.expected_pickups(t, t + 1800.0)

    t1 = time.time()
    frames = video.render(out / f"nearest_vs_{best}_big_cluster.mp4", ex.city, seg, panels, ex.city.rest, expected,
                          title="Curitiba, simulated evening peak, same start and orders")
    stills = video.stills(out / f"still_{{minute:03d}}min.png", ex.city, seg, panels, ex.city.rest, expected,
                          minutes=(0, 30, 60, 120, 240))
    (out / "video.json").write_text(json.dumps({"best_model": best, "seed": SEED, **CELL, "frames": frames,
                                                "render_seconds": round(time.time() - t1, 1),
                                                "curve_seconds": round(t1 - t0, 1),
                                                "stills": [Path(s).name for s in stills]}, indent=1))
    print("best", best, "frames", frames, flush=True)


if __name__ == "__main__":
    main()
