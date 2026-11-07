"""G2 ruling 2: mean straight move per idle gap, simulated (fitted behavior, the 10 validation episodes of the final
behavior fit, seeds 311 to 320) and Meituan (17:00 to 20:59 and all day), with the shared definition of
sim/core/idle_moments.py.

Usage: python scripts/move_per_gap.py <project_root> <behavior_out_dir> [workers]
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
sys.path.insert(0, str(ROOT))
import sim.behavior_fit as bf  # noqa: E402
from sim.core import idle_moments as im  # noqa: E402
from sim.core.behavior import BehaviorParams  # noqa: E402


def run(seed):
    bp = BehaviorParams()
    return bf.episode(seed, {"p_return": bp.p_return, "epoch_s": bp.epoch_s, "cruise_radius_m": bp.cruise_radius_m,
                             "asc_stay": bp.coef["asc_stay"]})


def main():
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    idle, xy, _ = bf.meituan_gaps(ROOT)
    peak = idle.hour.isin(bf.PEAK_HOURS).to_numpy()
    rng = np.random.default_rng(20261101)
    out = {}
    for name, sel in [("meituan_peak", peak), ("meituan_all_day", np.ones(len(idle), bool))]:
        p, _ = bf.meituan_prepare(idle[sel], xy)
        out[name] = im.moments(p)["move_mean"]
        boot = im.bootstrap(p, ["move_mean"], 200, rng)[:, 0]
        out[name + "_ci95"] = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
    with Pool(workers, initializer=bf._init, initargs=(ROOT, bf.load_calibration(), {"single_decision": True})) as pool:
        res = pool.map(run, bf.SEEDS_VALID)
    g = {k: np.concatenate([x[0][k] for x in res]) for k in res[0][0]}
    p = im.prepare(g["courier"], g["gap_min"], g["D"], g["G"], g["H"], np.random.default_rng(13))
    out["simulated"] = im.moments(p)["move_mean"]
    boot = im.bootstrap(p, ["move_mean"], 200, rng)[:, 0]
    out["simulated_ci95"] = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
    out["simulated_gaps"], out["meituan_peak_gaps"] = int(len(p["move"])), int(peak.sum())
    (OUT / "move_per_gap.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
