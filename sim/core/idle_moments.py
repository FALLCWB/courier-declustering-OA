"""Idle-move moments, the drift-back targets: one definition for Meituan gaps and for simulated gaps.

A gap runs from a courier's last drop-off D to its position G when it accepts its next order; H is the centre of its
preferred area. For gaps that start outside the area (|D - H| > R), the return share is the share that end inside
(|G - H| <= R). The null keeps each move's length and turns it in a uniformly random direction (20 draws per gap);
excess = return share minus null share. Stay share: moves under 300 m, by gap length. Move quantiles over all gaps.
This is the definition of `scripts/meituan_idle_behavior.py`; `sim/behavior_fit.py` checks that both give the same
Meituan numbers. Bootstrap replicates resample couriers (the cluster) through integer weights.
"""
import numpy as np

RADII_M = (1000, 2000, 3000)
GAP_EDGES = (5, 15, 30)                  # bins [0, 5), [5, 15), [15, 30), [30, inf) minutes
BINS = ("<5", "5-15", "15-30", ">=30")
STAY_M = 300.0
NULL_DRAWS = 20
QUANTILES = (0.1, 0.25, 0.5, 0.75, 0.9)
FIT_RADIUS_M = 2000
MIN_GAPS = 50


def fit_names():
    """The moments the behavior fit matches: at the 2 km radius, return share and excess by gap length; stay share by
    gap length; move quantiles."""
    r = FIT_RADIUS_M
    return ([f"ret_{r}_{b}" for b in BINS] + [f"exc_{r}_{b}" for b in BINS] + [f"stay_{b}" for b in BINS]
            + [f"move_q{int(100 * q)}" for q in QUANTILES])


def prepare(courier, gap_min, D, G, H, rng):
    """Per-gap arrays. courier: any labels; gap_min: minutes; D, G, H: (n, 2) planar metres."""
    move = np.linalg.norm(G - D, axis=1)
    d_start, d_end = np.linalg.norm(D - H, axis=1), np.linalg.norm(G - H, axis=1)
    theta = rng.uniform(0, 2 * np.pi, (len(D), NULL_DRAWS))
    Gn = D[:, None, :] + move[:, None, None] * np.stack([np.cos(theta), np.sin(theta)], axis=-1)
    d_null = np.linalg.norm(Gn - H[:, None, :], axis=2)
    _, code = np.unique(np.asarray(courier), return_inverse=True)
    out = {"code": code, "n_couriers": int(code.max() + 1) if len(code) else 0, "move": move,
           "bin": np.digitize(np.asarray(gap_min, float), GAP_EDGES), "order": np.argsort(move, kind="stable")}
    for R in RADII_M:
        out[f"out_{R}"] = d_start > R
        out[f"ret_{R}"] = (d_end <= R).astype(float)
        out[f"null_{R}"] = (d_null <= R).mean(axis=1)
    return out


def moments(p, w=None):
    """Moment dict; w = one integer weight per courier (bootstrap), None for the point estimate."""
    gw = np.ones(len(p["move"])) if w is None else np.asarray(w, float)[p["code"]]
    m = {}
    for R in RADII_M:
        o = p[f"out_{R}"]
        for b, name in [(None, "all"), *enumerate(BINS)]:
            sel = o if b is None else o & (p["bin"] == b)
            den = gw[sel].sum()
            if sel.sum() < MIN_GAPS or den == 0:
                m[f"ret_{R}_{name}"] = m[f"exc_{R}_{name}"] = np.nan
                continue
            ret = p[f"ret_{R}"][sel]
            m[f"ret_{R}_{name}"] = float((gw[sel] * ret).sum() / den)
            m[f"exc_{R}_{name}"] = float((gw[sel] * (ret - p[f"null_{R}"][sel])).sum() / den)
            m[f"gaps_{R}_{name}"] = int(sel.sum())
    for b, name in enumerate(BINS):
        sel = p["bin"] == b
        den = gw[sel].sum()
        m[f"stay_{name}"] = float((gw[sel] * (p["move"][sel] < STAY_M)).sum() / den) if den > 0 else np.nan
    if w is None:
        qs = np.quantile(p["move"], QUANTILES)
    else:
        cw = np.cumsum(gw[p["order"]])
        qs = p["move"][p["order"]][np.minimum(np.searchsorted(cw, np.array(QUANTILES) * cw[-1]), len(cw) - 1)]
    for q, v in zip(QUANTILES, qs):
        m[f"move_q{int(100 * q)}"] = float(v)
    m["move_mean"] = float((gw * p["move"]).sum() / gw.sum())          # mean straight move per gap (G2 ruling 2)
    m["gaps"], m["couriers"] = int(len(p["move"])), p["n_couriers"]
    return m


def bootstrap(p, names, n, rng):
    """(n, len(names)) moment replicates, resampling couriers with replacement."""
    k = p["n_couriers"]
    out = np.empty((n, len(names)))
    for i in range(n):
        w = np.bincount(rng.integers(0, k, k), minlength=k)
        m = moments(p, w)
        out[i] = [m[x] for x in names]
    return out
