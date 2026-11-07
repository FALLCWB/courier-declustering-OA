"""X3: train the Xu et al. value table (learning and planning) offline, under the training budget fixed in DECISIONS.md.

Usage: python sim/train_xu.py <project_root> <out_dir> [workers]
For each training seed k = 1 to 5: 200 peaks under nearest courier (fitted behavior), each at a start and supply level
drawn from (k, i), episode seeds 90000 + 1000 k + i; their transitions give the value table by one backward
dynamic-programming pass (`models/xu_value.fit_value`). Learning curve: the table fitted on the first 25, 50, ..., 200
episodes, run on validation seeds 95001 to 95003 (big cluster and scattered, normal supply). Outputs
models/trained/xu_value_seed<k>.npz and <out_dir>/curve.csv, run.json.
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
from models.xu_value import N_SLOTS, XuValue, fit_value, transitions_from  # noqa: E402
from sim.runner import Experiment  # noqa: E402

SEEDS = [1, 2, 3, 4, 5]
EPISODES = 200
CHECKPOINTS = [25, 50, 75, 100, 125, 150, 175, 200]
VALID = [(s, "normal", v) for s in ["big_cluster", "scattered"] for v in (95001, 95002, 95003)]
COMBOS = [(s, l) for s in ["big_cluster", "three_clusters", "scattered", "mixed", "burst"] for l in ["tight", "normal", "loose"]]
_EX = {}


def ex():
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def collect(job):
    k, i = job
    rng = np.random.default_rng(np.random.SeedSequence([k, i, 77]))
    scenario, level = COMBOS[rng.integers(len(COMBOS))]
    _, sim = ex().episode(scenario, level, 90000 + 1000 * k + i, "nearest")
    return k, i, transitions_from(sim)


def evaluate(job):
    k, n, V, (scenario, level, seed) = job
    row, _ = ex().episode(scenario, level, seed, "xu", model_kw={"value": V})
    return {"training_seed": k, "episodes": n, "scenario": scenario, "seed": seed, "w1_rule_min": row["w1_rule_min"],
            "p90_c2d_min": row["p90_c2d_min"]}


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "models/trained").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    n_zones = ex().city.n_zones
    cache = out / "transitions.npz"                          # collected data kept, so a later failure loses nothing
    if cache.exists():
        z = np.load(cache)
        data = [(int(k), int(i), z[f"t_{k}_{i}"]) for k in SEEDS for i in range(EPISODES)]
    else:
        with Pool(workers) as pool:
            data = pool.map(collect, [(k, i) for k in SEEDS for i in range(EPISODES)])
        np.savez_compressed(cache, **{f"t_{k}_{i}": t for k, i, t in data})
    t1 = time.time()
    tables, jobs = {}, []
    for k in SEEDS:
        tr = sorted([(x[1], x[2]) for x in data if x[0] == k])
        for n in CHECKPOINTS:
            V = fit_value(np.vstack([t for _, t in tr[:n]]), n_zones)
            tables[(k, n)] = V
            jobs += [(k, n, V, case) for case in VALID]
        np.savez_compressed(ROOT / f"models/trained/xu_value_seed{k}.npz", V=tables[(k, EPISODES)], n_slots=N_SLOTS,
                            episodes=EPISODES)
    with Pool(workers) as pool:
        curve = pool.map(evaluate, jobs)
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "xu", "training_seeds": SEEDS, "episodes": EPISODES,
                                              "collect_wall_s": round(t1 - t0, 1), "total_wall_s": round(time.time() - t0, 1),
                                              "workers": workers}, indent=1))
    print(pd.DataFrame(curve).groupby(["episodes", "scenario"])[["w1_rule_min", "p90_c2d_min"]].mean().round(3))


if __name__ == "__main__":
    main()
