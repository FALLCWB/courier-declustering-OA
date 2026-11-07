"""G7 verdict, "For Paper A": the 25 forecast-aware S8 regression episodes replayed at one BLAS thread, against their
reference values at 30 threads (the S8 setting).

Reports, over the 25 episodes, the paired mean difference (1 thread minus 30) in W1 and in p90 order to door with 95%
percentile bootstrap intervals (10,000 resamples, generator seed 20261103), and how many episodes take other decisions
(any delivery or distance metric differs) or differ in W1 only.

Usage: python scripts/forecast_thread_check.py <project_root> <out_dir> [workers]
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
pin(1)  # the setting under test; the reference ran at 30
import json
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
REF = ROOT / "tests/regression/s8_reference.json"
W1 = ["w1_rule_min", "w1_rule_first30_min", "w1_min", "w1_idle_weighted_min"]
DECISION = ["p90_c2d_min", "mean_c2d_min", "late_rate", "extra_km_per_order", "idle_km_per_order", "delivered",
            "food_wait_mean_min", "food_wait_p90_min"]
_EX = {}


def replay(case):
    from sim.blas import threads
    from sim.runner import Experiment
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    row, _ = _EX["ex"].episode(case["scenario"], case["level"], case["seed"], case["model"], setting=case["behavior"])
    return case, row, threads()


def boot(d, reps=10000, seed=20261103):
    rng = np.random.default_rng(seed)
    m = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(reps)]
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    out.mkdir(parents=True, exist_ok=True)
    cases = [c for c in json.loads(REF.read_text()) if c["model"] == "forecast"]
    assert len(cases) == 25
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(replay, cases, chunksize=1)
    rows = []
    for case, row, th in res:
        e = case["expected"]
        rows.append({"scenario": case["scenario"], "level": case["level"], "behavior": case["behavior"], "seed": case["seed"],
                     "blas_threads": th, "w1_30": e["w1_rule_min"], "w1_1": row["w1_rule_min"],
                     "p90_30": e["p90_c2d_min"], "p90_1": row["p90_c2d_min"],
                     "decisions_differ": any(e[k] != row[k] for k in DECISION),
                     "w1_differs": any(e[k] != row[k] for k in W1)})
    df = pd.DataFrame(rows)
    df.to_csv(out / "episodes.csv", index=False)
    dw, dp = (df.w1_1 - df.w1_30).to_numpy(), (df.p90_1 - df.p90_30).to_numpy()
    summary = {"episodes": len(df), "blas_threads": sorted(df.blas_threads.unique().tolist()),
               "decisions_differ": int(df.decisions_differ.sum()),
               "w1_only_differs": int((df.w1_differs & ~df.decisions_differ).sum()),
               "identical": int((~df.w1_differs & ~df.decisions_differ).sum()),
               "w1_mean_diff_min": float(dw.mean()), "w1_mean_diff_ci95": boot(dw),
               "w1_max_abs_diff_min": float(np.abs(dw).max()),
               "p90_mean_diff_min": float(dp.mean()), "p90_mean_diff_ci95": boot(dp),
               "p90_max_abs_diff_min": float(np.abs(dp).max()),
               "wall_s": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
