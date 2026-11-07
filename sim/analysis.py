"""S8: results of the full runs, as fixed in preregistration.md (sections 4 to 7 and the G3 joint reading).

Usage: python sim/analysis.py <out_dir> <full_runs_dir> [<f3_f4_runs_dir> ...] --pilot <pilot_dir>
Reads every episodes.jsonl given; writes contrasts.csv (every family, Holm within each), classes.csv and
class_counts.csv (F1 joint reading), secondary.csv (descriptive differences with 95% intervals) and results.md.
The smallest effect for W1 is 10% of nearest-courier's mean W1 in the same cell from the pilot; cells without a
pilot (F3, F4) use the nearest-courier mean of their own runs.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.stats import P90_SESOI_MIN, W1_SESOI_SHARE, classify, contrast_rng, holm, paired_contrast  # noqa: E402

PRIMARY = {"w1_rule_min": "W1", "p90_c2d_min": "p90"}
SECONDARY = ["w1_rule_first30_min", "w1_idle_weighted_min", "tv", "gini_idle", "uncovered", "late_rate",
             "extra_km_per_order", "idle_km_per_order", "earnings_gini", "mean_c2d_min", "unassigned_over_30min_share",
             "food_wait_mean_min", "food_wait_p90_min", "fallback_draw_none_share", "fallback_zone_empty_share",
             "fallback_no_neighbor_share", "undelivered", "w1_rule_nan_snapshots"]
MODELS = ["foodmatch", "forecast", "backpressure"]
CELL = ["family", "scenario", "level", "behavior", "layout", "scale", "time_mult"]
FAMILY_SIZE = {"F1": 90, "F2": 360, "F3": 30, "F4": 12}


def load(dirs):
    ep = pd.concat([pd.read_json(Path(d) / "episodes.jsonl", lines=True, precise_float=True) for d in dirs], ignore_index=True)
    dup = ep.duplicated(CELL + ["seed", "model"])
    if dup.any():
        raise SystemExit(f"{int(dup.sum())} duplicated episodes")
    return ep


def pilot_means(pilot_dir):
    """Nearest-courier mean W1 per pilot cell, from the nearest rows themselves (`sim/power.py`)."""
    c = pd.read_csv(Path(pilot_dir) / "pilot_nearest_w1.csv")
    return {(r.family, r.scenario, r.level, r.behavior): r.nearest_w1_mean for r in c.itertuples()}


def check_seeds(ep):
    """Every (cell, model) must hold the same seeds; returns the seed count."""
    seeds = ep.groupby(CELL + ["model"]).seed.apply(lambda s: tuple(sorted(s)))
    if seeds.nunique() != 1:
        short = seeds[seeds.map(len) < seeds.map(len).max()]
        raise SystemExit(f"cells with missing seeds:\n{short.map(len).to_string()}")
    return len(seeds.iloc[0])


def contrasts(ep, pilot):
    rows, sec = [], []
    for cell, g in ep.groupby(CELL, sort=True):
        base = g[g.model == "nearest"].set_index("seed")
        for m in MODELS:
            mod = g[g.model == m].set_index("seed")
            seeds = base.index.intersection(mod.index).sort_values()
            for col, name in PRIMARY.items():
                c = paired_contrast(mod.loc[seeds, col], base.loc[seeds, col], contrast_rng(cell, m, name))
                if col == "w1_rule_min":
                    ref = pilot.get(cell[:4], float(base.loc[seeds, col].mean()))
                    delta = W1_SESOI_SHARE * ref
                else:
                    delta = P90_SESOI_MIN
                rows.append({**dict(zip(CELL, cell)), "model": m, "metric": name, "delta": delta, **c})
            for col in SECONDARY:
                if col in mod and col in base and mod[col].notna().any() and base[col].notna().any():
                    a, b = mod.loc[seeds, col].fillna(0.0), base.loc[seeds, col].fillna(0.0)
                    c = paired_contrast(a, b, contrast_rng(cell, m, col, seed=20261104), n_boot=2000)
                    sec.append({**dict(zip(CELL, cell)), "model": m, "metric": col, "model_mean": float(a.mean()),
                                "nearest_mean": float(b.mean()), **{k: c[k] for k in ["n", "mean", "lo", "hi"]}})
    out = pd.DataFrame(rows)
    for fam, size in out.groupby("family").size().items():
        if size != FAMILY_SIZE[fam]:
            raise SystemExit(f"family {fam} has {size} contrasts, the pre-registration fixes {FAMILY_SIZE[fam]}")
    out["p_holm"] = np.nan
    for fam, idx in out.groupby("family").groups.items():
        out.loc[idx, "p_holm"] = holm(out.loc[idx, "p"].to_numpy())
    out["established"] = out.p_holm < 0.05
    out["at_least_sesoi"] = out["mean"].abs() >= out.delta
    return out, pd.DataFrame(sec)


CLUSTERED = ["big_cluster", "three_clusters", "mixed"]


def gap_share(ep, n_boot=10_000):
    """G4 verdict V1 (descriptive, not a test): on each clustered start, a model's W1 cut against nearest courier
    divided by the gap between nearest courier's W1 on that start and on the scattered start, same supply level and
    behavior setting (and seeds); ratio of means with a 95% percentile bootstrap interval over seeds."""
    rows = []
    sub = ep[ep.family.isin(["F1", "F2"])]
    w = sub.pivot_table(index=["level", "behavior", "seed"], columns=["scenario", "model"], values="w1_rule_min")
    for (lvl, beh), g in w.groupby(level=["level", "behavior"]):
        for sc in CLUSTERED:
            gap = (g[(sc, "nearest")] - g[("scattered", "nearest")]).to_numpy()
            for m in ["foodmatch", "forecast", "backpressure"]:
                cut = (g[(sc, "nearest")] - g[(sc, m)]).to_numpy()
                rng = contrast_rng((lvl, beh, sc), m, "gap_share", seed=20261105)
                idx = rng.integers(0, len(cut), (n_boot, len(cut)))
                boot = cut[idx].mean(axis=1) / gap[idx].mean(axis=1)
                rows.append({"family": "F1" if beh == "fitted" else "F2", "scenario": sc, "level": lvl, "behavior": beh,
                             "model": m, "seeds": len(cut), "nearest_w1": float(g[(sc, "nearest")].mean()),
                             "nearest_w1_scattered": float(g[("scattered", "nearest")].mean()), "gap": float(gap.mean()),
                             "cut": float(cut.mean()), "gap_share": float(cut.mean() / gap.mean()),
                             "lo": float(np.percentile(boot, 2.5)), "hi": float(np.percentile(boot, 97.5))})
    return pd.DataFrame(rows)


def foodmatch_tight(ep, con):
    """G4 verdict V4: FoodMatch's tight-supply p90 contrast beside its unassigned-over-30-min share and undelivered count."""
    rows = []
    f1 = con[(con.family == "F1") & (con.metric == "p90") & (con.model == "foodmatch") & (con.level == "tight")]
    for r in f1.itertuples():
        g = ep[(ep.family == "F1") & (ep.scenario == r.scenario) & (ep.level == "tight") & (ep.behavior == "fitted")]
        fm, nn = g[g.model == "foodmatch"], g[g.model == "nearest"]
        rows.append({"scenario": r.scenario, "p90_diff": r.mean, "p90_lo": r.lo, "p90_hi": r.hi, "p90_p_holm": r.p_holm,
                     "unassigned_30_foodmatch": float(fm.unassigned_over_30min_share.mean()),
                     "unassigned_30_nearest": float(nn.unassigned_over_30min_share.mean()),
                     "undelivered_foodmatch": int(fm.undelivered.sum()), "undelivered_nearest": int(nn.undelivered.sum()),
                     "seeds": int(len(fm))})
    return pd.DataFrame(rows)


def classes(con):
    f1 = con[con.family == "F1"]
    rows = []
    for (sc, lvl, m), g in f1.groupby(["scenario", "level", "model"]):
        w1 = g[g.metric == "W1"].iloc[0].to_dict()
        p90 = g[g.metric == "p90"].iloc[0].to_dict()
        rows.append({"scenario": sc, "level": lvl, "model": m, "class": classify(w1, p90, w1["delta"]),
                     "w1_mean": w1["mean"], "w1_lo": w1["lo"], "w1_hi": w1["hi"], "w1_p_holm": w1["p_holm"],
                     "p90_mean": p90["mean"], "p90_lo": p90["lo"], "p90_hi": p90["hi"], "p90_p_holm": p90["p_holm"]})
    cl = pd.DataFrame(rows)
    counts = cl.pivot_table(index="model", columns="class", values="scenario", aggfunc="count", fill_value=0)
    return cl, counts


def main():
    args = sys.argv[1:]
    pilot_dir = args[args.index("--pilot") + 1]
    dirs = [a for a in args[1:args.index("--pilot")]]
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    ep = load(dirs)
    n_seeds = check_seeds(ep)
    con, sec = contrasts(ep, pilot_means(pilot_dir))
    con.to_csv(out / "contrasts.csv", index=False)
    sec.to_csv(out / "secondary.csv", index=False)
    cl, counts = classes(con)
    cl.to_csv(out / "classes.csv", index=False)
    counts.to_csv(out / "class_counts.csv")
    gs = gap_share(ep)
    gs.to_csv(out / "gap_share.csv", index=False)
    ft = foodmatch_tight(ep, con)
    ft.to_csv(out / "foodmatch_tight.csv", index=False)
    L = [f"# Part 1 results, untrained models ({out.name})", "",
         "This research was supported by data provided by Meituan.", "",
         f"Episodes: {len(ep):,}; {n_seeds} seeds in every cell and model; undelivered orders at the drain's end: "
         f"{int(ep.undelivered.sum())}. The smallest W1 effect of F3 and F4 cells, which have no pilot, uses the "
         f"nearest-courier mean of their own runs.",
         "Contrasts: model minus nearest courier, paired by seed; 95% percentile bootstrap intervals (10,000 resamples); "
         "two-sided paired t-test p-values, Holm within each family.", "",
         "## F1 joint reading (cells per class and model)", "", "| Model | " + " | ".join(counts.columns) + " |",
         "|---|" + "---|" * len(counts.columns)]
    for m, r in counts.iterrows():
        L.append(f"| {m} | " + " | ".join(str(int(x)) for x in r.to_numpy()) + " |")
    L += ["", "## Share of the gap to a scattered start closed on clustered starts (G4 verdict V1; descriptive, fitted behavior)",
          "", "Cut = nearest-courier W1 minus the model's W1; gap = nearest-courier W1 on that start minus on the scattered "
          "start, same supply level and seeds; share = mean cut / mean gap with a 95% bootstrap interval over seeds. "
          "Sweep settings: `gap_share.csv`.", "",
          "| Start | Level | Model | Nearest W1 | Nearest W1, scattered | Gap (min) | Cut (min) | Share of gap (95% CI) |",
          "|---|---|---|---|---|---|---|---|"]
    for r in gs[gs.behavior == "fitted"].itertuples():
        L.append(f"| {r.scenario} | {r.level} | {r.model} | {r.nearest_w1:.2f} | {r.nearest_w1_scattered:.2f} | {r.gap:.2f} | "
                 f"{r.cut:.2f} | {r.gap_share:.3f} ({r.lo:.3f} to {r.hi:.3f}) |")
    L += ["", "## FoodMatch at tight supply (G4 verdict V4)", "",
          "Its p90 gain is read only with the orders it leaves unassigned for more than 30 min and those not delivered by "
          "the drain's end; the paper's own design rejects orders unassigned for 30 min (fidelity note, adaptation 2).", "",
          "| Start | p90 difference (95% CI) | Holm p | Unassigned over 30 min, FoodMatch / nearest | Undelivered, FoodMatch / nearest (30 seeds) |",
          "|---|---|---|---|---|"]
    for r in ft.itertuples():
        L.append(f"| {r.scenario} | {r.p90_diff:.2f} ({r.p90_lo:.2f} to {r.p90_hi:.2f}) | {r.p90_p_holm:.2g} | "
                 f"{100 * r.unassigned_30_foodmatch:.2f}% / {100 * r.unassigned_30_nearest:.2f}% | "
                 f"{r.undelivered_foodmatch} / {r.undelivered_nearest} |")
    for fam in ["F1", "F2", "F3", "F4"]:
        f = con[con.family == fam]
        if not len(f):
            continue
        L += ["", f"## {fam}: {len(f)} contrasts, {int(f.established.sum())} established after Holm", "",
              "| Start | Level | Behavior | Layout | Scale | Time x | Model | Metric | Mean (95% CI) | Holm p | delta |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in f.itertuples():
            L.append(f"| {r.scenario} | {r.level} | {r.behavior} | {r.layout} | {r.scale:g} | {r.time_mult:g} | {r.model} | "
                     f"{r.metric} | {r.mean:.3f} ({r.lo:.3f} to {r.hi:.3f}) | {r.p_holm:.2g} | {r.delta:.2f} |")
    L += ["", "Secondary metrics (descriptive): `secondary.csv`. Classes per cell: `classes.csv`."]
    (out / "results.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
