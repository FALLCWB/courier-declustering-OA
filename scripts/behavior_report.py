"""Render the S3 behavior report (report.md) from the outputs of sim/behavior_fit.py.

Usage: python scripts/behavior_report.py <behavior_out_dir>
"""
import json
import sys
from pathlib import Path

import pandas as pd

out = Path(sys.argv[1])
r = json.loads((out / "report.json").read_text())
tab = pd.read_csv(out / "moments_table.csv")
fit, val = r["fit"], r["validation"]
ep = val["episodes"]
L = []
say = L.append


def f(x, d=3):
    return f"{x:,.{d}f}"


def ci(v, d=3):
    return f"{f(v[0], d)} ({f(v[1], d)} to {f(v[2], d)})"


say(f"# Behavior fit report (S3), {out.name}, structure \"{r.get('variant', 'free')}\"")
say("")
say("This research was supported by data provided by Meituan. Meituan rows never leave `data/`; this report holds "
    "fitted parameters and aggregates only.")
say("")
say("## Fitted parameters (grid-limited bootstrap bands, conditional on the structure: the grid points picked by "
    "refitting on 100 bootstrap replicates of the targets and of each grid point; not coverage intervals)")
say("")
say("| Parameter | Fitted | 95% interval | Grid searched |")
say("|---|---|---|---|")
local = {"p_return": "then +/-0.075", "epoch_s": "then x0.7 and x1.4", "cruise_radius_m": "then x0.7 and x1.4",
         "asc_stay": "then +/-0.5"}
grids = {k: ", ".join(f"{x:g}" for x in v) + ", " + local[k] for k, v in r.get("grid", {
    "p_return": [0, 0.15, 0.3, 0.5, 0.75, 1], "epoch_s": [120, 240, 480, 960], "cruise_radius_m": [500, 1000, 2000, 3000],
    "asc_stay": [-1, 0, 1, 2, 3]}).items()}
names = {"p_return": "Return probability per decision outside the 2 km area", "epoch_s": "Decision interval while idle (s)",
         "cruise_radius_m": "Cruise radius (m)", "asc_stay": "Stay constant of the logit"}
for k in ["p_return", "epoch_s", "cruise_radius_m", "asc_stay"]:
    say(f"| {names[k]} | {fit['params'][k]:g} | {fit['ci95'][k][0]:g} to {fit['ci95'][k][1]:g} | {grids[k]} |")
say("")
say(f"Distance at the fit {f(fit['objective'], 1)} over 17 moments; {fit['grid_points']} grid points; "
    f"{fit['near_best_within_chi2_4']} grid points within 9.49 (chi-square, 4 degrees of freedom, 95%) of the best; "
    f"the bootstrap refits picked {fit['bootstrap_picks_distinct']} distinct points.")
say("")
say("## Simulated against observed moments")
say("")
say("Meituan targets: idle gaps between waves whose last drop-off falls between 17:00 and 20:59 local time. The "
    f"shared definition reproduces the handed-over all-day moments to {r['reproduction_max_abs_diff']:.1e}. "
    "Simulation: 10 validation episodes (seeds 311 to 320), nearest courier, normal supply, scattered start, fitted "
    "behavior. Moments outside the fit (radii 1 and 3 km, all gap lengths pooled) are out-of-sample checks.")
say("")
say("| Moment | In fit | Meituan 17:00 to 21:00 | Meituan all day | Simulated |")
say("|---|---|---|---|---|")
for row in tab.itertuples():
    d = 0 if row.moment.startswith("move") else 3
    say(f"| {row.moment} | {'yes' if row.in_fit else 'no'} | {f(row.meituan_peak, d)} | {f(row.meituan_all_day, d)} | "
        f"{f(row.simulated, d)} |")
say("")
say("## Checks")
say("")
pa = r["check_preferred_area_vs_hotspot"]
say(f"Preferred area against the nearest hotspot outside it (Meituan, all day, gaps starting more than 2 km from both; "
    f"{pa['gaps']:,} gaps, {pa['couriers']:,} couriers; 95% courier-bootstrap intervals): excess over random direction "
    f"toward the preferred area {ci(pa['home'])}, toward the hotspot {ci(pa['hot'])}, difference {ci(pa['home_minus_hot'])}. "
    f"Mean start distance {f(pa['dist_home'][0] / 1000, 2)} km to the preferred area and {f(pa['dist_hot'][0] / 1000, 2)} km "
    f"to the hotspot.")
pm = out / "pull_check_matched.json"
if pm.exists():
    m = json.loads(pm.read_text())
    say("")
    say(f"Same check with the two targets at a similar distance from the drop-off (within {m['match_m']:.0f} m; "
        f"`pull_check_matched.json`; {m['gaps']:,} gaps, {m['couriers']:,} couriers): excess toward the preferred area "
        f"{ci(m['home'])}, toward the hotspot {ci(m['hot'])}, difference {ci(m['home_minus_hot'])}; mean distance "
        f"{f(m['dist_home'][0] / 1000, 2)} and {f(m['dist_hot'][0] / 1000, 2)} km.")
say("")
dc = r["check_district"]
say("Returns within the courier's business district against across districts (gaps starting more than 2 km from the "
    "preferred area; district = `da_id` of the last drop-off against the courier's most frequent `da_id` on other days):")
say("")
say("| Start | Gaps | Couriers | Return share | Excess over random direction |")
say("|---|---|---|---|---|")
for k, lab in [("same_district", "inside the home district"), ("other_district", "in another district")]:
    x = dc[k]
    say(f"| {lab} | {x['gaps']:,} | {x['couriers']:,} | {ci(x['ret'])} | {ci(x['exc'])} |")
say("")
say(f"Idle kilometres per order (simulation, 10 episodes): {f(ep['idle_km_per_order'], 2)} km idle; "
    f"{f(ep['extra_km_per_order'], 2)} km without an order (idle plus the ride to the restaurant). Allen et al. 2021 "
    f"(London, Table 1): about {val['allen_km_without_order_per_job']} km per job without an order. Busiest-hour "
    f"utilization {f(ep['util_peak'])}; p90 order to door {f(ep['p90_c2d_min'], 1)} min; mean episode "
    f"{f(ep['seconds'], 1)} s.")
say("")
mpg = out / "move_per_gap.json"
if mpg.exists():
    g = json.loads(mpg.read_text())
    say(f"Mean straight move per idle gap (same definition; `scripts/move_per_gap.py`, `move_per_gap.json`): simulated "
        f"{g['simulated'] / 1000:.2f} km ({g['simulated_ci95'][0] / 1000:.2f} to {g['simulated_ci95'][1] / 1000:.2f}; "
        f"{g['simulated_gaps']:,} gaps, seeds 311 to 320), Meituan 17:00 to 21:00 {g['meituan_peak'] / 1000:.2f} km "
        f"({g['meituan_peak_ci95'][0] / 1000:.2f} to {g['meituan_peak_ci95'][1] / 1000:.2f}), all day "
        f"{g['meituan_all_day'] / 1000:.2f} km. The simulator carries one order per gap, Meituan 3.8, so km per order "
        f"differ while the move per gap matches; 3.34 km without an order per order is a stated limit (G2 ruling 2).")
    say("")
say("Figures: `behavior_fit.png`. Tables: `moments_table.csv`, `grid.csv`, `validation_episodes.csv`.")
(out / "report.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
