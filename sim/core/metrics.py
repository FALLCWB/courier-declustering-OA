"""Concentration of idle couriers against expected demand, and per-episode summaries.

Primary metric (fixed before the runs): W1, the earth mover's distance in minutes between the share of
idle couriers per zone (H3 resolution 8) and the share of pickups expected in the next 30 minutes per
zone, with road travel time from courier zone to demand zone as ground cost. It reads as the average
minutes an idle courier would need to ride to match the expected demand. Reported beside it: total
variation distance between the two shares, the Gini of idle couriers across all zones, and the share
of expected demand with no idle courier within `cover_s` seconds.
"""
import numpy as np
import ot
from scipy import sparse


def cover_matrix(city, speed_factor, cover_s):
    """Sparse [cells, cells]: True where T * speed_factor <= cover_s (same float32 test as a dense comparison),
    built once per city, speed factor and cover radius."""
    cache = city.__dict__.setdefault("_cover", {})
    key = (float(speed_factor), float(cover_s))
    if key not in cache:
        rows, cols = np.nonzero(city.T * speed_factor <= cover_s)
        cache[key] = sparse.csr_matrix((np.ones(len(rows), bool), (rows, cols)), shape=(city.n, city.n))
    return cache[key]


def gini(x):
    x = np.sort(np.asarray(x, float))
    n, s = len(x), x.sum()
    if n == 0 or s == 0:
        return 0.0
    return float(2 * np.sum(np.arange(1, n + 1) * x) / (n * s) - (n + 1) / n)


def zone_minutes(city, speed_factor):
    """Zone-to-zone riding minutes between representative cells, cached per city and speed factor."""
    cache = city.__dict__.setdefault("_zone_min", {})
    if speed_factor not in cache:
        cache[speed_factor] = city.T[np.ix_(city.zone_rep, city.zone_rep)].astype(np.float64) * speed_factor / 60.0
    return cache[speed_factor]


def _w1(city, pn, qn, speed_factor):
    si, sj = np.flatnonzero(pn), np.flatnonzero(qn)
    M = zone_minutes(city, speed_factor)[np.ix_(si, sj)].copy()
    M[si[:, None] == sj[None, :]] = 0.0          # no riding cost inside a zone, even with intra-cell trip times
    a, b = pn[si] / pn[si].sum(), qn[sj] / qn[sj].sum()
    cost, log = ot.emd2(a, b, M, numItermax=10_000_000, log=True)
    return float(cost), int(log.get("warning") is not None)


def w1(city, cells, expected_cell, speed_factor, with_warning=False):
    """W1 in minutes between couriers at `cells` and the expected pickups, by zone; NaN when either side is empty.
    with_warning: also return 1 when the transport solver reported a problem (0 otherwise)."""
    p = np.bincount(city.zone[cells], minlength=city.n_zones).astype(float)
    q = np.bincount(city.zone, weights=expected_cell, minlength=city.n_zones)
    if p.sum() == 0 or q.sum() == 0:
        return (np.nan, 0) if with_warning else np.nan
    cost, warn = _w1(city, p / p.sum(), q / q.sum(), speed_factor)
    return (cost, warn) if with_warning else cost


def concentration(city, idle_cells, expected_cell, speed_factor, cover_s):
    Z = city.n_zones
    p = np.bincount(city.zone[idle_cells], minlength=Z).astype(float)
    q = np.bincount(city.zone, weights=expected_cell, minlength=Z)
    # With no idle courier the Gini is undefined, not "perfectly equal" (five-agent review, S8).
    out = {"n_idle": int(len(idle_cells)), "gini_idle": gini(p) if p.sum() > 0 else np.nan, "emd_warning": 0}
    if p.sum() == 0 or q.sum() == 0:
        out.update(w1_min=np.nan, tv=np.nan, uncovered=1.0 if q.sum() > 0 else 0.0)
        return out
    pn, qn = p / p.sum(), q / q.sum()
    out["w1_min"], out["emd_warning"] = _w1(city, pn, qn, speed_factor)
    out["tv"] = float(0.5 * np.abs(pn - qn).sum())
    dc = np.flatnonzero(expected_cell > 0)
    reach = cover_matrix(city, speed_factor, cover_s)[np.unique(idle_cells)]
    near = np.zeros(city.n, bool)
    near[reach.indices] = True
    near = near[dc]
    out["uncovered"] = float(expected_cell[dc][~near].sum() / expected_cell[dc].sum())
    return out


def summarize(sim):
    """One row per episode: the primary and co-primary metrics and the secondary ones."""
    o, p = sim.orders, sim.params
    inside = o.placed < p.horizon_s
    door_raw = sim.o_door[inside]
    end = p.horizon_s + p.drain_s
    # An order not delivered by the end of the drain, never assigned or scheduled to reach the door later, counts at
    # the drain's end, a lower bound (preregistration section 7, G3 verdict C2).
    done = ~np.isnan(door_raw) & (door_raw <= end)
    door = np.where(done, door_raw, end)
    c2d = (door - o.placed[inside]) / 60.0
    snaps = sim.snapshots
    first = [s for s in snaps if s["t"] < 1800]
    return {
        "orders": int(inside.sum()),
        "delivered": int(done.sum()),
        "undelivered": int((~done).sum()),
        "w1_min": float(np.nanmean([s["w1_min"] for s in snaps])),
        "w1_first30_min": float(np.nanmean([s["w1_min"] for s in first])) if first else np.nan,
        "tv": float(np.nanmean([s["tv"] for s in snaps])),
        "gini_idle": float(np.nanmean([s["gini_idle"] for s in snaps])),
        "no_idle_snapshots": int(sum(1 for s in snaps if s["n_idle"] == 0)),
        "emd_warnings": int(sum(s.get("emd_warning", 0) + s.get("emd_warning_soon", 0) for s in snaps)),
        "uncovered": float(np.mean([s["uncovered"] for s in snaps])),
        "p90_c2d_min": float(np.percentile(c2d, 90)) if len(c2d) else np.nan,
        "mean_c2d_min": float(c2d.mean()) if len(c2d) else np.nan,
        "late_rate": float((door > o.due[inside]).mean()) if len(door) else np.nan,
        "extra_km_per_order": float((sim.km_dead.sum() + sim.km_idle.sum()) / max(done.sum(), 1)),
        "idle_km_per_order": float(sim.km_idle.sum() / max(done.sum(), 1)),
        "earnings_gini": gini(sim.trips),
    }
