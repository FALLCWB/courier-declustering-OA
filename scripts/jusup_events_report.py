"""G8 item 1 (Filipe, 2026-11-04): how many couriers Jusup's adaptation 10 reaches per policy step.

Adaptation 10 (models/fidelity/jusup_mf.md): the idle mass fed to the policy counts a courier at its current cell
(`sim.pos`), while the leave probability that applies to it is that of the zone of the cell it can start from (`v.cell`,
the next cell for a courier in mid-hop). `JusupMF.events` counts, per 20-min policy step, the obedient idle couriers seen
and those whose two zones differ; the runner writes them as `events_*` on every Jusup row.

Usage: python scripts/jusup_events_report.py <full_dir> <out_dir> --n <n>
Per cell (start, supply, behavior, obedience) holding all n seeds 1001 to 1000 + n: policy steps per episode,
obedient idle couriers per step, couriers reached per step (zone mismatch), their share, and the largest count in one
step. Aggregates over seeds only. Writes jusup_events.csv and jusup_events.md.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ACK = "This research was supported by data provided by Meituan."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("full_dir", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--n", type=int, required=True)
    a = ap.parse_args()
    seeds = set(range(1001, 1001 + a.n))
    rows = [json.loads(x) for x in (a.full_dir / "episodes.jsonl").read_text().splitlines() if x.strip()]
    ep = pd.DataFrame([r for r in rows if r.get("model") == "jusup" and r.get("set") == "new" and r["seed"] in seeds])
    out, left = [], []
    for (s, lvl, b, o), g in ep.groupby(["scenario", "level", "behavior", "obedience"]):
        if set(g.seed) != seeds:
            left.append(f"{s} {lvl} {b} {o:.2f}: {g.seed.nunique()} of {len(seeds)} seeds")
            continue
        steps, cour, mis = g.events_steps.sum(), g.events_couriers.sum(), g.events_zone_mismatch.sum()
        out.append({"scenario": s, "level": lvl, "behavior": b, "obedience": o, "episodes": len(g),
                    "policy_steps_taken_per_episode": steps / len(g), "couriers_per_step": cour / steps,
                    "mismatched_per_step": mis / steps, "mismatched_share": mis / cour if cour else 0.0,
                    "max_mismatched_in_one_step": int(g.events_max_zone_mismatch_in_step.max())})
    t = pd.DataFrame(out)
    a.out.mkdir(parents=True, exist_ok=True)
    t.to_csv(a.out / "jusup_events.csv", index=False)
    L = ["# Jusup et al., adaptation 10: couriers reached per policy step", "", ACK, "",
         f"Seeds 1001 to {1000 + a.n}. A courier is reached when the zone where it is counted in the idle mass "
         "(its current cell) differs from the zone whose leave probability applies to it (the cell it can start from). "
         "A policy step runs at the first 30-s epoch with at least one obedient idle courier, 20 min or more after the "
         "previous step, so tight supply, with stretches of no idle courier, takes fewer steps. Per cell: policy steps "
         "taken, obedient idle couriers per step taken, those reached, their share, and the largest count in one step "
         "over all episodes.", "",
         "| Start | Supply | Behavior | Obedience | Episodes | Policy steps taken per episode | Idle obedient per step | Reached per step "
         "| Share | Max in one step |", "|---|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r.scenario} | {r.level} | {r.behavior} | {r.obedience:.2f} | {r.episodes} | {r.policy_steps_taken_per_episode:.1f} | "
          f"{r.couriers_per_step:.1f} | {r.mismatched_per_step:.2f} | {100 * r.mismatched_share:.2f}% | "
          f"{r.max_mismatched_in_one_step} |" for r in t.itertuples()]
    if left:
        L += ["", "Cells left out, not yet holding every seed: " + "; ".join(left) + "."]
    (a.out / "jusup_events.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
