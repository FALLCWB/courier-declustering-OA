"""X4: train Auad, Lagos and Lagos' n-step SARSA with holding (arm B) in the simulator, configured from the paper's grid
(p.29) and the training budget of DECISIONS.md.

Usage:
  python sim/train_auad.py <project_root> <out_dir> grid
  python sim/train_auad.py <project_root> <out_dir> final <alpha> <mem> <n_step>

grid: for every alpha and n of the paper's grid, with m = 3000 (the paper's best n-step SARSA setting), training seed
1 trains for 200 peaks and its theta_best runs on the
validation seeds 95001 to 95003 (training range, never an evaluation seed); the configuration with the lowest mean
total cost (K_late lateness + K_dist distance + K_lost lost orders, p.10) is chosen. n = 3000 equals n = 1000 here:
an episode has 840 epochs, so both give the Monte Carlo return to the episode's end; only n = 1000 runs.
final: training seeds 1 to 5 with the chosen configuration; checkpoints of theta_best every 25 peaks, then each runs on
the validation seeds with every metric.

Each training seed k: peaks at a start and supply level drawn from (k, i), episode seeds 90000 + 1000 k + i, theta_0 = 0
(Table 6), epsilon-greedy on the hold-or-offer choice from 1.0 to 0.02 over the first 100 peaks (the paper explores
through its hyper-heuristic, which is off here). The policy acts with theta_best; after every peak the learned theta
runs once, greedily, on the gate peak of seed k (start and supply drawn from (k, 79), episode seed 97000 + k) and
replaces theta_best if its total cost is lower (Algorithm 1 lines 13-14, once per peak instead of every 200 epochs).
theta_0 = 0 holds every order to the lost limit, so its own gate run is skipped (it loses to any policy that offers); a
gate or selection run stops as soon as a lower bound of its cost passes min(theta_best's cost, 3 x nearest courier's
cost on the same peak), since it could not win. A theta that is no longer finite ends that configuration. Training and gate peaks run in the runner's light mode.
Outputs models/trained/auad_seed<k>.npz (final) and <out_dir>/grid.csv or training.csv, curve.csv, run.json.
"""
import json
import sys
import time
from itertools import product
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from models.auad_holding import GRID, CostCapExceeded, Learner, episode_cost  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import CHECKPOINTS, COMBOS, EPISODES, SEEDS, VALID  # noqa: E402

EPS_START, EPS_END, EPS_EPISODES = 1.0, 0.02, 100
N_STEPS = (2, 1000)                         # 3000 gives the same Monte Carlo return as 1000 on an 840-epoch episode
MEM_GRID = (3000,)                          # m = 3000, the paper's best n-step SARSA setting (p.30); alpha and n vary
CAP_FACTOR = 3.0                            # a capped run stops above 3 x nearest courier's cost on the same peak
_EX = {}


def ex():
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def run_cost(theta, scenario, level, seed, light=True, cap=None):
    """Total cost of theta run greedily on one peak; inf if a capped run passes its cap (it could not win)."""
    try:
        row, sim = ex().episode(scenario, level, seed, "auad", model_kw={"theta": np.array(theta, float), "cap": cap},
                                light=light)
    except CostCapExceeded:
        return np.inf, None
    return episode_cost(sim), row


def nearest_cost(scenario, level, seed):
    _, sim = ex().episode(scenario, level, seed, "nearest", light=True)
    return episode_cost(sim)


def gate_case(k):
    rng = np.random.default_rng(np.random.SeedSequence([k, 79]))
    scenario, level = COMBOS[rng.integers(len(COMBOS))]
    return scenario, level, 97000 + k


def train(k, alpha, mem, n_step, out=None):
    learner = Learner(seed=3000 + k, alpha=alpha, mem=mem, n_step=n_step)
    gs, gl, gseed = gate_case(k)
    # theta_best = theta_0 = 0 holds every order to the lost limit, dearer than any policy that offers: its gate run is
    # skipped (best_cost = inf), and every gate run stops once its cost passes min(best_cost, 3 x nearest courier).
    cap0 = CAP_FACTOR * nearest_cost(gs, gl, gseed)
    log, ckpt, t0 = [], {}, time.time()
    for i in range(EPISODES):
        rng = np.random.default_rng(np.random.SeedSequence([k, i, 77]))
        scenario, level = COMBOS[rng.integers(len(COMBOS))]
        eps = EPS_START + (EPS_END - EPS_START) * min(1.0, i / EPS_EPISODES)
        row, sim = ex().episode(scenario, level, 90000 + 1000 * k + i, "auad", model_kw={"learner": learner, "epsilon": eps},
                                light=True)
        learner.end_episode()
        diverged = learner.diverged()
        cost = np.nan if diverged else run_cost(learner.theta, gs, gl, gseed, cap=min(learner.best_cost, cap0))[0]
        replaced = (not diverged) and learner.consider(cost)
        log.append({"alpha": alpha, "mem": mem, "n_step": n_step, "training_seed": k, "episode": i + 1, "scenario": scenario,
                    "level": level, "epsilon": eps, "train_cost": episode_cost(sim), "p90_c2d_min": row["p90_c2d_min"],
                    "unassigned_over_30min_share": row["unassigned_over_30min_share"],
                    "td_mse": float(np.mean(learner.errors[-200:])) if learner.errors else np.nan,
                    "theta_norm": float(np.linalg.norm(learner.theta)), "gate_cost": cost, "best_cost": learner.best_cost,
                    "replaced": replaced, "diverged": diverged, "wall_s": round(time.time() - t0, 1)})
        if (i + 1) in CHECKPOINTS:
            ckpt[i + 1] = learner.theta_best.copy()
            if out is not None:
                np.savez_compressed(out / f"auad_seed{k}_ep{i + 1}.npz", theta=learner.theta_best, theta_learned=learner.theta)
        if diverged:
            break
    return log, learner, ckpt


def grid_job(cfg):
    alpha, mem, n_step = cfg
    log, learner, _ = train(1, alpha, mem, n_step)
    costs = [run_cost(learner.theta_best, *case, cap=CAP_FACTOR * nearest_cost(*case))[0] for case in VALID]
    return log, {"alpha": alpha, "mem": mem, "n_step": n_step, "diverged": learner.diverged(),
                 "theta_best_is_theta0": bool(np.all(learner.theta_best == 0)), "valid_cost": float(np.mean(costs)),
                 "gate_best_cost": learner.best_cost, "peaks": len(log), "theta_best": learner.theta_best.tolist()}


def final_job(job):
    k, alpha, mem, n_step, out = job
    log, learner, _ = train(k, alpha, mem, n_step, out=Path(out))
    np.savez_compressed(ROOT / f"models/trained/auad_seed{k}.npz", theta=learner.theta_best, alpha=alpha, mem=mem,
                        n_step=n_step)
    return log


def evaluate(job):
    k, n, (scenario, level, seed), out = job
    theta = np.load(Path(out) / f"auad_seed{k}_ep{n}.npz")["theta"]
    cost, row = run_cost(theta, scenario, level, seed, light=False)
    return {"training_seed": k, "episodes": n, "scenario": scenario, "seed": seed, "cost": cost,
            "w1_rule_min": row["w1_rule_min"], "p90_c2d_min": row["p90_c2d_min"],
            "unassigned_over_30min_share": row["unassigned_over_30min_share"]}


def main():
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "models/trained").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if sys.argv[3] == "grid":
        cfgs = list(product(GRID["alpha"], MEM_GRID, N_STEPS))
        with Pool(len(cfgs)) as pool:
            res = pool.map(grid_job, cfgs)
        pd.DataFrame([r for log, _ in res for r in log]).to_csv(out / "grid_training.csv", index=False)
        g = pd.DataFrame([s for _, s in res]).sort_values("valid_cost")
        g.to_csv(out / "grid.csv", index=False)
        best = g[~g.diverged].iloc[0] if (~g.diverged).any() else None
        (out / "run.json").write_text(json.dumps({"model": "auad", "stage": "grid", "configs": len(cfgs), "episodes": EPISODES,
                                                  "chosen": None if best is None else {"alpha": float(best.alpha),
                                                  "mem": int(best.mem), "n_step": int(best.n_step)},
                                                  "total_wall_s": round(time.time() - t0, 1)}, indent=1))
        print(g.drop(columns="theta_best").to_string())
        return
    alpha, mem, n_step = float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    with Pool(len(SEEDS)) as pool:
        logs = pool.map(final_job, [(k, alpha, mem, n_step, str(out)) for k in SEEDS])
    t1 = time.time()
    pd.DataFrame([r for log in logs for r in log]).to_csv(out / "training.csv", index=False)
    with Pool(10) as pool:
        curve = pool.map(evaluate, [(k, n, case, str(out)) for k in SEEDS for n in CHECKPOINTS for case in VALID])
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "auad", "stage": "final", "alpha": alpha, "mem": mem, "n_step": n_step,
                                              "training_seeds": SEEDS, "episodes": EPISODES, "train_wall_s": round(t1 - t0, 1),
                                              "total_wall_s": round(time.time() - t0, 1)}, indent=1))
    print(pd.DataFrame(curve).groupby(["episodes", "scenario"])[["cost", "w1_rule_min", "p90_c2d_min"]].mean().round(3))


if __name__ == "__main__":
    main()
