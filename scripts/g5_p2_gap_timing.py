"""G5 verdict, P2: when the cluster gap arises (descriptive, not a new test).

Nearest courier, normal supply, seeds 1001 to 1030, two behavior settings: the fitted behavior and return
probability 0. For each, the soon-free W1 of every minute's snapshot from the scattered start and from the big
cluster (the quantity the episode W1 averages), and the share of the evening-mean gap (big cluster minus scattered)
that accrues before 18:30 (snapshots 17:00 to 18:29) and from 18:30 on. 95% percentile bootstrap over seeds.

Usage: python scripts/g5_p2_gap_timing.py <project_root> <out_dir> [workers]
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

SEEDS = list(range(1001, 1031))
SETTINGS = ("fitted", "p0")
SCENARIOS = ("scattered", "big_cluster")
SPLIT_MIN = 90                      # 18:30 is minute 90 after 17:00
_EX = {}


def job(args):
    scenario, setting, seed = args
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    row, _ = _EX["ex"].episode(scenario, "normal", seed, "nearest", setting=setting)
    return scenario, setting, seed, row["w1_rule_min"], np.array(row["w1_rule_series"])


def boot(fn, n_seeds, reps=10000, seed=7):
    rng = np.random.default_rng(seed)
    vals = [fn(rng.integers(0, n_seeds, n_seeds)) for _ in range(reps)]
    return [round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)]


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(job, [(sc, st, s) for st in SETTINGS for sc in SCENARIOS for s in SEEDS], chunksize=1)
    S = {(sc, st): np.vstack([r[4] for r in res if r[0] == sc and r[1] == st]) for sc in SCENARIOS for st in SETTINGS}
    W = {(sc, st): np.array([r[3] for r in res if r[0] == sc and r[1] == st]) for sc in SCENARIOS for st in SETTINGS}
    minutes = np.arange(S[SCENARIOS[0], SETTINGS[0]].shape[1])
    curves, summary = [], {"seeds": [SEEDS[0], SEEDS[-1]], "split": "18:30 (minute 90)", "wall_s": None}
    for st in SETTINGS:
        sct, big = S["scattered", st], S["big_cluster", st]
        for sc, M in (("scattered", sct), ("big_cluster", big)):
            curves.append(pd.DataFrame({"behavior": st, "scenario": sc, "minute_from_1700": minutes,
                                        "w1_mean": np.nanmean(M, 0)}))
        gap = big - sct                                                   # seeds x minutes

        def share_before(idx):
            g = np.nanmean(gap[idx], 0)
            return g[:SPLIT_MIN].sum() / g.sum()

        def mean_gap(idx):
            return np.nanmean(np.nanmean(gap[idx], 0))

        all_idx = np.arange(len(SEEDS))
        g = np.nanmean(gap, 0)
        per_hour = {f"{17 + h // 2}:{'00' if h % 2 == 0 else '30'}": round(float(g[30 * h:30 * h + 30].mean()), 3)
                    for h in range(len(g) // 30)}
        summary[st] = {
            "episode_w1_scattered": round(float(W["scattered", st].mean()), 3),
            "episode_w1_big_cluster": round(float(W["big_cluster", st].mean()), 3),
            "evening_mean_gap_min": round(float(mean_gap(all_idx)), 3),
            "evening_mean_gap_ci95": boot(mean_gap, len(SEEDS)),
            "gap_share_before_1830": round(float(share_before(all_idx)), 4),
            "gap_share_before_1830_ci95": boot(share_before, len(SEEDS)),
            "gap_share_from_1830": round(float(1 - share_before(all_idx)), 4),
            "mean_gap_before_1830_min": round(float(g[:SPLIT_MIN].mean()), 3),
            "mean_gap_from_1830_min": round(float(g[SPLIT_MIN:].mean()), 3),
            "mean_gap_by_half_hour_min": per_hour,
            "w1_scattered_by_half_hour": {k: round(float(np.nanmean(sct, 0)[30 * i:30 * i + 30].mean()), 3)
                                          for i, k in enumerate(per_hour)},
            "w1_big_cluster_by_half_hour": {k: round(float(np.nanmean(big, 0)[30 * i:30 * i + 30].mean()), 3)
                                            for i, k in enumerate(per_hour)},
        }
    pd.concat(curves).to_csv(out / "w1_by_minute.csv", index=False)
    summary["wall_s"] = round(time.time() - t0, 1)
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
