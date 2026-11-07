"""G6 evidence for Xu et al. (reviewer pre-note): (1) convergence of the value table over training episodes, from the
cached transitions of the training run; (2) the units of the edge weight and its decomposition for sample matches and
for orders left waiting, on validation peak big_cluster / normal / 95001 with the training seed 1 table.

Usage: python scripts/xu_g6_evidence.py <project_root> <training_dir>
Writes <training_dir>/g6_convergence.csv, g6_edges.csv (every pair the planner kept, and the best pair of every order it
left waiting, with R_gamma, gamma^dt, V(s'), V(s) and the weight) and prints summaries.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
import models.xu_value as xv  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import CHECKPOINTS, EPISODES, SEEDS  # noqa: E402

out = Path(sys.argv[2])
e = Experiment(ROOT)
n_zones = e.city.n_zones

# (1) convergence: table fitted on the first n episodes against the table of all 200, per training seed
z = np.load(out / "transitions.npz")
rows = []
for k in SEEDS:
    tr = [z[f"t_{k}_{i}"] for i in range(EPISODES)]
    final = xv.fit_value(np.vstack(tr), n_zones)
    prev = None
    for n in CHECKPOINTS:
        V = xv.fit_value(np.vstack(tr[:n]), n_zones)
        live = V[:, :xv.N_SLOTS]
        rows.append({"training_seed": k, "episodes": n, "mean_abs_V": float(np.abs(live).mean()),
                     "mean_abs_diff_to_200": float(np.abs(live - final[:, :xv.N_SLOTS]).mean()),
                     "max_abs_diff_to_200": float(np.abs(live - final[:, :xv.N_SLOTS]).max()),
                     "mean_abs_change_from_previous": np.nan if prev is None else float(np.abs(live - prev).mean()),
                     "visited_state_share": len({(int(a), int(b)) for a, b in np.vstack(tr[:n])[:, :2] if b < xv.N_SLOTS})
                     / (n_zones * xv.N_SLOTS)})
        prev = live
conv = pd.DataFrame(rows)
conv.to_csv(out / "g6_convergence.csv", index=False)
print(conv.groupby("episodes")[["mean_abs_V", "mean_abs_diff_to_200", "mean_abs_change_from_previous", "visited_state_share"]].mean().round(4))

# (2) edge-weight decomposition on one validation peak
edges = []
orig = xv.XuValue.assign


def assign(self, v):
    city, p = v.city, v.sim.params
    approach = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf
    at_rest = v.t + approach
    ready = v.ready[:, None]
    pickup = np.maximum(at_rest + p.pickup_service_s, ready) if p.pickup_overlaps_wait else np.maximum(at_rest, ready) + p.pickup_service_s
    door = pickup + (city.T[v.rest, v.cust] * v.sf + p.door_overhead_s)[:, None]
    k = (door - v.t) / xv.SLOT_S
    s_now = min(int(v.t // xv.SLOT_S), self.n_slots)
    s_end = np.minimum((door // xv.SLOT_S).astype(int), self.n_slots)
    v_next = self.V[city.zone[v.cust][:, None], s_end]
    v_now = np.broadcast_to(self.V[city.zone[v.cell], s_now][None, :], k.shape)
    r_g = xv.discounted_reward(xv.REWARD, k, self.gamma)
    disc = self.gamma ** k
    rho = r_g + disc * v_next - v_now
    pairs = orig(self, v)
    kept = {(int(np.flatnonzero(v.orders == o)[0]), int(np.flatnonzero(v.couriers == c)[0])) for o, c in pairs}
    for i in range(len(v.orders)):
        mine = [j for (ii, j) in kept if ii == i]
        j, kind = (mine[0], "kept") if mine else (int(np.argmax(rho[i])), "waiting_best_pair")
        if not mine and v.t - v.placed[i] >= xv.WAIT_FALLBACK_S:
            kind = "fallback_due"
        edges.append({"t_min": v.t / 60.0, "order": int(v.orders[i]), "kind": kind, "approach_min": approach[i, j] / 60.0,
                      "dt_slots": k[i, j], "R_gamma": r_g[i, j], "gamma_dt": disc[i, j], "V_next": v_next[i, j],
                      "gamma_dt_V_next": disc[i, j] * v_next[i, j], "V_now": v_now[i, j], "weight": rho[i, j],
                      "pairs_positive_share": float((rho[i] > 0).mean())})
    return pairs


xv.XuValue.assign = assign
row, _ = e.episode("big_cluster", "normal", 95001, "xu", model_kw={"value_path": ROOT / "models/trained/xu_value_seed1.npz"},
                   light=True)
d = pd.DataFrame(edges)
d.to_csv(out / "g6_edges.csv", index=False)
print("p90 order to door:", round(row["p90_c2d_min"], 1), "| order-rounds:", len(d))
print(d.groupby("kind")[["R_gamma", "gamma_dt", "V_next", "gamma_dt_V_next", "V_now", "weight", "approach_min", "dt_slots",
                          "pairs_positive_share"]].mean().round(3).to_string())
print(d[d.kind == "kept"].sample(6, random_state=1)[["t_min", "R_gamma", "gamma_dt", "V_next", "gamma_dt_V_next", "V_now",
                                                      "weight", "dt_slots"]].round(3).to_string(index=False))
print(d[d.kind == "waiting_best_pair"].sample(6, random_state=1)[["t_min", "R_gamma", "gamma_dt", "V_next", "gamma_dt_V_next",
                                                                    "V_now", "weight", "dt_slots"]].round(3).to_string(index=False))
