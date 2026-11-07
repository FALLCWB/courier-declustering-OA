"""S2: calibrate the Curitiba simulator. Meituan rules timing; Grubhub and Meituan set the supply levels.

Usage: python sim/calibrate.py <project_root> <out_dir> [workers]

Fitted here, each with its source (report.md lists them):
  pickup handling  Meituan: courier within 100 m of the restaurant when accepting, food estimated ready: fetch minus
                   accept time (median); it overlaps the wait for food: leave at max(arrival + handling, ready)
  ride time        Meituan single-order waves, 17:00 to 20:59: ride_min = a + b * straight_km (OLS, courier bootstrap);
                   b sets the speed factor on the road travel times, a becomes the door overhead (park, walk, hand over)
  travel noise     lognormal factor with mean 1 on each order's pickup-to-door time and, with its own draw, on the
                   approach leg; sigma = 1.4826 * MAD of the log residuals of those rides around the fitted line (G1 F1)
  gravity scale    restaurant choice, fitted so simulated restaurant-to-customer straight distance matches Meituan (KS)
  preparation      parametric fit (lognormal, gamma, Weibull; lowest KS) to Meituan estimated meal-ready times, 1 to 60 min
  promise          Meituan promised time: intercept + per km, with the observed floor
  arrival shape    Meituan orders per 15 minutes, 17:00 to 20:59, mean over the 8 days
  fleet and volume IBGE PNAD 2022 delivery-app workers per resident, times Meituan shares of couriers working a given
                   day and active in the busiest hour, sets the normal fleet (all delivery apps under one dispatcher);
                   the volume is the load that fleet carries at Meituan's busiest-hour wave-time share, not Curitiba's
                   demand; loose is Meituan's lowest peak-hour share; tight is 0.925, near saturation, by design (G1 F2)
Then 10 validation episodes per supply level give the KS tests and the utilization intervals.
Courier idle behavior is "stay" here; the behavior fit is S3, and S4 resizes the fleets with the fitted behavior.
"""
import ast
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import h3
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.config import load_calibration, make_demand, make_params, prep_sample_s, rate_per_min  # noqa: E402
from sim.core.behavior import StayBehavior  # noqa: E402
from sim.core.city import hex_points, load  # noqa: E402
from sim.core.engine import Fleet, Simulator  # noqa: E402
from sim.core.metrics import summarize  # noqa: E402
from sim.core.policies import NearestIdle  # noqa: E402

TZ = "Asia/Shanghai"
PEAK_HOURS = range(17, 21)
LAYOUT = "s0"
EDGE_M = h3.average_hexagon_edge_length(9, unit="m")
GRAVITY_GRID = [60, 90, 120, 150, 180, 240, 300, 360, 420, 480, 600, 750, 900, 1200, 1500, 1800]
# IBGE, PNAD Continua 2022, "Teletrabalho e trabalho por meio de plataformas digitais" (informativo liv102035,
# experimental statistics, 4th quarter 2022): 589 thousand people worked through delivery apps (food, products etc.)
PNAD_DELIVERY_WORKERS = 589_000
BRAZIL_POP_2022 = 203_080_756      # IBGE Census 2022, resident population (SIDRA table 4709)
BAND_HALF = 0.05
TIGHT_UTIL = 0.925                 # by design, near saturation (G1 F2); Grubhub orders per courier-hour is context only
SEEDS_SEARCH = [101, 102, 103]
SEEDS_VALID = list(range(201, 211))
PEAK_WINDOW = (3600.0, 7200.0)     # 18:00 to 19:00, the busiest Meituan hour


def haversine_m(lat1, lng1, lat2, lng2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lng2 - lng1) / 2) ** 2
    return 2 * 6371000.0 * np.arcsin(np.sqrt(a))


def cluster_boot(df, fn, key, n=1000, seed=0):
    """95% percentile interval of fn(df) resampling clusters (couriers)."""
    rng = np.random.default_rng(seed)
    groups = {k: g for k, g in df.groupby(key)}
    keys = np.array(list(groups))
    vals = [fn(pd.concat([groups[k] for k in rng.choice(keys, len(keys))])) for _ in range(n)]
    return np.percentile(vals, [2.5, 97.5], axis=0)


# ---- targets -------------------------------------------------------------------------------------------------------
def meituan_targets(root):
    wb = pd.read_parquet(root / "data/derived/waybills.parquet")
    t = pd.to_datetime(wb.platform_order_time, unit="s", utc=True).dt.tz_convert(TZ)
    wb["hour"], wb["bin"] = t.dt.hour, (t.dt.hour * 60 + t.dt.minute) // 15
    ok = wb[(wb.is_courier_grabbed == 1) & (wb.fetch_time > 0) & (wb.arrive_time > wb.platform_order_time)
            & (wb.is_prebook == 0) & wb.sender_lat.notna() & wb.recipient_lat.notna()].copy()
    pk = ok[ok.hour.isin(PEAK_HOURS)].copy()
    pk["dist_m"] = haversine_m(pk.sender_lat, pk.sender_lng, pk.recipient_lat, pk.recipient_lng)
    pk["c2d_min"] = (pk.arrive_time - pk.platform_order_time) / 60
    pk["prep_min"] = (pk.estimate_meal_prepare_time - pk.platform_order_time) / 60
    pk["promise_min"] = (pk.estimate_arrived_time - pk.platform_order_time) / 60
    out = {"waybills": len(wb), "usable_orders": int(len(ok)), "peak_orders": int(len(pk)),
           "prebook_share": float(wb.is_prebook.mean()), "days": int(wb.dt.nunique())}

    wv = pd.read_csv(root / "data/raw/meituan/courier_wave_info_meituan.csv")
    wv["ids"] = wv.order_ids.map(ast.literal_eval)
    single = {ids[0] for ids in wv.ids if len(ids) == 1}
    wave_n = {o: len(ids) for ids in wv.ids for o in ids}
    pk["wave_n"] = pk.order_id.map(wave_n)
    out["share_peak_orders_in_single_order_waves"] = float((pk.wave_n == 1).mean())
    out["c2d_by_wave_size_q10_25_50_75_90"] = {str(k): g.c2d_min.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).tolist()
                                               for k, g in pk.groupby(pk.wave_n.clip(upper=4))}
    s1 = pk[pk.order_id.isin(single)].copy()
    s1["ride_min"] = (s1.arrive_time - s1.fetch_time) / 60
    s1 = s1[(s1.ride_min > 0) & (s1.ride_min < 120) & (s1.dist_m > 100)]
    s1["km"] = s1.dist_m / 1000

    def ols(d):
        b, a = np.polyfit(d.km, d.ride_min, 1)
        return np.array([a, b])

    ab = ols(s1)
    res = np.log(s1.ride_min / (ab[0] + ab[1] * s1.km))
    out["ride"] = {"orders": int(len(s1)), "couriers": int(s1.courier_id.nunique()), "intercept_min": float(ab[0]),
                   "per_km_min": float(ab[1]), "ci95": cluster_boot(s1, ols, "courier_id", n=300).tolist(),
                   "median_straight_kmh": float((s1.km / (s1.ride_min / 60)).median()),
                   "marginal_straight_kmh": float(60 / ab[1]),
                   "log_residual_sd": float(res.std()), "log_residual_median": float(res.median()),
                   "log_residual_sigma_robust": float(1.4826 * (res - res.median()).abs().median())}

    # Orders delivered alone (single-order waves): the comparable targets for a one-order simulator (G1 F4).
    sw = pk[pk.wave_n == 1]
    q5 = [0.1, 0.25, 0.5, 0.75, 0.9]
    acc = (sw.grab_time - sw.platform_order_time)[sw.grab_time > 0] / 60
    fme = (sw.fetch_time - sw.estimate_meal_prepare_time) / 60
    out["single_order_waves"] = {
        "orders": int(len(sw)), "late_share": float((sw.arrive_time > sw.estimate_arrived_time).mean()),
        "order_to_fetch_q10_25_50_75_90": ((sw.fetch_time - sw.platform_order_time) / 60).quantile(q5).tolist(),
        "accept_after_order_q10_25_50_75_90": acc.quantile(q5).tolist(),
        "fetch_minus_estimated_ready_q10_25_50_75_90": fme.quantile(q5).tolist(),
        "fetched_before_estimated_ready_share": float((fme < 0).mean())}
    acc_all = (pk.grab_time - pk.platform_order_time)[pk.grab_time > 0] / 60
    out["accept_after_order_all_peak_q10_25_50_75_90"] = acc_all.quantile(q5).tolist()

    pr = pk[(pk.promise_min > 0) & (pk.promise_min < 180)]
    b, a = np.polyfit(pr.dist_m / 1000, pr.promise_min, 1)
    out["promise"] = {"intercept_min": float(a), "per_km_min": float(b), "floor_min": float(pr.promise_min.quantile(0.01)),
                      "late_share": float((pk.arrive_time > pk.estimate_arrived_time).mean())}
    valid = pk.prep_min.between(1, 60)
    out["prep_excluded_share"] = float(1 - valid.mean())
    low = pk.prep_min < 1
    out["prep_under_1min_order_to_fetch_median_min"] = float(((pk.fetch_time - pk.platform_order_time)[low] / 60).median())
    out["prep_valid_order_to_fetch_median_min"] = float(((pk.fetch_time - pk.platform_order_time)[valid] / 60).median())
    # Pickup handling: courier within 100 m of the restaurant when accepting, food estimated ready by then.
    pk["grab_rest_m"] = haversine_m(pk.grab_lat, pk.grab_lng, pk.sender_lat, pk.sender_lng)
    near = pk[(pk.grab_rest_m < 100) & (pk.grab_time > 0) & (pk.estimate_meal_prepare_time <= pk.grab_time)]
    hand = (near.fetch_time - near.grab_time) / 60
    out["pickup_handling"] = {"orders": int(len(near)), "median_min": float(hand.median()),
                              "quantiles_10_25_50_75_90": hand.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).tolist()}

    days = sorted(ok.dt.unique())
    shape = (ok[ok.hour.isin(PEAK_HOURS)].groupby(["dt", "bin"]).size().unstack(0).reindex(range(68, 84)).fillna(0))
    out["shape_15min"] = (shape.mean(axis=1) / shape.mean(axis=1).sum()).tolist()
    out["orders_4h_per_day_mean"] = float(shape.sum().mean())

    wv["t0"] = pd.to_datetime(wv.wave_start_time, unit="s", utc=True).dt.tz_convert(TZ)
    wv["t1"] = pd.to_datetime(wv.wave_end_time, unit="s", utc=True).dt.tz_convert(TZ)
    rows = []
    for dt, g in wv.groupby("dt"):
        day = pd.Timestamp(str(dt), tz=TZ)
        for h in PEAK_HOURS:
            a0, a1 = day + pd.Timedelta(hours=h), day + pd.Timedelta(hours=h + 1)
            ov = g[(g.t0 < a1) & (g.t1 > a0)]
            busy = ((ov.t1.clip(upper=a1) - ov.t0.clip(lower=a0)).dt.total_seconds() / 3600).sum()
            rows.append({"dt": dt, "hour": h, "couriers": ov.courier_id.nunique(), "busy_h": busy,
                         "orders": int(((pk.dt == dt) & (pk.hour == h)).sum()), "day_couriers": g.courier_id.nunique()})
    hr = pd.DataFrame(rows)
    hr["och"], hr["wave_share"] = hr.orders / hr.couriers, hr.busy_h / hr.couriers
    by_h = hr.groupby("hour")[["couriers", "orders", "och", "wave_share", "day_couriers"]].mean()
    busiest = int(by_h.orders.idxmax())
    out["hourly"] = by_h.reset_index().to_dict("records")
    out["busiest_hour"] = busiest
    out["share_working_a_given_day"] = float(by_h.day_couriers.iloc[0] / wv.courier_id.nunique())
    out["share_of_day_couriers_active_busiest_hour"] = float(by_h.couriers[busiest] / by_h.day_couriers[busiest])
    out["wave_share_busiest_hour"] = float(by_h.wave_share[busiest])
    out["wave_share_lowest_peak_hour"] = float(by_h.wave_share.min())
    samples = {"dist_m": pk.dist_m.to_numpy(), "c2d_min": pk.c2d_min.to_numpy(),
               "prep_min_valid": pk.prep_min[valid].to_numpy(),
               "prep_min_all": pk.prep_min[pk.prep_min.between(-1, 120)].to_numpy().clip(0, None),
               "ride_min_single": s1.ride_min.to_numpy(), "ride_km_single": s1.km.to_numpy(),
               "to_fetch_min": ((pk.fetch_time - pk.platform_order_time) / 60).to_numpy(),
               "to_fetch_min_single_wave": ((sw.fetch_time - sw.platform_order_time) / 60).to_numpy(),
               "c2d_min_single_wave": pk.c2d_min[pk.wave_n == 1].to_numpy()}
    return out, samples


def grubhub_targets(root):
    rows, prep, dist = [], [], []
    for d in sorted((root / "data/raw/grubhub/mdrplib-master/public_instances").glob("*o100t100s1p100")):
        o = pd.read_csv(d / "orders.txt", sep="\t")
        c = pd.read_csv(d / "couriers.txt", sep="\t")
        r = pd.read_csv(d / "restaurants.txt", sep="\t")
        o = o.merge(r, on="restaurant", suffixes=("", "_r"))
        prep.append((o.ready_time - o.placement_time).to_numpy(float))
        dist.append(np.hypot(o.x - o.x_r, o.y - o.y_r).to_numpy(float))
        h = (o.placement_time // 60).astype(int)
        peak = int(h.value_counts().idxmax())
        ch = (np.minimum(c.off_time, (peak + 1) * 60) - np.maximum(c.on_time, peak * 60)).clip(lower=0).sum() / 60
        mpm = float(pd.read_csv(d / "instance_parameters.txt", sep="\t").meters_per_minute.iloc[0])
        rows.append({"instance": d.name, "orders": len(o), "peak_hour": peak, "peak_orders": int((h == peak).sum()),
                     "peak_courier_hours": float(ch), "och_peak": float((h == peak).sum() / ch), "meters_per_minute": mpm})
    t = pd.DataFrame(rows)
    return ({"instances": rows, "och_peak_median": float(t.och_peak.median()),
             "och_peak_range": [float(t.och_peak.min()), float(t.och_peak.max())],
             "meters_per_minute_range": [float(t.meters_per_minute.min()), float(t.meters_per_minute.max())],
             "speed_kmh_range": [float(t.meters_per_minute.min()) * 0.06, float(t.meters_per_minute.max()) * 0.06]},
            {"prep_min": np.concatenate(prep), "dist_m": np.concatenate(dist)})


# ---- simulated quantities --------------------------------------------------------------------------------------------
def planar(city):
    lat0 = np.radians(city.lat.mean())
    return np.stack([np.radians(city.lng) * np.cos(lat0) * 6371000.0, np.radians(city.lat) * 6371000.0], axis=1)


def jittered_m(xy, a, b, rng):
    """Straight distance between uniform points inside cells a and b (hexagons of the H3 resolution-9 edge)."""
    pa, pb = hex_points(len(a), rng) * EDGE_M, hex_points(len(b), rng) * EDGE_M
    return np.linalg.norm(xy[a] + pa - xy[b] - pb, axis=1)


def sample_pairs(demand, n, rng):
    city = demand.city
    cust = rng.choice(city.n, size=n, p=city.pop / city.pop.sum())
    u = rng.uniform(size=n)
    j = np.minimum((demand.choice_cdf[cust] < u[:, None]).sum(axis=1), len(demand.rest_cells) - 1)
    return demand.rest_cells[j], cust


def ks(a, b):
    r = stats.ks_2samp(a, b)
    return {"D": float(r.statistic), "p": float(r.pvalue), "n_sim": int(len(a)), "n_obs": int(len(b))}


# ---- episodes ------------------------------------------------------------------------------------------------------
_W = {}


def _init(root, cal):
    city = load(root / "sim/city/curitiba", layout=LAYOUT)
    _W.update(city=city, cal=cal)


def scattered_start(city, demand, n, seed):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 4]))
    share = demand.expected_pickups(0, 1800)
    return rng.choice(city.n, size=n, p=share / share.sum())


def episode(args):
    """One 4-hour episode, nearest-courier policy, couriers stay where they are while idle."""
    seed, n_couriers, orders_4h, sf_mult, keep_orders = args
    city, cal = _W["city"], _W["cal"]
    demand = make_demand(city, cal, orders_4h=orders_4h)
    params = make_params(cal, speed_factor=cal["speed_factor"] * sf_mult)
    orders = demand.sample(seed)
    start = scattered_start(city, demand, n_couriers, seed)
    fleet = Fleet(start=start, home=start.copy(), full_time=np.ones(n_couriers, bool))
    t0 = time.time()
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), StayBehavior(n_couriers), params, seed=seed).run()
    snaps = pd.DataFrame(sim.snapshots)
    win = snaps[(snaps.t >= PEAK_WINDOW[0]) & (snaps.t < PEAK_WINDOW[1])]
    inside = orders.placed < params.horizon_s
    busy_time = (sim.o_free - sim.o_assigned)[inside]
    row = {"seed": seed, "couriers": n_couriers, "orders_4h": orders_4h, "sf_mult": sf_mult,
           "util_peak": float((win.n_busy / n_couriers).mean()), "util_max_15min": float(
               (snaps.n_busy / n_couriers).rolling(15).mean().max()),
           "pending_peak_mean": float(win.n_pending.mean()), "busy_min_per_order": float(np.nanmean(busy_time) / 60),
           "seconds": round(time.time() - t0, 1), **summarize(sim)}
    if keep_orders:
        done = inside & ~np.isnan(sim.o_door)
        row["_orders"] = {"rest": orders.rest[done], "cust": orders.cust[done],
                          "c2d_min": (sim.o_door[done] - orders.placed[done]) / 60,
                          "prep_min": (orders.ready[done] - orders.placed[done]) / 60,
                          "ride_min": (sim.o_door[done] - sim.o_pickup[done]) / 60,
                          "to_pickup_min": (sim.o_pickup[done] - orders.placed[done]) / 60}
    return row


def run_many(pool, jobs):
    return pool.map(episode, jobs)


def mean_util(rows):
    return float(np.mean([r["util_peak"] for r in rows]))


def solve(pool, f, lo, hi, target, tol=0.005, iters=14, integer=False):
    """Find x in [lo, hi] with f(x) close to target, f monotone (bisection); returns (x, value, trace)."""
    trace = []
    flo, fhi = f(lo), f(hi)
    trace += [(lo, flo), (hi, fhi)]
    if not min(flo, fhi) - tol <= target <= max(flo, fhi) + tol:
        raise ValueError(f"target {target} is not between f({lo}) = {flo} and f({hi}) = {fhi}")
    inc = fhi > flo
    for _ in range(iters):
        mid = (lo + hi) / 2
        if integer:
            mid = int(round(mid))
            if mid in (lo, hi):
                break
        fm = f(mid)
        trace.append((mid, fm))
        if abs(fm - target) <= tol:
            return mid, fm, trace
        if (fm < target) == inc:
            lo = mid
        else:
            hi = mid
    best = min(trace, key=lambda x: abs(x[1] - target))
    if abs(best[1] - target) > 2 * tol:
        raise ValueError(f"bisection stopped {abs(best[1] - target):.4f} from the target; trace {trace}")
    return best[0], best[1], trace


# ---- main ------------------------------------------------------------------------------------------------------------
def main():
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    rep = {}

    mt, ms = meituan_targets(ROOT)
    gt, gs = grubhub_targets(ROOT)
    rep["meituan"], rep["grubhub"] = mt, gt
    print("targets ready", round(time.time() - t_start), "s", flush=True)

    city = load(ROOT / "sim/city/curitiba", layout=LAYOUT)
    xy = planar(city)
    rep["intra_cell_trip"] = {"t_s": float(city.T[0, 0]), "d_m": float(city.Dm[0, 0])}

    # Preparation time: parametric fit on valid estimates.
    prep_obs = ms["prep_min_valid"]
    fits = {}
    for name in ["lognorm", "gamma", "weibull_min"]:
        par = getattr(stats, name).fit(prep_obs, floc=0)
        d = stats.kstest(prep_obs, name, args=par)
        fits[name] = {"params": [float(x) for x in par], "ks_D": float(d.statistic)}
    best_prep = min(fits, key=lambda k: fits[k]["ks_D"])
    rep["prep_fits"] = fits

    # Gravity scale: KS distance between simulated and Meituan restaurant-to-customer straight distances.
    rng = np.random.default_rng(20261102)
    base = {"arrival_shape_15min": mt["shape_15min"], "orders_4h": 1000.0,
            "prep": {"dist": best_prep, "params": fits[best_prep]["params"]},
            "promise": {"intercept_s": mt["promise"]["intercept_min"] * 60, "per_km_s": mt["promise"]["per_km_min"] * 60,
                        "floor_s": mt["promise"]["floor_min"] * 60}, "gravity_s": 600.0}
    grav = []
    for g in GRAVITY_GRID:
        dem = make_demand(city, base, gravity_s=float(g))
        r, k = sample_pairs(dem, 100000, rng)
        grav.append({"gravity_s": g, "ks_D": ks(jittered_m(xy, r, k, rng), ms["dist_m"])["D"],
                     "median_m": float(np.median(jittered_m(xy, r, k, rng))), "same_cell_share": float((r == k).mean())})
    g0 = min(grav, key=lambda x: x["ks_D"])["gravity_s"]
    i0 = GRAVITY_GRID.index(g0)
    lo_g, hi_g = GRAVITY_GRID[max(i0 - 1, 0)], GRAVITY_GRID[min(i0 + 1, len(GRAVITY_GRID) - 1)]
    for g in np.linspace(lo_g, hi_g, 9)[1:-1]:
        dem = make_demand(city, base, gravity_s=float(g))
        r, k = sample_pairs(dem, 100000, rng)
        grav.append({"gravity_s": float(g), "ks_D": ks(jittered_m(xy, r, k, rng), ms["dist_m"])["D"],
                     "median_m": float(np.median(jittered_m(xy, r, k, rng))), "same_cell_share": float((r == k).mean())})
    gravity = float(min(grav, key=lambda x: x["ks_D"])["gravity_s"])
    pd.DataFrame(grav).sort_values("gravity_s").to_csv(out / "gravity_search.csv", index=False)
    base["gravity_s"] = gravity
    print("gravity", gravity, flush=True)

    # Speed factor: simulated ride time T * sf equals Meituan's per-km slope times straight km (ratio of sums).
    dem = make_demand(city, base)
    r, k = sample_pairs(dem, 200000, rng)
    m = r != k
    km = city.straight_m(r[m], k[m]) / 1000
    sf = float(mt["ride"]["per_km_min"] * km.sum() / (city.T[r[m], k[m]].astype(float) / 60).sum())
    cal = {**base, "speed_factor": sf, "door_overhead_s": mt["ride"]["intercept_min"] * 60,
           "ride_sigma": mt["ride"]["log_residual_sigma_robust"],
           "pickup_service_s": mt["pickup_handling"]["median_min"] * 60, "pickup_overlaps_wait": True,
           "dropoff_service_s": 0.0, "layout": LAYOUT}

    # Normal fleet from IBGE PNAD and Meituan activity shares.
    pop = float(city.pop.sum())
    cwb_workers = PNAD_DELIVERY_WORKERS / BRAZIL_POP_2022 * pop
    n_normal = int(round(cwb_workers * mt["share_working_a_given_day"] * mt["share_of_day_couriers_active_busiest_hour"]))
    u_normal, u_loose = mt["wave_share_busiest_hour"], mt["wave_share_lowest_peak_hour"]
    rep["fleet_anchor"] = {"pnad_delivery_workers_brazil": PNAD_DELIVERY_WORKERS, "brazil_pop_2022": BRAZIL_POP_2022,
                           "curitiba_pop_in_grid": pop, "curitiba_delivery_workers": cwb_workers,
                           "share_working_a_given_day": mt["share_working_a_given_day"],
                           "share_active_busiest_hour": mt["share_of_day_couriers_active_busiest_hour"],
                           "normal_fleet": n_normal}

    tmp = out / "calibration_tmp.json"
    tmp.write_text(json.dumps(cal))
    with Pool(workers, initializer=_init, initargs=(ROOT, cal)) as pool:
        # Volume: busiest-hour utilization of the normal fleet equals Meituan's busiest-hour wave share.
        def util_v(v):
            rows = run_many(pool, [(s, n_normal, float(v), 1.0, False) for s in SEEDS_SEARCH])
            u = mean_util(rows)
            print(f"  volume {v:.0f}: util {u:.3f}", flush=True)
            return u
        vol, u_v, tr_v = solve(pool, util_v, 0.5 * n_normal, 6.0 * n_normal, u_normal, integer=True)
        cal["orders_4h"] = float(vol)
        rows = run_many(pool, [(s, n_normal, float(vol), 1.0, False) for s in SEEDS_SEARCH])
        tau_h = float(np.mean([x["busy_min_per_order"] for x in rows])) / 60
        u_tight = TIGHT_UTIL
        bands = {"tight": [u_tight - BAND_HALF, u_tight + BAND_HALF], "normal": [u_normal - BAND_HALF, u_normal + BAND_HALF],
                 "loose": [u_loose - BAND_HALF, u_loose + BAND_HALF]}
        rep["bands"] = {"centres": {"tight": u_tight, "normal": u_normal, "loose": u_loose}, "bands": bands,
                        "busy_hours_per_order_at_normal": tau_h,
                        "grubhub_och_peak_times_busy_hours_context_only": gt["och_peak_median"] * tau_h}
        print("bands", bands, flush=True)

        def util_n(n):
            rows = run_many(pool, [(s, int(n), float(vol), 1.0, False) for s in SEEDS_SEARCH])
            u = mean_util(rows)
            print(f"  fleet {int(n)}: util {u:.3f}", flush=True)
            return u
        fleets = {"normal": n_normal}
        n_t, _, tr_t = solve(pool, util_n, int(0.3 * n_normal), n_normal, u_tight, integer=True)
        n_l, _, tr_l = solve(pool, util_n, n_normal, int(3 * n_normal), u_loose, integer=True)
        fleets["tight"], fleets["loose"] = int(n_t), int(n_l)
        cal["fleet"] = fleets
        cal["bands"] = bands
        pd.DataFrame([{"search": "volume", "x": x, "util": u} for x, u in tr_v]
                     + [{"search": "tight_fleet", "x": x, "util": u} for x, u in tr_t]
                     + [{"search": "loose_fleet", "x": x, "util": u} for x, u in tr_l]).to_csv(out / "fleet_search.csv", index=False)

        # Validation: 10 episodes per supply level, and the speed sensitivity at the normal level.
        valid = {}
        for lvl in ["tight", "normal", "loose"]:
            valid[lvl] = run_many(pool, [(s, fleets[lvl], float(vol), 1.0, lvl == "normal") for s in SEEDS_VALID])
        sens = {m_: run_many(pool, [(s, n_normal, float(vol), m_, False) for s in SEEDS_VALID[:3]]) for m_ in [0.75, 1.25]}

    # Utilization per level with a 95% interval over episodes (the episode is the unit).
    util = {}
    for lvl, rows in valid.items():
        u = np.array([x["util_peak"] for x in rows])
        half = stats.t.ppf(0.975, len(u) - 1) * u.std(ddof=1) / np.sqrt(len(u))
        util[lvl] = {"mean": float(u.mean()), "ci95": [float(u.mean() - half), float(u.mean() + half)],
                     "band": bands[lvl], "inside": bool(bands[lvl][0] <= u.mean() <= bands[lvl][1]),
                     "couriers": fleets[lvl], "p90_c2d_min": float(np.mean([x["p90_c2d_min"] for x in rows])),
                     "late_rate": float(np.mean([x["late_rate"] for x in rows])),
                     "pending_peak_mean": float(np.mean([x["pending_peak_mean"] for x in rows])),
                     "episode_seconds": float(np.mean([x["seconds"] for x in rows]))}
    rep["utilization"] = util
    rep["speed_sensitivity"] = {str(m_): {"util_peak": mean_util(rows),
                                          "p90_c2d_min": float(np.mean([x["p90_c2d_min"] for x in rows]))}
                                for m_, rows in sens.items()}

    # KS tests on pooled orders of the normal level.
    od = {k: np.concatenate([x["_orders"][k] for x in valid["normal"]]) for k in valid["normal"][0]["_orders"]}
    dist_sim = jittered_m(xy, od["rest"], od["cust"], rng)
    rep["ks"] = {"c2d_vs_meituan": ks(od["c2d_min"], ms["c2d_min"]),
                 "c2d_vs_meituan_single_order_waves": ks(od["c2d_min"], ms["c2d_min_single_wave"]),
                 "distance_vs_meituan": ks(dist_sim, ms["dist_m"]),
                 "distance_vs_grubhub": ks(dist_sim, gs["dist_m"]),
                 "prep_vs_meituan_valid": ks(od["prep_min"], ms["prep_min_valid"]),
                 "prep_vs_meituan_all": ks(od["prep_min"], ms["prep_min_all"]),
                 "prep_vs_grubhub": ks(od["prep_min"], gs["prep_min"]),
                 "order_to_pickup_vs_meituan": ks(od["to_pickup_min"], ms["to_fetch_min"]),
                 "order_to_pickup_vs_meituan_single_order_waves": ks(od["to_pickup_min"], ms["to_fetch_min_single_wave"])}
    q = [0.1, 0.25, 0.5, 0.75, 0.9]
    rep["quantiles"] = {
        "c2d_min": {"sim": np.quantile(od["c2d_min"], q).tolist(), "meituan": np.quantile(ms["c2d_min"], q).tolist(),
                    "meituan_single_order_waves": np.quantile(ms["c2d_min_single_wave"], q).tolist()},
        "distance_m": {"sim": np.quantile(dist_sim, q).tolist(), "meituan": np.quantile(ms["dist_m"], q).tolist(),
                       "grubhub": np.quantile(gs["dist_m"], q).tolist()},
        "prep_min": {"sim": np.quantile(od["prep_min"], q).tolist(), "meituan_valid": np.quantile(ms["prep_min_valid"], q).tolist(),
                     "meituan_all": np.quantile(ms["prep_min_all"], q).tolist(), "grubhub": np.quantile(gs["prep_min"], q).tolist()},
        "order_to_pickup_min": {"sim": np.quantile(od["to_pickup_min"], q).tolist(),
                                "meituan": np.quantile(ms["to_fetch_min"], q).tolist(),
                                "meituan_single_order_waves": np.quantile(ms["to_fetch_min_single_wave"], q).tolist()},
        "ride_min_pickup_to_door": {"sim": np.quantile(od["ride_min"], q).tolist(),
                                    "meituan_single_order": np.quantile(ms["ride_min_single"], q).tolist()}}
    rep["quantile_levels"] = q
    rep["calibration"] = cal
    rep["seconds"] = round(time.time() - t_start)
    pd.DataFrame([{"level": lvl, **{k: v for k, v in x.items() if k != "_orders"}} for lvl, rows in valid.items()
                  for x in rows]).to_csv(out / "validation_episodes.csv", index=False)
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=float))
    params_dir = ROOT / "sim/params"
    params_dir.mkdir(exist_ok=True)
    (params_dir / "calibration.json").write_text(json.dumps(cal, indent=1))
    tmp.unlink()
    figures(out, ms, gs, od, dist_sim, valid, bands)
    print(json.dumps({k: rep[k] for k in ["bands", "utilization", "ks", "speed_sensitivity"]}, indent=1, default=float))


def figures(out, ms, gs, od, dist_sim, valid, bands):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 4, figsize=(17, 4.2), constrained_layout=True)
    for a, sim, obs, gh, title, rng_ in [
            (ax[0], od["c2d_min"], ms["c2d_min_single_wave"], None, "Order to door (min), Meituan orders delivered alone", (0, 90)),
            (ax[1], dist_sim / 1000, ms["dist_m"] / 1000, gs["dist_m"] / 1000, "Restaurant to customer, straight (km)", (0, 8)),
            (ax[2], od["prep_min"], ms["prep_min_valid"], gs["prep_min"], "Preparation (min)", (0, 45))]:
        bins = np.linspace(*rng_, 61)
        a.hist(obs, bins=bins, density=True, histtype="step", lw=1.6, label="Meituan 17:00 to 21:00")
        a.hist(sim, bins=bins, density=True, histtype="step", lw=1.6, label="Simulation, normal supply")
        if gh is not None:
            a.hist(gh, bins=bins, density=True, histtype="step", lw=1.2, ls="--", label="Grubhub MDRP")
        a.set_title(title, fontsize=10)
    for i, (lvl, rows) in enumerate(valid.items()):
        u = [x["util_peak"] for x in rows]
        ax[3].scatter(np.full(len(u), i) + np.linspace(-0.15, 0.15, len(u)), u, s=12)
        ax[3].fill_between([i - 0.3, i + 0.3], *bands[lvl], alpha=0.2)
    ax[3].set_xticks(range(3), list(valid))
    ax[3].set_title("Busiest-hour utilization and target bands", fontsize=10)
    h, lab = ax[1].get_legend_handles_labels()
    fig.legend(h, lab, loc="outside lower center", ncol=3, frameon=False)
    fig.text(0.99, 0.01, "This research was supported by data provided by Meituan.", ha="right", fontsize=7)
    fig.savefig(out / "calibration.png", dpi=130)


if __name__ == "__main__":
    main()
