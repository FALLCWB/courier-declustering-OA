"""Extension plan, decision 4 (G6 verdict ruling 4): the meet-up share check, on training-range seeds only.

Rule, fixed before the run (DECISIONS.md, 2026-11-04): nearest courier, scattered start, normal supply, fitted behavior,
seeds 96001 to 96030, each run with the meet-up (jump variant, 20% of the idle couriers at the manifest's cell at
19:00) and without it (the scattered start). W1 at 19:15 is the soon-free W1 of the snapshot at 8,100 s, the quantity
the episode W1 averages. If the mean over seeds of W1 at 19:15 with the meet-up exceeds the mean without it by less
than 10% of the latter, the share becomes 40%. The 40% runs are made too and reported for information; the decision
reads only the 20% runs.

Usage: python scripts/meetup_share_check.py <project_root> <out_dir> [workers]
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
T_CHECK = 8100.0
SHARES = (0.2, 0.4)
_EX = {}


def job(args):
    scenario, share, seed = args
    if share not in _EX:
        man = json.loads((ROOT / "scenarios/manifest.json").read_text())
        man["meetup"]["share"] = share
        _EX[share] = Experiment(ROOT, manifest=man)
    row, sim = _EX[share].episode(scenario, "normal", seed, "nearest")
    series = row["w1_rule_series"]
    t = [s["t"] for s in sim.snapshots]
    return {"scenario": scenario, "share": share if scenario != "scattered" else 0.0, "seed": seed,
            "w1_1915": float(series[t.index(T_CHECK)]), "w1_rule_min": row["w1_rule_min"],
            "w1_rule_60min_after_min": row["w1_rule_60min_after_min"], "p90_c2d_min": row["p90_c2d_min"],
            "series": series}


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    jobs = [("scattered", SHARES[0], s) for s in SEEDS] + [("meetup", sh, s) for sh in SHARES for s in SEEDS]
    t0 = time.time()
    with Pool(workers) as pool:
        rows = pool.map(job, jobs, chunksize=1)
    df = pd.DataFrame(rows)
    pd.DataFrame([dict(r, series=None) for r in rows]).drop(columns="series").to_csv(out / "episodes.csv", index=False)
    series = pd.DataFrame({f"{r['scenario']}_{r['share']}_{r['seed']}": r["series"] for r in rows})
    series.insert(0, "minute_from_1700", np.arange(len(series)))
    series.to_csv(out / "w1_series.csv", index=False)
    base = df[df.scenario == "scattered"].set_index("seed")["w1_1915"]
    summary = {"seeds": [SEEDS[0], SEEDS[-1]], "t_check_s": T_CHECK, "w1_1915_without": round(float(base.mean()), 3),
               "wall_s": round(time.time() - t0, 1)}
    for sh in SHARES:
        m = df[(df.scenario == "meetup") & (df.share == sh)].set_index("seed")["w1_1915"]
        d = (m - base.loc[m.index]).to_numpy()
        rng = np.random.default_rng(7)
        boot = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(10000)]
        summary[f"share_{sh}"] = {"w1_1915_with": round(float(m.mean()), 3),
                                  "rise_min": round(float(d.mean()), 3),
                                  "rise_share_of_without": round(float(d.mean() / base.mean()), 4),
                                  "rise_ci95_min": [round(float(np.percentile(boot, 2.5)), 3),
                                                    round(float(np.percentile(boot, 97.5)), 3)]}
    rise = summary["share_0.2"]["rise_share_of_without"]
    summary["decision"] = {"rule": "share 40% if the 20% rise at 19:15 is below 10% of W1 without the meet-up",
                           "rise_share_at_20pct": rise, "share": 0.2 if rise >= 0.10 else 0.4}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
