"""Extension plan X0: replay the 100 S8 reference episodes and compare every metric bit for bit.

Usage: python scripts/regression_check.py [workers]   (FE-SIM-1, needs the built city)
Prints the number of differing values by metric and exits 1 if any differs. The S8 reference ran at OpenBLAS's
default of 30 threads on FE-SIM-1, and values depend on the exact count (at 1, 2 or 8 threads W1 differs in the
last digit and forecast-aware matching decides differently in some episodes; DECISIONS.md, 2026-11-04), so the
script pins 30 threads itself. tests/test_regression.py runs it in a plain process.
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import collections
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REF = ROOT / "tests/regression/s8_reference.json"
METRICS = ["w1_rule_min", "w1_rule_first30_min", "w1_min", "w1_idle_weighted_min", "p90_c2d_min", "mean_c2d_min",
           "late_rate", "tv", "gini_idle", "uncovered", "extra_km_per_order", "idle_km_per_order", "earnings_gini",
           "food_wait_mean_min", "food_wait_p90_min", "unassigned_over_30min_share", "delivered", "undelivered", "orders"]
_EX = {}


def same(a, b):
    """Bit-for-bit equality, with two NaN counted as equal."""
    return a == b or (a != a and b != b)


def replay(case):
    from sim.runner import Experiment
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    row, _ = _EX["ex"].episode(case["scenario"], case["level"], case["seed"], case["model"], setting=case["behavior"])
    return case, {k: row[k] for k in METRICS}


def main():
    ref = json.loads(REF.read_text())
    assert len(ref) == 100
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else min(20, os.cpu_count() or 1)
    with Pool(workers) as pool:
        out = pool.map(replay, ref)
    bad = [(c["scenario"], c["model"], c["seed"], k, c["expected"][k], got[k])
           for c, got in out for k in METRICS if not same(got[k], c["expected"][k])]
    print(json.dumps({"episodes": len(out), "differ": len(bad), "by_metric": collections.Counter(b[3] for b in bad),
                      "first": bad[:5]}))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
