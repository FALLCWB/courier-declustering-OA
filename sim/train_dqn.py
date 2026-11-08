"""X3: train Jahanshahi et al.'s double DQN (assignment only) in the simulator, under the training budget of DECISIONS.md.

Usage: python sim/train_dqn.py <project_root> <out_dir>
One process per training seed k = 1 to 5 (the learning is sequential within a seed): 200 peaks, each at a start and
supply level drawn from (k, i), episode seeds 90000 + 1000 k + i, epsilon-greedy from 1.0 to 0.05 over the first 100
peaks (the paper gives no schedule), one update per decision. Checkpoints every 25 peaks; afterwards each checkpoint runs
on validation seeds 95001 to 95003 (big cluster and scattered, normal supply). Outputs
models/trained/jahanshahi_seed<k>.npz and <out_dir>/curve.csv, training.csv, run.json.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from models.jahanshahi_dqn import HIDDEN, LR, TRAIN_EVERY, Learner  # noqa: E402
from sim.nn import MLP  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import CHECKPOINTS, COMBOS, EPISODES, SEEDS, VALID  # noqa: E402

EPS_START, EPS_END, EPS_EPISODES = 1.0, 0.05, 100
TRAINED = ROOT / "models/trained"            # the budget check retrains into models/trained_budget (sim/train_budget.py)
ANNEAL = EPISODES                            # peaks behind the replay-weight schedule (total updates)
_EX = {}


def ex():
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def train(k):
    out = Path(sys.argv[2])
    net = MLP([1, *HIDDEN, 1], seed=1000 + k, lr=LR)
    learner = Learner(net, seed=k, total_updates=ANNEAL * 12_000 // TRAIN_EVERY)
    log, t0 = [], time.time()
    if 0 in CHECKPOINTS:                         # the untrained network (budget check: curves from peak 0)
        np.savez_compressed(out / f"jahanshahi_seed{k}_ep0.npz", **net.state())
    for i in range(EPISODES):
        rng = np.random.default_rng(np.random.SeedSequence([k, i, 77]))
        scenario, level = COMBOS[rng.integers(len(COMBOS))]
        eps = EPS_START + (EPS_END - EPS_START) * min(1.0, i / EPS_EPISODES)
        n0 = learner.updates
        row, _ = ex().episode(scenario, level, 90000 + 1000 * k + i, "jahanshahi",
                              model_kw={"net": net, "learner": learner, "epsilon": eps})
        learner.end_episode()
        log.append({"training_seed": k, "episode": i + 1, "scenario": scenario, "level": level, "epsilon": eps,
                    "updates": learner.updates - n0, "loss": float(np.mean(learner.losses[-1000:])) if learner.losses else np.nan,
                    "episode_reward": learner.rewards[-1],
                    "w1_rule_min": row["w1_rule_min"], "p90_c2d_min": row["p90_c2d_min"], "wall_s": round(time.time() - t0, 1)})
        if (i + 1) in CHECKPOINTS:
            np.savez_compressed(out / f"jahanshahi_seed{k}_ep{i + 1}.npz", **net.state())
    np.savez_compressed(TRAINED / f"jahanshahi_seed{k}.npz", **net.state())
    return log


def evaluate(job):
    k, n, (scenario, level, seed) = job
    path = Path(sys.argv[2]) / f"jahanshahi_seed{k}_ep{n}.npz"
    row, _ = ex().episode(scenario, level, seed, "jahanshahi", model_kw={"weights_path": path})
    return {"training_seed": k, "episodes": n, "scenario": scenario, "seed": seed, "w1_rule_min": row["w1_rule_min"],
            "p90_c2d_min": row["p90_c2d_min"]}


def main():
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    TRAINED.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(len(SEEDS)) as pool:
        logs = pool.map(train, SEEDS)
    t1 = time.time()
    pd.DataFrame([r for log in logs for r in log]).to_csv(out / "training.csv", index=False)
    with Pool(12) as pool:                  # half the cores: the two trainings may evaluate at once
        curve = pool.map(evaluate, [(k, n, case) for k in SEEDS for n in CHECKPOINTS for case in VALID])
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "jahanshahi", "training_seeds": SEEDS, "episodes": EPISODES,
                                              "train_wall_s": round(t1 - t0, 1), "total_wall_s": round(time.time() - t0, 1)},
                                             indent=1))
    print(pd.DataFrame(curve).groupby(["episodes", "scenario"])[["w1_rule_min", "p90_c2d_min"]].mean().round(3))


if __name__ == "__main__":
    main()
