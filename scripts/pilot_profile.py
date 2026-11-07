"""Preliminary profile of the ten models on the pilot seeds (Filipe, 2026-11-04): one page, descriptive, labelled pilot.

The pilot's mean differences are shown for information only. They are not results: the pre-registration keeps the pilot
for sigma_d, the smallest effects and the runtime, and the confirmatory analysis uses seeds 1001 on.

Usage: python scripts/pilot_profile.py <project_root> <pilot_dir>
Writes <pilot_dir>/pilot_profile.md and pilot_profile.csv (fitted behavior; arm C at 100% obedience).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.stats import time_to_undo  # noqa: E402

PILOT = Path(sys.argv[2])
NAMES = {"nearest": "Nearest courier (reference)", "foodmatch": "FoodMatch, bundling off", "forecast": "Forecast-aware",
         "backpressure": "Mirror backpressure", "xu": "Xu et al., value + KM", "li": "Li et al., mean-field AC",
         "jahanshahi": "Jahanshahi et al., DQN (descriptive)", "auad": "Auad et al., holding",
         "zhu": "Zhu et al., coverage (100% obedient)", "jusup": "Jusup et al., constrained MF (100% obedient)"}
LEVELS = ["tight", "normal", "loose"]
Q1 = [(s, lvl) for s in ("scattered", "burst") for lvl in LEVELS]
Q2S = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in LEVELS]


def cell(ep, s, lvl, m):
    g = ep[(ep.scenario == s) & (ep.level == lvl) & (ep.behavior == "fitted") & (ep.model == m)
           & ep.set.isin(["new", "frozen_rerun"])]
    g = g[g.obedience == 1.0] if m in ("zhu", "jusup") else g[g.obedience.isna()]
    return g.set_index("seed").sort_index()


def diff(ep, cells, m, col):
    """Mean over cells of the paired mean difference, model minus nearest courier."""
    out = []
    for s, lvl in cells:
        a, b = cell(ep, s, lvl, m), cell(ep, s, lvl, "nearest")
        k = a.index.intersection(b.index)
        out.append((a.loc[k, col] - b.loc[k, col]).mean())
    return float(np.mean(out))


def undo_median(ep, cells, m):
    t = []
    for s, lvl in cells:
        a, sc = cell(ep, s, lvl, m), cell(ep, "scattered", lvl, m)
        start = 120 if s == "meetup" else 0
        t += [time_to_undo(a.loc[k, "w1_rule_series"], sc.loc[k, "w1_rule_series"], start_min=start)
              for k in a.index.intersection(sc.index)]
    t = np.array(t)
    cens = t >= (120 if cells[0][0] == "meetup" else 240)
    return float(np.median(t)), float(cens.mean())


def main():
    ep = pd.read_json(PILOT / "episodes.jsonl", lines=True, precise_float=True, dtype={"obedience": float})
    rows = []
    for m in NAMES:
        r = {"model": NAMES[m]}
        if m != "nearest":
            r["Q1 W1 diff"] = diff(ep, Q1, m, "w1_rule_min")
            r["Q1 p90 diff"] = diff(ep, Q1, m, "p90_c2d_min")
            r["Q2 W1 60 min diff (starts)"] = diff(ep, Q2S, m, "w1_rule_60min_after_min")
            r["Q2 p90 diff (starts)"] = diff(ep, Q2S, m, "p90_c2d_min")
            r["Meet-up W1 60 min diff"] = diff(ep, [("meetup", "normal")], m, "w1_rule_60min_after_min")
            r["Idle km per order diff"] = diff(ep, Q1 + Q2S, m, "idle_km_per_order")
        r["Time to undo, starts (median min)"], _ = undo_median(ep, Q2S, m)
        r["Meet-up time to undo (median min)"], r["Meet-up censored"] = undo_median(ep, [("meetup", "normal")], m)
        r["Unassigned over 30 min"] = float(np.mean([cell(ep, s, lvl, m).unassigned_over_30min_share.mean()
                                                     for s, lvl in Q1 + Q2S]))
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(PILOT / "pilot_profile.csv", index=False)
    cols = ["model", "Q1 W1 diff", "Q1 p90 diff", "Q2 W1 60 min diff (starts)", "Q2 p90 diff (starts)",
            "Time to undo, starts (median min)", "Meet-up W1 60 min diff", "Meet-up time to undo (median min)",
            "Idle km per order diff", "Unassigned over 30 min"]

    def f(v, c, ref):
        if isinstance(v, str):
            return v
        if v != v:
            return "ref." if ref else "n/a"
        if c.startswith("Unassigned"):
            return f"{100 * v:.1f}%"
        if "time to undo" in c.lower():
            return f"{v:.0f}"
        return f"{v:+.2f}"
    head = ["Model", "Q1 W1", "Q1 p90", "Q2 W1 (1st h)", "Q2 p90", "Undo, starts", "Meet-up W1 (1st h)", "Undo, meet-up",
            "Idle km/order", "Unassigned >30 min"]
    L = ["# Preliminary profile of the ten models (PILOT, descriptive)", "",
         "**Pilot seeds 1 to 30. These are not results.** The pre-registration (frozen at 8e082e3) keeps the pilot for "
         "variances, smallest effects and runtime only; the confirmatory tests run on seeds 1001 on, with Holm within each "
         "family. Shown at Filipe's request (2026-11-04) so the direction of each model is visible early.", "",
         "Fitted behavior; normal, tight and loose supply. Differences are model minus nearest courier, averaged over the "
         "cells (lower is better): W1 and p90 order to door in minutes, idle km per delivered order. Q1 cells: scattered "
         "and burst starts. Q2 cells: big cluster, three clusters and mixed starts (W1 over 17:00 to 17:59), and the "
         "meet-up at 19:00 (W1 over 19:00 to 19:59). Time to undo: median minutes until W1 is within 10% of the same "
         "model's scattered start, censored at 21:00 (240 on the starts, 120 on the meet-up). Arm C at 100% obedience is "
         "an upper bound.", "",
         "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in df.to_dict("records"):
        ref = r["model"] == NAMES["nearest"]
        L.append("| " + " | ".join(f(r.get(c, float("nan")), c, ref) for c in cols) + " |")
    near = df.iloc[0]
    L += ["", f"Nearest courier, for scale: time to undo {near['Time to undo, starts (median min)']:.0f} min on the starts, "
          f"{near['Meet-up time to undo (median min)']:.0f} on the meet-up ({100 * near['Meet-up censored']:.0f}% censored). "
          "Smallest effects of interest: 10% of nearest courier's W1 in the cell, and 1.0 min of p90.", "",
          "This research was supported by data provided by Meituan."]
    (PILOT / "pilot_profile.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
