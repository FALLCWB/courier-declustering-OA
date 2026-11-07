"""G4 verdict checks V2 and V3 (2026-11-03).

V2: the fitted behavior under the per-gap draws of the S8 review fix. The S3 validation episodes (seeds 311 to 320)
are rerun and their 17 fit moments set beside the values of `avaliacao/20261102-1146-behavior-single-final`; the S4
supply check (scattered start, nearest courier, seeds 201 to 210) gives the three busiest-hour utilizations beside
their bands and the S4 values. Nothing is refitted.
V3 (exploratory, outside the pre-registration): nearest courier, normal supply, return probability 0, seeds 1001 to
1030, big cluster and scattered starts, with and without the hotspot alternative (idle couriers then only stay or
cruise). If the big cluster's W1 falls toward the scattered level without hotspots, the hotspot explanation is
supported.

Usage: python scripts/g4_checks.py <project_root> <out_dir> [workers]
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
import sim.behavior_fit as bf  # noqa: E402
import sim.scenarios as sc  # noqa: E402
from sim.config import load_calibration  # noqa: E402
from sim.core import idle_moments as im  # noqa: E402
from sim.core.behavior import BehaviorParams  # noqa: E402
from sim.runner import Experiment  # noqa: E402

_W = {}


def v2_moments(seed):
    if "bf" not in _W:
        bf._init(ROOT, load_calibration(), {"single_decision": True})
        _W["bf"] = True
    bp = BehaviorParams()
    return bf.episode(seed, {"p_return": bp.p_return, "epoch_s": bp.epoch_s, "cruise_radius_m": bp.cruise_radius_m,
                             "asc_stay": bp.coef["asc_stay"]})


def v2_util(args):
    level, n, seed = args
    if "sc" not in _W:
        sc._init(ROOT, load_calibration(), {"hub_zones": [], "burst_zone": None})
        _W["sc"] = True
    man = json.loads((ROOT / "scenarios/manifest.json").read_text())
    row = sc.episode(("scattered", n, float(man["orders_4h"]), seed, False))
    return {"level": level, **row}


def v3(args):
    scenario, setting, seed = args
    if "ex" not in _W:
        _W["ex"] = Experiment(ROOT)
    row, _ = _W["ex"].episode(scenario, "normal", seed, "nearest", setting=setting)
    return row


def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    man = json.loads((ROOT / "scenarios/manifest.json").read_text())
    old = json.loads((ROOT / "avaliacao/20261102-1146-behavior-single-final/report.json").read_text())
    with Pool(min(workers, 10)) as pool:                 # one city per worker and phase (memory)
        mom = pool.map(v2_moments, bf.SEEDS_VALID)
    with Pool(workers) as pool:
        util = pool.map(v2_util, [(lvl, man["fleets"][lvl], s) for lvl in man["levels"] for s in range(201, 211)])
    with Pool(workers) as pool:
        exp = pool.map(v3, [(s_, b, seed) for s_ in ["big_cluster", "scattered"] for b in ["p0", "p0-nohotspot"]
                            for seed in range(1001, 1031)])
    g = {k: np.concatenate([x[0][k] for x in mom]) for k in mom[0][0]}
    p = im.prepare(g["courier"], g["gap_min"], g["D"], g["G"], g["H"], np.random.default_rng(13))
    new = im.moments(p)
    boot = im.bootstrap(p, bf.NAMES, 200, np.random.default_rng(14))
    rows = []
    for i, name in enumerate(bf.NAMES):
        lo, hi = np.percentile(boot[:, i], [2.5, 97.5])
        o = old["validation"]["moments"][name]
        rows.append({"moment": name, "meituan_peak": old["meituan_peak"][name], "old": o, "new": new[name], "new_lo": lo,
                     "new_hi": hi, "old_inside_new_interval": bool(lo <= o <= hi)})
    m = pd.DataFrame(rows)
    m.to_csv(out / "v2_moments.csv", index=False)
    u = pd.DataFrame(util)
    old_u = {"tight": 0.935, "normal": 0.718, "loose": 0.558}          # S4 report, `avaliacao/20261102-1156-scenarios`
    urows = []
    for lvl, gg in u.groupby("level"):
        band = man["utilization_bands"][lvl]
        urows.append({"level": lvl, "couriers": man["fleets"][lvl], "util_new": gg.util_peak.mean(), "util_old": old_u[lvl],
                      "band_lo": band[0], "band_hi": band[1], "inside": bool(band[0] <= gg.util_peak.mean() <= band[1]),
                      "idle_km_per_order": gg.idle_km_per_order.mean(), "extra_km_per_order": gg.extra_km_per_order.mean()})
    uu = pd.DataFrame(urows)
    uu.to_csv(out / "v2_utilization.csv", index=False)
    e = pd.DataFrame(exp)
    e.to_csv(out / "v3_episodes.csv", index=False)
    rng = np.random.default_rng(15)
    vrows = []
    for (s_, b), gg in e.groupby(["scenario", "behavior"]):
        x = gg.w1_rule_min.to_numpy()
        bs = x[rng.integers(0, len(x), (10_000, len(x)))].mean(axis=1)
        vrows.append({"scenario": s_, "behavior": b, "seeds": len(x), "w1_mean": x.mean(), "lo": np.percentile(bs, 2.5),
                      "hi": np.percentile(bs, 97.5), "idle_km_per_order": gg.idle_km_per_order.mean(),
                      "p90_c2d_min": gg.p90_c2d_min.mean()})
    v = pd.DataFrame(vrows)
    v.to_csv(out / "v3_summary.csv", index=False)
    piv = e.pivot_table(index="seed", columns=["scenario", "behavior"], values="w1_rule_min")
    gap_with = (piv[("big_cluster", "p0")] - piv[("scattered", "p0")]).mean()
    gap_without = (piv[("big_cluster", "p0-nohotspot")] - piv[("scattered", "p0-nohotspot")]).mean()
    res = {"v2_moments_outside": int((~m.old_inside_new_interval).sum()), "v2_utilization_inside_all": bool(uu.inside.all()),
           "v3_gap_with_hotspots": float(gap_with), "v3_gap_without_hotspots": float(gap_without)}
    (out / "summary.json").write_text(json.dumps(res, indent=1))
    print(m.round(3).to_string(index=False))
    print(uu.round(3).to_string(index=False))
    print(v.round(3).to_string(index=False))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
