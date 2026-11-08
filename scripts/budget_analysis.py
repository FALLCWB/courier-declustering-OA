"""Training-budget check (preregistration-addendum-budget.md, committed at c217ca4 before any retraining): exploratory,
outside every family.

Usage: python scripts/budget_analysis.py <out_dir> --full <full_dir> --budget-runs <dir> --train <retrain_dir>
           --pilot <pilot_dir> --g8 <g8_analysis_dir> --per-policy <c5_per_policy.csv> --auad-grid <dir> --auad-final <dir>
           [--n 30]
Writes:
  b1_checkpoints.csv  per model: the checkpoint kept, peaks or epochs run, and the reproduction of the frozen policy 1
                      at peak 200 (Jusup et al.: the validation objective per epoch against the frozen training)
  b1_curves.csv       per model and checkpoint: its own training objective, and W1 and p90 on the validation seeds
  b2_contrasts.csv    W1 (W1 over 60 min on Q2) and p90 against nearest courier, retrained and current policy 1 at the
                      seeds of policy 1, Holm within the E1- and E2-shaped sets of each, as a reading device
  b2_classes.csv      the joint class of each, and whether it changes; b2_dqn.csv the DQN's descriptive differences
  b3_per_policy.csv   for each prevent or undo class of G8: whether each training policy's mean lies beyond -delta
  b4_auad_grid.csv    the six configurations of Auad et al.'s search; b4_auad_validation.csv the validation cost per
                      checkpoint at the selected step size
and paper-numbers-budget.md. Parts whose retraining or runs are not complete are marked pending.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_c_analysis import FULL_SETS, Cells, explore_md, read_set, side_by_side  # noqa: E402
from sim.analysis_extension import P90, Q1, Q2, W160, W1, deltas, load, md  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
ADDENDUM = "c217ca4"
TESTED = ["xu", "li", "auad", "jusup"]
FROZEN = Path("models/trained")
FROZEN_TRAIN = {"jusup": Path("avaliacao/20261104-0040-training-jusup")}
KEPT = {"xu": "final table (the frozen code saves the table of all peaks)",
        "li": "final actor (the frozen code saves the actor after the last peak)",
        "dqn": "final network (the frozen code saves the network after the last peak)",
        "auad": "theta_best, the theta with the lowest cost on its gate peak (Algorithm 1 lines 13-14)",
        "jusup": "the best validation objective (early stopping keeps the best state)"}
OBJECTIVES = {"xu": ["table_change_frobenius", "table_change_max_abs"], "li": ["actor_loss", "critic_loss", "episode_reward"],
              "dqn": ["loss", "episode_reward"], "auad": ["gate_cost", "best_cost", "train_cost"],
              "jusup": ["valid_objective"]}
CKPT = {"xu": ("xu_value_seed1_ep200.npz", "xu_value_seed1.npz"), "li": ("li_seed1_ep200.npz", "li_seed1.npz"),
        "dqn": ("jahanshahi_seed1_ep200.npz", "jahanshahi_seed1.npz"), "auad": ("auad_seed1_ep200.npz", "auad_seed1.npz")}


def same_npz(a, b, keys=None):
    za, zb = np.load(a), np.load(b)
    keys = keys or sorted(set(za.files) & set(zb.files))
    return all(np.array_equal(za[k], zb[k]) for k in keys)


def checkpoints(train, root):
    rows = []
    for m in ("xu", "li", "dqn", "auad", "jusup"):
        d = train / m
        done = (d / "run.json").exists()
        row = {"model": m, "kept": KEPT[m], "status": "done" if done else "pending"}
        if done:
            rj = json.loads((d / "run.json").read_text())
            row["peaks_or_epochs"] = rj.get("episodes", rj.get("max_epochs"))
        if m in CKPT and (d / CKPT[m][0]).exists():
            keys = ["V"] if m == "xu" else (["theta"] if m == "auad" else None)
            row["reproduces_frozen_policy_1_at_200"] = same_npz(d / CKPT[m][0], root / FROZEN / CKPT[m][1], keys)
        if m == "jusup" and (d / "training.csv").exists():
            new = pd.read_csv(d / "training.csv")
            old = pd.read_csv(root / FROZEN_TRAIN["jusup"] / "training.csv")
            old = old[old.training_seed == 1].set_index("epoch").valid_objective
            new_ = new[new.epoch >= 1].set_index("epoch").valid_objective
            both = old.index.intersection(new_.index)
            row["epochs_run"] = int(new.epoch.max())
            row["best_epoch"] = int(new_.idxmax())
            row["frozen_epochs_reproduced"] = f"{int((old[both] == new_[both]).sum())} of {len(both)}"
        rows.append(row)
    return pd.DataFrame(rows)


def curves(train):
    """Long table: model, checkpoint, measure, value. The objective is the mean over the 25 peaks (100 epochs) that end
    at the checkpoint; W1 and p90 are the means over the validation cases at the checkpoint."""
    out = []
    for m in ("xu", "li", "dqn", "auad", "jusup"):
        d = train / m
        step = 100 if m == "jusup" else 25
        if m == "xu" and (d / "table_change.csv").exists():
            for r in pd.read_csv(d / "table_change.csv").itertuples():
                out += [{"model": m, "checkpoint": r.checkpoint, "measure": "table_change_frobenius", "value": r.frobenius},
                        {"model": m, "checkpoint": r.checkpoint, "measure": "table_change_max_abs", "value": r.max_abs}]
        elif (d / "training.csv").exists():
            t = pd.read_csv(d / "training.csv")
            x = "epoch" if m == "jusup" else "episode"
            t["checkpoint"] = np.ceil(t[x] / step).astype(int) * step
            for meas in OBJECTIVES[m]:
                if meas in t:
                    x_ = t[meas].replace([np.inf, -np.inf], np.nan)   # a capped gate run (inf) could not win: left out
                    g = x_.groupby(t.checkpoint).mean()
                    out += [{"model": m, "checkpoint": int(c), "measure": meas, "value": float(v)} for c, v in g.items()]
            if m == "auad" and "gate_cost" in t:
                g = np.isinf(t.gate_cost).groupby(t.checkpoint).mean()
                out += [{"model": m, "checkpoint": int(c), "measure": "gate_capped_share", "value": float(v)} for c, v in g.items()]
        cf = d / ("curve_checkpoints.csv" if m == "jusup" else "curve.csv")
        if cf.exists():
            c = pd.read_csv(cf)
            x = "epochs" if m == "jusup" else "episodes"
            for (n), g in c.groupby(x):
                out += [{"model": m, "checkpoint": int(n), "measure": "w1_valid", "value": float(g.w1_rule_min.mean())},
                        {"model": m, "checkpoint": int(n), "measure": "p90_valid", "value": float(g.p90_c2d_min.mean())}]
    return pd.DataFrame(out, columns=["model", "checkpoint", "measure", "value"])


def compare(bud, full, dl):
    dl_of = lambda s, lvl, met: dl[(s, lvl, "fitted")][met]
    ca = read_set(bud, "fitted", full, "fitted", TESTED, dl_of, "retrained")
    cr = read_set(full, "fitted", full, "fitted", TESTED, dl_of, "current")
    cl = side_by_side(ca, cr).rename(columns=lambda c: c.replace("_alt", "_retrained").replace("_ref", "_current"))
    dq = []
    for s, lvl in Q1 + Q2:
        n0 = full.rows(s, lvl, "fitted", "nearest")
        for lab, c in (("retrained", bud), ("current", full)):
            j = c.rows(s, lvl, "fitted", "jahanshahi")
            dq.append({"policy": lab, "scenario": s, "level": lvl, "w1_minus_nearest": float((j[W1] - n0[W1]).mean()),
                       "w1_60_minus_nearest": float((j[W160] - n0[W160]).mean()),
                       "p90_minus_nearest": float((j[P90] - n0[P90]).mean())})
    return pd.concat([ca, cr], ignore_index=True), cl, pd.DataFrame(dq)


def per_policy(g8, pp, dl):
    cl = pd.read_csv(g8 / "classes.csv")
    cl = cl[cl.model.isin(TESTED) & cl["class"].str.startswith(("prevents", "undoes"))]
    pp = pd.read_csv(pp)
    out = []
    for r in cl.to_dict("records"):
        met = W1 if r["question"] == "Q1" else W160
        d = dl[(r["scenario"], r["level"], "fitted")][met]
        g = pp[(pp.model == r["model"]) & (pp.scenario == r["scenario"]) & (pp.level == r["level"]) & (pp.metric == met)].set_index("policy")
        means = {k: float(g.loc[k, "mean"]) for k in range(1, 6)}
        out.append({"model": r["model"], "question": r["question"], "scenario": r["scenario"], "level": r["level"],
                    "class": r["class"], "delta": d,
                    **{f"policy_{k}_mean": v for k, v in means.items()},
                    "policies_beyond_minus_delta": int(sum(v < -d for v in means.values()))})
    return pd.DataFrame(out)


def auad_tables(grid_dir, final_dir):
    g = pd.read_csv(grid_dir / "grid.csv").drop(columns=["theta_best"], errors="ignore")
    ch = json.loads((grid_dir / "run.json").read_text())["chosen"]
    g["chosen"] = (g.alpha == ch["alpha"]) & (g.mem == ch["mem"]) & (g.n_step == ch["n_step"])
    c = pd.read_csv(final_dir / "curve.csv")
    v = c.groupby("episodes").cost.mean().rename("mean_cost").reset_index().rename(columns={"episodes": "checkpoint"})
    per = c.groupby(["episodes", "training_seed"]).cost.mean().unstack()
    for k in per.columns:
        v[f"seed_{k}"] = per[k].to_numpy()
    return g, v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    for k in ("--full", "--budget-runs", "--train", "--pilot", "--g8", "--per-policy", "--auad-grid", "--auad-final"):
        ap.add_argument(k, type=Path, required=True)
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    seeds = list(range(1001, 1001 + 5 * a.n, 5))
    dl = deltas(a.pilot)
    ck, cu = checkpoints(a.train, root), curves(a.train)
    ck.to_csv(a.out / "b1_checkpoints.csv", index=False)
    cu.to_csv(a.out / "b1_curves.csv", index=False)
    pp = per_policy(a.g8, a.per_policy, dl)
    pp.to_csv(a.out / "b3_per_policy.csv", index=False)
    g, v = auad_tables(a.auad_grid, a.auad_final)
    g.to_csv(a.out / "b4_auad_grid.csv", index=False)
    v.to_csv(a.out / "b4_auad_validation.csv", index=False)
    L = ["# Paper numbers, training-budget check (exploratory)", "", ACK, "",
         f"Pre-registration addendum `preregistration-addendum-budget.md`, committed at {ADDENDUM} before any retraining; "
         "exploratory, outside every family. Policy 1 of each learned model retrained with three times the budget (600 "
         "peaks; Jusup et al. patience 300, at most 3,000 epochs), evaluated at the 30 seeds of policy 1 against the "
         "current policy 1 on the same seeds.", ""]
    ep_file = a.budget_runs / "episodes.jsonl"
    if ep_file.exists():
        bud = Cells(load(a.budget_runs), seeds)
        full = Cells(load(a.full), seeds, FULL_SETS)
        con, cl, dq = compare(bud, full, dl)
        con.to_csv(a.out / "b2_contrasts.csv", index=False)
        cl.to_csv(a.out / "b2_classes.csv", index=False)
        dq.to_csv(a.out / "b2_dqn.csv", index=False)
        ex = cl.rename(columns=lambda c: c.replace("_retrained", "_alt").replace("_current", "_ref"))
        L += explore_md("## Classes, retrained against current policy 1", ex, con, "retrained", "current", a.n,
                        f"Seeds {', '.join(map(str, seeds[:3]))}, ..., {seeds[-1]} (n = {len(seeds)}), the 16 primary "
                        "cells, fitted behavior, arm C at 100%. Smallest effects from the pilot; Holm within the "
                        "E1-shaped and E2-shaped sets of each policy, as a reading device. Contrasts: "
                        "`b2_contrasts.csv`; classes: `b2_classes.csv`; the DQN's differences: `b2_dqn.csv`.")
    else:
        L += ["## Classes, retrained against current policy 1", "", "Pending: the evaluation runs are not complete.", ""]
    ckm = ck.copy()
    for c in ("peaks_or_epochs", "epochs_run", "best_epoch"):
        if c in ckm:
            ckm[c] = ckm[c].map(lambda v: "" if pd.isna(v) else str(int(v)))
    ckm = ckm.astype(object).where(ckm.notna(), "").rename(columns={"peaks_or_epochs": "budget (peaks; Jusup: most epochs)"})
    L += ["## Training: the checkpoint kept and the reproduction at peak 200", "", md(ckm, index=False), "",
          "Curves (each model's own objective, and W1 and p90 on the validation seeds, per checkpoint): `b1_curves.csv`.", ""]
    for m, gm in cu.groupby("model", sort=False):           # one table per model: its own measures, every 100 peaks
        piv = gm.pivot_table(index="checkpoint", columns="measure", values="value")
        step = 200 if m == "jusup" else 100
        piv = piv[piv.index % step == 0].round(3)
        L += [f"**{m}** (every {step} {'epochs' if m == 'jusup' else 'peaks'})", "",
              md(piv.astype(object).where(piv.notna(), "")), ""]
    L += ["## Per-policy check of the G8 classes (existing rows)", "",
          "For each prevent or undo class: each training policy's mean contrast (30 seeds each) against -delta, the "
          "pilot's smallest effect of the cell.", "", md(pp.round(3), index=False) if len(pp) else "None.", "",
          "## Auad et al.: the configuration search and the validation cost", "",
          md(g.assign(alpha=g.alpha.map(lambda x: f"{x:.0e}")).round(1), index=False), "",
          "Validation cost per checkpoint at the selected configuration (mean over the five training seeds and the "
          f"validation cases): change from {int(v.checkpoint.min())} to {int(v.checkpoint.max())} peaks "
          f"{float(v.mean_cost.iloc[-1] - v.mean_cost.iloc[0]):+.1f}.", "", md(v.round(2), index=False), "", ACK]
    (a.out / "paper-numbers-budget.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
