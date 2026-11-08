"""Policy 5 validation check (DECISIONS.md, declared at 5a15a35): tables and paper numbers.

Usage: python scripts/policy5_report.py <out_dir> --run <run_dir> --train-xu <dir> --train-li <dir> --train-dqn <dir>
       --train-auad <dir> --calibration <dir> --full-episodes <episodes.jsonl>
The rows for 95001 to 95003 are the frozen training folders' curve.csv; the rows for 95501 to 95503 are <run_dir>/rows.jsonl
(sim/policy5_validation.py). Gap = mean over the six cases on 95001 to 95003 minus the mean on 95501 to 95503, at the kept
state (200 peaks). Reading rule (declared): policy 5 reads as unaffected when, for every model, its gap lies within the
range of policies 1 to 4, widened by 0.10 min for W1 and 0.5 min for p90. Auad's cost is reported beside, without a rule.
Outputs p5_kept.csv, p5_gap.csv, p5_curve.csv, p5_curve_move.csv, p5_p90_sources.csv and paper-numbers-policy5.md.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ACK = "This research was supported by data provided by Meituan."
DECLARED = "5a15a35"
OLD, NEW = (95001, 95002, 95003), (95501, 95502, 95503)
KEPT = 200
WIDEN = {"w1_rule_min": 0.10, "p90_c2d_min": 0.5}
METRICS = ("w1_rule_min", "p90_c2d_min", "cost")
NAMES = {"xu": "Xu et al.", "li": "Li et al.", "jahanshahi": "Deep Q-network", "auad": "Auad et al."}
ORDER = ["xu", "li", "jahanshahi", "auad"]
LABEL = {"w1_rule_min": "W1", "p90_c2d_min": "p90", "cost": "Auad cost"}

CODE_READING = [
    ("Xu et al.", "Keeps the final value table, fitted once on the nearest-courier transitions of all 200 peaks; training "
     "seed 5's peaks ran on episode seeds 95000 to 95199, and no choice reads any validation seed (the curve is recorded, "
     "never used)."),
    ("Li et al.", "Keeps the actor after peak 200 (final); training seed 5 trains on 95000 to 95199 with a temperature "
     "schedule fixed by the peak count, and no choice reads any validation seed."),
    ("Deep Q-network", "Keeps the network after peak 200 (final); training seed 5 trains on 95000 to 95199 with an "
     "epsilon schedule fixed by the peak count, and no choice reads any validation seed."),
    ("Auad et al.", "Keeps theta_best, the theta with the lowest cost on the gate peak, which for training seed 5 is seed "
     "97005 (big-cluster start, normal supply); training seed 5 trains on 95000 to 95199; the configuration (alpha 1e-7, "
     "m 3,000, n 1,000) was chosen once from training seed 1 (seeds 91000 to 91199) by its cost on 95001 to 95003 and holds "
     "for all five policies, so no policy-5 state ran in any choice on those seeds."),
    ("Jusup et al.", "Keeps the epoch with the best validation objective on 95001 to 95003 (mean-field rollouts from those "
     "seeds' start positions); training seed 5 trains on seeds 103000 to 103726 (98000 + 1000 k + epoch, 727 epochs), "
     "disjoint from the validation seeds, so it is not affected and does not run here."),
]


def load_old(dirs):
    out = []
    for m, d in dirs.items():
        c = pd.read_csv(Path(d) / "curve.csv")
        c["model"] = m
        out.append(c[c.seed.isin(OLD)])
    return pd.concat(out, ignore_index=True)


def load_new(run):
    return pd.DataFrame([json.loads(x) for x in (Path(run) / "rows.jsonl").read_text().splitlines()])


def _means(df, n=None):
    d = df if n is None else df[df.episodes == n]
    cols = [c for c in METRICS if c in d.columns]
    return d.groupby(["model", "training_seed", "episodes"])[cols].agg(["mean", "count"])


def kept(old, new):
    rows = []
    for name, df in (("95001-95003", old), ("95501-95503", new)):
        d = df[df.episodes == KEPT]
        for (m, k), g in d.groupby(["model", "training_seed"]):
            rows.append({"model": m, "policy": int(k), "seeds": name, "cases": len(g), "w1_mean": g.w1_rule_min.mean(),
                         "p90_mean": g.p90_c2d_min.mean(),
                         "cost_mean": g.cost.mean() if m == "auad" and "cost" in g else np.nan})
    return pd.DataFrame(rows).sort_values(["model", "policy", "seeds"], key=lambda s: s.map(ORDER.index) if s.name == "model" else s)


def gaps(old, new):
    rows = []
    o, n = old[old.episodes == KEPT], new[new.episodes == KEPT]
    for m in [x for x in ORDER if x in set(o.model)]:
        for met in METRICS:
            if met == "cost" and m != "auad":
                continue
            g = (o[o.model == m].groupby("training_seed")[met].mean() - n[n.model == m].groupby("training_seed")[met].mean())
            ref = g[g.index != 5]
            r = {"model": m, "metric": met, "gap_policy5": g.loc[5], "range_lo": ref.min(), "range_hi": ref.max(),
                 "beyond_range": max(0.0, ref.min() - g.loc[5], g.loc[5] - ref.max()),
                 "side": "below" if g.loc[5] < ref.min() else ("above" if g.loc[5] > ref.max() else "inside")}
            r.update({f"gap_policy{int(k)}": v for k, v in ref.items()})
            if met in WIDEN:
                w = WIDEN[met]
                r.update({"widen": w, "widened_lo": ref.min() - w, "widened_hi": ref.max() + w,
                          "within": bool(ref.min() - w <= g.loc[5] <= ref.max() + w)})
            else:
                r.update({"widen": np.nan, "widened_lo": np.nan, "widened_hi": np.nan, "within": None})
            rows.append(r)
    return pd.DataFrame(rows)


def outside_count(g):
    """Checks (model x W1 or p90) whose policy-5 gap lies outside the range of policies 1 to 4 before widening."""
    w = g[g.metric.isin(list(WIDEN))]
    return int((w.beyond_range > 0).sum()), len(w)


def verdict(g):
    w = g[g.metric.isin(list(WIDEN))]
    return "unaffected" if bool(w.within.astype(bool).all()) else "affected"


def curve(old, new):
    rows = []
    for name, df in (("new", new), ("old", old)):
        d = df[df.training_seed == 5]
        cols = [c for c in METRICS if c in d.columns]
        m = d.groupby(["model", "episodes"])[cols].mean()
        m.columns = [f"{c}_{name}" for c in cols]
        rows.append(m)
    cu = rows[0].join(rows[1], how="outer").reset_index()
    cu["w1_gap_old_minus_new"] = cu.w1_rule_min_old - cu.w1_rule_min_new
    return cu.rename(columns={"episodes": "checkpoint"})


def largest_move(cu):
    out = []
    for m, g in cu.groupby("model"):
        g = g.set_index("checkpoint").sort_index()
        r = {"model": m}
        for s in ("new", "old"):
            d = (g[f"w1_rule_min_{s}"] - g[f"w1_rule_min_{s}"].iloc[0]).iloc[1:].abs()
            r[f"largest_w1_move_{s}"] = d.max()
            r[f"at_checkpoint_{s}"] = int(d.idxmax())
            r[f"w1_range_{s}"] = g[f"w1_rule_min_{s}"].max() - g[f"w1_rule_min_{s}"].min()
        out.append(r)
    return pd.DataFrame(out).set_index("model")


def p90_sources(cal, full):
    rep = json.loads((Path(cal) / "report.json").read_text())
    v = pd.read_csv(Path(cal) / "validation_episodes.csv")
    nv = v[v.level == "normal"]
    near = []
    with open(full) as f:
        for line in f:
            r = json.loads(line)
            if (r.get("model"), r.get("scenario"), r.get("level"), r.get("behavior")) == ("nearest", "scattered", "normal", "fitted") \
                    and 1001 <= r.get("seed", 0) <= 1150:
                near.append((r["seed"], r["p90_c2d_min"]))
    per_seed = pd.DataFrame(near, columns=["seed", "p90"]).drop_duplicates("seed")
    cal_runs = (f"calibration `avaliacao/20261102-1026-calibration` (code 572610b): normal supply, {len(nv)} episodes, nearest "
                "idle courier, calibration's scattered start, every courier full-time and staying where it is while idle")
    rows = [
        {"source": "calibration, mean of per-episode p90", "value": float(nv.p90_c2d_min.mean()), "runs": cal_runs,
         "seeds": f"{nv.seed.min()} to {nv.seed.max()}"},
        {"source": "calibration, p90 of pooled orders", "value": float(rep["quantiles"]["c2d_min"]["sim"][4]), "runs": cal_runs,
         "seeds": f"{nv.seed.min()} to {nv.seed.max()}"},
        {"source": "study runs, mean of per-episode p90", "value": float(per_seed.p90.mean()),
         "runs": f"frozen code, nearest courier, scattered start, normal supply, fitted behavior, {len(per_seed)} episodes",
         "seeds": "1001 to 1150"},
        {"source": "Meituan orders delivered alone, p90 of pooled orders",
         "value": float(rep["quantiles"]["c2d_min"]["meituan_single_order_waves"][4]),
         "runs": "Meituan single-order waves, 17:00 to 20:59", "seeds": ""},
    ]
    assert abs(rep["quantile_levels"][4] - 0.9) < 1e-12
    return pd.DataFrame(rows)


def f(x, d=3):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{d}f}"


def markdown(kp, g, cu, mv, ps, run_meta):
    v = verdict(g)
    L = ["# Policy 5 on validation seeds disjoint from its training", "", ACK, "",
         f"Exploratory, outside every family. Question, seeds and reading rule declared in `DECISIONS.md` at commit "
         f"**{DECLARED}**, before any episode (Filipe, 2026-11-08: \"Package B\").", "", "## Summary", "",
         "| Question | Answer |", "|---|---|"]
    w = g[g.metric == "w1_rule_min"].set_index("model")
    p = g[g.metric == "p90_c2d_min"].set_index("model")
    L.append(f"| Does any choice for training seed 5 use 95001 to 95003? | No. Xu, Li and the DQN keep their final state, "
             f"Auad's theta_best is chosen on gate seed 97005, and the shared Auad configuration was chosen with policy 1 |")
    L.append(f"| Reading rule | Policy 5 reads as **{v}** by the overlap: "
             + "; ".join(f"{NAMES[m]} W1 gap {f(w.loc[m, 'gap_policy5'])} (policies 1 to 4: {f(w.loc[m, 'range_lo'])} to "
                         f"{f(w.loc[m, 'range_hi'])}), p90 gap {f(p.loc[m, 'gap_policy5'])} ({f(p.loc[m, 'range_lo'])} to "
                         f"{f(p.loc[m, 'range_hi'])})" for m in w.index) + " |")
    L.append("| Policy 5's curve on 95501 to 95503 | Largest move of W1 from its peak-25 value: "
             + "; ".join(f"{NAMES[m]} {f(mv.loc[m, 'largest_w1_move_new'])} min (peak {mv.loc[m, 'at_checkpoint_new']})"
                         for m in ORDER if m in mv.index) + " |")
    s = ps.set_index("source")
    L.append(f"| Where 35.9 min comes from | The calibration run of 2026-11-02 (normal supply, seeds 201 to 210): mean of "
             f"per-episode p90 {f(s.loc['calibration, mean of per-episode p90', 'value'])}, p90 of pooled orders "
             f"{f(s.loc['calibration, p90 of pooled orders', 'value'])}; the 35.8 of Results is the mean of per-episode p90 "
             f"on seeds 1001 to 1150 ({f(s.loc['study runs, mean of per-episode p90', 'value'])}) |")
    L += ["", f"Policy 5 reads as **{v}** by the overlap under the declared rule: for every model, its gap lies "
               "within the range of policies 1 to 4, widened by 0.10 min for W1 and 0.5 min for p90." if v == "unaffected" else
          f"Policy 5 reads as **{v}** by the overlap under the declared rule: at least one model's gap lies outside the "
          "range of policies 1 to 4, widened by 0.10 min for W1 and 0.5 min for p90 (table 3.2).", ""]
    k, n = outside_count(g)
    w8 = g[g.metric.isin(list(WIDEN)) & (g.beyond_range > 0)]
    if k:
        L += [f"Before the widening, policy 5's gap lies outside the range of policies 1 to 4 in {k} of {n} checks; a fifth "
              f"value drawn like the other four falls outside their range with probability 2/5, about {0.4 * n:.1f} of {n}. "
              f"Of these, {int((w8.side == 'below').sum())} lie below the range (policy 5 relatively lower on 95001 to 95003, "
              f"its training seeds) and {int((w8.side == 'above').sum())} above it; the distances are "
              + ", ".join(f"{NAMES[r.model]} {LABEL[r.metric]} {f(r.beyond_range)} ({r.side})" for _, r in w8.iterrows()) + " min.", ""]
    L += ["## 1. What the code keeps, and which seeds its choices used", "", "| Model | Kept state and seeds |", "|---|---|"]
    L += [f"| {a} | {b} |" for a, b in CODE_READING]
    L += ["", "No choice for training seed 5 used 95001 to 95003, so the check ran.", "",
          "## 2. What ran", "",
          f"- {run_meta.get('episodes', 288)} episodes on FE-SIM-1 (`sim/policy5_validation.py`, {run_meta.get('workers', '')} "
          "workers, one BLAS thread per process): the curve code's validation cases (big-cluster and scattered starts, "
          "normal supply, fitted behavior) on seeds 95501 to 95503, which no training, gate or choice of these four models ever ran.",
          "- Policy 5 at every checkpoint (25 to 200 peaks): the recorded checkpoint files of Li, the DQN and Auad; Xu's tables "
          "refit from the recorded transitions (the refit at 200 peaks equals the kept table bit for bit). Policies 1 to 4 at "
          "the kept state. Each episode is the call the training code's own evaluation makes (a test checks it).",
          "- The rows for 95001 to 95003 are the existing curve rows. At one BLAS thread the current code reproduces them: the "
          "budget check's peak-200 rows of policy 1 equal them bit for bit.", ""]
    L += ["## 3.1 Kept state, mean over the six cases (minutes; Auad's cost in its own units)", "",
          "| Model | Policy | W1, 95001-95003 | W1, 95501-95503 | p90, 95001-95003 | p90, 95501-95503 | Auad cost, 95001-95003 | Auad cost, 95501-95503 |",
          "|---|---|---|---|---|---|---|---|"]
    for m in ORDER:
        for k in range(1, 6):
            a = kp[(kp.model == m) & (kp.policy == k)].set_index("seeds")
            if a.empty:
                continue
            L.append(f"| {NAMES[m]} | {k} | {f(a.loc['95001-95003', 'w1_mean'])} | {f(a.loc['95501-95503', 'w1_mean'])} | "
                     f"{f(a.loc['95001-95003', 'p90_mean'], 2)} | {f(a.loc['95501-95503', 'p90_mean'], 2)} | "
                     f"{f(a.loc['95001-95003', 'cost_mean'], 1)} | {f(a.loc['95501-95503', 'cost_mean'], 1)} |")
    L += ["", "## 3.2 Gap, 95001-95003 minus 95501-95503, at the kept state", "",
          "| Model | Metric | Policy 5 | Policies 1 to 4 | Beyond that range | Widened range | Within |", "|---|---|---|---|---|---|---|"]
    for _, r in g.iterrows():
        d = 1 if r.metric == "cost" else 3
        wr = "" if np.isnan(r.widen) else f"{f(r.widened_lo, d)} to {f(r.widened_hi, d)}"
        wi = "no rule (descriptive)" if r.within is None or (isinstance(r.within, float) and np.isnan(r.within)) else ("yes" if r.within else "**no**")
        by = "0" if r.beyond_range == 0 else f"{f(r.beyond_range, d)} ({r.side})"
        L.append(f"| {NAMES[r.model]} | {LABEL[r.metric]} | {f(r.gap_policy5, d)} | {f(r.range_lo, d)} to {f(r.range_hi, d)} | {by} | {wr} | {wi} |")
    L += ["", "## 3.3 Policy 5's curve (mean over the six cases)", "",
          "| Model | Peak | W1, 95501-95503 | W1, 95001-95003 | Gap | p90, 95501-95503 | p90, 95001-95003 | Auad cost, 95501-95503 |",
          "|---|---|---|---|---|---|---|---|"]
    for m in ORDER:
        for _, r in cu[cu.model == m].sort_values("checkpoint").iterrows():
            L.append(f"| {NAMES[m]} | {int(r.checkpoint)} | {f(r.w1_rule_min_new)} | {f(r.w1_rule_min_old)} | {f(r.w1_gap_old_minus_new)} | "
                     f"{f(r.p90_c2d_min_new, 2)} | {f(r.p90_c2d_min_old, 2)} | {f(r.get('cost_new', np.nan), 1)} |")
    flat = [NAMES[m] for m in ORDER if m in mv.index and mv.loc[m, "w1_range_new"] == 0 and mv.loc[m, "w1_range_old"] == 0]
    if flat:
        L += ["", f"Checkpoints 25 to 200 give identical rows for {', '.join(flat[:-1]) + ' and ' + flat[-1] if len(flat) > 1 else flat[0]}: "
              "they hold the same state on both seed sets."]
    L += ["", "Largest move of W1 from the peak-25 value, peaks 50 to 200:", "",
          "| Model | 95501-95503 | At peak | 95001-95003 | At peak |", "|---|---|---|---|---|"]
    for m in ORDER:
        if m in mv.index:
            L.append(f"| {NAMES[m]} | {f(mv.loc[m, 'largest_w1_move_new'])} | {mv.loc[m, 'at_checkpoint_new']} | "
                     f"{f(mv.loc[m, 'largest_w1_move_old'])} | {mv.loc[m, 'at_checkpoint_old']} |")
    L += ["", "## 4. The 35.9 min of the threats paragraph", "", "| Source | p90 order to door (min) | Runs | Seeds |", "|---|---|---|---|"]
    L += [f"| {r.source} | {f(r.value, 2)} | {r.runs} | {r.seeds} |" for _, r in ps.iterrows()]
    L += ["", "The 35.9 min is the calibration run's p90 at normal supply, the number the calibration report prints beside "
          "Meituan's 41.1. Both statistics give it there: the mean of the ten per-episode p90 values and the p90 of the pooled "
          "orders round to 35.9. Meituan's 41.1 is the p90 of pooled orders, so the like-for-like figure is the pooled one. "
          "The 35.8 of Results is another sample: the study's frozen code (fitted idle behavior, part-time couriers, the "
          "scenario start), seeds 1001 to 1150, mean of per-episode p90.", "",
          "## Files", "", "`p5_kept.csv`, `p5_gap.csv`, `p5_curve.csv`, `p5_curve_move.csv`, `p5_p90_sources.csv`; run rows in "
          "`rows.jsonl` beside `run.json`.", "", ACK, ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    for a in ("--run", "--train-xu", "--train-li", "--train-dqn", "--train-auad", "--calibration", "--full-episodes"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    old = load_old({"xu": a.train_xu, "li": a.train_li, "jahanshahi": a.train_dqn, "auad": a.train_auad})
    new = load_new(a.run)
    kp, g, cu = kept(old, new), gaps(old, new), curve(old, new)
    mv, ps = largest_move(cu), p90_sources(a.calibration, a.full_episodes)
    kp.to_csv(out / "p5_kept.csv", index=False)
    g.to_csv(out / "p5_gap.csv", index=False)
    cu.to_csv(out / "p5_curve.csv", index=False)
    mv.reset_index().to_csv(out / "p5_curve_move.csv", index=False)
    ps.to_csv(out / "p5_p90_sources.csv", index=False)
    meta = json.loads((Path(a.run) / "run.json").read_text()) if (Path(a.run) / "run.json").exists() else {}
    (out / "paper-numbers-policy5.md").write_text(markdown(kp, g, cu, mv, ps, meta))
    print(f"policy 5 reads as {verdict(g)}")


if __name__ == "__main__":
    main()
