"""S4: starting scenarios, supply levels with the fitted behavior, the few-idle rule of W1, and the scenario files.

Usage: python sim/scenarios.py <project_root> <out_dir> [workers]

Scenarios (plan decision 7). Each courier's preferred area is its start cell.
  big_cluster     every courier uniform over the cells within 1.5 km of the busiest pickup zone
  three_clusters  a third of the couriers around each of the three busiest pickup zones at least 4 km apart
  scattered       start cells drawn in proportion to the pickups expected in the first 30 min (as in S2)
  mixed           half as big_cluster, half as scattered
  burst           the scattered start, plus a 30-minute surge at 18:00 of 10% of the city's expected orders in that
                  half hour, with customers in one zone that has few couriers: among zones with restaurants and
                  residents at least 5 km from the busiest pickup zone and in the lowest quarter of expected pickups,
                  the most populated. The surge is a known event: it is part of the expected demand that W1 and the
                  forecasting models see.
Supply levels: the normal fleet stays at 2,495 couriers; with the fitted behavior, the volume is re-solved so the
normal fleet reaches the normal utilization on the scattered start, then the tight and loose fleets reach theirs
(G1 verdict, ruling 1).
Few-idle rule (plan decision 6), from nearest-courier runs only, 10 seeds per scenario and level:
  idle_weighted   episode W1 = snapshot W1 weighted by the number of idle couriers
  soon_free       supply = idle couriers plus couriers free within 5 min at their drop-off cell; plain mean
The rule with the lower mean between-seed coefficient of variation over the 15 scenario-level cells is chosen
(fewer episodes for the same power); the snapshot-to-snapshot jump size is reported beside it.
Outputs: scenarios/manifest.json, scenarios/starts.parquet (pilot seeds 1 to 30), <out_dir>/report.json, report.md.
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
from sim.calibrate import PEAK_WINDOW, SEEDS_SEARCH, SEEDS_VALID, scattered_start, solve  # noqa: E402
from sim.config import load_calibration, make_demand, make_params  # noqa: E402
from sim.core.behavior import Behavior, BehaviorParams  # noqa: E402
from sim.core.city import load  # noqa: E402
from sim.core.demand import Component  # noqa: E402
from sim.core.engine import Fleet, Simulator  # noqa: E402
from sim.core.metrics import summarize  # noqa: E402
from sim.core.policies import NearestIdle  # noqa: E402

SCENARIOS = ["big_cluster", "three_clusters", "scattered", "mixed", "burst"]
LEVELS = ["tight", "normal", "loose"]
CLUSTER_RADIUS_M = 1500.0
CLUSTER_MIN_SEP_M = 4000.0
BURST_START_S, BURST_DUR_S, BURST_SHARE, BURST_MIN_DIST_M = 3600.0, 1800.0, 0.10, 5000.0
FULL_TIME_SHARE = 0.4             # US ride-hailing figure (Ashkrof et al. 2024); Paris couriers 48% (via Allen et al. 2021)
SOON_S = 300.0
SEEDS_RULE = list(range(401, 411))
SEEDS_PILOT = list(range(1, 31))


# ---- scenario definitions --------------------------------------------------------------------------------------------
def zone_expected(city, demand, t0=0.0, t1=1800.0):
    return np.bincount(city.zone, weights=demand.expected_pickups(t0, t1), minlength=city.n_zones)


def busiest_zones(city, demand, k, min_sep_m):
    picked = []
    for z in np.argsort(-zone_expected(city, demand), kind="stable"):
        rep = int(city.zone_rep[z])
        if all(city.straight_m(rep, int(city.zone_rep[p])) >= min_sep_m for p in picked):
            picked.append(int(z))
        if len(picked) == k:
            break
    return picked


def near_cells(city, cell, radius_m=CLUSTER_RADIUS_M):
    return np.flatnonzero(city.straight_m(int(cell), np.arange(city.n)) <= radius_m)


def meetup_point(city, demand, hubs, t0_s, t1_s, min_hub_m=3000.0, radius_m=2000.0, target="min"):
    """Extension plan, decision 4 (rule of 2026-11-04, G6 verdict ruling 4): among cells at least min_hub_m (straight
    line) from every hub and with resident population above zero, the cell with the fewest expected pickups within
    radius_m (straight line) over [t0_s, t1_s). target="median" (G7 verdict E2(c), the exploratory point): the cell whose
    sum is closest to the median of those cells' sums. Returns (cell, expected pickups within radius_m). Ties (in
    Curitiba, 58 fringe cells have no restaurant within 2 km) go to the tied cell closest to the city centre, the most
    reachable one, then to the lower cell index."""
    allc = np.arange(city.n)
    ok = (city.pop > 0) & np.all([city.straight_m(int(h), allc) >= min_hub_m for h in hubs], axis=0)
    exp = demand.expected_pickups(t0_s, t1_s)
    cand = np.flatnonzero(ok)
    near = np.array([exp[city.straight_m(int(c), allc) <= radius_m].sum() for c in cand])
    gap = np.abs(near - {"min": near.min(), "median": np.median(near)}[target])
    tied = np.flatnonzero(gap == gap.min())
    best = tied[np.argmin(city.straight_m(city.centre, cand[tied]))]
    return int(cand[best]), float(near[best])


def burst_zone(city, demand):
    ze = zone_expected(city, demand, BURST_START_S, BURST_START_S + BURST_DUR_S)
    hub = int(city.zone_rep[busiest_zones(city, demand, 1, 0.0)[0]])
    pop = np.bincount(city.zone, weights=city.pop, minlength=city.n_zones)
    has_rest = np.bincount(city.zone, weights=(city.rest > 0).astype(float), minlength=city.n_zones) > 0
    far = np.array([city.straight_m(hub, int(city.zone_rep[z])) >= BURST_MIN_DIST_M for z in range(city.n_zones)])
    ok = has_rest & (pop > 0) & far & (ze > 0)
    cand = np.flatnonzero(ok & (ze <= np.quantile(ze[ok], 0.25)))
    return int(cand[np.argmax(pop[cand])])


def burst_component(city, base_demand, zone):
    n_half_hour = base_demand.expected_pickups(BURST_START_S, BURST_START_S + BURST_DUR_S).sum()
    rate = np.zeros(len(base_demand.components[0].rate_per_min))
    m0, m1 = int(BURST_START_S // 60), int((BURST_START_S + BURST_DUR_S) // 60)
    rate[m0:m1] = BURST_SHARE * n_half_hour / (m1 - m0)
    return Component(rate, np.where(city.zone == zone, city.pop, 0.0))


def scenario_demand(city, cal, scenario, orders_4h, zone=None):
    base = make_demand(city, cal, orders_4h=orders_4h)
    if scenario != "burst":
        return base
    return make_demand(city, cal, orders_4h=orders_4h, extra=[burst_component(city, base, zone)])


def starts(city, base_demand, scenario, n, seed, hubs):
    """Start cells for n couriers; base_demand (no burst) sets the scattered draw, so burst and scattered coincide."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 8, SCENARIOS.index(scenario)]))
    if scenario in ("scattered", "burst"):
        return scattered_start(city, base_demand, n, seed)
    if scenario == "big_cluster":
        return rng.choice(near_cells(city, hubs[0]), n)
    if scenario == "three_clusters":
        part = np.array_split(np.arange(n), 3)
        return np.concatenate([rng.choice(near_cells(city, h), len(p)) for h, p in zip(hubs, part)])
    half = n // 2
    return np.concatenate([rng.choice(near_cells(city, hubs[0]), half), scattered_start(city, base_demand, n, seed)[half:]])


def full_time(n, seed):
    return np.random.default_rng(np.random.SeedSequence([seed, 6])).uniform(size=n) < FULL_TIME_SHARE


# ---- episodes ----------------------------------------------------------------------------------------------------------
_W = {}


def _init(root, cal, setup):
    city = load(root / "sim/city/curitiba", layout=cal["layout"])
    _W.update(city=city, cal=cal, setup=setup)


def episode(args):
    """Nearest courier with the fitted behavior. Returns the summary row and, for the rule test, W1 under both rules."""
    scenario, n, orders_4h, seed, rule_test = args
    city, cal, st = _W["city"], _W["cal"], _W["setup"]
    base = make_demand(city, cal, orders_4h=orders_4h)
    demand = scenario_demand(city, cal, scenario, orders_4h, st.get("burst_zone"))
    params = make_params(cal, soon_s=SOON_S if rule_test else 0.0)
    orders = demand.sample(seed)
    s = starts(city, base, scenario, n, seed, [int(city.zone_rep[z]) for z in st["hub_zones"]])
    fleet = Fleet(start=s, home=s.copy(), full_time=full_time(n, seed))
    beh = Behavior(city, BehaviorParams(), base.pickup_share[0], params.speed_factor, seed, n)
    t0 = time.time()
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), beh, params, seed=seed).run()
    snaps = pd.DataFrame(sim.snapshots)
    win = snaps[(snaps.t >= PEAK_WINDOW[0]) & (snaps.t < PEAK_WINDOW[1])]
    row = {"scenario": scenario, "couriers": n, "orders_4h": orders_4h, "seed": seed,
           "util_peak": float((win.n_busy / n).mean()), "seconds": round(time.time() - t0, 1), **summarize(sim)}
    if rule_test:
        ok = snaps.w1_min.notna()
        row["w1_idle_weighted"] = float((snaps.w1_min[ok] * snaps.n_idle[ok]).sum() / snaps.n_idle[ok].sum())
        row["w1_soon_free"] = float(snaps.w1_soon_min.mean())
        row["few_idle_share"] = float((snaps.n_idle < 0.02 * n).mean())
        for col, key in [("w1_min", "jump_plain"), ("w1_soon_min", "jump_soon_free")]:
            x = snaps[col].to_numpy()
            row[key] = float(np.nanmean(np.abs(np.diff(x))) / np.nanmean(x))
        x, w = snaps.w1_min.to_numpy(), snaps.n_idle.to_numpy()
        d = np.abs(np.diff(x))
        ww = np.minimum(w[1:], w[:-1])
        good = np.isfinite(d)
        row["jump_idle_weighted"] = float((d[good] * ww[good]).sum() / ww[good].sum() / row["w1_idle_weighted"])
    return row


def cv(x):
    x = np.asarray(x, float)
    return float(x.std(ddof=1) / x.mean())


# ---- main ----------------------------------------------------------------------------------------------------------------
def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    cal = load_calibration()
    city = load(ROOT / "sim/city/curitiba", layout=cal["layout"])
    base = make_demand(city, cal)
    hubs = busiest_zones(city, base, 3, CLUSTER_MIN_SEP_M)
    bz = burst_zone(city, base)
    setup = {"hub_zones": hubs, "burst_zone": bz}
    rep = {"behavior": BehaviorParams().__dict__, "hub_zones": [str(city.cell[city.zone_rep[z]]) for z in hubs],
           "burst_zone_rep_cell": str(city.cell[city.zone_rep[bz]]),
           "burst_zone_km_from_hub": float(city.straight_m(int(city.zone_rep[hubs[0]]), int(city.zone_rep[bz])) / 1000),
           "cluster_cells": [int(len(near_cells(city, city.zone_rep[z]))) for z in hubs]}
    n_normal = cal["fleet"]["normal"]
    bands = cal["bands"]
    centres = {k: (v[0] + v[1]) / 2 for k, v in bands.items()}

    with Pool(workers, initializer=_init, initargs=(ROOT, cal, setup)) as pool:
        def util_at(n, v):
            rows = pool.map(episode, [("scattered", int(n), float(v), s, False) for s in SEEDS_SEARCH])
            u = float(np.mean([r["util_peak"] for r in rows]))
            print(f"  fleet {int(n)}, volume {v:.0f}: util {u:.3f}", flush=True)
            return u
        vol, _, tr_v = solve(pool, lambda v: util_at(n_normal, v), 0.5 * cal["orders_4h"], 1.5 * cal["orders_4h"],
                             centres["normal"], integer=True)
        n_t, _, tr_t = solve(pool, lambda n: util_at(n, vol), int(0.5 * n_normal), n_normal, centres["tight"], integer=True)
        n_l, _, tr_l = solve(pool, lambda n: util_at(n, vol), n_normal, int(2 * n_normal), centres["loose"], integer=True)
        fleets = {"tight": int(n_t), "normal": n_normal, "loose": int(n_l)}
        pd.DataFrame([{"search": "volume", "x": x, "util": u} for x, u in tr_v]
                     + [{"search": "tight_fleet", "x": x, "util": u} for x, u in tr_t]
                     + [{"search": "loose_fleet", "x": x, "util": u} for x, u in tr_l]).to_csv(out / "fleet_search.csv", index=False)
        print("volume", vol, "fleets", fleets, flush=True)
        valid = pool.map(episode, [("scattered", fleets[l], float(vol), s, False) for l in LEVELS for s in SEEDS_VALID])
        rule = pool.map(episode, [(sc, fleets[l], float(vol), s, True) for sc in SCENARIOS for l in LEVELS for s in SEEDS_RULE])

    v = pd.DataFrame(valid)
    v["level"] = np.repeat(LEVELS, len(SEEDS_VALID))
    v.to_csv(out / "validation_episodes.csv", index=False)
    util = {}
    for l in LEVELS:
        u = v[v.level == l].util_peak
        util[l] = {"couriers": fleets[l], "mean": float(u.mean()), "sd": float(u.std(ddof=1)), "band": bands[l],
                   "inside": bool(bands[l][0] <= u.mean() <= bands[l][1]),
                   "idle_km_per_order": float(v[v.level == l].idle_km_per_order.mean()),
                   "extra_km_per_order": float(v[v.level == l].extra_km_per_order.mean()),
                   "p90_c2d_min": float(v[v.level == l].p90_c2d_min.mean()),
                   "seconds": float(v[v.level == l].seconds.mean())}
    r = pd.DataFrame(rule)
    r["level"] = np.tile(np.repeat(LEVELS, len(SEEDS_RULE)), len(SCENARIOS))
    r.to_csv(out / "rule_episodes.csv", index=False)
    cells = r.groupby(["scenario", "level"]).agg(
        cv_idle_weighted=("w1_idle_weighted", cv), cv_soon_free=("w1_soon_free", cv), cv_plain=("w1_min", cv),
        jump_idle_weighted=("jump_idle_weighted", "mean"), jump_soon_free=("jump_soon_free", "mean"),
        jump_plain=("jump_plain", "mean"), few_idle_share=("few_idle_share", "mean"),
        w1_idle_weighted=("w1_idle_weighted", "mean"), w1_soon_free=("w1_soon_free", "mean"), w1_plain=("w1_min", "mean"))
    cells.to_csv(out / "rule_cells.csv")
    mean_cv = {k: float(cells[f"cv_{k}"].mean()) for k in ["idle_weighted", "soon_free", "plain"]}
    chosen = min(["idle_weighted", "soon_free"], key=lambda k: mean_cv[k])
    rep.update({"orders_4h": int(vol), "fleets": fleets, "utilization": util,
                "few_idle_rule": {"chosen": chosen, "mean_cv": mean_cv,
                                  "mean_jump": {k: float(cells[f"jump_{k}"].mean()) for k in ["idle_weighted", "soon_free", "plain"]}},
                "seconds": round(time.time() - t_start)})
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=float))
    write_files(city, cal, base, setup, vol, fleets, chosen, rep)
    print(json.dumps({k: rep[k] for k in ["orders_4h", "fleets", "utilization", "few_idle_rule"]}, indent=1, default=float))


def write_files(city, cal, base, setup, vol, fleets, rule, rep):
    folder = ROOT / "scenarios"
    folder.mkdir(exist_ok=True)
    hubs = [int(city.zone_rep[z]) for z in setup["hub_zones"]]
    rows = []
    for sc in SCENARIOS:
        for l in LEVELS:
            for seed in SEEDS_PILOT:
                s = starts(city, base, sc, fleets[l], seed, hubs)
                rows.append(pd.DataFrame({"scenario": sc, "level": l, "seed": seed, "courier": np.arange(len(s)),
                                          "start_cell": city.cell[s], "full_time": full_time(len(s), seed)}))
    df = pd.concat(rows, ignore_index=True)
    for c in ["scenario", "level", "start_cell"]:
        df[c] = df[c].astype("category")
    df.to_parquet(folder / "starts.parquet", index=False)
    manifest = {
        "scenarios": SCENARIOS, "levels": LEVELS, "fleets": fleets, "orders_4h": int(vol),
        "utilization_bands": cal["bands"], "behavior": rep["behavior"], "full_time_share": FULL_TIME_SHARE,
        "cluster": {"radius_m": CLUSTER_RADIUS_M, "min_separation_m": CLUSTER_MIN_SEP_M, "hub_cells": rep["hub_zones"]},
        "burst": {"start_s": BURST_START_S, "duration_s": BURST_DUR_S, "share_of_half_hour_orders": BURST_SHARE,
                  "min_distance_from_hub_m": BURST_MIN_DIST_M, "zone_rep_cell": rep["burst_zone_rep_cell"],
                  "known_event": True},
        "few_idle_rule": rule, "soon_s": SOON_S,
        "seeds": {"pilot": SEEDS_PILOT, "full_from": 1001, "rule_test": SEEDS_RULE, "fleet_search": SEEDS_SEARCH,
                  "fleet_validation": SEEDS_VALID},
        "starts_file": "scenarios/starts.parquet (pilot seeds; other seeds from sim/scenarios.py starts())",
        "calibration": "sim/params/calibration.json", "layout": cal["layout"]}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1, default=float))


if __name__ == "__main__":
    main()


def indep_homes(share, n, seed, tag=41):
    """Home cells independent of the start (package C, E6, setting `indep`): courier c's home is drawn from `share` (the
    scattered start's distribution: pickups expected in the first 30 min) with its own stream keyed by (seed, 41, c),
    so no other draw of the episode moves and a courier keeps its home whatever the fleet size. C6 (setting `resid`)
    draws from the expected drop-offs with the stream (seed, 42, c)."""
    p = np.asarray(share, float) / np.sum(share)
    return np.array([np.random.default_rng(np.random.SeedSequence([seed, tag, c])).choice(len(p), p=p) for c in range(n)],
                    dtype=np.int64)
