"""Package C, parts 1 to 4 (preregistration-addendum-C.md, committed at ed05df2 before any of their episodes).

Usage: python scripts/package_c_analysis.py <e6|stay|noise|ashkrof> <out_dir> --full <full_dir> --pkgc <pkgc_dir>
           --pilot <pilot_dir> --g8 <g8_results_dir> [--fitted-fit <behavior_fit_dir>] --n 150 [--n-explore 30]

  e6       confirmatory. 144 contrasts (8 tested models x 9 clustered cells x {W1 over 60 min, p90}), Holm at 0.05
           within E6, smallest effects as in E2 (10% of nearest courier's fitted pilot mean; 1.0 min for p90). The joint
           class with p90 from E6, the R3 reading, the time to undo against the fitted scattered rows of the full runs,
           the second-hour check, the DQN row, and the secondary W1 over 20:00 to 20:59. Each class sits beside the class
           Paper A quotes for the same cell from E2 (the new five) or E2-fresh (the frozen three, R4).
  stay     exploratory. stay - nearest, zhu - stay and jusup - stay, paired by seed, in the 16 primary cells.
  noise    exploratory. The four models with noisy demand input against nearest courier, beside the same contrasts
           with the true input at the same seeds; joint class with Holm within the E1-shaped and E2-shaped sets.
  ashkrof  exploratory. The eight tested models under the Ashkrof setting beside the fitted behavior at the same seeds,
           read the same way, and the recalibrated values with their moments.

Differences are model minus reference, paired by seed, lower is better; 95% percentile bootstrap over seeds (10,000
resamples, generator seed 20261103 keyed by the contrast). Every number written is an aggregate over seeds.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.analysis_extension import (FROZEN3, FROZEN_METRICS, LABEL, NEW5, P90, Q1, Q2, W160, W1, deltas,  # noqa: E402
                                    equivalence, load, md, same, start_min, window)
from sim.stats import P90_SESOI_MIN, W1_SESOI_SHARE, classify, contrast_rng, holm, paired_contrast, time_to_undo  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
TESTED8 = [*NEW5, *FROZEN3]
CLUSTERED = Q2[:9]
PRIMARY = Q1 + Q2
ACTIVE = ("zhu", "jusup", "stay")                     # policies with commands, run at 100% obedience in package C
EVENING = "w1_2000_2059"
FULL_SETS = ("new", "frozen_rerun")


def ob(m):
    return 1.0 if m in ACTIVE else None


class Cells:
    """Rows of one cell by (scenario, level, behavior, model), indexed by seed; active policies at 100% obedience. A
    cell missing any seed stops the analysis."""

    def __init__(self, ep, seeds, sets=None):
        ep = ep[ep.seed.isin(seeds)]
        if sets is not None:
            ep = ep[ep.set.isin(list(sets))]
        ep = ep.assign(ob=ep.obedience.fillna(-1.0))
        self.g = {k: g.set_index("seed").sort_index() for k, g in ep.groupby(["scenario", "level", "behavior", "model", "ob"])}
        self.seeds = list(seeds)

    def rows(self, scenario, level, behavior, model):
        o = 1.0 if model in ACTIVE else -1.0
        g = self.g.get((scenario, level, behavior, model, o))
        if g is None or list(g.index) != self.seeds:
            raise SystemExit(f"cell {scenario} {level} {behavior} {model} is not complete "
                             f"({0 if g is None else len(g)} of {len(self.seeds)} seeds)")
        return g


def series(g, k):
    """One episode's per-minute W1 series; a missing minute stops the analysis (none in the runs read so far), since
    the time to undo and the window means would otherwise skip it silently."""
    x = np.asarray(g.loc[k, "w1_rule_series"], float)
    if len(x) != 240 or not np.isfinite(x).all():
        raise SystemExit(f"missing minute in w1_rule_series: {g.loc[k, 'scenario']} {g.loc[k, 'level']} "
                         f"{g.loc[k, 'model']} seed {k} ({len(x)} minutes, {int((~np.isfinite(x)).sum())} not finite)")
    return x


def values(g, metric, scenario, seeds):
    if metric == EVENING:                             # 20:00 to 20:59 is minutes 180 to 239 of the evening
        s0 = start_min(scenario)
        return np.array([window(series(g, k), scenario, 180 - s0, 240 - s0) for k in seeds])
    return g.loc[seeds, metric].to_numpy(float)


def pair(a, b, metric, scenario, seeds, key):
    return paired_contrast(values(a, metric, scenario, seeds), values(b, metric, scenario, seeds), contrast_rng(*key))


def finish(con):
    con["established"] = con.p_holm < 0.05
    con["at_least_sesoi"] = con["mean"].abs() >= con.delta
    con["lower_at_least_sesoi"] = -con["mean"] >= con.delta
    con["equivalence"] = equivalence(con)
    return con


def class_rows(con, question_of):
    """One joint class per cell and model from its W1 row (W1 on Q1 cells, W1 over 60 min on Q2 cells) and p90 row."""
    out = []
    for (s, lvl, m), g in con.groupby(["scenario", "level", "model"], sort=False):
        q = question_of(s)
        w = g[g.metric == (W1 if q == "Q1" else W160)].iloc[0].to_dict()
        p = g[g.metric == P90].iloc[0].to_dict()
        out.append({"question": q, "scenario": s, "level": lvl, "model": m,
                    "class": LABEL[q][classify(w, p, w["delta"])], "w1_mean": w["mean"], "w1_lo": w["lo"], "w1_hi": w["hi"],
                    "w1_p_holm": w["p_holm"], "p90_mean": p["mean"], "p90_hi": p["hi"], "p90_p_holm": p["p_holm"]})
    return pd.DataFrame(out)


def q_of(s):
    return "Q1" if s in ("scattered", "burst") else "Q2"


# ---------------------------------------------------------------- part 1: E6

def cluster_read(c, beh, full, dl, family):
    """The E6 tables for one behavior setting on the 9 clustered cells (E6; reused by C6 and its references): 144
    contrasts with Holm within them, the joint classes, the time to undo against the fitted scattered rows of the full
    runs with the second-hour check, the W1 over 20:00 to 20:59, and the DQN row."""
    rows = []
    for m in TESTED8:
        for s, lvl in CLUSTERED:
            base, mod = c.rows(s, lvl, beh, "nearest"), c.rows(s, lvl, beh, m)
            for met in (W160, P90):
                pc = pair(mod, base, met, s, c.seeds, ((s, lvl, beh, ob(m)), m, met))
                delta = P90_SESOI_MIN if met == P90 else dl[(s, lvl, "fitted")][W160]
                rows.append({"family": family, "scenario": s, "level": lvl, "behavior": beh, "model": m,
                             "obedience": ob(m), "metric": met, "delta": delta, "model_mean": float(mod[met].mean()),
                             "nearest_mean": float(base[met].mean()), **pc})
    con = pd.DataFrame(rows)
    if len(con) != 144:
        raise SystemExit(f"{len(con)} contrasts in {family}, the addendum fixes 144")
    con["p_holm"] = holm(con.p.to_numpy())
    con = finish(con)
    cl = class_rows(con, q_of)

    cls = cl.set_index(["scenario", "level", "model"])["class"]
    und = []
    for s, lvl in CLUSTERED:
        res = {}
        for m in ("nearest", *TESTED8, "jahanshahi"):
            r = c.rows(s, lvl, beh, m)
            sc = full.rows("scattered", lvl, "fitted", m)
            t = np.array([time_to_undo(series(r, k), series(sc, k), start_min=start_min(s)) for k in c.seeds])
            second = np.array([window(series(r, k), s, 60, 120) for k in c.seeds])
            res[m] = (t, t >= 240 - start_min(s), second)
        nt, _, ns = res["nearest"]
        for m, (t, cens, second) in res.items():
            k = cls.get((s, lvl, m), "nearest courier" if m == "nearest" else "descriptive")
            flag = ""
            if k.startswith("undoes"):
                worse = second.mean() - ns.mean() >= dl[(s, lvl, "fitted")]["second_hour"] or np.median(t) > np.median(nt)
                flag = "undoes in the first hour, not after" if worse else "holds after the first hour"
            und.append({"scenario": s, "level": lvl, "model": m, "class": k,
                        "time_to_undo_median": float(np.median(t)), "time_to_undo_q25": float(np.percentile(t, 25)),
                        "time_to_undo_q75": float(np.percentile(t, 75)), "censored_count": int(cens.sum()),
                        "censored_share": float(cens.mean()), "nearest_time_to_undo_median": float(np.median(nt)),
                        "second_hour_w1": float(second.mean()), "nearest_second_hour_w1": float(ns.mean()),
                        "second_hour_check": flag})
    ud = pd.DataFrame(und)

    ev, dq = [], []
    for s, lvl in CLUSTERED:
        base = c.rows(s, lvl, beh, "nearest")
        for m in (*TESTED8, "jahanshahi"):
            mod = c.rows(s, lvl, beh, m)
            pc = pair(mod, base, EVENING, s, c.seeds, ((s, lvl, beh, ob(m)), m, EVENING))
            ev.append({"scenario": s, "level": lvl, "model": m, "n": pc["n"],
                       "model_mean": float(values(mod, EVENING, s, c.seeds).mean()),
                       "nearest_mean": float(values(base, EVENING, s, c.seeds).mean()),
                       "mean": pc["mean"], "lo": pc["lo"], "hi": pc["hi"]})
        j = c.rows(s, lvl, beh, "jahanshahi")
        dq.append({"scenario": s, "level": lvl, "model": "jahanshahi",
                   "w1_60_minus_nearest": float((j[W160] - base[W160]).mean()),
                   "p90_minus_nearest": float((j[P90] - base[P90]).mean())})
    return con, cl, ud, pd.DataFrame(ev), pd.DataFrame(dq)


def e6(e6c, full, dl, g8):
    con, cl, ud, ev, dq = cluster_read(e6c, "indep", full, dl, "E6")
    e2 = pd.read_csv(g8 / "classes.csv")
    e2 = e2[(e2.question == "Q2") & e2.model.isin(NEW5)].assign(e2_source="E2")
    fr = pd.read_csv(g8 / "classes_e2_fresh.csv").assign(e2_source="E2-fresh (R4)")
    ref = pd.concat([e2, fr[fr.model.isin(FROZEN3)]])[["scenario", "level", "model", "class", "e2_source"]]
    if ref.duplicated(["scenario", "level", "model"]).any():
        raise SystemExit("duplicated cells in the Paper A class files")
    cl = cl.merge(ref.rename(columns={"class": "e2_class"}), on=["scenario", "level", "model"], how="left",
                  validate="many_to_one")
    miss = cl[cl.e2_class.isna()]
    if len(miss):
        raise SystemExit(f"Paper A class missing for {len(miss)} cells, e.g. {miss.iloc[0][['scenario', 'level', 'model']].tolist()}")
    cl["changed"] = cl["class"] != cl.e2_class
    return con, cl, ud, ev, dq


# ---------------------------------------------------------------- C6: homes where customers live (exploratory)

def resid(rc, e6c30, full30, dl):
    """C6 beside E6 and the fitted setting at the same seeds, each read with the E6 tables (Holm within its own 144 as a
    reading device), and nearest courier's own W1 over the first hour under the three settings."""
    out = {}
    for name, c, beh in (("resid", rc, "resid"), ("indep", e6c30, "indep"), ("fitted", full30, "fitted")):
        out[name] = cluster_read(c, beh, full30, dl, {"resid": "C6", "indep": "E6 at these seeds",
                                                      "fitted": "fitted, E6 cells at these seeds"}[name])
    con = pd.concat([o[0].assign(setting=k) for k, o in out.items()], ignore_index=True)
    k = ["scenario", "level", "model"]
    cl = out["resid"][1][k + ["class", "w1_mean", "p90_mean"]].rename(
        columns={"class": "class_resid", "w1_mean": "w1_resid", "p90_mean": "p90_resid"})
    for name in ("indep", "fitted"):
        cl = cl.merge(out[name][1][k + ["class", "w1_mean", "p90_mean"]].rename(
            columns={"class": f"class_{name}", "w1_mean": f"w1_{name}", "p90_mean": f"p90_{name}"}), on=k, validate="one_to_one")
    ud = pd.concat([o[2].assign(setting=k_) for k_, o in out.items()], ignore_index=True)
    ev = pd.concat([o[3].assign(setting=k_) for k_, o in out.items()], ignore_index=True)
    ne = pd.DataFrame([{"scenario": s, "level": lvl, **{name: float(c.rows(s, lvl, beh, "nearest")[W160].mean())
                                                         for name, c, beh in (("resid", rc, "resid"), ("indep", e6c30, "indep"),
                                                                              ("fitted", full30, "fitted"))}}
                       for s, lvl in CLUSTERED])
    return con, cl, ud, ev, ne


def resid_md(con, cl, ud, ev, ne, n):
    counts = pd.concat([cl[f"class_{x}"].value_counts().rename(x) for x in ("resid", "indep", "fitted")], axis=1).fillna(0).astype(int)
    counts.index.name = "class"
    und = cl[cl.class_resid.str.startswith("undoes") | cl.class_indep.str.startswith("undoes") | cl.class_fitted.str.startswith("undoes")]
    cell = lambda d: [f"{r.scenario}, {r.level}" for r in d.itertuples()]
    side = pd.DataFrame({"cell": cell(und), "model": und.model,
                         "W1 60 min resid": und.w1_resid.map(lambda v: f"{v:+.2f}"), "class resid": und.class_resid,
                         "W1 60 min indep": und.w1_indep.map(lambda v: f"{v:+.2f}"), "class indep": und.class_indep,
                         "W1 60 min fitted": und.w1_fitted.map(lambda v: f"{v:+.2f}"), "class fitted": und.class_fitted})
    est = con.groupby("setting").agg(contrasts=("p", "size"), established=("established", "sum")).reindex(["resid", "indep", "fitted"])
    pairs = set(zip(und.scenario, und.level, und.model))          # undoing under any setting: shown under all three
    keep = np.array([(r.scenario, r.level, r.model) in pairs for r in ud.itertuples()]) | (ud.model == "nearest").to_numpy()
    u = ud[keep].assign(_first=lambda d: d.model != "nearest").sort_values(["_first", "model", "scenario", "level", "setting"],
                                                                         kind="stable").drop(columns="_first")
    evp = ev.pivot_table(index="model", columns="setting", values="mean", aggfunc="mean")[["resid", "indep", "fitted"]]
    nef = ne.assign(**{x: ne[x].map(lambda v: f"{v:.2f}") for x in ("resid", "indep", "fitted")})
    return ["## C6. Homes where customers live (exploratory, no test; declared after the E6 results were seen)", "",
            f"Setting `resid`: as `indep`, except that each courier's home cell is drawn in proportion to the expected "
            f"drop-offs over 17:00 to 21:00 (the customer side of the demand model, which follows resident population), "
            f"from its own stream keyed by (seed, 42, courier). The 9 clustered cells, ten models, arm C at 100%, seeds 1001 "
            f"to {1000 + n}. Beside E6 (`indep`) and the fitted setting at the same seeds, each read with the E6 tables and "
            "Holm within its own 144 contrasts as a reading device. Differences are model minus nearest courier, in "
            "minutes; lower is better.", "", md(est), "", "Classes (cells of 72):", "", md(counts), "",
            "Cell-model pairs that undo under any of the three settings:", "", md(side, index=False) if len(und) else "None.", "",
            "### Nearest courier's own W1 over the first 60 min (min, mean over the seeds)", "",
            md(nef, index=False), "",
            "### Time to undo and the second-hour check (pairs that undo under any setting, and nearest courier)", "",
            "The time to undo is measured against the same model's scattered start under the fitted setting, for all "
            "three settings (as in E6); the second-hour check applies to the cells classed as undoing.", "",
            md(u[["setting", "scenario", "level", "model", "class", "time_to_undo_median", "censored_count",
                  "nearest_time_to_undo_median", "second_hour_check"]].round(1), index=False), "",
            "### W1 over 20:00 to 20:59, model minus nearest courier, mean of the nine cells", "",
            md(evp.round(2)), "", "The DQN row is descriptive.", "",
            "Every number per cell: `c6_resid_contrasts.csv`, `c6_resid_classes.csv`, "
            "`c6_resid_undo.csv`, `c6_resid_evening.csv`, `c6_resid_nearest.csv`.", ""]



def ci(r, k=""):
    return f"{r['mean' + k]:+.2f} [{r['lo' + k]:+.2f}, {r['hi' + k]:+.2f}]"


def e6_md(con, cl, ud, ev, dq, n):
    est = con[con.established]
    tab = pd.DataFrame([{"contrasts": len(con), "established": int(con.established.sum()),
                         "established decrease of at least delta": int((con.established & con.lower_at_least_sesoi).sum()),
                         "established increase": int((con.established & (con["mean"] > 0)).sum()),
                         "equivalent within delta (R3)": int((con.equivalence == "equivalent within delta").sum()),
                         "inconclusive (R3)": int((con.equivalence == "inconclusive").sum())}])
    counts = cl.pivot_table(index="model", columns="class", values="scenario", aggfunc="count", fill_value=0)
    ch = cl[cl.changed]
    side = pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in cl.itertuples()], "model": cl.model,
                         "W1 over 60 min [95% CI]": [ci({"mean": r.w1_mean, "lo": r.w1_lo, "hi": r.w1_hi}) for r in cl.itertuples()],
                         "p_Holm": cl.w1_p_holm.map(lambda v: f"{v:.3g}"), "p90": cl.p90_mean.map(lambda v: f"{v:+.2f}"),
                         "p90 upper 95%": cl.p90_hi.map(lambda v: f"{v:+.2f}"), "p90 p_Holm": cl.p90_p_holm.map(lambda v: f"{v:.3g}"),
                         "E6 class": cl["class"], "Paper A class (source)": [f"{r.e2_class} ({r.e2_source})" for r in cl.itertuples()]})
    u = ud[ud["class"].str.startswith("undoes") | (ud.model == "nearest")]
    L = ["## Part 1. E6: clustered starts with preferred areas independent of the start (confirmatory)", "",
         f"Behavior `indep`, seeds 1001 to {1000 + n} (n = {n}), arm C at 100% obedience. 144 contrasts, Holm at 0.05 "
         "within E6; smallest effects as in E2. Differences are model minus nearest courier, in minutes; lower is better.",
         "", md(tab, index=False), "",
         f"{len(est)} established contrasts. Classes by model:", "", md(counts), "",
         f"Cells whose class differs from the class Paper A quotes (E2, or E2-fresh for the frozen three): {len(ch)} of {len(cl)}.", "",
         md(side[cl.changed.to_numpy()], index=False) if len(ch) else "None.", "",
         "Every cell: `c1_e6_classes.csv`; every contrast with its R3 reading: `c1_e6_contrasts.csv`.", "",
         "### Time to undo and the second-hour check (cells classed as undoing, and nearest courier)", "",
         "Against the same model, obedience, supply level and seed from the scattered start (fitted rows of the full runs).", "",
         md(u[["scenario", "level", "model", "class", "time_to_undo_median", "time_to_undo_q25", "time_to_undo_q75",
               "censored_count", "nearest_time_to_undo_median", "second_hour_w1", "nearest_second_hour_w1",
               "second_hour_check"]].rename(columns={"nearest_time_to_undo_median": "nearest median",
                                                     "second_hour_w1": "second-hour W1", "nearest_second_hour_w1": "nearest second-hour W1"})
            .round(2), index=False) if len(u) else "None.", "",
         "### DQN (descriptive)", "", md(dq.round(3), index=False), "",
         "### Pre-registered secondary: W1 over 20:00 to 20:59, model minus nearest courier", "",
         md(ev.assign(cell=[f"{r.scenario}, {r.level}" for r in ev.itertuples()],
                      diff=[ci(r) for r in ev.to_dict("records")])
            .pivot(index="model", columns="cell", values="diff")), ""]
    return L


# ---------------------------------------------------------------- part 2: stay

STAY_METRICS = [W1, W160, EVENING, P90, "extra_km_per_order"]


def stay(stc, full):
    out = []
    for s, lvl in PRIMARY:
        st, near = stc.rows(s, lvl, "fitted", "stay"), full.rows(s, lvl, "fitted", "nearest")
        zhu, jus = full.rows(s, lvl, "fitted", "zhu"), full.rows(s, lvl, "fitted", "jusup")
        for name, a, b in (("stay - nearest", st, near), ("zhu - stay", zhu, st), ("jusup - stay", jus, st)):
            for met in STAY_METRICS:
                c = pair(a, b, met, s, stc.seeds, ((s, lvl, "fitted", 1.0), name, met))
                out.append({"scenario": s, "level": lvl, "contrast": name, "metric": met, "n": c["n"],
                            "a_mean": float(values(a, met, s, stc.seeds).mean()),
                            "b_mean": float(values(b, met, s, stc.seeds).mean()),
                            "mean": c["mean"], "lo": c["lo"], "hi": c["hi"]})
    return pd.DataFrame(out)


def stay_md(st, n):
    L = ["## Part 2. Stay without commands: suppression against repositioning (exploratory, no test)", "",
         f"Fitted behavior, seeds 1001 to {1000 + n} (n = {n}); `stay` and arm C at 100% obedience. Rows are cells, "
         "columns the contrasts; every number with its interval is in `c2_stay.csv`.", ""]
    names = {W1: "W1", W160: "W1 over the first 60 min", EVENING: "W1 over 20:00 to 20:59", P90: "p90 order to door (min)",
             "extra_km_per_order": "km without an order per order"}
    for met in STAY_METRICS:
        d = st[st.metric == met]
        L += [f"### {names[met]}", "",
              md(d.assign(cell=[f"{r.scenario}, {r.level}" for r in d.itertuples()], diff=[ci(r) for r in d.to_dict("records")])
                 .pivot(index="cell", columns="contrast", values="diff").reindex([f"{s}, {lvl}" for s, lvl in PRIMARY])
                 [["stay - nearest", "zhu - stay", "jusup - stay"]]), ""]
    return L


# ---------------------------------------------------------------- parts 3 and 4: one reading, two inputs

def read_set(alt, alt_beh, base, base_beh, models, dl_of, label):
    """Contrasts of `models` against nearest courier in the 16 primary cells (W1 and p90 on Q1, W1 over 60 min and p90
    on Q2), with Holm within the E1-shaped (Q1) and E2-shaped (Q2) sets, and the joint class per cell and model."""
    rows = []
    for m in models:
        for s, lvl in PRIMARY:
            near, mod = base.rows(s, lvl, base_beh, "nearest"), alt.rows(s, lvl, alt_beh, m)
            q = q_of(s)
            for met in ((W1, P90) if q == "Q1" else (W160, P90)):
                c = pair(mod, near, met, s, alt.seeds, ((s, lvl, alt_beh, ob(m)), m, met))
                rows.append({"input": label, "holm_set": "E1-shaped" if q == "Q1" else "E2-shaped", "scenario": s,
                             "level": lvl, "model": m, "metric": met,
                             "delta": P90_SESOI_MIN if met == P90 else dl_of(s, lvl, met),
                             "model_mean": float(mod[met].mean()), "nearest_mean": float(near[met].mean()), **c})
    con = pd.DataFrame(rows)
    con["p_holm"] = np.nan
    for _, idx in con.groupby("holm_set").groups.items():
        con.loc[idx, "p_holm"] = holm(con.loc[idx, "p"].to_numpy())
    return finish(con)


def side_by_side(ca, cr):
    a, r = class_rows(ca, q_of), class_rows(cr, q_of)
    k = ["question", "scenario", "level", "model"]
    out = a.merge(r, on=k, suffixes=("_alt", "_ref"))
    out["changed"] = out.class_alt != out.class_ref
    return out


def explore_md(title, cl, con, alt_name, ref_name, n, note):
    counts = pd.concat([cl.groupby("model").class_alt.value_counts().rename(alt_name),
                        cl.groupby("model").class_ref.value_counts().rename(ref_name)], axis=1).fillna(0).astype(int)
    ch = cl[cl.changed]
    tab = pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in ch.itertuples()], "model": ch.model,
                        f"{ref_name} class": ch.class_ref, f"{alt_name} class": ch.class_alt,
                        f"W1 {ref_name}": ch.w1_mean_ref.map(lambda v: f"{v:+.2f}"),
                        f"W1 {alt_name}": ch.w1_mean_alt.map(lambda v: f"{v:+.2f}"),
                        f"p90 {ref_name}": ch.p90_mean_ref.map(lambda v: f"{v:+.2f}"),
                        f"p90 {alt_name}": ch.p90_mean_alt.map(lambda v: f"{v:+.2f}")})
    est = con.groupby(["input", "holm_set"]).agg(contrasts=("p", "size"), established=("established", "sum")).reset_index()
    return [title, "", note, "", "W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model "
            "minus nearest courier, in minutes; lower is better.", "", md(est, index=False), "", "Classes by model (cells):", "",
            md(counts), "",
            f"Classes that change: {len(ch)} of {len(cl)}.", "", md(tab, index=False) if len(ch) else "None.", ""]


def noise(noc, full30, dl):
    models = ["forecast", "li", "zhu", "jusup"]
    dl_of = lambda s, lvl, met: dl[(s, lvl, "fitted")][met]
    ca = read_set(noc, "fitted", full30, "fitted", models, dl_of, "noisy")
    cr = read_set(full30, "fitted", full30, "fitted", models, dl_of, "true")
    idn = []
    for m in models:                                  # a policy that reads no expected demand at run time is unchanged
        eq = 0
        for s, lvl in PRIMARY:
            a, b = noc.rows(s, lvl, "fitted", m), full30.rows(s, lvl, "fitted", m)
            eq += sum(all(same(a.loc[k, c], b.loc[k, c]) for c in FROZEN_METRICS) for k in noc.seeds)
        idn.append({"model": m, "episodes": len(PRIMARY) * len(noc.seeds), "episodes_equal_to_true": eq})
    return pd.concat([ca, cr], ignore_index=True), side_by_side(ca, cr), pd.DataFrame(idn)


def ashkrof(akc, full30, dl, beh="ashkrof", label="ashkrof"):
    """Smallest effects per behavior, as E3 and E4 take them: 10% of nearest courier's mean under that behavior. No pilot
    ran under `ashkrof`, so its nearest-courier means come from seeds 1001 to 1030 of this part."""
    near = {(s, lvl): akc.rows(s, lvl, beh, "nearest") for s, lvl in PRIMARY}
    dl_a = lambda s, lvl, met: W1_SESOI_SHARE * float(near[(s, lvl)][met].mean())
    dl_f = lambda s, lvl, met: dl[(s, lvl, "fitted")][met]
    ca = read_set(akc, beh, akc, beh, TESTED8, dl_a, label)
    cr = read_set(full30, "fitted", full30, "fitted", TESTED8, dl_f, "fitted")
    dq = []
    for s, lvl in PRIMARY:
        for lab, c, b in ((label, akc, beh), ("fitted", full30, "fitted")):
            j, n0 = c.rows(s, lvl, b, "jahanshahi"), c.rows(s, lvl, b, "nearest")
            dq.append({"behavior": lab, "scenario": s, "level": lvl, "w1_minus_nearest": float((j[W1] - n0[W1]).mean()),
                       "w1_60_minus_nearest": float((j[W160] - n0[W160]).mean()),
                       "p90_minus_nearest": float((j[P90] - n0[P90]).mean())})
    nm = pd.DataFrame([{"scenario": s, "level": lvl, "behavior": lab, **{m: float(c.rows(s, lvl, b, "nearest")[m].mean())
                                                                         for m in (W1, W160, P90)}}
                       for s, lvl in PRIMARY for lab, c, b in ((label, akc, beh), ("fitted", full30, "fitted"))])
    return pd.concat([ca, cr], ignore_index=True), side_by_side(ca, cr), pd.DataFrame(dq), nm


def fit_tables(fit_dir, fitted_dir, fitted_wide_dir=None):
    """The recalibrated values beside the fitted behavior's (Table 1); with `fitted_wide_dir` (C7), also the fitted
    behavior's bands on the wide grid, so that a wide Ashkrof band is read beside a wide fitted band."""
    a, f = (json.loads((d / "report.json").read_text())["fit"] for d in (fit_dir, fitted_dir))
    w = json.loads((fitted_wide_dir / "report.json").read_text())["fit"] if fitted_wide_dir else None
    rows = []
    for k in ("p_return", "asc_stay", "epoch_s", "cruise_radius_m"):
        rows.append({"parameter": k, "fitted": f["params"][k], "fitted_ci_lo": f["ci95"][k][0], "fitted_ci_hi": f["ci95"][k][1],
                     **({"fitted_wide_ci_lo": w["ci95"][k][0], "fitted_wide_ci_hi": w["ci95"][k][1]} if w else {}),
                     "ashkrof": a["params"][k], "ashkrof_ci_lo": a["ci95"][k][0], "ashkrof_ci_hi": a["ci95"][k][1],
                     "ashkrof_note": "recalibrated" if k in ("p_return", "asc_stay") else "fixed at the fitted value"})
    rows.append({"parameter": "part_time_stay", "fitted": np.nan, "ashkrof": 0.0, "ashkrof_note": "set to 0 (Scenario 1 Primary otherwise)"})
    rows.append({"parameter": "objective", "fitted": f["objective"], "ashkrof": a["objective"], "ashkrof_note": ""})
    ma, mf = (pd.read_csv(d / "moments_table.csv") for d in (fit_dir, fitted_dir))
    mo = mf[["moment", "in_fit", "meituan_peak", "meituan_all_day", "simulated"]].rename(columns={"simulated": "simulated_fitted"})
    mo = mo.merge(ma[["moment", "simulated"]].rename(columns={"simulated": "simulated_ashkrof"}), on="moment", how="outer")
    return pd.DataFrame(rows), mo


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["e6", "stay", "noise", "ashkrof", "ashkrof_wide", "resid"])
    ap.add_argument("out", type=Path)
    for k in ("--full", "--pkgc", "--pilot", "--g8"):
        ap.add_argument(k, type=Path, required=True)
    ap.add_argument("--fitted-fit", type=Path, default=Path("avaliacao/20261102-1146-behavior-single-final"))
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--n-explore", type=int, default=30)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    full_ep = load(a.full)
    seeds, seeds30 = list(range(1001, 1001 + a.n)), list(range(1001, 1001 + a.n_explore))
    dl = deltas(a.pilot)
    if a.part == "e6":
        con, cl, ud, ev, dq = e6(Cells(load(a.pkgc / "e6"), seeds), Cells(full_ep, seeds, FULL_SETS), dl, a.g8)
        for name, d in (("contrasts", con), ("classes", cl), ("undo", ud), ("evening", ev), ("dqn", dq)):
            d.to_csv(a.out / f"c1_e6_{name}.csv", index=False)
        L = e6_md(con, cl, ud, ev, dq, a.n)
    elif a.part == "resid":
        con, cl, ud, ev, ne = resid(Cells(load(a.pkgc / "resid"), seeds30), Cells(load(a.pkgc / "e6"), seeds30),
                                    Cells(full_ep, seeds30, FULL_SETS), dl)
        for name, d in (("contrasts", con), ("classes", cl), ("undo", ud), ("evening", ev), ("nearest", ne)):
            d.to_csv(a.out / f"c6_resid_{name}.csv", index=False)
        L = resid_md(con, cl, ud, ev, ne, a.n_explore)
    elif a.part == "stay":
        st = stay(Cells(load(a.pkgc / "stay"), seeds), Cells(full_ep, seeds, FULL_SETS))
        st.to_csv(a.out / "c2_stay.csv", index=False)
        L = stay_md(st, a.n)
    elif a.part == "noise":
        con, cl, idn = noise(Cells(load(a.pkgc / "noise"), seeds30), Cells(full_ep, seeds30, FULL_SETS), dl)
        con.to_csv(a.out / "c4_noise_contrasts.csv", index=False)
        cl.to_csv(a.out / "c4_noise_classes.csv", index=False)
        idn.to_csv(a.out / "c4_noise_identity.csv", index=False)
        L = explore_md("## Part 4. Noisy demand information (exploratory, no test)", cl, con, "noisy", "true", a.n_explore,
                       f"Forecast-aware matching, Li et al., Zhu et al. and Jusup et al. read the expected demand times a "
                       f"lognormal factor per zone and episode (mean 1, CV 0.2); W1 keeps the true demand. Seeds 1001 to "
                       f"{1000 + a.n_explore}; nearest courier and the true-input rows come from the full runs at the same "
                       "seeds. Holm runs within the E1-shaped and E2-shaped sets of each input, as a reading device. "
                       "The noisy and true intervals of one contrast share their bootstrap resamples (common random "
                       "numbers), so their difference is not blurred by resampling. Episodes equal to the true-input "
                       "episode in every metric: " + ", ".join(f"{r.model} {r.episodes_equal_to_true} of {r.episodes}"
                                                             for r in idn.itertuples()) + "; a model with all its "
                       "episodes equal reads no expected demand at run time. Contrasts: `c4_noise_contrasts.csv`; "
                       "classes: `c4_noise_classes.csv`; identity: `c4_noise_identity.csv`.")
    else:
        wide = a.part == "ashkrof_wide"
        pre, sub, beh, fd = (("c3w_ashkrof", "ashkrof_wide", "ashkrofw", "ashkrof_fit_wide") if wide else
                             ("c3_ashkrof", "ashkrof", "ashkrof", "ashkrof_fit"))
        lab = "ashkrofw" if wide else "ashkrof"
        con, cl, dq, nm = ashkrof(Cells(load(a.pkgc / sub), seeds30), Cells(full_ep, seeds30, FULL_SETS), dl, beh, lab)
        c7 = a.pkgc / "c7_fit_wide"
        fit, mo = fit_tables(a.pkgc / fd, a.fitted_fit, c7 if wide and (c7 / "report.json").exists() else None)
        first = json.loads((a.pkgc / "ashkrof_fit" / "report.json").read_text())["fit"]["params"]["asc_stay"] if wide else None
        wfit = json.loads((a.pkgc / fd / "report.json").read_text())["fit"] if wide else None
        for name, d in (("contrasts", con), ("classes", cl), ("dqn", dq), ("nearest_means", nm), ("fit", fit), ("moments", mo)):
            d.to_csv(a.out / f"{pre}_{name}.csv", index=False)
        L = ["## Part 3 again, at the wide-grid recalibration (exploratory, no test)" if wide else
             "## Part 3. One coherent behavior specification, Ashkrof et al. (exploratory, no test)", "",
             *([f"The first recalibration's grid cut the beta0 interval. The wide-grid recalibration (`ashkrof_fit_wide/`, "
                f"setting `ashkrofw`) moved beta0 from {first:g} to {wfit['params']['asc_stay']:g}, with the band "
                f"[{wfit['ci95']['asc_stay'][0]:g}, {wfit['ci95']['asc_stay'][1]:g}]; the first runs at beta0 {first:g} "
                "lie inside it and stay beside these (`c3_ashkrof_*`). The objective is flat in beta0, so the two points "
                "fit the moments about equally well. Part 3 ran again at the new values; everything else as in part 3. "
                "The fitted columns `fitted_wide_ci_*` are the fitted behavior's bands on its own wide grid (C7).", ""] if wide else []),
             "Recalibrated values beside the fitted behavior (95% bootstrap intervals over the Meituan moments):", "",
             md(fit, index=False), "", "Moments (Meituan peak hours, the fitted behavior and the Ashkrof setting):", "",
             md(mo, index=False), ""]
        L += explore_md("### Contrasts and classes", cl, con, lab, "fitted", a.n_explore,
                        f"All ten models ran, seeds 1001 to {1000 + a.n_explore}; the eight tested models are read against "
                        "nearest courier, beside the fitted behavior's full-run rows at the same seeds, read the same way. "
                        "Smallest effects per behavior: 10% of nearest courier's mean under that behavior (the fitted "
                        f"pilot for the fitted rows; seeds 1001 to 1030 of this part for `{beh}`, which had no pilot). "
                        "Holm within the E1-shaped and E2-shaped sets of each "
                        "behavior, as a reading device. The DQN is a descriptive row (mean differences, no interval). "
                        f"Contrasts: `{pre}_contrasts.csv`; classes: `{pre}_classes.csv`; DQN: `{pre}_dqn.csv`.")
    (a.out / f"{ {'e6': 'c1_e6', 'stay': 'c2_stay', 'noise': 'c4_noise', 'ashkrof': 'c3_ashkrof', 'ashkrof_wide': 'c3w_ashkrof', 'resid': 'c6_resid'}[a.part]}.md").write_text(
        "\n".join([ACK, "", *L, ACK]) + "\n")


if __name__ == "__main__":
    main()
