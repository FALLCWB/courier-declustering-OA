"""G6 verdict, "For X5 and X6": Jusup et al.'s W1 over time against nearest courier on the big cluster.

Big cluster, normal supply, fitted behavior, full obedience, seeds 96001 to 96030 (training range, outside every
evaluation seed); seed s runs the policy of training seed ((s - 1) mod 5) + 1. Per minute: soon-free W1 (the quantity
the episode W1 averages), mean over seeds with a 95% percentile bootstrap, for both models and their difference (the
share of free couriers moved per 20-minute step is in the training folder's moved_share.csv). W1 counts an idle courier at the cell it is in, so a relocating courier counts where it is along its route.

Usage: python scripts/jusup_w1_over_time.py <project_root> <out_dir> [workers]
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.runner import Experiment  # noqa: E402

SEEDS = list(range(96001, 96031))
_EX = {}


def job(args):
    model, seed = args
    if "ex" not in _EX:
        import torch
        torch.set_num_threads(1)
        _EX["ex"] = Experiment(ROOT)
    k = (seed - 1) % 5 + 1
    kw = {"weights_path": ROOT / f"models/trained/jusup_seed{k}.pt", "q": 1.0} if model == "jusup" else None
    row, _ = _EX["ex"].episode("big_cluster", "normal", seed, model, obedience=1.0 if model == "jusup" else None,
                               model_kw=kw)
    return model, seed, np.array(row["w1_rule_series"]), row["w1_rule_min"], row["p90_c2d_min"]


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(job, [(m, s) for m in ("nearest", "jusup") for s in SEEDS], chunksize=1)
    S = {m: np.vstack([r[2] for r in res if r[0] == m]) for m in ("nearest", "jusup")}
    rng = np.random.default_rng(7)
    idx = rng.integers(0, len(SEEDS), (5000, len(SEEDS)))
    rows = []
    for name, M in (("nearest", S["nearest"]), ("jusup", S["jusup"]), ("jusup_minus_nearest", S["jusup"] - S["nearest"])):
        boot = np.nanmean(M[idx], axis=1)                                 # 5000 x minutes
        rows.append(pd.DataFrame({"series": name, "minute_from_1700": np.arange(M.shape[1]), "mean": np.nanmean(M, 0),
                                  "lo": np.percentile(boot, 2.5, axis=0), "hi": np.percentile(boot, 97.5, axis=0)}))
    curve = pd.concat(rows)
    curve.to_csv(out / "w1_over_time.csv", index=False)
    d = S["jusup"] - S["nearest"]
    halves = {f"{17 + h // 2}:{'00' if h % 2 == 0 else '30'}": [round(float(np.nanmean(S['nearest'][:, 30 * h:30 * h + 30])), 3),
                                                                 round(float(np.nanmean(S['jusup'][:, 30 * h:30 * h + 30])), 3),
                                                                 round(float(np.nanmean(d[:, 30 * h:30 * h + 30])), 3)]
              for h in range(S["nearest"].shape[1] // 30)}
    summary = {"seeds": [SEEDS[0], SEEDS[-1]], "episode_w1_nearest": round(float(np.mean([r[3] for r in res if r[0] == "nearest"])), 3),
               "episode_w1_jusup": round(float(np.mean([r[3] for r in res if r[0] == "jusup"])), 3),
               "p90_nearest": round(float(np.mean([r[4] for r in res if r[0] == "nearest"])), 3),
               "p90_jusup": round(float(np.mean([r[4] for r in res if r[0] == "jusup"])), 3),
               "half_hour_means_nearest_jusup_difference": halves, "wall_s": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for name, col, lab in (("nearest", "#555555", "Nearest courier"), ("jusup", "#c53030", "Jusup et al., 100% obedient")):
        c = curve[curve.series == name]
        x = 17 + c.minute_from_1700 / 60
        ax.fill_between(x, c.lo, c.hi, color=col, alpha=0.2, lw=0)
        ax.plot(x, c["mean"], color=col, lw=1.6, label=lab)
    ax.set_xlabel("Time of day (h)")
    ax.set_ylabel("W1 (min of riding)")
    ax.set_title("Big cluster, normal supply, seeds 96001 to 96030 (gate evidence, not a paper figure)", fontsize=10)
    fig.legend(loc="lower center", ncol=2, frameon=False)
    fig.text(0.99, 0.005, "This research was supported by data provided by Meituan.", ha="right", fontsize=7, color="#555555")
    fig.subplots_adjust(bottom=0.25)
    fig.savefig(out / "w1_over_time.png", dpi=150)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
