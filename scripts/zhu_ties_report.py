"""G8 item (Filipe, 2026-11-04): Zhu with random partition ties against the frozen Zhu and nearest courier, descriptive,
post-freeze and outside every family. Changes no confirmatory number.

Usage: python scripts/zhu_ties_report.py <project_root> <ties_dir> <full_dir> <out_dir>
Reads <ties_dir>/episodes.jsonl (plan zhu_ties: big cluster, meet-up and scattered start, normal supply, fitted
behavior, 100% obedience, seeds 1001 to 1030) and the same cells of the full runs (frozen Zhu and nearest courier).
Writes zhu_ties.csv (per start and variant), zhu_ties_pairs.csv (random minus frozen, per start) and zhu_ties.md.
Paired differences are over seeds, with 95% percentile bootstrap intervals (10,000 resamples, seed 20261106).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.stats import time_to_undo  # noqa: E402

SEEDS = list(range(1001, 1031))
STARTS = ["big_cluster", "meetup"]
METRICS = {"w1_rule_min": "W1", "w1_rule_60min_after_min": "W1, first 60 min", "time_to_undo_min": "time to undo",
           "p90_c2d_min": "p90", "unassigned_over_30min_share": "unassigned >30 min",
           "owns_no_cell_per_step": "couriers owning no cell per step", "commands_per_step": "commands per step"}


def load(path, cond):
    ep = pd.read_json(Path(path) / "episodes.jsonl", lines=True, precise_float=True, dtype={"obedience": float})
    return ep[cond(ep)]


def cell(ep, scenario, model):
    g = ep[(ep.scenario == scenario) & (ep.model == model)].set_index("seed").sort_index()
    if list(g.index) != SEEDS:
        raise SystemExit(f"{scenario} {model}: {len(g)} of 30 seeds")
    return g.copy()


def boot(d, reps=10000, seed=20261106):
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), (reps, len(d)))].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    ties_dir, full_dir, out = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    ties = load(ties_dir, lambda e: e.set == "zhu_random_ties")
    full = load(full_dir, lambda e: e.set.isin(["new", "frozen_rerun"]) & (e.level == "normal") & (e.behavior == "fitted")
                & (e.seed <= 1030) & (e.obedience.isna() | (e.obedience == 1.0)))
    variants = {"Zhu, random ties (sensitivity)": (ties, "zhu"), "Zhu, lower-index ties (frozen)": (full, "zhu"),
                "Nearest courier": (full, "nearest")}
    rows, per = [], {}
    for name, (ep, m) in variants.items():
        sc = cell(ep, "scattered", m)
        for s in STARTS:
            g = cell(ep, s, m)
            g["time_to_undo_min"] = [time_to_undo(g.loc[k, "w1_rule_series"], sc.loc[k, "w1_rule_series"],
                                                  start_min=120 if s == "meetup" else 0) for k in SEEDS]
            if m == "zhu":
                g["owns_no_cell_per_step"] = g.events_owns_no_cell / g.events_steps
                g["commands_per_step"] = g.events_commands / g.events_steps
            per[(name, s)] = g
            cens = (g.time_to_undo_min >= (120 if s == "meetup" else 240)).mean()
            rows.append({"variant": name, "start": s, **{v: float(g[k].mean()) for k, v in METRICS.items() if k in g},
                         "time to undo, median": float(g.time_to_undo_min.median()), "censored share": float(cens)})
    tab = pd.DataFrame(rows)
    tab.to_csv(out / "zhu_ties.csv", index=False)
    pairs = []
    for s in STARTS:
        a, b = per[("Zhu, random ties (sensitivity)", s)], per[("Zhu, lower-index ties (frozen)", s)]
        for k, v in METRICS.items():
            if k in a and k in b:
                d = (a[k] - b[k]).to_numpy(float)
                lo, hi = boot(d)
                pairs.append({"start": s, "metric": v, "random_minus_frozen": float(d.mean()), "lo": lo, "hi": hi})
    pr = pd.DataFrame(pairs)
    pr.to_csv(out / "zhu_ties_pairs.csv", index=False)
    L = ["# Zhu et al. with random partition ties (post-freeze sensitivity, descriptive)", "",
         "Outside every family; changes no confirmatory number (Filipe, 2026-11-04). Normal supply, fitted behavior, "
         "100% obedience, seeds 1001 to 1030. The frozen rule sends a cell tied between closest couriers to the lower "
         "courier index, so couriers in one cell leave one per 30-s step; the sensitivity draws the winner of each tied "
         "cell at random from the episode's own stream.", "",
         "| Variant | Start | W1 | W1, first 60 min | Time to undo, median (censored) | p90 | Unassigned >30 min | Own no cell per step |",
         "|---|---|---|---|---|---|---|---|"]
    for r in tab.to_dict("records"):
        L.append(f"| {r['variant']} | {r['start']} | {r['W1']:.2f} | {r['W1, first 60 min']:.2f} | "
                 f"{r['time to undo, median']:.0f} ({100 * r['censored share']:.0f}%) | {r['p90']:.2f} | "
                 f"{100 * r['unassigned >30 min']:.1f}% | "
                 f"{r.get('couriers owning no cell per step', float('nan')):.0f} |".replace("| nan |", "| none |"))
    L += ["", "Random minus frozen, paired by seed (95% bootstrap interval):", "", "| Start | Metric | Difference | 95% CI |",
          "|---|---|---|---|"]
    for r in pr.to_dict("records"):
        L.append(f"| {r['start']} | {r['metric']} | {r['random_minus_frozen']:+.3f} | {r['lo']:+.3f} to {r['hi']:+.3f} |")
    L += ["", "This research was supported by data provided by Meituan."]
    (out / "zhu_ties.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
