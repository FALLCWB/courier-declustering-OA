"""Q4 addendum to the G8 paper numbers (instructions of 2026-11-05, section 3, last item): E5 (arm C at 25, 50 and 75%
obedience) in both directions with the 100% contrast beside it, the Zhu mechanism check at 75% against 100%, and E3 and
E4 (the return sweep) once phase 4 is complete.

Usage: python scripts/paper_numbers_q4.py <analysis_out> <full_dir> <out_dir> --n <n>
  analysis_out  outputs of sim/analysis_extension.py run with --families E1,E2,E5 (and E3,E4 when phase 4 is done)
  full_dir      episodes.jsonl of the full runs (the Zhu mechanism check reads the rows)
Writes q4_e5.csv, zhu_mechanism_75_vs_100.csv, q4_e3.csv and q4_e4.csv when present, and paper-numbers-addendum.md.
Aggregates over seeds only. Holm stays within each family (E3, E4, E5), as pre-registered; the class per cell applies
the joint reading of section 5 within the family, descriptive beside the confirmatory contrasts.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sim.analysis_extension import P90, Q1, Q2, W160, W1, Runs, load, md  # noqa: E402
from sim.stats import classify, contrast_rng, paired_contrast  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from paper_numbers import evening  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
LAB = {"declusters at no delivery cost": "{s} at no delivery cost", "declusters at a delivery cost": "{s} at a delivery cost",
       "declusters, cost unresolved": "{s}, cost unresolved", "does not decluster": "does not {v}"}
VERB = {True: ("prevents", "prevent"), False: ("undoes", "undo")}       # Q1 cell or Q2 cell


def direction(r):
    if not r["established"]:
        return "not established"
    if r["mean"] > 0:
        return "established increase"
    return ("established decrease, at least the smallest effect" if r["lower_at_least_sesoi"]
            else "established decrease, below the smallest effect")


def classes(df, key, f2=None):
    """Joint reading per cell, model and key (obedience or behavior) within one family, and the source of its p90. As
    E2 takes the frozen three's p90 on the Q2 starts from F1, E4 takes it from the first round's F2 at the same return
    value (`f2`: the first round's contrasts); on the meet-up the p90 is in the family itself."""
    out, src = {}, {}
    f2 = f2[(f2.family == "F2") & (f2.metric == "p90")].set_index(["scenario", "level", "behavior", "model"]) \
        if f2 is not None else None
    for k, g in df.groupby(["scenario", "level", "model", key], dropna=False):
        q1 = (k[0], k[1]) in Q1
        w, p = g[g.metric == (W1 if q1 else W160)], g[g.metric == P90]
        if not len(w):
            continue
        w = w.iloc[0].to_dict()
        if len(p):
            p, src[k] = p.iloc[0].to_dict(), g.family.iloc[0]
        elif f2 is not None and (k[0], k[1], k[3], k[2]) in f2.index:
            p, src[k] = f2.loc[(k[0], k[1], k[3], k[2])].to_dict(), "F2 (first round)"
        else:
            continue
        sv, v = VERB[q1]
        out[k] = LAB[classify(w, p, w["delta"])].format(s=sv, v=v)
    ks = [(r.scenario, r.level, r.model, getattr(r, key)) for r in df.itertuples()]
    return [out.get(k, "no p90 in the family") for k in ks], [src.get(k, "none") for k in ks]


def family_table(con, fam, key, ref_name, f2=None):
    d = con[con.family == fam].copy()
    d["established"] = d.established.astype(str).str.lower().eq("true")
    d["lower_at_least_sesoi"] = d.lower_at_least_sesoi.astype(str).str.lower().eq("true")
    d["pct_of_nearest"] = 100.0 * d["mean"] / d["nearest_mean"]
    d["direction"] = [direction(r) for r in d.to_dict("records")]
    d["equivalence"] = d.equivalence.fillna("").replace("", "not read: established")
    d["class"], d["p90_source"] = classes(d, key, f2)
    ref = con[con.family.isin(["E1", "E2"])].set_index(["scenario", "level", "model", "metric"])
    for c in ("mean", "lo", "hi", "p_holm"):
        d[f"{c}_at_{ref_name}"] = [ref[c].get((r.scenario, r.level, r.model, r.metric), np.nan) for r in d.itertuples()]
    return d


def zhu_mechanism(runs):
    """Zhu at 75% against 100% obedience, paired by seed, in its 16 primary cells: the primary W1 metric (W1 on Q1
    cells, W1 over 60 min on Q2 cells), and per control step the couriers owning no cell and the commands sent (ratios
    of sums over episodes). Descriptive (G8 item)."""
    out = []
    for s, lvl in Q1 + Q2:
        met = W1 if (s, lvl) in Q1 else W160
        a, b = runs.rows(s, lvl, "fitted", "zhu", 0.75), runs.rows(s, lvl, "fitted", "zhu", 1.0)
        c = paired_contrast(a[met], b[met], contrast_rng((s, lvl, "fitted", "75 vs 100"), "zhu", met))
        row = {"scenario": s, "level": lvl, "metric": met, "n": c["n"], "w1_75": float(a[met].mean()),
               "w1_100": float(b[met].mean()), "w1_diff": c["mean"], "w1_lo": c["lo"], "w1_hi": c["hi"]}
        for ev in ("owns_no_cell", "commands"):
            r75 = a[f"events_{ev}"].sum() / a.events_steps.sum()
            r100 = b[f"events_{ev}"].sum() / b.events_steps.sum()
            row.update({f"{ev}_per_step_75": float(r75), f"{ev}_per_step_100": float(r100),
                        f"{ev}_per_step_diff": float(r75 - r100)})
        out.append(row)
    return pd.DataFrame(out)


def show(d, key, ref_name):
    return md(pd.DataFrame({
        "cell": [f"{r.scenario}, {r.level}" for r in d.itertuples()], "model": d.model, key: getattr(d, key),
        "metric": d.metric, "difference [95% CI]": [f"{r['mean']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]" for r in d.to_dict("records")],
        "% of nearest": [f"{v:+.1f}%" for v in d.pct_of_nearest], "p (Holm)": [f"{v:.3g}" for v in d.p_holm],
        "direction": d.direction, "class": d["class"],
        f"at {ref_name}": [f"{r[f'mean_at_{ref_name}']:+.2f}, p {r[f'p_holm_at_{ref_name}']:.3g}" for r in d.to_dict("records")]}),
        index=False)


def main():
    ap = argparse.ArgumentParser()
    for name in ("analysis", "full_dir", "out"):
        ap.add_argument(name, type=Path)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--first", type=Path, help="the first round's results (F2 p90 of the frozen three for E4)")
    a = ap.parse_args()
    f2 = pd.read_csv(a.first / "contrasts.csv") if a.first else None
    a.out.mkdir(parents=True, exist_ok=True)
    con = pd.read_csv(a.analysis / "contrasts.csv", keep_default_na=False, na_values=[""])
    fams = set(con.family)
    L = ["# Paper A numbers, Q4 addendum (E5, E3, E4)", "", ACK, "",
         f"Seeds 1001 to {1000 + a.n} (n = {a.n}). Differences are model minus nearest courier, lower is better; Holm "
         "within each family as pre-registered. Directions: an established decrease of at least the smallest effect, an "
         "established decrease below it, an established increase, or not established (with the R3 equivalence reading). "
         "The class applies the joint reading within the family. The reference column is the same cell, model and "
         "metric in E1 or E2: 100% obedience for E5, the fitted behavior for E3 and E4.", ""]
    if "E5" in fams:
        e5 = family_table(con, "E5", "obedience", "100")
        e5.to_csv(a.out / "q4_e5.csv", index=False)
        cnt = e5.pivot_table(index=["model", "obedience"], columns="direction", values="metric", aggfunc="count",
                             fill_value=0)
        runs = Runs(load(a.full_dir), a.n)
        zm = zhu_mechanism(runs)
        zm.to_csv(a.out / "zhu_mechanism_75_vs_100.csv", index=False)
        a3 = evening(runs, [(m, o) for m in ("zhu", "jusup") for o in (0.25, 0.5, 0.75)])   # Filipe, 2026-11-06
        a3.to_csv(a.out / "a3_evening_obedience.csv", index=False)
        L += ["## E5, obedience of arm C (25, 50 and 75%)", "", "Contrasts per model and obedience, by direction:", "",
              md(cnt), "", "Every contrast, with the same cell at 100% obedience (E1 or E2) beside it:", "",
              show(e5, "obedience", "100"), "",
              "## Zhu et al. at 75% against 100% obedience (mechanism check, descriptive)", "",
              "Paired by seed. Per control step: couriers owning no cell (an obedient courier sharing a cell with a "
              "lower-index courier owns none) and commands sent, as ratios of sums over episodes.", "",
              md(zm.round(3), index=False), "",
              "## A3 at 25, 50 and 75% obedience: W1 over 20:00 to 20:59 on the clustered starts (exploratory)", "",
              "Exploratory: defined after the results were seen (G8 verdict, ruling 5; extended to partial obedience by "
              "Filipe, 2026-11-06), outside every family, no test. Mean W1 over minutes 180 to 239, model minus nearest "
              "courier paired by seed, with 95% intervals. The same table at 100% is in the G8 paper numbers "
              "(`a3_evening_2000_2059.csv`).", "",
              md(pd.DataFrame({"cell": [f"{r.scenario}, {r.level}" for r in a3.itertuples()], "model": a3.model,
                               "obedience": a3.obedience, "model W1": a3.model_mean.round(2),
                               "nearest W1": a3.nearest_mean.round(2),
                               "difference [95% CI]": [f"{r['mean']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]"
                                                       for r in a3.to_dict("records")]}), index=False), ""]
    else:
        L += ["## E5", "", "Phase 3 is not complete; E5 enters when it is.", ""]
    for fam in ("E3", "E4"):
        if fam in fams:
            d = family_table(con, fam, "behavior", "fitted", f2)
            d.to_csv(a.out / f"q4_{fam.lower()}.csv", index=False)
            L += [f"## {fam}, return sweep", "", md(d.pivot_table(index=["model", "behavior"], columns="direction",
                                                                values="metric", aggfunc="count", fill_value=0)), "",
                  "Every contrast, with the same cell at the fitted behavior (E1 or E2) beside it:", "",
                  show(d, "behavior", "fitted"), ""]
        else:
            L += [f"## {fam}", "", "Phase 4 (the return sweep at 0 and 1) is running; it enters when complete.", ""]
    L += [ACK]
    (a.out / "paper-numbers-addendum.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
