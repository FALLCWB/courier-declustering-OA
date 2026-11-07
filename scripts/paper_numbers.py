"""G8 numbers for Paper A (instructions of 2026-11-05, section 3): one Markdown file and one CSV per table.

Usage: python scripts/paper_numbers.py <analysis_out> <full_dir> <zhu_ties_dir> <out_dir> --n <n> --first <dir>
  analysis_out   outputs of sim/analysis_extension.py (contrasts, classes, undo, descriptive, profile, the R4 files)
  full_dir       episodes.jsonl of the full runs (Q3 and the secondary agreement are computed from the rows)
  zhu_ties_dir   zhu_ties.csv of scripts/zhu_ties_report.py (G8 item 2)
  --first        the first round's results (F1 p90 of the frozen three on the Q1 starts, for the Q3 cost reading)
Every number is an aggregate over seeds; no per-episode row is written.

Per contrast: mean paired difference against nearest courier (model minus nearest, lower is better), 95% percentile
bootstrap interval (10,000 resamples, generator seed 20261103 keyed by the contrast), Holm-adjusted p within the family
("descriptive" where no family applies), the difference as % of nearest courier's mean, n, the joint-reading class and
the R3 equivalence reading.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sim.analysis_extension import ARM_C, FROZEN3, NEW5, P90, Q1, Q2, W160, W1, Runs, load, md, window  # noqa: E402
from sim.run_extension import FRESH0  # noqa: E402
from sim.stats import P90_SESOI_MIN, contrast_rng, paired_contrast  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
NINE = [*FROZEN3, "xu", "li", "jahanshahi", "auad", *ARM_C]
Q3 = [P90, "mean_c2d_min", "late_rate", "idle_km_per_order", "extra_km_per_order"]
SECONDARY = ["tv", "uncovered", "w1_idle_weighted_min"]
COLS = ["family", "scenario", "level", "model", "metric", "n", "nearest_mean", "model_mean", "mean", "lo", "hi",
        "pct_of_nearest", "p_holm", "established", "equivalence", "class"]
TRAINING = {   # final training runs (DECISIONS.md, X3 to X5); the text columns restate the decision log and fidelity notes
    "xu": ("avaliacao/20261103-1021-training-xu",
           "fixed budget of 200 peaks per seed (X3 ruling); validation curve every 25 peaks, flat from 25 on; value table "
           "mean absolute change between checkpoints 0.077 to 0.018 (G6)",
           "none at decision time: a value table by H3 resolution-8 zone and 5-min slot, learned offline from 200 peaks "
           "under nearest courier"),
    "li": ("avaliacao/20261103-1449-training-li",
           "fixed budget of 200 interacting peaks per seed (X3 ruling); validation curve every 25 peaks",
           "expected pickups over the next 30 min by zone from the demand model (code: `models/li_meanfield.py`, "
           "`expected_pickups(t, t + 1800)`), for the destination potential of Eq. 3, with the open orders and couriers"),
    "jahanshahi": ("avaliacao/20261103-1449-training-dqn",
                   "fixed budget of 200 interacting peaks per seed (X3 ruling), epsilon 1.0 to 0.05 over the first 100; "
                   "validation curve every 25 peaks",
                   "none: the only input is each pair's expected delivery time delta (Eq. 1)"),
    "auad": ("avaliacao/20261103-2154-training-auad",
             "200 peaks per seed with the theta_best gate after each (Algorithm 1); configuration alpha 1e-7, n = 1000, "
             "memory 3000 from the paper's grid on training seed 1 (G6)",
             "none: 14 raw state counts (active and open orders per courier, deadline buckets, couriers with no offer, "
             "mean restaurant-to-customer distance)"),
    "jusup": ("avaliacao/20261104-0040-training-jusup",
              "early stopping on the validation objective, at most 1,000 epochs (stops at 361 to 727, X5)",
              "expected orders per zone and 20-min step from the demand model, and the idle courier mass per zone"),
    "forecast": (None, "not learned",
                 "the rates of Ozkan and Ward's Remark 3 from the demand model: expected pickups per minute by restaurant "
                 "zone and expected drop-offs per minute by customer zone, per 15-min bin"),
}


OTHER_RUNS = {   # training runs behind each final model that the final run's wall hours leave out (DECISIONS.md)
    "xu": "the final run is the curve re-run with the planner of Eqs. 6-8 (92 min, a pause for the core limit inside); "
          "an earlier run failed at its end and lost its 1,000 collection episodes (time not recorded)",
    "li": "none recorded",
    "jahanshahi": "a first configuration was stopped at about 11 min per peak (time not recorded; X3)",
    "auad": "first training with scaled features, discarded (5.26 h); configuration grid on training seed 1 (1.04 h)",
    "jusup": "two earlier trainings superseded by objective fixes (0.32 h and 0.68 h)",
}


def sign_agreement(secondary_mean, w1_mean):
    """Sign agreement of a secondary difference with the W1 difference; an exact zero has no sign."""
    if secondary_mean == 0 or w1_mean == 0:
        return "no sign"
    return "agrees" if np.sign(secondary_mean) == np.sign(w1_mean) else "disagrees"


def mean_ci(x, key):
    """Mean over seeds with its 95% percentile bootstrap interval (the pre-registered bootstrap, keyed)."""
    c = paired_contrast(np.asarray(x, float), np.zeros(len(x)), contrast_rng(*key))
    return c["mean"], c["lo"], c["hi"]


def second_hour_split(runs, cl):
    """G8 verdict A1 (descriptive): on every undoing Q2 cell, the second-hour W1 (minutes 60 to 119 after the cluster
    appears; 180 to 239 for the meet-up) of the model and of nearest courier, on the cell and from the scattered start
    at the same clock minutes, same supply, behavior and seeds; and the excess over nearest courier on the cell, from
    the scattered start, and the difference of the two (paired by seed)."""
    out = []
    for x in cl[(cl.question == "Q2") & cl["class"].str.startswith("undoes")].to_dict("records"):
        s, lvl, m = x["scenario"], x["level"], x["model"]
        sec = lambda g: np.array([window(g.loc[k, "w1_rule_series"], s, 60, 120) for k in runs.seeds])
        v = {"model": sec(runs.rows(s, lvl, "fitted", m, 1.0)), "nearest": sec(runs.rows(s, lvl, "fitted", "nearest")),
             "model_scattered": sec(runs.rows("scattered", lvl, "fitted", m, 1.0)),
             "nearest_scattered": sec(runs.rows("scattered", lvl, "fitted", "nearest"))}
        v["excess_cell"] = v["model"] - v["nearest"]
        v["excess_scattered"] = v["model_scattered"] - v["nearest_scattered"]
        v["excess_beyond_scattered"] = v["excess_cell"] - v["excess_scattered"]
        row = {"scenario": s, "level": lvl, "model": m, "class": x["class"], "n": len(runs.seeds)}
        for k, arr in v.items():
            row[f"{k}_mean"], row[f"{k}_lo"], row[f"{k}_hi"] = mean_ci(arr, ((s, lvl, "second_hour", k), m, "A1"))
        out.append(row)
    return pd.DataFrame(out)


def km_split(runs):
    """G8 verdict A2 (descriptive): km ridden without an order, split into the ride to the restaurant
    (extra_km_per_order - idle_km_per_order) and idle riding (idle_km_per_order), per model and primary cell."""
    out = []
    for s, lvl in Q1 + Q2:
        base = runs.rows(s, lvl, "fitted", "nearest")
        for m in NINE:
            mod = runs.rows(s, lvl, "fitted", m, 1.0)
            row = {"scenario": s, "level": lvl, "model": m, "n": len(runs.seeds)}
            for name, f in (("pickup_km_per_order", lambda g: g.extra_km_per_order - g.idle_km_per_order),
                            ("idle_km_per_order", lambda g: g.idle_km_per_order)):
                a, b = f(mod), f(base)
                c = paired_contrast(a, b, contrast_rng((s, lvl, "fitted", 1.0 if m in ARM_C else None), m, name))
                row.update({f"{name}_model": float(a.mean()), f"{name}_nearest": float(b.mean()),
                            f"{name}_diff": c["mean"], f"{name}_lo": c["lo"], f"{name}_hi": c["hi"]})
            out.append(row)
    return pd.DataFrame(out)


def evening(runs, cases=None):
    """G8 verdict A3 (exploratory, defined after the results were seen, outside every family, no test): mean W1 over
    20:00 to 20:59 (minutes 180 to 239) per model on the clustered starts, paired with nearest courier by seed.
    `cases` lists (model, obedience); the default is the nine models with arm C at 100%."""
    cases = cases or [(m, 1.0 if m in ARM_C else None) for m in NINE]
    out = []
    for s in ("big_cluster", "three_clusters", "mixed"):
        for lvl in ("tight", "normal", "loose"):
            base = runs.rows(s, lvl, "fitted", "nearest")
            b = np.array([window(base.loc[k, "w1_rule_series"], s, 180, 240) for k in runs.seeds])
            for m, ob in cases:
                mod = runs.rows(s, lvl, "fitted", m, 1.0 if ob is None else ob)
                a = np.array([window(mod.loc[k, "w1_rule_series"], s, 180, 240) for k in runs.seeds])
                c = paired_contrast(a, b, contrast_rng((s, lvl, "fitted", ob), m, "w1_2000_2059"))
                out.append({"scenario": s, "level": lvl, "model": m, "obedience": ob, "n": len(runs.seeds),
                            "model_mean": float(a.mean()),
                            "nearest_mean": float(b.mean()), "mean": c["mean"], "lo": c["lo"], "hi": c["hi"],
                            "reading": "exploratory"})
    return pd.DataFrame(out)


def pct(df):
    return 100.0 * df["mean"] / df["nearest_mean"]


def described(runs, s, lvl, m, metric, family="descriptive"):
    """A descriptive contrast with the pre-registered bootstrap and t-test, outside every family."""
    base = runs.rows(s, lvl, "fitted", "nearest")
    mod = runs.rows(s, lvl, "fitted", m, 1.0)
    c = paired_contrast(mod[metric], base[metric], contrast_rng((s, lvl, "fitted", 1.0 if m in ARM_C else None), m, metric))
    return {"family": family, "scenario": s, "level": lvl, "model": m, "metric": metric, "n": c["n"],
            "nearest_mean": float(base[metric].mean()), "model_mean": float(mod[metric].mean()), "mean": c["mean"],
            "lo": c["lo"], "hi": c["hi"], "p_holm": "descriptive", "established": "descriptive",
            "equivalence": "not read: descriptive", "class": "descriptive"}


def with_class(con, cl, question):
    k = cl[cl.question == question].set_index(["scenario", "level", "model"])["class"]
    con = con.copy()
    con["class"] = [k.get((r.scenario, r.level, r.model), "") for r in con.itertuples()]
    return con


def cost_reading(mean, hi, p_holm):
    """Q3 per cell, the cost branch of the joint reading applied to every primary cell (pre-registration section 5)."""
    if hi < P90_SESOI_MIN:
        return "no delivery cost"
    if p_holm < 0.05 and mean >= P90_SESOI_MIN:
        return "delivery cost"
    return "cost unresolved"


def fmt(r):
    return f"{r['mean']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]"


def table(df, extra=()):
    rows = []
    for r in df.to_dict("records"):
        p = r["p_holm"]
        rows.append({"cell": f"{r['scenario']}, {r['level']}", "model": r["model"], "metric": r["metric"],
                     "difference [95% CI]": fmt(r), "% of nearest": f"{r['pct_of_nearest']:+.1f}%", "n": int(r["n"]),
                     "p (Holm)": p if isinstance(p, str) else f"{p:.3g}", **{e: r.get(e, "") for e in extra}})
    return md(pd.DataFrame(rows), index=False)


def training_budgets():
    rows, curves = [], []
    for m, (folder, criterion, info) in TRAINING.items():
        if folder is None:
            rows.append({"model": m, "training_seeds": "not learned", "episodes_per_seed": "not learned",
                         "wall_hours": "not learned", "wall_hours_scope": "not learned", "other_runs": "not learned",
                         "convergence": criterion, "demand_information": info, "folder": "none (not learned)"})
            continue
        run = json.loads((ROOT / folder / "run.json").read_text())
        eps = run.get("episodes", f"at most {run.get('max_epochs')} epochs")
        rows.append({"model": m, "training_seeds": " ".join(map(str, run["training_seeds"])), "episodes_per_seed": eps,
                     "wall_hours": round(run["total_wall_s"] / 3600, 2), "wall_hours_scope": "final run only",
                     "other_runs": OTHER_RUNS[m], "convergence": criterion,
                     "demand_information": info, "folder": folder})
        c = pd.read_csv(ROOT / folder / "curve.csv")
        if "episodes" not in c:
            c["episodes"] = "final"
        num = [k for k in c.columns if k not in ("training_seed", "episodes", "scenario", "seed")]
        g = c.groupby(["training_seed", "episodes", "scenario"])
        a = g[num].mean().add_suffix("_mean").reset_index()
        a["validation_seeds"] = g.seed.nunique().to_numpy()
        curves.append(a.assign(model=m))
    return pd.DataFrame(rows), pd.concat(curves, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    for name in ("analysis", "full_dir", "ties", "out"):
        ap.add_argument(name, type=Path)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--first", type=Path, required=True)
    a = ap.parse_args()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    con = pd.read_csv(a.analysis / "contrasts.csv", keep_default_na=False, na_values=[""])
    cl = pd.read_csv(a.analysis / "classes.csv")
    fr = pd.read_csv(a.analysis / "contrasts_e2_fresh.csv", keep_default_na=False, na_values=[""])
    clf = pd.read_csv(a.analysis / "classes_e2_fresh.csv")
    full = load(a.full_dir)
    runs = Runs(full, a.n)
    fresh = Runs(full, a.n, sets=("fresh_q2",), first=FRESH0)
    for d in (con, fr):
        d["equivalence"] = d["equivalence"].fillna("").replace("", "not read: established")
        d["pct_of_nearest"] = pct(d)

    # Q1 (E1) with the DQN as a descriptive row
    q1 = with_class(con[con.family == "E1"], cl, "Q1")
    dqn = pd.DataFrame([described(runs, s, lvl, "jahanshahi", met) for met in (W1, P90) for s, lvl in Q1])
    dqn["pct_of_nearest"] = pct(dqn)
    q1 = pd.concat([q1, dqn], ignore_index=True)[COLS]
    q1.to_csv(out / "q1_e1.csv", index=False)

    # Q2 (E2), the frozen seeds, and the frozen three on the fresh block (R4)
    q2 = with_class(con[con.family == "E2"], cl, "Q2")
    dq2 = pd.DataFrame([described(runs, s, lvl, "jahanshahi", met) for met in (W160, P90) for s, lvl in Q2])
    dq2["pct_of_nearest"] = pct(dq2)
    q2 = pd.concat([q2, dq2], ignore_index=True)[COLS]                 # the DQN as a descriptive row (G8 verdict D1)
    q2.to_csv(out / "q2_e2.csv", index=False)
    q2f = with_class(fr[fr.model.isin(FROZEN3)], clf, "Q2")[COLS + ["seeds"]]
    q2f.to_csv(out / "q2_e2_fresh.csv", index=False)

    # Q2 time to undo (median, IQR, censored count), second-hour check, unassigned share; both seed sets
    ud = []
    for f, r, seeds in (("undo.csv", runs, f"{runs.seeds[0]}-{runs.seeds[-1]}"),
                        ("undo_e2_fresh.csv", fresh, f"{fresh.seeds[0]}-{fresh.seeds[-1]}")):
        u = pd.read_csv(a.analysis / f).assign(seeds=seeds)
        u["unassigned_over_30min_share_model"] = [float(r.rows(x.scenario, x.level, "fitted", x.model, 1.0)
                                                        .unassigned_over_30min_share.mean()) for x in u.itertuples()]
        u["unassigned_over_30min_share_nearest"] = [float(r.rows(x.scenario, x.level, "fitted", "nearest")
                                                          .unassigned_over_30min_share.mean()) for x in u.itertuples()]
        ud.append(u)
    ud = pd.concat(ud, ignore_index=True)
    ud["second_hour_check"] = (ud.second_hour_check.astype(object).where(ud.second_hour_check.notna(), "")
                               .replace("", "not read (cell not classed as undoing)"))
    ud.to_csv(out / "q2_undo.csv", index=False)
    ds = pd.read_csv(a.analysis / "descriptive.csv")
    ds = ds[ds.part.isin(["ride", "explore"])]
    ds.to_csv(out / "q2_descriptive.csv", index=False)

    # Q3: descriptive contrasts per model on the primary cells
    q3 = pd.DataFrame([described(runs, s, lvl, m, met) for met in Q3 for s, lvl in Q1 + Q2 for m in NINE])
    q3["pct_of_nearest"] = pct(q3)
    q3 = q3[COLS]
    q3.to_csv(out / "q3_costs.csv", index=False)
    q3s = []                                            # G8 verdict D1: one row per model, every metric
    for m in NINE:
        row = {"model": m}
        for met in Q3:
            g = q3[(q3.model == m) & (q3.metric == met)]
            row[f"{met} mean"] = g["mean"].mean()
            row[f"{met} range"] = f"{g['mean'].min():+.3f} to {g['mean'].max():+.3f}"
            row[f"{met} cells above 0"] = int((g.lo > 0).sum())
            row[f"{met} cells below 0"] = int((g.hi < 0).sum())
        un = [(float(runs.rows(s, lvl, "fitted", m, 1.0).unassigned_over_30min_share.mean()), f"{s}, {lvl}")
              for s, lvl in Q1 + Q2]
        row["largest_unassigned_over_30min_share"], row["cell_of_largest"] = max(un)
        if row["largest_unassigned_over_30min_share"] == 0:
            row["cell_of_largest"] = "none: 0 in every cell"
        q3s.append(row)
    q3s = pd.DataFrame(q3s)
    q3s.to_csv(out / "q3_summary.csv", index=False)
    q3md = pd.DataFrame({"model": q3s.model, **{
        lab: [f"{r[f'{met} mean']:+.3f} ({r[f'{met} range']}; {r[f'{met} cells above 0']} up, {r[f'{met} cells below 0']} down)"
              for _, r in q3s.iterrows()]
        for met, lab in ((P90, "p90 (min)"), ("mean_c2d_min", "mean order to door (min)"), ("late_rate", "late share"),
                         ("extra_km_per_order", "km without an order per order"), ("idle_km_per_order", "idle km per order"))},
        "largest share unassigned >30 min": [f"{100 * v:.1f}% ({c})" for v, c in
                                             zip(q3s.largest_unassigned_over_30min_share, q3s.cell_of_largest)]})
    a1 = second_hour_split(runs, cl)
    a1.to_csv(out / "a1_second_hour_split.csv", index=False)
    a2 = km_split(runs)
    a2.to_csv(out / "a2_km_split.csv", index=False)
    a3 = evening(runs)
    a3.to_csv(out / "a3_evening_2000_2059.csv", index=False)

    # secondary: agreement of W1 with TV, uncovered share and idle-weighted W1 over the established W1 cells
    sec = []
    for fam, metric in (("E1", W1), ("E2", W160)):
        est = con[(con.family == fam) & (con.metric == metric) & (con.established.astype(str) == "True")]
        for r in est.itertuples():
            for k in SECONDARY:
                d = described(runs, r.scenario, r.level, r.model, k)
                sec.append({"family": fam, "w1_metric": metric, "scenario": r.scenario, "level": r.level,
                            "model": r.model, "w1_mean": r.mean, "secondary": k, "secondary_mean": d["mean"],
                            "secondary_lo": d["lo"], "secondary_hi": d["hi"],
                            "sign_agreement": sign_agreement(d["mean"], r.mean)})
    sec = pd.DataFrame(sec, columns=["family", "w1_metric", "scenario", "level", "model", "w1_mean", "secondary",
                                     "secondary_mean", "secondary_lo", "secondary_hi", "sign_agreement"])
    sec.to_csv(out / "secondary_agreement.csv", index=False)
    agree = (sec.pivot_table(index=["family", "secondary"], columns="sign_agreement", values="model", aggfunc="count",
                             fill_value=0).reset_index() if len(sec) else
             pd.DataFrame(columns=["family", "secondary", "agrees", "disagrees", "no sign"]))

    # profile: cells per class on Q1, Q2 and Q3 (Q3 = the cost reading on p90 in every primary cell)
    pr = pd.read_csv(a.analysis / "profile.csv")
    f1 = pd.read_csv(a.first / "contrasts.csv")
    f1 = f1[(f1.family == "F1") & (f1.metric == "p90")].set_index(["scenario", "level", "model"])
    pc = []
    for r in pr.itertuples():
        for q, js in (("Q1", r.q1_classes), ("Q2", r.q2_classes)):
            for k, v in json.loads(js).items():
                pc.append({"model": r.model, "question": q, "class": k, "cells": int(v)})
    cost = [(x.model, cost_reading(x.p90_mean, x.p90_hi, x.p90_p_holm)) for x in cl.itertuples()]
    cost += [(m, cost_reading(f1.loc[(s, lvl, m), "mean"], f1.loc[(s, lvl, m), "hi"], f1.loc[(s, lvl, m), "p_holm"]))
             for m in FROZEN3 for s, lvl in Q1]
    for (m, k), v in pd.Series([k for _, k in cost], index=[m for m, _ in cost]).groupby(level=0).value_counts().items():
        pc.append({"model": m, "question": "Q3", "class": k, "cells": int(v)})
    for (m, k), v in clf.groupby("model")["class"].value_counts().items():          # R4: the frozen three, fresh block
        pc.append({"model": m, "question": "Q2 fresh block (R4)", "class": k, "cells": int(v)})
    fc = pd.Series([cost_reading(x.p90_mean, x.p90_hi, x.p90_p_holm) for x in clf.itertuples()], index=clf.model)
    for (m, k), v in fc.groupby(level=0).value_counts().items():
        pc.append({"model": m, "question": "Q3 fresh block (R4)", "class": k, "cells": int(v)})
    pc = pd.DataFrame(pc)
    pc.to_csv(out / "profile_counts.csv", index=False)

    ties = pd.read_csv(a.ties / "zhu_ties.csv")
    ties.to_csv(out / "zhu_ties.csv", index=False)
    tb, lc = training_budgets()
    tb.to_csv(out / "training_budgets.csv", index=False)
    lc.to_csv(out / "learning_curves.csv", index=False)
    je = pd.read_csv(ROOT / TRAINING["jusup"][0] / "training.csv")      # Jusup: validation objective per epoch
    je = je.groupby(["training_seed", "epoch"], as_index=False)[["valid_objective", "valid_reward"]].first()
    je.to_csv(out / "learning_curves_jusup_epochs.csv", index=False)

    eq = pd.concat([con, fr[fr.model.isin(FROZEN3)].assign(family="E2-fresh, frozen three only (R4)")])
    eq = eq.groupby("family").equivalence.value_counts().unstack(fill_value=0)
    L = ["# Paper A numbers at G8 (E1, E2 and the R4 fresh seed block)", "", ACK, "",
         f"Seeds {runs.seeds[0]} to {runs.seeds[-1]} (n = {a.n}); the frozen four's Q2 cells also on the fresh seed block "
         f"{fresh.seeds[0]} to {fresh.seeds[-1]} (R4). Differences are model minus nearest courier, lower is better; "
         "95% percentile bootstrap intervals; Holm within each family. Arm C (Zhu, Jusup) at 100% obedience, an upper "
         "bound. The DQN row is descriptive. Q4 (E3, E4, E5) is added to this file when phases 3 and 4 finish.", "",
         "## Q1, prevent (E1)", "", table(q1, ("class", "equivalence")), "",
         "## Q2, undo (E2, seeds as pre-registered)", "", table(q2, ("class", "equivalence")), "",
         "## Q2, frozen three on the fresh seed block (R4; the numbers Paper A quotes for these models on Q2)", "",
         "Holm over the 160 contrasts of E2 with the frozen three's rows from the fresh block.", "",
         table(q2f, ("class", "equivalence")), "",
         "## Q2, time to undo, second-hour check and unassigned share", "",
         "Time to undo has no pre-registered smallest effect, so it gets no equivalence reading (R3).", "",
         md(ud[["seeds", "scenario", "level", "model", "class", "time_to_undo_median", "time_to_undo_q25",
                "time_to_undo_q75", "censored_count", "second_hour_check", "unassigned_over_30min_share_model",
                "unassigned_over_30min_share_nearest"]].round(3), index=False), "",
         "## Q2, descriptive meet-ups (exploratory median meet-up and ride variant)", "", md(ds, index=False), "",
         "## Q3, cost (descriptive, primary cells)", "",
         "Per model and metric over the 16 primary cells (6 Q1, 10 Q2): the mean of the cell differences, their range, and "
         "the cells whose 95% interval lies above or below 0. Every cell: `q3_costs.csv`.", "",
         md(q3md, index=False), "",
         "Each cell: the mean over the 16 primary cells of the model-minus-nearest difference, its range over the cells, "
         "and the cells whose 95% interval lies above (up) or below (down) 0. Wherever Paper A quotes Xu et al., the "
         "unassigned share goes beside it (G8 verdict, ruling 6).", "",
         "## A1, second-hour split on the undoing cells (descriptive)", "",
         "W1 over the second hour after the cluster appears (minutes 60 to 119; 180 to 239 for the meet-up), mean and 95% "
         "interval over seeds: the model and nearest courier on the cell, and both from the scattered start at the same "
         "clock minutes, supply and seeds. Excess = model minus nearest courier, paired by seed; the last column is the "
         "part of the excess on the cell beyond the excess the model already carries from a spread start. "
         "Every interval: `a1_second_hour_split.csv`.", "",
         md(pd.DataFrame({"cell": [f"{r.model}, {r.scenario}, {r.level}" for r in a1.itertuples()],
                          **{k: [f"{getattr(r, k + '_mean'):.2f} [{getattr(r, k + '_lo'):.2f}, {getattr(r, k + '_hi'):.2f}]"
                                 for r in a1.itertuples()]
                             for k in ("model", "nearest", "model_scattered", "nearest_scattered", "excess_cell",
                                       "excess_scattered", "excess_beyond_scattered")}}), index=False)
         if len(a1) else "No Q2 cell is classed as undoing.", "",
         "## A2, km ridden without an order: the ride to the restaurant and idle riding (descriptive)", "",
         "Per model, the mean over the 16 primary cells of the model-minus-nearest difference per delivered order. Arm C "
         "models at 100% obedience: their commands replace the couriers' own idle moves, the ride back to the preferred "
         "area included. Every cell, with 95% intervals: `a2_km_split.csv`.", "",
         md(a2.groupby("model", sort=False)[["pickup_km_per_order_diff", "idle_km_per_order_diff",
                                              "pickup_km_per_order_nearest", "idle_km_per_order_nearest"]].mean()
            .rename(columns={"pickup_km_per_order_diff": "ride to restaurant, difference",
                             "idle_km_per_order_diff": "idle riding, difference",
                             "pickup_km_per_order_nearest": "ride to restaurant, nearest courier",
                             "idle_km_per_order_nearest": "idle riding, nearest courier"})), "",
         "## A3, W1 over 20:00 to 20:59 on the clustered starts (exploratory)", "",
         "Exploratory: defined after the results were seen (G8 verdict, ruling 5), outside every family, no test. Mean "
         "W1 over minutes 180 to 239, model minus nearest courier paired by seed, with 95% intervals. The Q2 window covers "
         "only the first hour, and the time to undo stops at the first crossing.", "",
         md(pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in a3.itertuples()], "model": a3.model,
                          "model W1": a3.model_mean.round(2), "nearest W1": a3.nearest_mean.round(2),
                          "difference [95% CI]": [fmt(r) for r in a3.to_dict("records")]}), index=False), "",
         "## Secondary: does W1 agree with total variation, uncovered share and idle-weighted W1?", "",
         "Sign agreement over the established W1 cells. On Q2 the W1 metric is the 60-min window and the secondary "
         "metrics are evening means.", "", md(agree, index=False), "",
         "## Profile: cells per class", "", "Q3 is the cost reading of the joint reading on p90, applied to every primary "
         "cell: no delivery cost when the interval's upper end is below +1 min, a delivery cost when an established "
         "difference is at least +1 min, unresolved otherwise.", "",
         *[x for q in ("Q1", "Q2", "Q3", "Q2 fresh block (R4)", "Q3 fresh block (R4)")
           for x in (f"**{q}**", "", md(pc[pc.question == q].pivot_table(
             index="model", columns="class", values="cells", aggfunc="sum", fill_value=0).astype(int)), "")],
         "## R3 equivalence reading, counts per family", "", md(eq), "",
         "## Zhu with random partition ties (post-freeze sensitivity, outside every family)", "", md(ties, index=False), "",
         "## Training budgets", "", md(tb, index=False), "",
         "Wall hours are the final run's only; `other_runs` lists the runs behind it. Learning curves (means over the "
         "validation seeds): `learning_curves.csv`; Jusup et al.'s validation objective per epoch: "
         "`learning_curves_jusup_epochs.csv`.", "", ACK]
    (out / "paper-numbers-G8.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
