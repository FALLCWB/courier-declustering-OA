"""X3: train Li et al.'s mean-field actor-critic (COD) in the simulator, under the training budget of DECISIONS.md.

Usage: python sim/train_li.py <project_root> <out_dir>
One process per training seed k = 1 to 5: 200 peaks, each at a start and supply level drawn from (k, i), episode seeds
90000 + 1000 k + i, Boltzmann temperature from 1.0 down to 0.01 (p.7) linearly over the 200 peaks, updates every 3,000
new samples on batches of 2,048 (p.7). Checkpoints every 25 peaks; afterwards each checkpoint runs on validation seeds
95001 to 95003 at temperature 0.01. Outputs models/trained/li_seed<k>.npz (the actor) and <out_dir>/curve.csv,
training.csv, run.json.
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
from models.li_meanfield import Learner  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import CHECKPOINTS, COMBOS, EPISODES, SEEDS, VALID  # noqa: E402

TRAINED = ROOT / "models/trained"            # the budget check retrains into models/trained_budget (sim/train_budget.py)
ANNEAL = EPISODES                            # peaks over which the temperature falls; it then stays at 0.01
_EX = {}


def temperature(i):
    return 1.0 + (0.01 - 1.0) * min(i, ANNEAL - 1) / (ANNEAL - 1)


def ex():
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def train(k):
    out = Path(sys.argv[2])
    learner = Learner(seed=2000 + k)
    log, t0 = [], time.time()
    if 0 in CHECKPOINTS:                         # the untrained actor (budget check: curves from peak 0)
        np.savez_compressed(out / f"li_seed{k}_ep0.npz", **learner.actor.state())
    for i in range(EPISODES):
        rng = np.random.default_rng(np.random.SeedSequence([k, i, 77]))
        scenario, level = COMBOS[rng.integers(len(COMBOS))]
        temp = temperature(i)
        learner.beta = 1.0 / temp
        n0 = len(learner.losses)
        row, _ = ex().episode(scenario, level, 90000 + 1000 * k + i, "li",
                              model_kw={"actor": learner.actor, "learner": learner, "beta": 1.0 / temp})
        learner.end_episode()
        log.append({"training_seed": k, "episode": i + 1, "scenario": scenario, "level": level, "temperature": temp,
                    "updates": len(learner.losses) - n0, "critic_loss": float(np.mean(learner.losses[-20:])) if learner.losses else np.nan,
                    "actor_loss": float(np.mean(learner.actor_losses[-20:])) if learner.actor_losses else np.nan,
                    "episode_reward": learner.rewards[-1],
                    "w1_rule_min": row["w1_rule_min"], "p90_c2d_min": row["p90_c2d_min"], "wall_s": round(time.time() - t0, 1)})
        if (i + 1) in CHECKPOINTS:
            np.savez_compressed(out / f"li_seed{k}_ep{i + 1}.npz", **learner.actor.state())
    np.savez_compressed(TRAINED / f"li_seed{k}.npz", **learner.actor.state())
    return log


def evaluate(job):
    k, n, (scenario, level, seed) = job
    row, _ = ex().episode(scenario, level, seed, "li", model_kw={"weights_path": Path(sys.argv[2]) / f"li_seed{k}_ep{n}.npz"})
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
    (out / "run.json").write_text(json.dumps({"model": "li", "training_seeds": SEEDS, "episodes": EPISODES,
                                              "train_wall_s": round(t1 - t0, 1), "total_wall_s": round(time.time() - t0, 1)},
                                             indent=1))
    print(pd.DataFrame(curve).groupby(["episodes", "scenario"])[["w1_rule_min", "p90_c2d_min"]].mean().round(3))


if __name__ == "__main__":
    main()
