"""Idle-move moments from Meituan: do couriers drift back to their preferred area between waves?

Usage: python meituan_idle_behavior.py <project_root> <out_dir>

Each idle gap runs from the last drop-off of a wave (D) to the courier's position when it accepts the
first order of the next wave (G). The preferred area of a courier on day d is the H3 resolution-8 zone
where it accepted most orders on the OTHER days (leave one day out), so the outcome does not define
its own reference. For gaps that start outside the preferred area (distance from D to its centre above
R), the return share is the share that end inside. The null keeps each gap's distance moved and turns
it in a uniformly random direction (20 draws per gap); excess return = observed minus null.
Intervals: 95% percentile bootstrap over couriers (1,000 resamples), the courier being the cluster.
These moments are the targets the simulator's behavior parameters are fitted to in step 6.
"""
import json
import sys
from pathlib import Path

import h3
import numpy as np
import pandas as pd

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
DER = ROOT / "data/derived"
RADII_M = [1000, 2000, 3000]
GAP_BINS = [0, 5, 15, 30, 1e9]
rng = np.random.default_rng(20261101)

wb = pd.read_parquet(DER / "waybills.parquet", columns=["dt", "courier_id", "grab_lat", "grab_lng", "is_courier_grabbed"])
wb = wb[(wb.is_courier_grabbed == 1) & wb.grab_lat.notna()]
wb["z8"] = [h3.latlng_to_cell(a, b, 8) for a, b in zip(wb.grab_lat, wb.grab_lng)]
counts = wb.groupby(["courier_id", "dt", "z8"]).size().rename("n").reset_index()
days = counts.groupby("courier_id").dt.nunique()

idle = pd.read_parquet(DER / "idle_moves.parquet")
idle = idle[idle.courier_id.isin(days[days >= 2].index)].copy()
home = {}
for cid, g in counts[counts.courier_id.isin(idle.courier_id.unique())].groupby("courier_id"):
    for d in g.dt.unique():
        other = g[g.dt != d].groupby("z8").n.sum()
        home[(cid, d)] = h3.cell_to_latlng(other.idxmax())
hl = np.array([home[(c, d)] for c, d in zip(idle.courier_id, idle.dt)])
idle["home_lat"], idle["home_lng"] = hl[:, 0], hl[:, 1]

lat0 = np.radians(idle.lat0.mean())


def xy(lat, lng):
    return np.stack([np.radians(lng) * np.cos(lat0) * 6371000.0, np.radians(lat) * 6371000.0], axis=-1)


D, G, H = xy(idle.lat0, idle.lng0), xy(idle.lat1, idle.lng1), xy(idle.home_lat, idle.home_lng)
move = np.linalg.norm(G - D, axis=1)
d_start, d_end = np.linalg.norm(D - H, axis=1), np.linalg.norm(G - H, axis=1)
theta = rng.uniform(0, 2 * np.pi, (len(idle), 20))
Gnull = D[:, None, :] + move[:, None, None] * np.stack([np.cos(theta), np.sin(theta)], axis=-1)
d_null = np.linalg.norm(Gnull - H[:, None, :], axis=2)
idle["move_m"], idle["d_start"], idle["d_end"] = move, d_start, d_end
idle["gap_bin"] = pd.cut(idle.gap_min, GAP_BINS, right=False, labels=["<5", "5-15", "15-30", ">=30"])


def boot_ratio(df, num, den, n=1000):
    """Ratio of sums with a 95% percentile interval, resampling couriers (cluster bootstrap)."""
    g = df.groupby("courier_id")[[num, den]].sum().to_numpy()
    k = len(g)
    w = np.stack([np.bincount(rng.integers(0, k, k), minlength=k) for _ in range(n)])
    vals = (w @ g[:, 0]) / (w @ g[:, 1])
    return float(g[:, 0].sum() / g[:, 1].sum()), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


rows = []
for R in RADII_M:
    idle[f"null_in_{R}"] = (d_null <= R).mean(axis=1)
    out = idle[idle.d_start > R]
    for gb in [None, "<5", "5-15", "15-30", ">=30"]:
        sub = out if gb is None else out[out.gap_bin == gb]
        if len(sub) < 50:
            continue
        sub = sub.assign(ret=(sub.d_end <= R).astype(float), one=1.0)
        sub = sub.assign(exc=sub.ret - sub[f"null_in_{R}"])
        obs = boot_ratio(sub, "ret", "one")
        exc = boot_ratio(sub, "exc", "one")
        rows.append({"radius_m": R, "gap_min": gb or "all", "gaps": len(sub), "couriers": sub.courier_id.nunique(),
                     "return_share": obs[0], "return_lo": obs[1], "return_hi": obs[2],
                     "excess_over_null": exc[0], "excess_lo": exc[1], "excess_hi": exc[2]})
ret = pd.DataFrame(rows)
ret.to_csv(OUT / "return_moments.csv", index=False)

stay = {gb: float((idle[idle.gap_bin == gb].move_m < 300).mean()) for gb in ["<5", "5-15", "15-30", ">=30"]}
inside = idle[idle.d_start <= 2000]
summary = {
    "gaps_used": int(len(idle)), "couriers": int(idle.courier_id.nunique()),
    "share_starting_outside_2km": float((idle.d_start > 2000).mean()),
    "stay_share_under_300m_by_gap": stay,
    "share_leaving_2km_area_when_starting_inside": float((inside.d_end > 2000).mean()),
    "move_m_quantiles": {str(q): float(np.quantile(move, q)) for q in [0.1, 0.25, 0.5, 0.75, 0.9]},
}
(OUT / "idle_summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
print(ret.round(3).to_string(index=False))
