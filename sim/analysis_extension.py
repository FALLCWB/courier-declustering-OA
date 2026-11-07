"""X8: results of the extension's full runs, as fixed in preregistration-extension.md (frozen at 8e082e3).

Usage: python sim/analysis_extension.py <out_dir> <full_dir> <pilot_dir> <first_round_results_dir> <s8_dir> --n <n>
                                          [--families E1,E2]
  full_dir        episodes.jsonl of `sim/run_extension.py ... full:<n>` (sets new, ride, frozen_rerun, explore)
  --n             seeds 1001 to 1000 + n; every cell the analysis reads must hold all of them
  --families      the families to test (default all five); G8 is sent with E1 and E2 while the other runs continue
                  (Filipe, 2026-11-04); the descriptive parts whose runs are not complete yet are marked pending
  pilot_dir       pilot_nearest_means.csv of `scripts/pilot_extension.py` (base of every smallest effect, section 6)
  first_round_results_dir   contrasts.csv and classes.csv of the first round (F1 p90 and Q1 classes of the frozen three)
  s8_dir          episodes.jsonl of S8 (the frozen reruns must equal it bit for bit at seeds 1001 to 1030)
Writes: contrasts.csv (E1 to E5, Holm within each family), classes.csv and class_counts.csv (joint reading), undo.csv
(time to undo and the second-hour check per Q2 cell), costs.csv (Q3), descriptive.csv (DQN, ride variant, exploratory
meet-up), profile.csv, checks.json and results.md.

Contrast: model minus nearest courier in one cell, paired by seed, lower is better; 95% percentile bootstrap (10,000
resamples, generator seed 20261103 with the contrast's key); two-sided paired t-test; Holm at 0.05 within each family.
Arm C enters E1 to E4 at 100% obedience (an upper bound) and E5 at 25, 50 and 75%.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.stats import P90_SESOI_MIN, W1_SESOI_SHARE, classify, contrast_rng, holm, paired_contrast, time_to_undo  # noqa: E402
from sim.run_extension import FRESH0  # noqa: E402

NEW5 = ["xu", "li", "auad", "zhu", "jusup"]
FROZEN3 = ["foodmatch", "forecast", "backpressure"]
ARM_C = ["zhu", "jusup"]
TEN = ["nearest", *FROZEN3, "xu", "li", "jahanshahi", "auad", *ARM_C]
LEVELS = ["tight", "normal", "loose"]
SWEEP = ["p0", "p0.25", "p0.5", "p1"]
Q1 = [(s, lvl) for s in ("scattered", "burst") for lvl in LEVELS]
Q2 = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in LEVELS] + [("meetup", "normal")]
W1, W160, P90 = "w1_rule_min", "w1_rule_60min_after_min", "p90_c2d_min"
FAMILY_SIZE = {"E1": 60, "E2": 133, "E3": 240, "E4": 532, "E5": 192}
FROZEN_METRICS = ["w1_rule_min", "w1_rule_first30_min", "w1_min", "w1_idle_weighted_min", "p90_c2d_min", "mean_c2d_min",
                  "late_rate", "tv", "gini_idle", "uncovered", "extra_km_per_order", "idle_km_per_order", "earnings_gini",
                  "food_wait_mean_min", "food_wait_p90_min", "unassigned_over_30min_share", "delivered", "undelivered",
                  "orders"]
COSTS = ["extra_km_per_order", "idle_km_per_order", "unassigned_over_30min_share", "undelivered"]


def same(a, b):
    return a == b or (a != a and b != b)


def load(path):
    ep = pd.read_json(Path(path) / "episodes.jsonl", lines=True, precise_float=True, dtype={"obedience": float})
    key = ["set", "scenario", "level", "behavior", "model", "obedience", "seed"]
    if ep.duplicated(key).any():
        raise SystemExit(f"{int(ep.duplicated(key).sum())} duplicated episodes in {path}")
    return ep


def start_min(scenario):
    return 120 if scenario.startswith("meetup") else 0


def window(series, scenario, lo, hi):
    """Mean of the soon-free W1 snapshots in minutes [lo, hi) after the cluster appears (nan snapshots skipped, as in
    the episode W1 of sim.runner.rule_w1)."""
    s = start_min(scenario)
    return float(np.nanmean(np.asarray(series, float)[s + lo:s + hi]))


class Runs:
    """Rows of one cell: rows(scenario, level, behavior, model, obedience) indexed by seed. Nearest courier comes from the
    frozen reruns on the starts and from the new cells on the meet-up; arm C rows need an obedience level."""

    def __init__(self, ep, n, sets=("new", "frozen_rerun"), first=1001):
        ep = ep[ep.set.isin(list(sets))].copy()
        ep["ob"] = ep.obedience.fillna(-1.0)
        self.g = {k: g.set_index("seed").sort_index() for k, g in ep.groupby(["scenario", "level", "behavior", "model", "ob"])}
        self.seeds = list(range(first, first + n))

    def rows(self, scenario, level, behavior, model, obedience=None):
        """A cell's rows; the run may still be going, so a cell missing any of the n seeds stops the analysis."""
        ob = -1.0 if model not in ARM_C else float(obedience)
        g = self.g.get((scenario, level, behavior, model, ob))
        if g is None or list(g.index) != self.seeds:
            raise SystemExit(f"cell {scenario} {level} {behavior} {model} {obedience} is not complete "
                             f"({0 if g is None else len(g)} of {len(self.seeds)} seeds)")
        return g


def deltas(pilot_dir):
    m = pd.read_csv(Path(pilot_dir) / "pilot_nearest_means.csv")
    return {(r.scenario, r.level, r.behavior): {W1: W1_SESOI_SHARE * r.w1_rule_min_mean,
                                                W160: W1_SESOI_SHARE * r.w1_rule_60min_after_min_mean,
                                                "second_hour": W1_SESOI_SHARE * r.w1_second_hour_mean}
            for r in m.itertuples()}


def contrast(runs, dl, family, scenario, level, behavior, model, metric, obedience=1.0):
    base = runs.rows(scenario, level, behavior, "nearest")
    mod = runs.rows(scenario, level, behavior, model, obedience)
    cell = (scenario, level, behavior, obedience if model in ARM_C else None)
    c = paired_contrast(mod[metric], base[metric], contrast_rng(cell, model, metric))
    delta = P90_SESOI_MIN if metric == P90 else dl[(scenario, level, behavior)][metric]
    return {"family": family, "scenario": scenario, "level": level, "behavior": behavior, "model": model,
            "obedience": obedience if model in ARM_C else np.nan, "metric": metric, "delta": delta,
            "model_mean": float(mod[metric].mean()), "nearest_mean": float(base[metric].mean()), **c}


def families(runs, dl, which=tuple(FAMILY_SIZE), sweep=tuple(SWEEP)):
    """The confirmatory families. `sweep` holds the return values run: all four, or 0 and 1 under the short plan
    (Filipe's 48-h rule, 2026-11-04), in which case E3 and E4 hold E1's and E2's contrasts at those values only."""
    rows = []
    sweep = list(sweep)
    for fam, settings in (("E1", ["fitted"]), ("E3", sweep)):
        if fam not in which:
            continue
        rows += [contrast(runs, dl, fam, s, lvl, b, m, met) for b in settings for m in NEW5 for met in (W1, P90)
                 for s, lvl in Q1]
    for fam, settings in (("E2", ["fitted"]), ("E4", sweep)):
        if fam not in which:
            continue
        for b in settings:
            rows += [contrast(runs, dl, fam, s, lvl, b, m, W160) for m in NEW5 + FROZEN3 for s, lvl in Q2]
            rows += [contrast(runs, dl, fam, s, lvl, b, m, P90) for m in NEW5 for s, lvl in Q2]
            rows += [contrast(runs, dl, fam, "meetup", "normal", b, m, P90) for m in FROZEN3]
    for o in (0.25, 0.5, 0.75) if "E5" in which else ():
        for m in ARM_C:
            rows += [contrast(runs, dl, "E5", s, lvl, "fitted", m, met, o) for met in (W1, P90) for s, lvl in Q1]
            rows += [contrast(runs, dl, "E5", s, lvl, "fitted", m, met, o) for met in (W160, P90) for s, lvl in Q2]
    con = pd.DataFrame(rows)
    sizes = con.groupby("family").size().to_dict()
    want = {**FAMILY_SIZE, "E3": FAMILY_SIZE["E1"] * len(sweep), "E4": FAMILY_SIZE["E2"] * len(sweep)}
    if sizes != {f: want[f] for f in which}:
        raise SystemExit(f"family sizes {sizes}, the pre-registration fixes {want} for the sweep {sweep}")
    con["p_holm"] = np.nan
    for fam, idx in con.groupby("family").groups.items():
        con.loc[idx, "p_holm"] = holm(con.loc[idx, "p"].to_numpy())
    con["established"] = con.p_holm < 0.05
    con["at_least_sesoi"] = con["mean"].abs() >= con.delta                  # either direction
    con["lower_at_least_sesoi"] = -con["mean"] >= con.delta                  # a decrease (better) of at least delta
    con["equivalence"] = equivalence(con)
    return con


def equivalence(con):
    """Secondary reading of preregistration-extension-addendum-R3.md (after the freeze, before any E1 or E2 row was read):
    a contrast that is not established is "equivalent within delta" when its 95% interval lies inside (-delta, +delta),
    else "inconclusive"; an established contrast gets no reading. It changes no class and no Holm result."""
    inside = (con.lo > -con.delta) & (con.hi < con.delta)
    est = con.established
    if pd.api.types.is_bool_dtype(est) or pd.api.types.is_numeric_dtype(est):
        est = est.astype(bool)
    else:                                               # "True"/"False" read from a CSV (object or string dtype)
        est = est.astype(str).str.strip().str.lower().eq("true")
    return np.where(est, "",
                    np.where(inside, "equivalent within delta", "inconclusive"))


LABEL = {"Q1": {"declusters at no delivery cost": "prevents at no delivery cost",
                "declusters at a delivery cost": "prevents at a delivery cost",
                "declusters, cost unresolved": "prevents, cost unresolved", "does not decluster": "does not prevent"},
         "Q2": {"declusters at no delivery cost": "undoes at no delivery cost",
                "declusters at a delivery cost": "undoes at a delivery cost",
                "declusters, cost unresolved": "undoes, cost unresolved", "does not decluster": "does not undo"}}


def joint_reading(con, f1):
    """One class per primary cell and model (section 5): E1 cells for the new five (Q1), E2 cells for the eight (Q2).
    The frozen three's p90 on the Q2 starts is their F1 contrast, which is not tested again."""
    rows = []
    e1, e2 = con[con.family == "E1"], con[con.family == "E2"]
    for (s, lvl, m), g in e1.groupby(["scenario", "level", "model"]):
        w, p = g[g.metric == W1].iloc[0].to_dict(), g[g.metric == P90].iloc[0].to_dict()
        rows.append({"question": "Q1", "scenario": s, "level": lvl, "model": m,
                     "class": LABEL["Q1"][classify(w, p, w["delta"])], "w1_mean": w["mean"], "w1_p_holm": w["p_holm"],
                     "p90_mean": p["mean"], "p90_hi": p["hi"], "p90_p_holm": p["p_holm"], "p90_source": "E1"})
    f1p = f1[(f1.family == "F1") & (f1.metric == "p90")].set_index(["scenario", "level", "model"])
    for (s, lvl, m), g in e2.groupby(["scenario", "level", "model"]):
        w = g[g.metric == W160].iloc[0].to_dict()
        pg = g[g.metric == P90]
        if len(pg):
            p, src = pg.iloc[0].to_dict(), "E2"
        else:
            p, src = f1p.loc[(s, lvl, m)].to_dict(), "F1 (first round)"
        rows.append({"question": "Q2", "scenario": s, "level": lvl, "model": m,
                     "class": LABEL["Q2"][classify(w, p, w["delta"])], "w1_mean": w["mean"], "w1_p_holm": w["p_holm"],
                     "p90_mean": p["mean"], "p90_hi": p["hi"], "p90_p_holm": p["p_holm"], "p90_source": src})
    cl = pd.DataFrame(rows)
    counts = cl.pivot_table(index=["question", "model"], columns="class", values="scenario", aggfunc="count", fill_value=0)
    return cl, counts


def fresh_q2(fresh, runs, dl, con):
    """R4 (Filipe, 2026-11-05; DECISIONS.md): the frozen three's Q2 contrasts again on the fresh block (seeds 5001 on),
    paired with nearest courier on the same seeds: W1 over 60 min and p90 in the ten Q2 cells, the p90 on the nine starts
    included (E2 takes those from F1, whose seeds were seen). They replace the frozen three's 33 rows of E2 next to the
    new five's 100, and Holm runs over these 160 (more contrasts than E2's 133, so no less strict)."""
    rows = [contrast(fresh, dl, "E2-fresh", s, lvl, "fitted", m, met) for m in FROZEN3 for met in (W160, P90) for s, lvl in Q2]
    fr = pd.DataFrame(rows).assign(seeds=f"{fresh.seeds[0]}-{fresh.seeds[-1]}")
    keep = con[(con.family == "E2") & ~con.model.isin(FROZEN3)][fr.columns.drop("seeds")].copy()
    keep = keep.assign(family="E2-fresh", seeds=f"{runs.seeds[0]}-{runs.seeds[-1]}")
    out = pd.concat([keep, fr], ignore_index=True)
    if len(out) != 160:
        raise SystemExit(f"{len(out)} contrasts in E2-fresh, R4 fixes 160")
    out["p_holm"] = holm(out.p.to_numpy())
    out["established"] = out.p_holm < 0.05
    out["at_least_sesoi"] = out["mean"].abs() >= out.delta
    out["lower_at_least_sesoi"] = -out["mean"] >= out.delta
    out["equivalence"] = equivalence(out)
    rows = []
    for (s, lvl, m), g in out[out.model.isin(FROZEN3)].groupby(["scenario", "level", "model"]):
        w, p = g[g.metric == W160].iloc[0].to_dict(), g[g.metric == P90].iloc[0].to_dict()
        rows.append({"question": "Q2", "scenario": s, "level": lvl, "model": m, "seeds": w["seeds"],
                     "class": LABEL["Q2"][classify(w, p, w["delta"])], "w1_mean": w["mean"], "w1_p_holm": w["p_holm"],
                     "p90_mean": p["mean"], "p90_hi": p["hi"], "p90_p_holm": p["p_holm"], "p90_source": "E2-fresh"})
    return out, pd.DataFrame(rows)


def undo(runs, dl, cl, models=("nearest", *NEW5, *FROZEN3, "jahanshahi")):
    """Q2 secondary, per Q2 cell at the fitted behavior: time to undo per episode against the same model, obedience,
    supply, behavior and seed from the scattered start (median and censored share), and the second-hour check for
    cells classed as undoing (section 5, Profile)."""
    rows = []
    cls = cl[cl.question == "Q2"].set_index(["scenario", "level", "model"])["class"]
    for s, lvl in Q2:
        ref_lvl = lvl
        res = {}
        for m in models:
            r = runs.rows(s, lvl, "fitted", m, 1.0)
            sc = runs.rows("scattered", ref_lvl, "fitted", m, 1.0)
            t = np.array([time_to_undo(r.loc[k, "w1_rule_series"], sc.loc[k, "w1_rule_series"], start_min=start_min(s))
                          for k in runs.seeds])
            censored = t >= 240 - start_min(s)
            second = np.array([window(r.loc[k, "w1_rule_series"], s, 60, 120) for k in runs.seeds])
            res[m] = (t, censored, second)
        nt, _, ns = res["nearest"]
        for m, (t, cens, second) in res.items():
            klass = cls.get((s, lvl, m), "nearest courier" if m == "nearest" else "descriptive")
            flag = ""
            if klass.startswith("undoes"):
                worse = (second.mean() - ns.mean() >= dl[(s, lvl, "fitted")]["second_hour"]
                         or np.median(t) > np.median(nt))
                flag = "undoes in the first hour, not after" if worse else "holds after the first hour"
            rows.append({"scenario": s, "level": lvl, "model": m, "class": klass,
                         "time_to_undo_median": float(np.median(t)), "time_to_undo_q25": float(np.percentile(t, 25)),
                         "time_to_undo_q75": float(np.percentile(t, 75)), "censored_count": int(cens.sum()),
                         "censored_share": float(cens.mean()),
                         "nearest_time_to_undo_median": float(np.median(nt)), "second_hour_w1": float(second.mean()),
                         "nearest_second_hour_w1": float(ns.mean()), "second_hour_check": flag})
    return pd.DataFrame(rows)


def costs(runs):
    """Q3, descriptive: model minus nearest courier in each fitted primary cell (Q1 and Q2), arm C at 100%."""
    rows = []
    for s, lvl in Q1 + Q2:
        base = runs.rows(s, lvl, "fitted", "nearest")
        for m in [*FROZEN3, "xu", "li", "jahanshahi", "auad", *ARM_C]:
            mod = runs.rows(s, lvl, "fitted", m, 1.0)
            rows.append({"scenario": s, "level": lvl, "model": m, "p90_diff": float((mod[P90] - base[P90]).mean()),
                         **{f"{k}_model": float(mod[k].mean()) for k in COSTS},
                         **{f"{k}_nearest": float(base[k].mean()) for k in COSTS}})
    return pd.DataFrame(rows)


def descriptive(full, runs):
    """The DQN row (equal to nearest courier by construction), the ride variant and the exploratory meet-up."""
    rows = []
    for s, lvl in Q1 + Q2:
        j, n = runs.rows(s, lvl, "fitted", "jahanshahi"), runs.rows(s, lvl, "fitted", "nearest")
        eq = [all(same(j.loc[k, c], n.loc[k, c]) for c in FROZEN_METRICS) for k in runs.seeds]
        rows.append({"part": "jahanshahi", "scenario": s, "level": lvl, "model": "jahanshahi",
                     "episodes_equal_to_nearest": int(sum(eq)), "seeds": len(eq),
                     "w1_minus_nearest": float((j[W1] - n[W1]).mean()),
                     "w1_60_minus_nearest": float((j[W160] - n[W160]).mean()),          # G8 verdict D1
                     "p90_minus_nearest": float((j[P90] - n[P90]).mean())})
    for part, ep, scen in (("ride", full[full.set == "ride"], "meetup_ride"), ("explore", full[full.set == "explore"], "meetup_median")):
        want = runs.seeds if part == "ride" else list(range(1001, 1031))
        if ep.groupby("model").seed.apply(lambda x: sorted(x) == want).sum() != 10:
            rows.append({"part": part, "scenario": scen, "status": "pending: runs not complete"})
            continue
        near = ep[ep.model == "nearest"].set_index("seed")
        for m, g in ep.groupby("model"):
            g = g.set_index("seed").sort_index()
            row = {"part": part, "scenario": scen, "level": "normal", "model": m, "seeds": len(g),
                   "w1_60_mean": float(g[W160].mean()), "w1_60_minus_nearest": float((g[W160] - near.loc[g.index, W160]).mean()),
                   "p90_mean": float(g[P90].mean()), "p90_minus_nearest": float((g[P90] - near.loc[g.index, P90]).mean()),
                   "unassigned_over_30min_share": float(g.unassigned_over_30min_share.mean()),
                   "undelivered": int(g.undelivered.sum())}
            if part == "explore":                        # time to undo against the same model's scattered start
                sc = runs.rows("scattered", "normal", "fitted", m, 1.0)
                t = np.array([time_to_undo(g.loc[k, "w1_rule_series"], sc.loc[k, "w1_rule_series"], start_min=120)
                              for k in g.index])
                row.update({"time_to_undo_median": float(np.median(t)), "censored_share": float((t >= 120).mean())})
            rows.append(row)
    return pd.DataFrame(rows)


def frozen_check(full, s8_dir):
    """Every frozen metric of each rerun row equals its S8 row bit for bit, where S8 has the seed (1001 to 1030)."""
    s8 = pd.read_json(Path(s8_dir) / "episodes.jsonl", lines=True, precise_float=True)
    s8 = s8[s8.family.isin(["F1", "F2"])].set_index(["scenario", "level", "behavior", "model", "seed"])
    out = {"compared": 0, "differ": 0, "examples": []}
    for r in full[full.set == "frozen_rerun"].to_dict("records"):
        k = (r["scenario"], r["level"], r["behavior"], r["model"], r["seed"])
        if k not in s8.index:
            continue
        old = s8.loc[k]
        bad = [c for c in FROZEN_METRICS if not same(r[c], old[c])]
        out["compared"] += 1
        if bad:
            out["differ"] += 1
            out["examples"] = (out["examples"] + [[*map(str, k), bad]])[:5]
    return out


def profile(cl, ud, cs, f1_classes):
    rows = []
    for m in TEN[1:]:
        q1 = cl[(cl.question == "Q1") & (cl.model == m)]["class"].value_counts().to_dict()
        if m in FROZEN3:                                 # Q1 of the frozen three: their F1 classes in the six Q1 cells
            f = f1_classes[(f1_classes.model == m) & f1_classes.scenario.isin(["scattered", "burst"])]
            q1 = f["class"].map(LABEL["Q1"]).value_counts().to_dict()
        q2 = cl[(cl.question == "Q2") & (cl.model == m)]["class"].value_counts().to_dict()
        u = ud[ud.model == m]
        c = cs[cs.model == m]
        rows.append({"model": m, "descriptive_only": m == "jahanshahi",
                     "q1_classes": json.dumps(q1, sort_keys=True), "q1_source": "F1" if m in FROZEN3 else ("E1" if m in NEW5 else "none"),
                     "q2_classes": json.dumps(q2, sort_keys=True),
                     "time_to_undo_median_of_cells": float(u.time_to_undo_median.median()),
                     "nearest_time_to_undo_median_of_cells": float(ud[ud.model == "nearest"].time_to_undo_median.median()),
                     "cells_undo_first_hour_only": int((u.second_hour_check == "undoes in the first hour, not after").sum()),
                     "p90_diff_mean": float(c.p90_diff.mean()),
                     **{f"{k}_diff_mean": float((c[f"{k}_model"] - c[f"{k}_nearest"]).mean()) for k in COSTS}})
    return pd.DataFrame(rows)


def md(df, index=True):
    """A Markdown table without extra packages."""
    d = df.reset_index() if index else df
    head = [str(c) if not isinstance(c, tuple) else " ".join(map(str, c)) for c in d.columns]
    fmt = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] +
                     ["| " + " | ".join(fmt(v) for v in r) + " |" for r in d.itertuples(index=False)])


def main():
    ap = argparse.ArgumentParser()
    for name in ("out", "full_dir", "pilot_dir", "first", "s8_dir"):
        ap.add_argument(name, type=Path)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--families", default=",".join(FAMILY_SIZE))
    ap.add_argument("--sweep", default=",".join(SWEEP), help="return values run: p0,p1 under the short plan")
    a = ap.parse_args()
    out, full_dir, pilot_dir, first, s8_dir, n = a.out, a.full_dir, a.pilot_dir, a.first, a.s8_dir, a.n
    which = tuple(a.families.split(","))
    out.mkdir(parents=True, exist_ok=True)
    full = load(full_dir)
    explore = full[full.set == "explore"]
    runs = Runs(full, n)
    dl = deltas(pilot_dir)
    f1 = pd.read_csv(first / "contrasts.csv")
    f1_classes = pd.read_csv(first / "classes.csv")
    con = families(runs, dl, which, tuple(a.sweep.split(",")))
    cl, counts = joint_reading(con, f1)
    ud = undo(runs, dl, cl)
    cs = costs(runs)
    ds = descriptive(full, runs)
    pr = profile(cl, ud, cs, f1_classes)
    if "E2" in which:                                   # R4: the frozen three on Q2 from the fresh block
        fresh = Runs(full, n, sets=("fresh_q2",), first=FRESH0)
        ef, clf = fresh_q2(fresh, runs, dl, con)
        udf = undo(fresh, dl, clf, models=("nearest", *FROZEN3))
        ef.to_csv(out / "contrasts_e2_fresh.csv", index=False)
        clf.to_csv(out / "classes_e2_fresh.csv", index=False)
        udf.to_csv(out / "undo_e2_fresh.csv", index=False)
    checks = {"families": list(which), "sweep": a.sweep.split(","), "seeds": [runs.seeds[0], runs.seeds[-1]], "n": len(runs.seeds), "episodes": int(len(full)),
              "explore_episodes": int(len(explore)), "fresh_episodes": int((full.set == "fresh_q2").sum()),
              "blas_threads": sorted(full.blas_threads.unique().tolist()),
              "frozen_vs_s8": frozen_check(full, s8_dir), "undelivered_total": int(full.undelivered.sum())}
    if checks["frozen_vs_s8"]["differ"]:
        print("FROZEN RERUNS DIFFER FROM S8: stop, this is a defect", json.dumps(checks["frozen_vs_s8"]))
    con.to_csv(out / "contrasts.csv", index=False)
    cl.to_csv(out / "classes.csv", index=False)
    counts.to_csv(out / "class_counts.csv")
    ud.to_csv(out / "undo.csv", index=False)
    cs.to_csv(out / "costs.csv", index=False)
    ds.to_csv(out / "descriptive.csv", index=False)
    pr.to_csv(out / "profile.csv", index=False)
    (out / "checks.json").write_text(json.dumps(checks, indent=1, default=str))
    L = [f"# Extension results (X8), {out.name}", "", "This research was supported by data provided by Meituan.", "",
         f"Seeds {checks['seeds'][0]} to {checks['seeds'][1]} (n = {checks['n']}); {checks['episodes']:,} episodes read "
         f"({checks['fresh_episodes']:,} of them in the R4 fresh block, seeds {FRESH0} on); "
         f"frozen reruns against S8: {checks['frozen_vs_s8']['compared']} compared, {checks['frozen_vs_s8']['differ']} differ.", "",
         "## Established contrasts per family (Holm within each)", "",
         "| Family | Contrasts | Established | Established decrease of at least the smallest effect | Established increase "
         "| Not established: equivalent within delta (R3) | Not established: inconclusive (R3) |",
         "|---|---|---|---|---|---|---|"]
    for fam, g in con.groupby("family"):
        L.append(f"| {fam} | {len(g)} | {int(g.established.sum())} | {int((g.established & g.lower_at_least_sesoi).sum())} | "
                 f"{int((g.established & (g['mean'] > 0)).sum())} | {int((g.equivalence == 'equivalent within delta').sum())} | "
                 f"{int((g.equivalence == 'inconclusive').sum())} |")
    if "E2" in which:                                   # R4: the Holm family of 160, and its frozen-three part
        for name, g in (("E2-fresh (R4)", ef), ("E2-fresh, frozen three only (R4)", ef[ef.model.isin(FROZEN3)])):
            L.append(f"| {name} | {len(g)} | {int(g.established.sum())} | {int((g.established & g.lower_at_least_sesoi).sum())} | "
                     f"{int((g.established & (g['mean'] > 0)).sum())} | {int((g.equivalence == 'equivalent within delta').sum())} | "
                     f"{int((g.equivalence == 'inconclusive').sum())} |")
    if "E2" in which:
        e2 = con[(con.family == "E2") & con.model.isin(FROZEN3)].set_index(["scenario", "level", "model", "metric"])
        side = []
        for r in ef[ef.model.isin(FROZEN3)].itertuples():
            k = (r.scenario, r.level, r.model, r.metric)
            a = e2.loc[k] if k in e2.index else None
            side.append({"cell": f"{r.scenario}, {r.level}", "model": r.model, "metric": r.metric,
                         f"seeds {runs.seeds[0]}-{runs.seeds[-1]}": "F1 (first round)" if a is None else
                         f"{a['mean']:+.2f} [{a['lo']:+.2f}, {a['hi']:+.2f}], p_Holm {a['p_holm']:.3g}",
                         f"fresh seed block {r.seeds}": f"{r.mean:+.2f} [{r.lo:+.2f}, {r.hi:+.2f}], p_Holm {r.p_holm:.3g}"})
        L += ["", "## Frozen three on Q2: frozen seeds and the fresh seed block (R4)", "",
              "The fresh-seed contrasts are the ones Paper A quotes for these models on Q2. Holm over the 160 contrasts of "
              "E2 with the frozen three's rows taken from the fresh block (`contrasts_e2_fresh.csv`); classes in "
              "`classes_e2_fresh.csv`, time to undo in `undo_e2_fresh.csv`.", "", md(pd.DataFrame(side), index=False)]
    L += ["", "## Joint reading, class counts", "", md(counts), "", "## Profile", "", md(pr, index=False),
          "", "Arm C models enter at 100% obedience, an upper bound, never real courier behavior. The DQN row is descriptive."]
    (out / "results.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
