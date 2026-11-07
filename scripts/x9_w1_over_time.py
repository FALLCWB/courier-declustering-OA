"""X9: W1 over the evening per model for Paper A, from the extension's full runs.

Usage: python scripts/x9_w1_over_time.py <full_dir> <out_dir> [--n N]
Reads <full_dir>/episodes.jsonl. For the big cluster, the meet-up and the scattered start (normal supply, fitted
behavior, arm C at 100% obedience, seeds 1001 to 1000 + n): the mean soon-free W1 per minute over seeds with a 95%
percentile bootstrap interval (2,000 resamples, generator seed 20261107), one row per model, start and minute. Nearest
courier's scattered curve is written once more with start "reference_scattered", the dashed grey line of the G5
verdict's ruling 5. Writes w1_over_time_extension.csv.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

TEN = ["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"]
STARTS = ["big_cluster", "meetup", "scattered"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("full_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    seeds = list(range(1001, 1001 + a.n))
    ep = pd.read_json(a.full_dir / "episodes.jsonl", lines=True, precise_float=True, dtype={"obedience": float})
    ep = ep[ep.set.isin(["new", "frozen_rerun"]) & (ep.level == "normal") & (ep.behavior == "fitted")
            & (ep.obedience.isna() | (ep.obedience == 1.0)) & ep.seed.isin(seeds)]
    rng = np.random.default_rng(20261107)
    rows = []
    for s in STARTS:
        for m in TEN:
            g = ep[(ep.scenario == s) & (ep.model == m)].sort_values("seed")
            if list(g.seed) != seeds:
                raise SystemExit(f"{s} {m}: {len(g)} of {len(seeds)} seeds")
            X = np.vstack(g.w1_rule_series.to_list()).astype(float)          # seeds x 240 minutes
            idx = rng.integers(0, len(seeds), (2000, len(seeds)))
            boot = np.nanmean(X[idx], axis=1)                                 # 2000 x 240
            lo, hi = np.nanpercentile(boot, 2.5, axis=0), np.nanpercentile(boot, 97.5, axis=0)
            for name in ([s] + (["reference_scattered"] if (s, m) == ("scattered", "nearest") else [])):
                rows += [{"start": name, "model": m, "minute": t, "mean": float(np.nanmean(X[:, t])), "lo": float(lo[t]),
                          "hi": float(hi[t])} for t in range(X.shape[1])]
    a.out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out_dir / "w1_over_time_extension.csv", index=False)
    print(f"wrote {len(rows)} rows")


if __name__ == "__main__":
    main()
