"""Package C deliverable: paper-numbers-C.md from the part files of scripts/package_c_analysis.py and
scripts/package_c_tables.py, with a one-screen summary first. Parts whose files are missing are marked pending.

Usage: python scripts/paper_numbers_c.py <dir> --addendum <commit>
"""
import argparse
from pathlib import Path

import pandas as pd

ACK = "This research was supported by data provided by Meituan."
PARTS = [("c1_e6.md", "Part 1, E6"), ("c2_stay.md", "Part 2, stay"), ("c3_ashkrof.md", "Part 3, Ashkrof et al."),
         ("c4_noise.md", "Part 4, noisy demand"), ("c5_tables.md", "Part 5, tables from the existing runs"),
         ("c6_resid.md", "C6, homes where customers live (exploratory, declared after E6 was seen)"),
         ("c7_bands.md", "C7, the fitted behavior's bands on a wider grid"),
         ("c3_ashkrof_bands.md", "The Ashkrof variant's bands on a wider grid"),
         ("c3w_ashkrof.md", "Part 3 again, at the wide-grid recalibration")]
NAME = {"p_return": "return probability", "epoch_s": "decision delay (s)", "cruise_radius_m": "cruise radius (m)",
        "asc_stay": "stay constant (beta0)"}


def body(text):
    """The part's text without its acknowledgment lines and with its headings one level down under the parts."""
    out = []
    for line in text.splitlines():
        if line.strip() == ACK:
            continue
        if line.startswith("# "):
            line = "#" + line
        out.append(line)
    return "\n".join(out).strip("\n")


def summary(d):
    L = []
    f = d / "c1_e6_contrasts.csv"
    if f.exists() and (d / "c1_e6.md").exists():
        con, cl = pd.read_csv(f), pd.read_csv(d / "c1_e6_classes.csv")
        und = cl[cl["class"].str.startswith("undoes")]
        L.append(f"- E6 (confirmatory, n = {int(con.n.iloc[0])}): {int(con.established.sum())} of {len(con)} contrasts established (Holm within E6); "
                 f"{len(und)} of {len(cl)} cell-model pairs undo the cluster "
                 f"({', '.join(f'{m} {k}' for m, k in und.model.value_counts().items()) or 'none'}); "
                 f"{int(cl.changed.sum())} classes differ from those Paper A quotes.")
    f = d / "c2_stay.csv"
    if f.exists() and (d / "c2_stay.md").exists():
        st = pd.read_csv(f)
        w = st[(st.metric == "w1_rule_60min_after_min") & ~st.scenario.isin(["scattered", "burst"])]
        cnt = lambda c: int(((w.contrast == c) & (w.hi < 0)).sum())
        L.append(f"- Stay (exploratory): on the 10 Q2 cells, W1 over 60 min falls below nearest courier's in "
                 f"{cnt('stay - nearest')} cells; Zhu et al. falls below `stay` in {cnt('zhu - stay')} and Jusup et al. in "
                 f"{cnt('jusup - stay')} (95% intervals below 0).")
    for f, lab, n in (("c3_ashkrof_classes.csv", "Ashkrof setting at the first recalibration (exploratory)", None), ("c4_noise_classes.csv", "Noisy demand (exploratory)", None),
                      ("c3w_ashkrof_classes.csv", "Ashkrof setting at the wide-grid recalibration (exploratory)", None)):
        if (d / f).exists() and (d / f.replace("_classes.csv", ".md")).exists():
            cl = pd.read_csv(d / f)
            ch = cl[cl.changed]
            L.append(f"- {lab}: {len(ch)} of {len(cl)} classes change"
                     + (f" ({', '.join(f'{m} {k}' for m, k in ch.model.value_counts().items())})" if len(ch) else "") + ".")
    for name, md_, lab in (("c3_ashkrof_fit.csv", "c3_ashkrof.md", "Ashkrof, first recalibration (its grid cut the beta0 interval)"),
                           ("c3w_ashkrof_fit.csv", "c3w_ashkrof.md", "Ashkrof, wide-grid recalibration")):
        f = d / name
        if f.exists() and (d / md_).exists():
            p = pd.read_csv(f).set_index("parameter")
            L.append(f"- {lab}: return probability {p.loc['p_return', 'ashkrof']:.3g} "
                     f"[{p.loc['p_return', 'ashkrof_ci_lo']:.3g}, {p.loc['p_return', 'ashkrof_ci_hi']:.3g}] (fitted "
                     f"{p.loc['p_return', 'fitted']:.3g}); stay constant {p.loc['asc_stay', 'ashkrof']:.3g} "
                     f"[{p.loc['asc_stay', 'ashkrof_ci_lo']:.3g}, {p.loc['asc_stay', 'ashkrof_ci_hi']:.3g}] (fitted "
                     f"{p.loc['asc_stay', 'fitted']:.3g}).")
    L += part5_summary(d)
    f = d / "c6_resid_classes.csv"
    if f.exists() and (d / "c6_resid.md").exists():
        cl = pd.read_csv(f)
        u = {x: int(cl[f"class_{x}"].str.startswith("undoes").sum()) for x in ("resid", "indep", "fitted")}
        L.append(f"- C6 (exploratory, homes at the drop-offs, seeds 1001 to 1030): cell-model pairs that undo the cluster: "
                 f"undo in {u['resid']} of {len(cl)} under `resid`, {u['indep']} under `indep`, {u['fitted']} under the fitted setting.")
    for f, lab in (("c7_bands", "C7, fitted behavior"), ("c3_ashkrof_bands", "Ashkrof variant")):
        if (d / f"{f}.csv").exists() and (d / f"{f}.md").exists():
            t = pd.read_csv(d / f"{f}.csv")
            t = t[~((t.old_lo == t.old_hi) & (t.new_lo == t.new_hi))] if "touches" not in t else t[t.touches != "fixed"]
            ch = "; ".join(f"{NAME[r.parameter]} [{r.old_lo:g}, {r.old_hi:g}] to [{r.new_lo:.4g}, {r.new_hi:.4g}]"
                           + (f" (point {r.old_point:g} to {r.new_point:g})" if r.point_moved else "")
                           + (" (still touches the grid)" if getattr(r, "touches", "no") not in ("no", "fixed") else "")
                           for r in t.itertuples())
            mv = [NAME[r.parameter] for r in t.itertuples() if r.point_moved]
            L.append(f"- {lab}, bands on a wider grid: {ch}. Point estimate {'moved for ' + ', '.join(mv) if mv else 'unchanged'}.")
    return L


def part5_summary(d):
    """Part 5 in a few lines: the arm C and Xu windows and evening edge averaged over the nine clustered cells, the
    largest shift without 20:30 to 21:00, and the largest spread between training policies."""
    L = []
    if not (d / "c5_tables.md").exists():
        return L
    three = ("zhu", "jusup", "xu")
    f = d / "c5_w1_windows.csv"
    if f.exists():
        w = pd.read_csv(f)
        w = w[w.scenario != "meetup"].groupby(["model", "window"])["mean"].mean()
        L.append("- Part 5, W1 by window after the cluster appears (0-60, 60-120, 180-240 min; model minus nearest courier, "
                 "mean of the nine clustered cells): "
                 + "; ".join(f"{m} {w[(m, '0-60')]:+.2f}, {w[(m, '60-120')]:+.2f}, {w[(m, '180-240')]:+.2f}" for m in three) + ".")
    f = d / "c5_evening_by_return.csv"
    if f.exists():
        e = pd.read_csv(f).groupby(["model", "behavior"])["mean"].mean()
        L.append("- Part 5, W1 over 20:00 to 20:59 by return probability (mean of the nine clustered cells): "
                 + "; ".join(f"{m} p0 {e[(m, 'p0')]:+.2f}, fitted {e[(m, 'fitted')]:+.2f}, p1 {e[(m, 'p1')]:+.2f}" for m in three) + ".")
    f = d / "c5_evening_truncated.csv"
    if f.exists():
        t = pd.read_csv(f)
        r = t.loc[(t.mean_truncated - t.mean_full).abs().idxmax()]
        L.append(f"- Part 5, Q1 W1 without 20:30 to 21:00: the largest shift is {r.model}, {r.scenario}, {r.level}: "
                 f"{r.mean_full:+.2f} to {r.mean_truncated:+.2f}.")
    f = d / "c5_per_policy.csv"
    if f.exists():
        p = pd.read_csv(f)
        g = p.groupby(["family", "model", "scenario", "level", "metric"])["mean"]
        s = (g.max() - g.min())
        k = s.idxmax()
        L.append(f"- Part 5, per training policy: the largest spread between the five policy means of one contrast is "
                 f"{s.max():.2f} min ({k[1]}, {k[0]}, {k[2]}, {k[3]}, {k[4]}).")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=Path)
    ap.add_argument("--addendum", required=True)
    a = ap.parse_args()
    d = a.dir
    L = ["# Paper numbers, package C", "",
         f"Pre-registration addendum C (`preregistration-addendum-C.md`) committed at {a.addendum}, before any episode of "
         "parts 1 to 4. Part 1 (E6) is confirmatory; parts 2 to 5 are exploratory or descriptive, with no test.", "", ACK, "",
         "## Summary", "", *(summary(d) or ["- No part is complete yet."]), ""]
    for f, name in PARTS:
        L += [f"# {name}", ""]
        L += [body((d / f).read_text()), ""] if (d / f).exists() else ["Pending: runs not complete.", ""]
    csvs = sorted(p.name for p in d.glob("c*.csv"))
    L += ["# Files", "", "One CSV per table, in this folder:", "", *[f"- `{c}`" for c in csvs], "", ACK]
    (d / "paper-numbers-C.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
