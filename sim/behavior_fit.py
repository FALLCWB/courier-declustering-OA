"""S3: fit courier idle behavior to the Meituan drift-back moments (simulated method of moments).

Usage: python sim/behavior_fit.py <project_root> <out_dir> [workers] [variant]

variant "free" (default): idle couriers re-decide every decision interval among stay, hotspot and cruise.
variant "one_move": at most one stay/hotspot/cruise move between two orders; returns to the preferred area still
repeat at every decision (BehaviorParams.one_move_per_gap), on a smaller grid.
variant "single": one decision per gap, one decision interval after the drop-off (return, stay, hotspot or cruise),
then the courier waits where it went (BehaviorParams.single_decision).
variant "single_ext": the same structure on a grid that extends past the edges where the "single" fit stopped.
variant "ashkrof" (package C part 3): the single structure with the part-time coefficient at 0, fitting only the stay
constant and the return probability (decision interval and cruise radius held at their fitted values).
An optional fifth argument gives the grid as JSON (keys p_return, epoch_s, cruise_radius_m, asc_stay).

Targets (sim/core/idle_moments.py, the definition of scripts/meituan_idle_behavior.py): Meituan idle gaps between waves
that start (last drop-off) at 17:00 to 20:59 local time, the window the simulator covers; at the 2 km radius, the
return share and its excess over the random-direction null by gap length, the stay share by gap length, and the move
quantiles. The all-day moments of the handed-over run are reproduced first as a check.

Simulated gaps: nearest-courier dispatch, normal fleet and volume of sim/params/calibration.json, scattered start,
preferred area = start cell, 40% full-time couriers; each gap from the drop-off to the cell the courier starts its
next order from. The drop-off point is uniform inside its hexagon; a courier that never moved keeps that point, one
that moved is uniform inside its end cell; H is the preferred cell's centre.

Fit: grid over return probability, decision interval, cruise radius and stay constant, then a local grid around the
best point; distance = sum over moments of (sim - obs)^2 / (var_obs + var_sim), variances from courier bootstraps.
Intervals: refit on 100 bootstrap replicates of the Meituan targets paired with bootstrap replicates of each grid
point's simulated moments. Checks: out-of-fit radii (1 and 3 km), all-day targets, idle and unladen km per order
against Allen et al. 2021 (about 2.1 km per job without an order, London), and two Meituan checks: the pull of the
preferred area against the nearest hotspot outside it, and returns within the courier's business district (da_id)
against across districts.
"""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import h3
import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.calibrate import EDGE_M, PEAK_HOURS, PEAK_WINDOW, TZ, planar, scattered_start  # noqa: E402
from sim.config import load_calibration, make_demand, make_params  # noqa: E402
from sim.core import idle_moments as im  # noqa: E402
from sim.core.behavior import Behavior, BehaviorParams  # noqa: E402
from sim.core.city import hex_points, load  # noqa: E402
from sim.core.engine import Fleet, Simulator  # noqa: E402
from sim.core.metrics import summarize  # noqa: E402
from sim.core.policies import NearestIdle  # noqa: E402

FULL_TIME_SHARE = 0.4          # Ashkrof et al. 2024: about 40% of US ride-hailing drivers rely fully on the job; for
                               # food couriers, Allen et al. 2021 cite a Paris survey with 48% full-time (claims check X1)
SEEDS_FIT = [301, 302]
SEEDS_VALID = list(range(311, 321))
N_BOOT = 100
GRID = {"p_return": [0.0, 0.15, 0.3, 0.5, 0.75, 1.0], "epoch_s": [120.0, 240.0, 480.0, 960.0],
        "cruise_radius_m": [500.0, 1000.0, 2000.0, 3000.0], "asc_stay": [-1.0, 0.0, 1.0, 2.0, 3.0]}
ALLEN_KM_WITHOUT_ORDER_PER_JOB = 2.1   # Allen et al. 2021, Table 1: (41.3 - 20.9) km / 9.6 jobs, London, Nov to Dec
GRID_SINGLE = {"p_return": [0.3, 0.5, 0.65, 0.8, 1.0], "epoch_s": [60.0, 120.0, 240.0, 480.0],
               "cruise_radius_m": [500.0, 1000.0, 2000.0, 3000.0], "asc_stay": [-1.0, 0.0, 1.0, 2.0]}
GRID_SINGLE_EXT = {"p_return": [0.85, 0.925, 1.0], "epoch_s": [15.0, 30.0, 42.0],
                   "cruise_radius_m": [2000.0, 2800.0], "asc_stay": [-3.0, -2.5, -2.0, -1.5]}
# package C part 3 (preregistration-addendum-C.md): part-time coefficient 0; only beta0 and the return probability move
GRID_ASHKROF = {"p_return": [0.55, 0.65, 0.75, 0.85, 0.95], "epoch_s": [42.0], "cruise_radius_m": [2000.0],
                "asc_stay": [-4.0, -3.5, -3.0, -2.5, -2.0]}
GRID_ONE_MOVE = {"p_return": [0.3, 0.5, 0.75, 1.0], "epoch_s": [120.0, 240.0, 480.0],
                 "cruise_radius_m": [500.0, 1000.0, 2000.0, 3000.0], "asc_stay": [-1.0, 0.0, 1.0, 2.0]}
NAMES = im.fit_names()


# ---- Meituan ---------------------------------------------------------------------------------------------------------
def meituan_gaps(root):
    """Idle gaps with D, G, H in planar metres, as in scripts/meituan_idle_behavior.py, plus the checks' columns."""
    wb = pd.read_parquet(root / "data/derived/waybills.parquet")
    g = wb[(wb.is_courier_grabbed == 1) & wb.grab_lat.notna()].copy()
    g["z8"] = [h3.latlng_to_cell(a, b, 8) for a, b in zip(g.grab_lat, g.grab_lng)]
    counts = g.groupby(["courier_id", "dt", "z8"]).size().rename("n").reset_index()
    days = counts.groupby("courier_id").dt.nunique()
    idle = pd.read_parquet(root / "data/derived/idle_moves.parquet")
    idle = idle[idle.courier_id.isin(days[days >= 2].index)].copy()
    home, home_da = {}, {}
    da = {cid: x for cid, x in g.groupby(["courier_id", "dt", "da_id"]).size().rename("n").reset_index().groupby("courier_id")}
    for cid, gg in counts[counts.courier_id.isin(idle.courier_id.unique())].groupby("courier_id"):
        dd = da[cid]
        for d in gg.dt.unique():
            other = gg[gg.dt != d].groupby("z8").n.sum()
            home[(cid, d)] = h3.cell_to_latlng(other.idxmax())
            od = dd[dd.dt != d].groupby("da_id").n.sum()
            home_da[(cid, d)] = od.idxmax() if len(od) else -1
    hl = np.array([home[(c, d)] for c, d in zip(idle.courier_id, idle.dt)])
    idle["home_lat"], idle["home_lng"] = hl[:, 0], hl[:, 1]
    idle["home_da"] = [home_da[(c, d)] for c, d in zip(idle.courier_id, idle.dt)]
    last = wb[wb.arrive_time > 0].drop_duplicates(["courier_id", "arrive_time"])[["courier_id", "arrive_time", "da_id"]]
    idle = idle.merge(last.rename(columns={"arrive_time": "t_end", "da_id": "start_da"}), on=["courier_id", "t_end"],
                      how="left")
    idle["hour"] = pd.to_datetime(idle.t_end, unit="s", utc=True).dt.tz_convert(TZ).dt.hour
    lat0 = np.radians(idle.lat0.mean())

    def xy(lat, lng):
        return np.stack([np.radians(lng) * np.cos(lat0) * 6371000.0, np.radians(lat) * 6371000.0], axis=-1)

    # Hotspots: H3 resolution-8 zones at or above the 95th percentile of pickups among zones with pickups.
    s = wb[wb.sender_lat.notna()]
    pz = pd.Series([h3.latlng_to_cell(a, b, 8) for a, b in zip(s.sender_lat, s.sender_lng)]).value_counts()
    hot = pz[pz >= pz.quantile(0.95)].index
    hot_ll = np.array([h3.cell_to_latlng(z) for z in hot])
    return idle, xy, xy(hot_ll[:, 0], hot_ll[:, 1])


def meituan_prepare(idle, xy, seed=20261101):
    D, G, H = xy(idle.lat0, idle.lng0), xy(idle.lat1, idle.lng1), xy(idle.home_lat, idle.home_lng)
    return im.prepare(idle.courier_id.to_numpy(), idle.gap_min.to_numpy(), D, G, H, np.random.default_rng(seed)), (D, G, H)


def pull_check(idle, D, G, H, hot_xy, rng, R=2000.0):
    """Gaps that start outside the preferred area and outside every candidate hotspot area: does the courier end in its
    preferred area more than in the nearest hotspot area outside it (both against the random-direction null)?"""
    dh = np.linalg.norm(hot_xy[None, :, :] - H[:, None, :], axis=2)
    dd = np.linalg.norm(hot_xy[None, :, :] - D[:, None, :], axis=2)
    cand = np.where((dh > R) & (dd > R), dd, np.inf)
    j = cand.argmin(axis=1)
    ok = np.isfinite(cand[np.arange(len(D)), j]) & (np.linalg.norm(D - H, axis=1) > R)
    X = hot_xy[j]
    move = np.linalg.norm(G - D, axis=1)
    theta = rng.uniform(0, 2 * np.pi, (len(D), im.NULL_DRAWS))
    Gn = D[:, None, :] + move[:, None, None] * np.stack([np.cos(theta), np.sin(theta)], axis=-1)
    exc_home = (np.linalg.norm(G - H, axis=1) <= R) - (np.linalg.norm(Gn - H[:, None, :], axis=2) <= R).mean(axis=1)
    exc_hot = (np.linalg.norm(G - X, axis=1) <= R) - (np.linalg.norm(Gn - X[:, None, :], axis=2) <= R).mean(axis=1)
    d = pd.DataFrame({"c": idle.courier_id.to_numpy()[ok], "home": exc_home[ok], "hot": exc_hot[ok],
                      "ret_home": (np.linalg.norm(G - H, axis=1) <= R)[ok], "ret_hot": (np.linalg.norm(G - X, axis=1) <= R)[ok],
                      "dist_home": np.linalg.norm(D - H, axis=1)[ok], "dist_hot": dd[np.arange(len(D)), j][ok]})
    return cluster_means(d, ["home", "hot", "ret_home", "ret_hot", "dist_home", "dist_hot"], rng, diff=("home", "hot"))


def district_check(idle, prep, rng, R=2000):
    """Return share and excess for gaps starting outside the preferred area, inside vs outside the home district."""
    o = prep[f"out_{R}"] & idle.start_da.notna().to_numpy() & (idle.home_da.to_numpy() != -1)
    same = (idle.start_da.to_numpy() == idle.home_da.to_numpy())
    out = {}
    for name, sel in [("same_district", o & same), ("other_district", o & ~same)]:
        d = pd.DataFrame({"c": idle.courier_id.to_numpy()[sel], "ret": prep[f"ret_{R}"][sel],
                          "exc": prep[f"ret_{R}"][sel] - prep[f"null_{R}"][sel]})
        out[name] = cluster_means(d, ["ret", "exc"], rng)
    return out


def cluster_means(d, cols, rng, diff=None, n=1000):
    """Means of columns with 95% courier-bootstrap intervals (ratio of sums), optionally of a difference."""
    g = d.groupby("c")[cols].sum()
    cnt = d.groupby("c").size().to_numpy()
    k = len(g)
    w = np.stack([np.bincount(rng.integers(0, k, k), minlength=k) for _ in range(n)])
    out = {"gaps": int(len(d)), "couriers": int(k)}
    for c in cols:
        v = (w @ g[c].to_numpy()) / (w @ cnt)
        out[c] = [float(g[c].sum() / cnt.sum()), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    if diff:
        v = (w @ (g[diff[0]] - g[diff[1]]).to_numpy()) / (w @ cnt)
        out[f"{diff[0]}_minus_{diff[1]}"] = [float((g[diff[0]] - g[diff[1]]).sum() / cnt.sum()),
                                              float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return out


# ---- simulation ------------------------------------------------------------------------------------------------------
_W = {}


def _init(root, cal, flags=None, coef_over=None):
    city = load(root / "sim/city/curitiba", layout=cal["layout"])
    _W.update(city=city, cal=cal, xy=planar(city), demand=make_demand(city, cal), flags=flags or {},
              coef_over=coef_over or {})


def episode(seed, bp, n=None, orders_4h=None):
    city, cal, xy = _W["city"], _W["cal"], _W["xy"]
    demand = _W["demand"] if orders_4h is None else make_demand(city, cal, orders_4h=orders_4h)
    params = make_params(cal)
    n = n or cal["fleet"]["normal"]
    orders = demand.sample(seed)
    start = scattered_start(city, demand, n, seed)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 6]))
    fleet = Fleet(start=start, home=start.copy(), full_time=rng.uniform(size=n) < FULL_TIME_SHARE)
    beh = Behavior(city, BehaviorParams(**{k: v for k, v in bp.items() if k != "asc_stay"}, coef=coef(bp),
                                        **_W.get("flags", {})),
                   demand.pickup_share[0], params.speed_factor, seed, n)
    t0 = time.time()
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), beh, params, seed=seed).run()
    secs = time.time() - t0
    g = np.array(sim.gaps, dtype=float).reshape(-1, 6)
    c, d_cell, g_cell, moved = g[:, 0].astype(int), g[:, 3].astype(int), g[:, 4].astype(int), g[:, 5] > 0
    D = xy[d_cell] + hex_points(len(g), rng) * EDGE_M
    G = np.where(moved[:, None], xy[g_cell] + hex_points(len(g), rng) * EDGE_M, D)
    H = xy[fleet.home[c]]
    snaps = pd.DataFrame(sim.snapshots)
    win = snaps[(snaps.t >= PEAK_WINDOW[0]) & (snaps.t < PEAK_WINDOW[1])]
    s = summarize(sim)
    row = {"seed": seed, "seconds": round(secs, 1), "util_peak": float((win.n_busy / n).mean()),
           "idle_km_per_order": s["idle_km_per_order"], "extra_km_per_order": s["extra_km_per_order"],
           "p90_c2d_min": s["p90_c2d_min"], "late_rate": s["late_rate"], "w1_min": s["w1_min"]}
    return {"courier": seed * 100000 + c, "gap_min": (g[:, 2] - g[:, 1]) / 60, "D": D, "G": G, "H": H}, row


def coef(bp):
    k = dict(BehaviorParams().coef)
    k.update(_W.get("coef_over", {}))                  # the ashkrof variant sets the part-time coefficient to 0
    k["asc_stay"] = bp["asc_stay"]
    return k


def variant_setup(variant):
    """(flags, grid, coefficient overrides, keys the local grid keeps fixed) of a fit variant."""
    flags = {"free": {"single_decision": False}, "one_move": {"one_move_per_gap": True, "single_decision": False},
             "single": {"single_decision": True}, "single_ext": {"single_decision": True},
             "ashkrof": {"single_decision": True}}[variant]
    grid = {"one_move": GRID_ONE_MOVE, "single": GRID_SINGLE, "single_ext": GRID_SINGLE_EXT,
            "ashkrof": GRID_ASHKROF}.get(variant, GRID)
    if variant == "ashkrof":
        return flags, grid, {"part_time_stay": 0.0}, {"epoch_s", "cruise_radius_m"}
    return flags, grid, {}, set()


def local_grid(best, fixed=frozenset()):
    """The local grid around the coarse best point; keys in `fixed` stay at the best value."""
    loc = {"p_return": sorted({min(max(best["p_return"] + d, 0.0), 1.0) for d in (-0.075, 0.0, 0.075)}),
           "epoch_s": [best["epoch_s"] * f for f in (0.7, 1.0, 1.4)],
           "cruise_radius_m": [best["cruise_radius_m"] * f for f in (0.7, 1.0, 1.4)],
           "asc_stay": [best["asc_stay"] + d for d in (-0.5, 0.0, 0.5)]}
    return {k: ([best[k]] if k in fixed else v) for k, v in loc.items()}


def local_points(best, fixed, seen):
    """The local grid around `best` as points keyed by name, in `best`'s key order, without the points already run
    (review of 2026-11-07: zipping the local values with the grid's key order scrambled parameters when they differed)."""
    have = {tuple(round(b[k], 9) for k in sorted(b)) for b in seen}
    loc = local_grid(best, fixed)
    out = []
    for v in itertools.product(*loc.values()):
        bp = dict(zip(loc, v))
        bp = {k: bp[k] for k in best}
        key = tuple(round(bp[k], 9) for k in sorted(bp))
        if key not in have:
            have.add(key)
            out.append(bp)
    return out


def edge_points(best, seen, fixed=frozenset()):
    """Grid points still to run when the best point lies on an edge of the values explored so far for a key that is
    fitted (not in `fixed`): the local grid around it, without the points already run. A return probability of 0 or 1
    is a bound of the parameter, not an edge. Empty when the best point is interior (G10 review, 2026-11-07)."""
    def edge(k):
        vals = {round(b[k], 9) for b in seen}
        x = round(best[k], 9)
        bound = k == "p_return"
        return (x == max(vals) and not (bound and x >= 1.0)) or (x == min(vals) and not (bound and x <= 0.0))
    if not any(edge(k) for k in best if k not in fixed):
        return []
    have = {tuple(round(b[k], 9) for k in sorted(b)) for b in seen}
    loc = local_grid(best, fixed)
    keys = list(loc)
    out = []
    for v in itertools.product(*loc.values()):
        bp = dict(zip(keys, v))
        if tuple(round(bp[k], 9) for k in sorted(bp)) not in have:
            out.append(bp)
    return out


STEP = {"p_return": 0.075, "asc_stay": 0.5}                            # additive steps (the fitted grid's)
RATIO = {"epoch_s": 1.4, "cruise_radius_m": 1.4}                       # multiplicative steps (as in local_grid)


def _step(k, x, d):
    """x moved d steps (d may be negative) for parameter k, kept inside its bounds; None when nothing is left."""
    y = x + d * STEP[k] if k in STEP else x * RATIO[k] ** d
    if k == "p_return":
        if (d > 0 and x >= 1.0) or (d < 0 and x <= 0.0):
            return None
        y = min(max(y, 0.0), 1.0)
    return round(y, 3)


def widen(k, coarse, explored):
    """The wide grid of parameter k (instructions 2026-11-07, package C extra; one rule for C7 and the Ashkrof interval):
    the coarse values, the lowest and highest values explored, and two steps beyond each of those, within bounds."""
    lo, hi = min(explored), max(explored)
    vals = set(coarse) | {lo, hi} | {v for v in (_step(k, lo, -2), _step(k, lo, -1), _step(k, hi, 1), _step(k, hi, 2))
                                     if v is not None}
    return sorted(round(v, 3) for v in vals)


def touches(band, vals):
    """(low, high): a band end lies in the outermost interval of the explored values (or on its end)."""
    v = sorted(set(round(x, 9) for x in vals))
    if len(v) < 2:
        return True, True
    return round(band[0], 9) < v[1] or round(band[0], 9) <= v[0], round(band[1], 9) > v[-2] or round(band[1], 9) >= v[-1]


def band_points(bands, seen, fixed=frozenset()):
    """Grid points that push a band end that still touches the explored values one step further out, across the other
    fitted keys' explored values inside their bands; a bound of the parameter is never passed."""
    keys = [k for k in seen[0] if k not in fixed]
    vals = {k: sorted({round(b[k], 9) for b in seen}) for k in seen[0]}
    have = {tuple(round(b[k], 9) for k in sorted(b)) for b in seen}
    out = []
    for k in keys:
        lo_t, hi_t = touches(bands[k], vals[k])
        new = [v for t, v in ((lo_t, _step(k, vals[k][0], -1)), (hi_t, _step(k, vals[k][-1], 1)))
               if t and v is not None and round(v, 9) not in vals[k]]
        if not new:
            continue
        other = {j: (vals[j] if j in fixed else [x for x in vals[j] if bands[j][0] - 1e-9 <= x <= bands[j][1] + 1e-9])
                 for j in seen[0] if j != k}
        for v in new:
            for combo in itertools.product(*other.values()):
                bp = {**dict(zip(other, combo)), k: v}
                bp = {j: bp[j] for j in seen[0]}
                key = tuple(round(bp[j], 9) for j in sorted(bp))
                if key not in have:
                    have.add(key)
                    out.append(bp)
    return out


def bands_of(res, obs_boot, var, keys):
    boots = np.stack([r["boot"] for r in res])                           # (grid, N_BOOT, moments)
    picks = [int(np.argmin(objective(boots[:, b, :], obs_boot[b], var))) for b in range(N_BOOT)]
    return picks, {k: [float(np.percentile([res[j]["bp"][k] for j in picks], 2.5)),
                       float(np.percentile([res[j]["bp"][k] for j in picks], 97.5))] for k in keys}


def grid_point(bp):
    gaps, rows = zip(*[episode(s, bp) for s in SEEDS_FIT])
    cat = {k: np.concatenate([x[k] for x in gaps]) for k in gaps[0]}
    p = im.prepare(cat["courier"], cat["gap_min"], cat["D"], cat["G"], cat["H"], np.random.default_rng(7))
    m = im.moments(p)
    boot = im.bootstrap(p, NAMES, N_BOOT, np.random.default_rng(11))
    return {"bp": bp, "m": m, "boot": boot, "rows": list(rows)}


def objective(sim, obs, var):
    """Distance over the fit moments; a grid point with a missing moment is rejected (infinite distance), and the
    targets and variances must be finite (five-agent review, S8)."""
    if not (np.isfinite(obs).all() and np.isfinite(var).all() and (var > 0).all()):
        raise ValueError("targets and variances of the fit must be finite and positive")
    d = (sim - obs) ** 2 / var
    return np.where(np.isfinite(d).all(axis=-1), d.sum(axis=-1), np.inf)


# ---- main ------------------------------------------------------------------------------------------------------------
def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    variant = sys.argv[4] if len(sys.argv) > 4 else "free"
    flags, grid, coef_over, fixed = variant_setup(variant)
    if len(sys.argv) > 5:                                    # a grid given as JSON, for a refit centred on an edge
        grid = json.loads(sys.argv[5])
    extend_bands = len(sys.argv) > 6 and sys.argv[6] == "bands"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    rep = {"variant": variant, "flags": flags, "grid": grid, "coef_overrides": coef_over}

    idle, xy, hot_xy = meituan_gaps(ROOT)
    # Check: the handed-over all-day moments are reproduced by the shared definition.
    p_all, (D, G, H) = meituan_prepare(idle, xy)
    m_all = im.moments(p_all)
    old = pd.read_csv(ROOT / "avaliacao/20261101-meituan-idle-moments/return_moments.csv")
    rep["reproduction_max_abs_diff"] = float(max(
        max(abs(m_all[f"ret_{r.radius_m}_{r.gap_min}"] - r.return_share), abs(m_all[f"exc_{r.radius_m}_{r.gap_min}"] - r.excess_over_null))
        for r in old.itertuples()))
    rng = np.random.default_rng(20261103)
    rep["meituan_all_day"] = m_all
    rep["check_preferred_area_vs_hotspot"] = pull_check(idle, D, G, H, hot_xy, rng)
    rep["check_district"] = district_check(idle, p_all, rng)

    peak = idle.hour.isin(PEAK_HOURS).to_numpy()
    p_obs, _ = meituan_prepare(idle[peak], xy)
    m_obs = im.moments(p_obs)
    obs = np.array([m_obs[x] for x in NAMES])
    obs_boot = im.bootstrap(p_obs, NAMES, N_BOOT, np.random.default_rng(12))
    rep["meituan_peak"] = m_obs
    rep["meituan_peak_se"] = dict(zip(NAMES, obs_boot.std(axis=0, ddof=1).tolist()))
    print("targets ready", round(time.time() - t_start), "s; reproduction diff", rep["reproduction_max_abs_diff"], flush=True)

    cal = load_calibration()
    keys = list(grid)
    coarse = [dict(zip(keys, v)) for v in itertools.product(*grid.values())]
    with Pool(workers, initializer=_init, initargs=(ROOT, cal, flags, coef_over)) as pool:
        res = []
        for i, r in enumerate(pool.imap(grid_point, coarse)):
            res.append(r)
            if i % 24 == 23:
                print(f"  coarse {i + 1}/{len(coarse)}", round(time.time() - t_start), "s", flush=True)
        var_sim = np.nanmedian(np.stack([r["boot"].var(axis=0, ddof=1) for r in res]), axis=0)
        var = obs_boot.var(axis=0, ddof=1) + var_sim
        best = min(res, key=lambda r: objective(np.array([r["m"][x] for x in NAMES]), obs, var))["bp"]
        print("coarse best", best, flush=True)

        fine = local_points(best, fixed, [r["bp"] for r in res])
        res += pool.map(grid_point, fine)
        rounds = 0                                                    # ashkrof: refine until the best point is interior
        while variant == "ashkrof" and rounds < 6:
            f = objective(np.stack([[r["m"][x] for x in NAMES] for r in res]), obs, var)
            extra = edge_points(res[int(np.argmin(f))]["bp"], [r["bp"] for r in res], fixed)
            if not extra:
                break
            print("best point on an edge; extending with", len(extra), "points", flush=True)
            res += pool.map(grid_point, extra)
            rounds += 1
        rep["edge_rounds"] = rounds
        brounds = 0                                                   # wide refits: grow while a band end touches
        while extend_bands and brounds < 8:
            _, ci = bands_of(res, obs_boot, var, keys)
            extra = band_points(ci, [r["bp"] for r in res], fixed)
            if not extra:
                break
            print("band end touches the grid; extending with", len(extra), "points", ci, flush=True)
            res += pool.map(grid_point, extra)
            brounds += 1
        rep["band_rounds"] = brounds

        sims = np.stack([[r["m"][x] for x in NAMES] for r in res])
        f = objective(sims, obs, var)
        i0 = int(np.argmin(f))
        fit = res[i0]["bp"]
        picks, ci = bands_of(res, obs_boot, var, keys)
        explored = {k: sorted({r["bp"][k] for r in res}) for k in keys}
        rep["bands_touch_grid"] = {k: list(touches(ci[k], explored[k])) for k in keys if k not in fixed}
        rep["explored_range"] = {k: [explored[k][0], explored[k][-1]] for k in keys}
        rep["fit"] = {"params": fit, "objective": float(f[i0]), "ci95": ci, "grid_points": len(res),
                      "bootstrap_picks_distinct": int(len(set(picks))),
                      "near_best_within_chi2_4": int((f - f[i0] <= 9.49).sum())}
        print("fit", rep["fit"], flush=True)

        valid = pool.starmap(episode, [(s, fit) for s in SEEDS_VALID])
    gaps = {k: np.concatenate([x[0][k] for x in valid]) for k in valid[0][0]}
    p_sim = im.prepare(gaps["courier"], gaps["gap_min"], gaps["D"], gaps["G"], gaps["H"], np.random.default_rng(13))
    m_sim = im.moments(p_sim)
    rows = pd.DataFrame([x[1] for x in valid])
    rows.to_csv(out / "validation_episodes.csv", index=False)
    rep["validation"] = {"moments": m_sim, "episodes": rows.mean(numeric_only=True).to_dict(),
                         "allen_km_without_order_per_job": ALLEN_KM_WITHOUT_ORDER_PER_JOB}
    table = pd.DataFrame({"moment": [k for k in m_sim if k.startswith(("ret_", "exc_", "stay_", "move_"))]})
    table["in_fit"] = table.moment.isin(NAMES)
    table["meituan_peak"] = table.moment.map(m_obs)
    table["meituan_all_day"] = table.moment.map(m_all)
    table["simulated"] = table.moment.map(m_sim)
    table.to_csv(out / "moments_table.csv", index=False)
    pd.DataFrame([{**r["bp"], "objective": float(fi), **{x: r["m"][x] for x in NAMES},
                   "util_peak": np.mean([z["util_peak"] for z in r["rows"]]),
                   "idle_km_per_order": np.mean([z["idle_km_per_order"] for z in r["rows"]]),
                   "extra_km_per_order": np.mean([z["extra_km_per_order"] for z in r["rows"]]),
                   "seconds": np.mean([z["seconds"] for z in r["rows"]])} for r, fi in zip(res, f)]).to_csv(
        out / "grid.csv", index=False)
    rep["seconds"] = round(time.time() - t_start)
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=float))
    figure(out, table)
    print(json.dumps({k: rep[k] for k in ["fit", "check_preferred_area_vs_hotspot", "check_district"]}, indent=1, default=float))


def figure(out, table):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2), constrained_layout=True)
    x = np.arange(len(im.BINS))
    for a, pre, title in [(ax[0], f"ret_{im.FIT_RADIUS_M}_", "Return share, 2 km area"),
                          (ax[1], f"exc_{im.FIT_RADIUS_M}_", "Excess over random direction, 2 km area"),
                          (ax[2], "stay_", "Stay share (move under 300 m)")]:
        t = table.set_index("moment")
        names = [pre + b for b in im.BINS]
        a.plot(x, t.loc[names, "meituan_peak"], "o-", label="Meituan 17:00 to 21:00")
        a.plot(x, t.loc[names, "simulated"], "s--", label="Simulation, fitted behavior")
        a.set_xticks(x, [f"{b} min" for b in im.BINS])
        a.set_title(title, fontsize=10)
        a.set_ylim(0, 1)
    h, lab = ax[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="outside lower center", ncol=2, frameon=False)
    fig.text(0.99, 0.01, "This research was supported by data provided by Meituan.", ha="right", fontsize=7)
    fig.savefig(out / "behavior_fit.png", dpi=130)


if __name__ == "__main__":
    main()
