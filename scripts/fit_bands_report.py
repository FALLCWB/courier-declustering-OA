"""Bands of a behavior fit on a wider grid against the earlier fit (instructions 2026-11-07, package C extra: C7 for the
fitted behavior of Paper A's Table 1, and the Ashkrof variant's interval).

Usage: python scripts/fit_bands_report.py <earlier_fit_dir> <wide_fit_dir> <out_stem> --title <title>
Writes <out_stem>.csv (one row per parameter: earlier band, wide-grid band, the wide grid's explored range, whether a
band end still touches it, the point estimates and whether the point moved) and <out_stem>.md. It also counts the grid
points the two fits share and how many reproduce the earlier fit's simulated moments exactly.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ACK = "This research was supported by data provided by Meituan."
K = ["p_return", "epoch_s", "cruise_radius_m", "asc_stay"]
NAME = {"p_return": "return probability", "epoch_s": "decision delay (s)", "cruise_radius_m": "cruise radius (m)",
        "asc_stay": "stay constant (beta0)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("out")
    ap.add_argument("--title", required=True)
    ap.add_argument("--note", default="", help="a sentence on what the runs use, after the point-estimate line")
    a = ap.parse_args()
    o, n = (json.loads((d / "report.json").read_text()) for d in (a.old, a.new))
    go, gn = (pd.read_csv(d / "grid.csv") for d in (a.old, a.new))
    rows = []
    for k in K:
        vals = sorted(gn[k].round(9).unique())
        ex = n.get("explored_range", {}).get(k, [vals[0], vals[-1]])
        lo, hi = n["fit"]["ci95"][k]
        fixed = len(vals) == 1
        rec = n.get("bands_touch_grid", {}).get(k)
        tl, th = (rec if rec is not None else [None, None])
        touch = ("fixed" if fixed else "not recorded" if rec is None else
                 " and ".join(x for x, f in (("low", tl), ("high", th)) if f) or "no")
        rows.append({"parameter": k, "old_lo": o["fit"]["ci95"][k][0], "old_hi": o["fit"]["ci95"][k][1],
                     "new_lo": lo, "new_hi": hi, "new_grid_lo": ex[0], "new_grid_hi": ex[1],
                     "new_touches_low": tl, "new_touches_high": th, "touches": touch,
                     "low_end_one_value_from_edge": (not fixed) and round(lo, 9) == vals[1],
                     "high_end_one_value_from_edge": (not fixed) and round(hi, 9) == vals[-2],
                     "points_at_lowest_value": int((gn[k].round(9) == vals[0]).sum()),
                     "points_at_highest_value": int((gn[k].round(9) == vals[-1]).sum()),
                     "median_points_per_value": float(gn[k].round(9).value_counts().median()),
                     "old_point": o["fit"]["params"][k], "new_point": n["fit"]["params"][k],
                     "point_moved": o["fit"]["params"][k] != n["fit"]["params"][k]})
    t = pd.DataFrame(rows)
    t.to_csv(f"{a.out}.csv", index=False)

    mom = [c for c in go.columns if c in gn.columns and c.startswith(("ret_", "exc_", "stay_", "move_"))]
    both = go.round({k: 9 for k in K}).merge(gn.round({k: 9 for k in K}), on=K, suffixes=("_old", "_new"))
    same = sum(all(r[f"{c}_old"] == r[f"{c}_new"] for c in mom) for _, r in both.iterrows())

    fmt = lambda lo, hi: f"[{lo:g}, {hi:g}]"
    tab = pd.DataFrame({"parameter": [NAME[k] for k in K],
                        "earlier band": [fmt(r.old_lo, r.old_hi) for r in t.itertuples()],
                        "wide-grid band": [fmt(r.new_lo, r.new_hi) for r in t.itertuples()],
                        "wide grid explored": [fmt(r.new_grid_lo, r.new_grid_hi) if r.new_grid_lo is not None else "" for r in t.itertuples()],
                        "end still touches the grid": list(t.touches),
                        "point: earlier, wide": [f"{r.old_point:g}, {r.new_point:g}" for r in t.itertuples()]})
    head = "| " + " | ".join(tab.columns) + " |\n|" + "---|" * len(tab.columns)
    body = "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in tab.itertuples(index=False))
    moved = [NAME[r.parameter] for r in t.itertuples() if r.point_moved]
    touch = [NAME[r.parameter] for r in t.itertuples() if r.touches not in ("no", "fixed")]
    near = [f"{NAME[r.parameter]} ({' and '.join(x for x, f in (('low', r.low_end_one_value_from_edge), ('high', r.high_end_one_value_from_edge)) if f)})"
            for r in t.itertuples() if r.low_end_one_value_from_edge or r.high_end_one_value_from_edge]
    sparse = [f"{NAME[r.parameter]}: {x} value at {c} points against a median of {r.median_points_per_value:g} per value"
              for r in t.itertuples() if r.touches != "fixed"
              for x, c in (("lowest", r.points_at_lowest_value), ("highest", r.points_at_highest_value))
              if c < r.median_points_per_value / 4]
    rounds = n.get("band_rounds")
    L = [f"## {a.title}", "", ACK, "",
         "Bands are 95% bootstrap intervals over the Meituan moments (the earlier fit's procedure: moments, seeds, "
         "objective, bootstrap picks over every grid point run). The wide grid adds two steps beyond the lowest and the "
         "highest value the earlier fit explored for every fitted parameter, then grows on any side a band end still "
         f"touches ({'not recorded' if rounds is None else rounds} rounds; at most 8).", "", head, body, "",
         f"Band ends that still touch the wide grid: {', '.join(touch) if touch else 'none'}"
         + (" (each still touches after the last round, or was not recorded)." if touch else "."),
         f"Band ends one value from the edge of the explored values: {', '.join(near) if near else 'none'}.",
         *([f"Values added in the rounds were tried only across the other parameters' values inside their bands, so a "
            f"band end there may be too narrow: {'; '.join(sparse)}."] if sparse else []),
         "Objective values are not comparable across fits: the moment weights depend on the grid's coarse points.",
         f"Point estimate: {'moved for ' + ', '.join(moved) if moved else 'unchanged'}." + (f" {a.note}" if a.note else ""),
         f"{same} of {len(both)} grid points shared with the earlier fit reproduce its moments exactly.", "", ACK]
    Path(f"{a.out}.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
