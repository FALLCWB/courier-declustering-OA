"""G7 verdict E1: Zhu et al.'s X5 rows rerun with the empty-part rule, beside the old rows.

Seed 501, normal supply, fitted behavior, policy as in sim/e2e_extension.py: Zhu at 100% and 0% obedience on the big
cluster, the meet-up and the scattered start, and nearest courier on the three (identity check at 0%). The old rows come
from avaliacao/20261104-0109-e2e-extension/metrics.csv (code before the rule). Per episode, the model's event counts:
control steps, commands sent, commands sent by the empty-part rule, couriers whose whole part holds no
pickup, and couriers that own no cell (they share a cell with a lower-index courier).

Usage: python scripts/x5_zhu_rerun.py <project_root> <out_dir> [workers]
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
from sim.stats import time_to_undo  # noqa: E402

SEED = 501
OLD = ROOT / "avaliacao/20261104-0109-e2e-extension/metrics.csv"
SCEN = ("big_cluster", "meetup", "scattered")
COLS = ["w1_rule_min", "w1_rule_60min_after_min", "time_to_undo_min", "p90_c2d_min", "unassigned_over_30min_share",
        "undelivered", "idle_km_per_order", "extra_km_per_order"]
_EX = {}


def job(args):
    model, scenario, obedience = args
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    t0 = time.time()
    row, _ = _EX["ex"].episode(scenario, "normal", SEED, model, obedience=obedience if model == "zhu" else None,
                               model_kw=None)
    row["seconds"] = round(time.time() - t0, 1)
    return (model, scenario, obedience), row


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    out.mkdir(parents=True, exist_ok=True)
    jobs = [("zhu", s, o) for s in SCEN for o in (1.0, 0.0)] + [("nearest", s, 1.0) for s in SCEN]
    t0 = time.time()
    with Pool(workers) as pool:
        rows = dict(pool.map(job, jobs, chunksize=1))
    for (m, s, o), r in rows.items():
        r["time_to_undo_min"] = (time_to_undo(r["w1_rule_series"], rows[(m, "scattered", o)]["w1_rule_series"],
                                              start_min=120 if s == "meetup" else 0) if s != "scattered" else np.nan)
    checks = {}
    for s in SCEN:
        z, n = rows[("zhu", s, 0.0)], rows[("nearest", s, 1.0)]
        checks[f"zhu_0pct_equals_nearest_{s}"] = bool(all(z[k] == n[k] or (pd.isna(z[k]) and pd.isna(n[k])) for k in COLS)
                                                      and np.array_equal(z["w1_rule_series"], n["w1_rule_series"], equal_nan=True))
    old = pd.read_csv(OLD)
    table = []
    for s in SCEN:
        for o in (1.0, 0.0):
            new = rows[("zhu", s, o)]
            prev = old[(old.model == "zhu") & (old.scenario == s) & (old.obedience == o)].iloc[0]
            for k in COLS:
                table.append({"scenario": s, "obedience": o, "metric": k, "old": prev[k], "new": new[k]})
            for k in ("events_steps", "events_commands", "events_whole_part_commands", "events_no_demand_in_part",
                      "events_owns_no_cell"):
                table.append({"scenario": s, "obedience": o, "metric": k, "old": np.nan, "new": new.get(k, np.nan)})
            table.append({"scenario": s, "obedience": o, "metric": "seconds", "old": prev["seconds"], "new": new["seconds"]})
    pd.DataFrame(table).to_csv(out / "zhu_old_and_new.csv", index=False)
    pd.DataFrame([dict(r, w1_rule_series=None) for r in rows.values()]).drop(columns="w1_rule_series").to_csv(
        out / "metrics.csv", index=False)
    series = pd.DataFrame({f"{m}|{s}|{o}": r["w1_rule_series"] for (m, s, o), r in rows.items()})
    series.insert(0, "minute_from_1700", np.arange(len(series)))
    series.to_csv(out / "w1_series.csv", index=False)
    summary = {"seed": SEED, "checks": checks, "wall_s": round(time.time() - t0, 1),
               "zhu_100pct_events": {s: {k[7:]: rows[("zhu", s, 1.0)].get(k) for k in rows[("zhu", s, 1.0)]
                                         if k.startswith("events_")} for s in SCEN}}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))
    print(pd.DataFrame(table).to_string(index=False))


if __name__ == "__main__":
    main()
