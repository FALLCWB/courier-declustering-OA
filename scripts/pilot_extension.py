"""X7: checks, sample size and runtime from the extension pilot, by the rules of preregistration-extension.md (frozen at
8e082e3), sections 6 and 8.

Usage: python scripts/pilot_extension.py <project_root> <pilot_dir> [full_workers] [--sweep-pending]
  --sweep-pending   the pilot's nearest-courier rows in the 60 sweep start cells are still running (they only set the
                    smallest effects of E3 and E4): n and the runtime are computed without them, and the run is
                    repeated without the flag once they are in, to write the full pilot_nearest_means.csv
Reads <pilot_dir>/episodes.jsonl, run_pilot.json and cpu_vmstat.log, and the S7 pilot rows; writes power_extension.json,
power_extension.md, contrasts.csv, identity.csv, frozen_check.csv and pilot_nearest_means.csv (nearest courier's mean W1
and W1 over 60 min per cell, the base of every smallest effect in X8) in <pilot_dir>.

- Identity check (section 8): Zhu and Jusup at 0% obedience equal nearest courier in every metric and in the per-minute
  W1 series of every pilot episode (16 start-supply combinations, fitted behavior).
- Frozen reruns against S7 (DECISIONS.md, X7 and 2026-11-05): a record, not a bit-for-bit criterion. S7 ran at a3e38b8,
  before the S8 review fixes (6cd370b: per-gap behavior draws), so every rerun row differs from it. The frozen four's
  identity is checked against S8: the regression harness and every frozen rerun of the full runs (sim/analysis_extension.py).
- Sample size (section 6): sigma_d of each E1 and E2 contrast over seeds 1 to 30; delta = 10% of nearest courier's mean
  of the same metric in the same cell for W1 and W1 over 60 min, 1.0 min for p90; n_c with alpha* = 0.05/60 in E1 and
  0.05/133 in E2 and 80% power; n = the largest n_c, at least 30, rounded up to a multiple of 10.
- Runtime: mean seconds per episode by model and start from the pilot, times the full runs' cells at n seeds, divided by
  the concurrency the pilot achieved; the limit is 24 h (section 6).
- Busy CPUs per minute from vmstat: (user + system) share x 30 vCPUs.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.run_extension import jobs, phase  # noqa: E402
from sim.stats import P90_SESOI_MIN, W1_SESOI_SHARE, required_n, sample_size  # noqa: E402

PILOT = Path(sys.argv[2])
S7 = ROOT / "avaliacao/20261102-1459-pilot/episodes.jsonl"
FROZEN_METRICS = ["w1_rule_min", "w1_rule_first30_min", "w1_min", "w1_idle_weighted_min", "p90_c2d_min", "mean_c2d_min",
                  "late_rate", "tv", "gini_idle", "uncovered", "extra_km_per_order", "idle_km_per_order", "earnings_gini",
                  "food_wait_mean_min", "food_wait_p90_min", "unassigned_over_30min_share", "delivered", "undelivered",
                  "orders"]
IDENTITY_METRICS = FROZEN_METRICS + ["w1_rule_60min_after_min", "w1_rule_nan_snapshots"]
NEW5 = ["xu", "li", "auad", "zhu", "jusup"]
FROZEN3 = ["foodmatch", "forecast", "backpressure"]
Q1 = [("scattered", lvl) for lvl in ("tight", "normal", "loose")] + [("burst", lvl) for lvl in ("tight", "normal", "loose")]
Q2 = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in ("tight", "normal", "loose")] + [("meetup", "normal")]
M_E1, M_E2 = 60, 133
VCPU, CPU_CAP, LIMIT_H = 30, 24, 24.0


def same(a, b):
    return a == b or (a != a and b != b)


def second_hour(series, scenario):
    """W1 over the next 60 min: 18:00 to 18:59 for the starts, 20:00 to 20:59 for the meet-ups (G7 verdict E2(b))."""
    s = 120 if scenario.startswith("meetup") else 0
    return float(np.nanmean(np.asarray(series, float)[s + 60:s + 120]))


def busy_cpus(path):
    """Busy CPUs per minute from `vmstat -n 60` output, which may hold several blocks (one per resume): each block is a
    'procs' line, the column names, a since-boot average (dropped), then one line per minute."""
    hdr, rows, skip = None, [], False
    for ln in path.read_text().splitlines():
        f = ln.split()
        if not f:
            continue
        if f[0] == "procs":
            skip = True
        elif f[:2] == ["r", "b"]:
            hdr = f
        elif skip:
            skip = False
        elif hdr is not None and len(f) == len(hdr) and all(x.isdigit() for x in f):   # skip a line cut mid-write
            rows.append(dict(zip(hdr, map(int, f))))
    vm = pd.DataFrame(rows)
    return (vm["us"] + vm["sy"]) / 100 * VCPU


def cell_rows(ep, scenario, level, model):
    """Fitted-behavior rows of one model in one cell, indexed by seed; arm C at 100% obedience."""
    sub = ep[(ep.scenario == scenario) & (ep.level == level) & (ep.behavior == "fitted") & (ep.model == model)]
    if model in ("zhu", "jusup"):
        sub = sub[sub.obedience == 1.0]
    else:
        sub = sub[sub.obedience.isna()]
    sub = sub[sub.set.isin(["new", "frozen_rerun"])]
    if sub.seed.duplicated().any():
        raise SystemExit(f"duplicate seeds in {scenario} {level} {model}")
    return sub.set_index("seed")


def contrast(ep, family, m_family, scenario, level, model, col):
    base, mod = cell_rows(ep, scenario, level, "nearest"), cell_rows(ep, scenario, level, model)
    seeds = base.index.intersection(mod.index)
    if len(seeds) != 30:
        raise SystemExit(f"{family} {scenario} {level} {model} {col}: {len(seeds)} paired seeds, the pilot has 30")
    d = mod.loc[seeds, col].astype(float) - base.loc[seeds, col].astype(float)
    delta = P90_SESOI_MIN if col == "p90_c2d_min" else W1_SESOI_SHARE * float(base.loc[seeds, col].mean())
    sd = float(d.std(ddof=1))
    return {"family": family, "scenario": scenario, "level": level, "model": model, "metric": col, "seeds": len(seeds),
            "nearest_mean": float(base.loc[seeds, col].mean()), "sd_diff": sd, "delta": delta,
            "n_required": required_n(sd, delta, m_family)}


def main():
    args = [a for a in sys.argv[3:] if not a.startswith("--")]
    pending = "--sweep-pending" in sys.argv
    full_workers = int(args[0]) if args else None
    ep = pd.read_json(PILOT / "episodes.jsonl", lines=True, precise_float=True, dtype={"obedience": float})
    run = json.loads((PILOT / "run_pilot.json").read_text())
    expected = len(jobs("pilot", {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"],
                                  "levels": ["tight", "normal", "loose"]}))
    sweep_near = 60 * 30                                 # nearest courier in the 60 sweep start cells
    if len(ep) != expected - (sweep_near if pending else 0) and not (pending and len(ep) >= expected - sweep_near):
        raise SystemExit(f"the pilot holds {len(ep)} episodes, the plan has {expected}: finish it first")
    checks = {"episodes": int(len(ep)), "episodes_expected": expected, "blas_threads": sorted(ep.blas_threads.unique().tolist()),
              "undelivered_total": int(ep.undelivered.sum()),
              "episodes_with_nan_w1_snapshots": {k: int(v) for k, v in
                                                 ep[ep.w1_rule_nan_snapshots > 0].groupby("scenario").size().items()}}

    # identity: arm C at 0% against nearest courier, same cell and seed
    allnear = ep[(ep.model == "nearest") & ep.set.isin(["new", "frozen_rerun"])]
    allnear = allnear.assign(w1_second_hour=[second_hour(r.w1_rule_series, r.scenario) for r in allnear.itertuples()])
    means = allnear.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min", "w1_second_hour"]].agg(["mean", "count"])
    means.columns = [f"{a}_{b}" for a, b in means.columns]
    means = means[(means.filter(like="_count") == 30).all(axis=1)] if pending else means
    if not (means.filter(like="_count") == 30).all().all() or len(means) < (20 if pending else 80):
        raise SystemExit("nearest courier must have 30 pilot seeds in each of the 80 cells (16 combinations x 5 settings)")
    means.reset_index().to_csv(PILOT / "pilot_nearest_means.csv", index=False)     # smallest effects for X8 (section 6)
    near = allnear[allnear.behavior == "fitted"].set_index(["scenario", "level", "seed"])
    idr = []
    for r in ep[ep.set == "identity"].itertuples(index=False):
        n = near.loc[(r.scenario, r.level, r.seed)]
        r = r._asdict()
        bad = [k for k in IDENTITY_METRICS if not same(r[k], n[k])]
        if not np.array_equal(np.array(r["w1_rule_series"], float), np.array(n["w1_rule_series"], float), equal_nan=True):
            bad.append("w1_rule_series")
        idr.append({"model": r["model"], "scenario": r["scenario"], "level": r["level"], "seed": r["seed"],
                    "differs": ",".join(bad)})
    idf = pd.DataFrame(idr)
    idf.to_csv(PILOT / "identity.csv", index=False)
    checks["identity_episodes"] = int(len(idf))
    if len(idf) != 2 * 16 * 30:
        raise SystemExit(f"{len(idf)} identity episodes, the plan has 960")
    checks["identity_failures"] = int((idf.differs != "").sum())

    # frozen reruns against S7, bit for bit
    s7 = pd.read_json(S7, lines=True, precise_float=True).set_index(["scenario", "level", "behavior", "model", "seed"])
    fr = []
    for r in ep[ep.set == "frozen_rerun"].itertuples(index=False):
        old = s7.loc[(r.scenario, r.level, r.behavior, r.model, r.seed)]
        r = r._asdict()
        fr.append({"model": r["model"], "scenario": r["scenario"], "level": r["level"], "behavior": r["behavior"],
                   "seed": r["seed"], "differs": ",".join(k for k in FROZEN_METRICS if not same(r[k], old[k]))})
    frf = pd.DataFrame(fr)
    frf.to_csv(PILOT / "frozen_check.csv", index=False)
    checks["frozen_rerun_episodes"] = int(len(frf))
    if len(frf) < (60 if pending else 120) * 30:
        raise SystemExit(f"{len(frf)} frozen reruns, the plan has 3,600")
    checks["frozen_rerun_differ_from_s7"] = int((frf.differs != "").sum())   # expected: S7 predates 6cd370b
    checks["frozen_rerun_reference"] = "S7 ran at a3e38b8, before 6cd370b; the bit-for-bit reference is S8"

    # Jahanshahi et al. (descriptive row): episodes equal to nearest courier in every frozen metric
    jah = ep[(ep.model == "jahanshahi") & (ep.behavior == "fitted") & (ep.set == "new")]
    eq = [all(same(r[k], near.loc[(r["scenario"], r["level"], r["seed"])][k]) for k in FROZEN_METRICS)
          for r in jah.to_dict("records")]
    checks["jahanshahi_fitted_episodes"] = len(eq)
    checks["jahanshahi_equal_to_nearest"] = int(sum(eq))

    # sample size
    rows = [contrast(ep, "E1", M_E1, s, lvl, m, col) for m in NEW5 for col in ("w1_rule_min", "p90_c2d_min") for s, lvl in Q1]
    rows += [contrast(ep, "E2", M_E2, s, lvl, m, "w1_rule_60min_after_min") for m in NEW5 + FROZEN3 for s, lvl in Q2]
    rows += [contrast(ep, "E2", M_E2, s, lvl, m, "p90_c2d_min") for m in NEW5 for s, lvl in Q2]
    rows += [contrast(ep, "E2", M_E2, "meetup", "normal", m, "p90_c2d_min") for m in FROZEN3]
    c = pd.DataFrame(rows)
    c.to_csv(PILOT / "contrasts.csv", index=False)
    sizes = c.groupby("family").size().to_dict()
    if sizes != {"E1": M_E1, "E2": M_E2}:
        raise SystemExit(f"contrast counts {sizes}, the pre-registration fixes E1 60 and E2 133")
    n = sample_size(c.n_required.tolist())

    # runtime of the full runs at n, timed on the largest completed segment only: the first pass (old Zhu code, about
    # twice as slow) was stopped before it wrote a segment record, and its rows come first in the file
    segs = run["segments"]
    start = len(ep) - sum(sg["episodes"] for sg in segs)
    spans = []
    for sg in segs:
        spans.append((start, start + sg["episodes"], sg))
        start += sg["episodes"]
    lo, hi, main_seg = max(spans, key=lambda x: x[2]["episodes"])
    timed = ep.iloc[lo:hi]
    sec = timed.groupby(["model", "scenario"]).seconds.mean()
    sec_model = timed.groupby("model").seconds.mean()
    full = pd.DataFrame(jobs(f"full:{n}", {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"],
                                           "levels": ["tight", "normal", "loose"]}))     # the exploratory meet-up included
    full["phase"] = [phase(j) for j in full.to_dict("records")]
    explore = full[full.set == "explore"]

    def cost(df):                                        # the median meet-up costs as the primary meet-up
        return float(sum(sec.get((m, "meetup" if s == "meetup_median" else s), sec_model.get(m, np.nan))
                         for m, s in zip(df.model, df.scenario)))

    wall = sum(sg["wall_seconds"] for sg in segs)
    concurrency = float(timed.seconds.sum()) / main_seg["wall_seconds"]
    workers = full_workers or main_seg["workers"]
    conc_full = concurrency * workers / main_seg["workers"]     # assumes linear scaling in the worker count
    hours_full, hours_explore = cost(full) / conc_full / 3600, cost(explore) / conc_full / 3600
    hours_phase = {int(k): cost(g) / conc_full / 3600 for k, g in full.groupby("phase")}
    short = pd.DataFrame(jobs(f"full:{n}:short", {"scenarios": ["big_cluster", "three_clusters", "scattered", "mixed", "burst"],
                                                  "levels": ["tight", "normal", "loose"]}))
    hours_short = cost(short) / conc_full / 3600

    # busy CPUs
    busy = busy_cpus(PILOT / "cpu_vmstat.log")
    res = {"checks": checks, "n": n, "n_required_max": {k: int(v) for k, v in c.groupby("family").n_required.max().items()},
           "n_required_median": {k: float(v) for k, v in c.groupby("family").n_required.median().items()},
           "pilot_wall_hours": wall / 3600, "pilot_concurrency": concurrency, "pilot_workers": main_seg["workers"],
           "timed_rows": [int(lo), int(hi)], "first_pass_rows_not_timed": int(spans[0][0]),
           "seconds_per_episode_by_model": {k: round(float(v), 1) for k, v in sec_model.items()},
           "full_episodes": int(len(full)), "explore_episodes": int(len(explore)), "full_workers": workers,
           "runtime_hours_full": hours_full, "runtime_hours_explore_part": hours_explore,
           "runtime_hours_by_phase": hours_phase, "runtime_hours_short_sweep": hours_short,
           "plan": f"full:{n}" if hours_full <= 48.0 else f"full:{n}:short",     # Filipe, 2026-11-04: cut only past 48 h
           "sweep_pending": pending, "limit_hours": LIMIT_H, "within_limit": bool(hours_full <= LIMIT_H),
           "busy_cpus": {"minutes": int(len(busy)), "mean": float(busy.mean()), "p95": float(busy.quantile(0.95)),
                         "max": float(busy.max()), "minutes_over_cap": int((busy > CPU_CAP).sum()), "cap": CPU_CAP}}
    (PILOT / "power_extension.json").write_text(json.dumps(res, indent=1))
    top = c.sort_values("n_required", ascending=False).head(12)
    L = [f"# Extension pilot (X7): checks, sample size and runtime, {PILOT.name}", "",
         "This research was supported by data provided by Meituan.", "",
         f"Pilot: {checks['episodes']:,} episodes ({expected:,} planned), seeds 1 to 30, {res['pilot_wall_hours']:.1f} h on "
         f"{res['pilot_workers']} workers, BLAS threads {checks['blas_threads']}. Undelivered orders: {checks['undelivered_total']}.", "",
         "## Checks", "",
         f"- Identity (section 8): Zhu and Jusup at 0% against nearest courier, {checks['identity_episodes']} episodes, "
         f"{checks['identity_failures']} differ (`identity.csv`).",
         f"- Frozen reruns against S7: {checks['frozen_rerun_episodes']} episodes, "
         f"{checks['frozen_rerun_differ_from_s7']} differ (`frozen_check.csv`), as expected: S7 ran at a3e38b8, before the S8 "
         "review fixes (6cd370b, per-gap behavior draws). Replayed on FE-SIM-1, a3e38b8 gives the S7 row and 6cd370b the "
         "pilot's rerun row bit for bit (nearest courier, big cluster, tight, seed 1). The frozen four's identity is checked "
         "against S8: the regression harness, and every frozen rerun of the full runs (`sim/analysis_extension.py`).",
         f"- Jahanshahi et al. (descriptive row): {checks['jahanshahi_equal_to_nearest']} of "
         f"{checks['jahanshahi_fitted_episodes']} fitted episodes equal nearest courier in every frozen metric.",
         f"- Busy CPUs per minute (vmstat, of {VCPU}): mean {busy.mean():.1f}, 95th percentile {busy.quantile(0.95):.1f}, "
         f"max {busy.max():.1f}; {res['busy_cpus']['minutes_over_cap']} of {len(busy)} minutes above {CPU_CAP}.", "",
         "## Sample size (section 6)", "",
         f"**n = {n} seeds per cell.** Largest n_c: E1 {res['n_required_max']['E1']}, E2 {res['n_required_max']['E2']}; "
         f"median E1 {res['n_required_median']['E1']:.0f}, E2 {res['n_required_median']['E2']:.0f}.", "",
         "| Family | Start | Level | Model | Metric | Nearest mean | SD of differences | delta | n_c |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in top.itertuples():
        L.append(f"| {r.family} | {r.scenario} | {r.level} | {r.model} | {r.metric} | {r.nearest_mean:.2f} | "
                 f"{r.sd_diff:.2f} | {r.delta:.2f} | {r.n_required} |")
    L += ["", "## Runtime", "",
          f"Pilot concurrency {concurrency:.1f} episodes at a time on {res['pilot_workers']} workers. Full runs at n = {n}: "
          f"{len(full):,} episodes (the exploratory meet-up's {len(explore)} included), about {hours_full:.1f} h on {workers} "
          f"workers; by phase (1 E1 and E2, 2 meet-ups, 3 E5, 4 E3 and E4): "
          + ", ".join(f"{k}: {v:.1f} h" for k, v in hours_phase.items()) + f". With the sweep cut to 0 and 1: {hours_short:.1f} h. "
          f"Plan run (Filipe, 2026-11-04: nothing is cut unless the total passes 48 h): `{res['plan']}`.", "",
          "| Model | Seconds per episode (pilot mean) |", "|---|---|"]
    for m, v in sec_model.sort_values(ascending=False).items():
        L.append(f"| {m} | {v:.1f} |")
    L += ["", "The pilot sets variances and runtime only; its mean differences are not results, and it is not reused "
          "(section 6). All contrasts: `contrasts.csv`."]
    (PILOT / "power_extension.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
