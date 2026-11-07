"""S7: sample size and runtime from the pilot, by the rule in preregistration.md section 6.

Usage: python sim/power.py <pilot_out_dir>
Reads episodes.jsonl and run_pilot.json; writes power.json, power.md and power_contrasts.csv in the same folder.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.stats import P90_SESOI_MIN, W1_SESOI_SHARE, required_n, sample_size  # noqa: E402

METRICS = {"w1_rule_min": "W1", "p90_c2d_min": "p90 order to door"}
MODELS = ["foodmatch", "forecast", "backpressure"]
F1_M = 90
EPISODES_PER_SEED = {"F1+F2": 300, "F3": 20, "F4": 8}
LIMIT_H = 24.0


def contrasts(ep, family):
    rows = []
    sub = ep[ep.family == family]
    for (sc, lvl, beh), cell in sub.groupby(["scenario", "level", "behavior"]):
        base = cell[cell.model == "nearest"].set_index("seed")
        for m in MODELS:
            mod = cell[cell.model == m].set_index("seed")
            seeds = base.index.intersection(mod.index)
            for col, name in METRICS.items():
                d = mod.loc[seeds, col] - base.loc[seeds, col]
                delta = W1_SESOI_SHARE * base.loc[seeds, col].mean() if col == "w1_rule_min" else P90_SESOI_MIN
                rows.append({"family": family, "scenario": sc, "level": lvl, "behavior": beh, "model": m, "metric": name,
                             "seeds": len(seeds), "nearest_mean": float(base.loc[seeds, col].mean()),
                             "sd_diff": float(d.std(ddof=1)), "delta": float(delta),
                             "n_required": required_n(float(d.std(ddof=1)), float(delta), F1_M)})
    return pd.DataFrame(rows)


def main():
    out = Path(sys.argv[1])
    ep = pd.read_json(out / "episodes.jsonl", lines=True, precise_float=True)
    run = json.loads((out / "run_pilot.json").read_text())
    c = pd.concat([contrasts(ep, "F1"), contrasts(ep, "F2")], ignore_index=True)
    c.to_csv(out / "power_contrasts.csv", index=False)
    f1 = c[c.family == "F1"]
    if len(f1) != F1_M:
        raise SystemExit(f"the pilot gives {len(f1)} F1 contrasts, the pre-registration fixes {F1_M}")
    near = ep[ep.model == "nearest"].groupby(["family", "scenario", "level", "behavior"]).w1_rule_min.mean()
    near.rename("nearest_w1_mean").reset_index().to_csv(out / "pilot_nearest_w1.csv", index=False)
    n = sample_size(f1.n_required.tolist())
    wall = run["wall_seconds"] / run["episodes"]
    hours = {k: v * n * wall / 3600 for k, v in EPISODES_PER_SEED.items()}
    total = sum(hours.values())
    top = f1.sort_values("n_required", ascending=False).head(10)
    res = {"pilot_episodes": int(len(ep)), "pilot_wall_hours": run["wall_seconds"] / 3600,
           "wall_seconds_per_episode": wall, "cpu_seconds_per_episode_mean": float(ep.seconds.mean()),
           "n": n, "n_required_max_f1": int(f1.n_required.max()), "n_required_median_f1": float(f1.n_required.median()),
           "n_required_max_f2_for_information": int(c[c.family == "F2"].n_required.max()),
           "runtime_hours": hours, "runtime_hours_total": total, "limit_hours": LIMIT_H, "within_limit": bool(total <= LIMIT_H),
           "undelivered_total": int(ep.undelivered.sum())}
    (out / "power.json").write_text(json.dumps(res, indent=1))
    L = [f"# Sample size and runtime from the pilot (S7), {out.name}", "",
         "This research was supported by data provided by Meituan.", "",
         f"Pilot: {res['pilot_episodes']:,} episodes (F1 and F2 cells, seeds 1 to 30) in {res['pilot_wall_hours']:.2f} h on 24 "
         f"workers: {wall:.2f} s wall per episode, {res['cpu_seconds_per_episode_mean']:.1f} s per episode on one core. "
         f"Undelivered orders at the end of the drain: {res['undelivered_total']}.", "",
         "Rule (preregistration section 6, normal approximation as fixed there; the t quantile with 29 degrees of "
         "freedom would ask somewhat more seeds per contrast): n_c = ceil(((z(1 - 0.05/90/2) + z(0.80)) sd_d / delta)^2); delta = 10% of "
         "nearest-courier's mean W1 in the cell, or 1.0 min of p90; n = the largest n_c over the 90 F1 contrasts, at least "
         "30, rounded up to a multiple of 10.", "",
         f"**n = {n} seeds per cell** (largest F1 n_c {res['n_required_max_f1']}, median {res['n_required_median_f1']:.0f}; "
         f"largest F2 n_c, for information only, {res['n_required_max_f2_for_information']}).", "",
         "| Family | Episodes per seed | Hours at n |", "|---|---|---|"]
    for k, v in hours.items():
        L.append(f"| {k} | {EPISODES_PER_SEED[k]} | {v:.1f} |")
    L += [f"| Total | {sum(EPISODES_PER_SEED.values())} | {total:.1f} |", "",
          f"Within the 24-hour limit: {'yes' if res['within_limit'] else 'no, the choice goes to Filipe (fewer sweep values or fewer episodes in F2 to F4)'}.",
          "", "F1 contrasts that need the most seeds:", "",
          "| Start | Level | Model | Metric | Nearest mean | SD of differences | delta | n_c |",
          "|---|---|---|---|---|---|---|---|"]
    for r in top.itertuples():
        L.append(f"| {r.scenario} | {r.level} | {r.model} | {r.metric} | {r.nearest_mean:.2f} | "
                 f"{r.sd_diff:.2f} | {r.delta:.2f} | {r.n_required} |")
    L += ["", "The pilot sets the variances only; its mean differences are not computed here, are not results and the "
          "pilot is not reused (preregistration 6).",
          "All contrasts: `power_contrasts.csv`."]
    (out / "power.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
