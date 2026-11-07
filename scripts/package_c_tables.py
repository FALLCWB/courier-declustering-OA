"""Package C, part 5 (instructions of 2026-11-07): tables from the existing full runs, no new episode. Descriptive.

Usage: python scripts/package_c_tables.py <full_dir> <out_dir> --n <n>
Writes, with paired 95% percentile bootstrap intervals over seeds (model minus nearest courier, lower is better):
  c5_w1_windows.csv         W1 over 0-60, 60-120 and 180-240 min after the cluster appears, per model, on the clustered
                            starts at three supply levels and on the meet-up (0-60 and 60-120 only; its evening ends)
  c5_evening_truncated.csv  Q1 W1 (scattered and burst starts) over the evening without 20:30 to 21:00, beside the
                            full evening, per model, and nearest courier's own means
  c5_per_policy.csv         every E1 and E2 contrast of Xu, Li, Auad and Jusup per training policy (5 policies x the
                            seeds that run it)
  c5_evening_by_return.csv  W1 over 20:00 to 20:59 at return probability 0, fitted and 1, for Zhu, Jusup and Xu on the
                            clustered starts, and nearest courier's own means
and c5_tables.md. Every number is an aggregate over seeds.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.analysis_extension import ARM_C, P90, Q1, Q2, W160, W1, Runs, load, md, window  # noqa: E402
from sim.stats import contrast_rng, paired_contrast  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
NINE = ["foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"]
CLUSTERED = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in ("tight", "normal", "loose")]


def ob(m):
    return 1.0 if m in ARM_C else None


def pair(a, b, key):
    c = paired_contrast(np.asarray(a, float), np.asarray(b, float), contrast_rng(*key))
    return c["mean"], c["lo"], c["hi"]


def series_window(g, seeds, s, lo, hi):
    return np.array([window(g.loc[k, "w1_rule_series"], s, lo, hi) for k in seeds])


def windows(runs):
    out = []
    for s, lvl in Q2:
        wins = [(0, 60), (60, 120)] + ([] if s == "meetup" else [(180, 240)])
        base = runs.rows(s, lvl, "fitted", "nearest")
        for lo, hi in wins:
            b = series_window(base, runs.seeds, s, lo, hi)
            for m in NINE:
                a = series_window(runs.rows(s, lvl, "fitted", m, ob(m)), runs.seeds, s, lo, hi)
                mean, l, h = pair(a, b, ((s, lvl, "fitted", ob(m)), m, f"w1_{lo}_{hi}"))
                out.append({"scenario": s, "level": lvl, "window": f"{lo}-{hi}", "model": m, "n": len(runs.seeds),
                            "model_mean": float(a.mean()), "nearest_mean": float(b.mean()), "mean": mean, "lo": l, "hi": h})
    return pd.DataFrame(out)


def truncated(runs):
    """Q1 W1 over the evening, all 240 minutes against minutes 0 to 209 (without 20:30 to 21:00)."""
    out = []
    for s, lvl in Q1:
        base = runs.rows(s, lvl, "fitted", "nearest")
        bf, bt = series_window(base, runs.seeds, s, 0, 240), series_window(base, runs.seeds, s, 0, 210)
        for m in NINE:
            g = runs.rows(s, lvl, "fitted", m, ob(m))
            af, at = series_window(g, runs.seeds, s, 0, 240), series_window(g, runs.seeds, s, 0, 210)
            mf, lf, hf = pair(af, bf, ((s, lvl, "fitted", ob(m)), m, "w1_full"))
            mt, lt, ht = pair(at, bt, ((s, lvl, "fitted", ob(m)), m, "w1_truncated"))
            out.append({"scenario": s, "level": lvl, "model": m, "n": len(runs.seeds),
                        "nearest_full": float(bf.mean()), "nearest_truncated": float(bt.mean()),
                        "model_full": float(af.mean()), "model_truncated": float(at.mean()),
                        "mean_full": mf, "lo_full": lf, "hi_full": hf,
                        "mean_truncated": mt, "lo_truncated": lt, "hi_truncated": ht})
    return pd.DataFrame(out)


def per_policy(runs):
    """Learned models run the policy of training seed ((s - 1) mod 5) + 1; each E1 and E2 contrast per policy."""
    out = []
    policy = np.array([(k - 1) % 5 + 1 for k in runs.seeds])
    cells = [(s, lvl, met) for s, lvl in Q1 for met in (W1, P90)] + [(s, lvl, met) for s, lvl in Q2 for met in (W160, P90)]
    for m in ("xu", "li", "auad", "jusup"):
        for s, lvl, met in cells:
            a = runs.rows(s, lvl, "fitted", m, ob(m))[met].to_numpy()
            b = runs.rows(s, lvl, "fitted", "nearest")[met].to_numpy()
            fam = "E1" if (s, lvl) in Q1 else "E2"
            for k in range(1, 6):
                sel = policy == k
                mean, l, h = pair(a[sel], b[sel], ((s, lvl, "fitted", ob(m), k), m, met))
                out.append({"family": fam, "scenario": s, "level": lvl, "metric": met, "model": m, "policy": k,
                            "seeds": int(sel.sum()), "mean": mean, "lo": l, "hi": h})
    return pd.DataFrame(out)


def by_return(runs):
    out = []
    for b in ("p0", "fitted", "p1"):
        for s, lvl in CLUSTERED:
            base = series_window(runs.rows(s, lvl, b, "nearest"), runs.seeds, s, 180, 240)
            out.append({"behavior": b, "scenario": s, "level": lvl, "model": "nearest", "n": len(runs.seeds),
                        "model_mean": float(base.mean()), "nearest_mean": float(base.mean()),
                        "mean": 0.0, "lo": 0.0, "hi": 0.0})
            for m in ("zhu", "jusup", "xu"):
                a = series_window(runs.rows(s, lvl, b, m, ob(m)), runs.seeds, s, 180, 240)
                mean, l, h = pair(a, base, ((s, lvl, b, ob(m)), m, "w1_180_240"))
                out.append({"behavior": b, "scenario": s, "level": lvl, "model": m, "n": len(runs.seeds),
                            "model_mean": float(a.mean()), "nearest_mean": float(base.mean()), "mean": mean, "lo": l, "hi": h})
    out = pd.DataFrame(out)
    return out[out.model != "nearest"].reset_index(drop=True), out[out.model == "nearest"].reset_index(drop=True)


def ci(r):
    return f"{r['mean']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("full_dir", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--n", type=int, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    runs = Runs(load(a.full_dir), a.n)
    w = windows(runs)
    w.to_csv(a.out / "c5_w1_windows.csv", index=False)
    t = truncated(runs)
    t.to_csv(a.out / "c5_evening_truncated.csv", index=False)
    p = per_policy(runs)
    p.to_csv(a.out / "c5_per_policy.csv", index=False)
    e, near = by_return(runs)
    e.to_csv(a.out / "c5_evening_by_return.csv", index=False)
    near.to_csv(a.out / "c5_evening_by_return_nearest.csv", index=False)
    spread = (p.groupby(["family", "model", "scenario", "level", "metric"])["mean"].agg(["min", "max"]).reset_index())
    L = ["# Package C, part 5: tables from the existing runs (descriptive)", "", ACK, "",
         f"Seeds 1001 to {1000 + a.n} (n = {a.n}), fitted behavior unless stated, arm C at 100% obedience. Differences are "
         "model minus nearest courier, paired by seed, with 95% percentile bootstrap intervals; no test.", "",
         "## W1 by window after the cluster appears", "",
         md(pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in w.itertuples()], "window (min)": w.window,
                          "model": w.model, "difference [95% CI]": [ci(r) for r in w.to_dict("records")]}), index=False), "",
         "## Q1 W1 without 20:30 to 21:00", "",
         md(pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in t.itertuples()], "model": t.model,
                          "full evening": [f"{r['mean_full']:+.2f} [{r['lo_full']:+.2f}, {r['hi_full']:+.2f}]" for r in t.to_dict("records")],
                          "without 20:30-21:00": [f"{r['mean_truncated']:+.2f} [{r['lo_truncated']:+.2f}, {r['hi_truncated']:+.2f}]" for r in t.to_dict("records")]}), index=False), "",
         "## Per training policy: range of the five policy means of each E1 and E2 contrast", "",
         "Every policy mean with its interval: `c5_per_policy.csv`.", "", md(spread.round(3), index=False), "",
         "## W1 over 20:00 to 20:59 by return probability (clustered starts)", "",
         md(pd.DataFrame({"behavior": e.behavior, "cell": [f"{r.scenario}, {r.level}" for r in e.itertuples()],
                          "model": e.model, "difference [95% CI]": [ci(r) for r in e.to_dict("records")]}), index=False), "",
         "Nearest courier's own means: `c5_evening_by_return_nearest.csv`.", "", ACK]
    (a.out / "c5_tables.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
