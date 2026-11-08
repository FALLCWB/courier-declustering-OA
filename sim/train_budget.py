"""Training-budget check (preregistration-addendum-budget.md): retrain policy 1 of one learned model with three times the
frozen budget, into models/trained_budget/, with curves from peak 0 (epoch 0). One BLAS thread per process, as in the
frozen training (sim/blas.py); the evaluation runs keep their 30.

Usage: python sim/train_budget.py <project_root> <out_dir> <xu|li|dqn|auad|jusup> [workers]
  xu, li, dqn, auad  training seed 1, 600 peaks (frozen: 200), checkpoints every 25 peaks from 0; the schedules keep their
                     frozen values in peaks (Li et al.'s temperature over 200 peaks, the DQN's replay-weight horizon),
                     so the first 200 peaks repeat the frozen training
  jusup              training seed 1, patience 300 and at most 3,000 epochs (frozen: 100 and 1,000), checkpoints every
                     100 epochs from 0
Each writes into <out_dir> the training script's own outputs (training.csv with the model's objective per peak or epoch,
curve.csv with W1 and p90 on the validation seeds per checkpoint, run.json); Xu et al. adds table_change.csv. The kept
policy (the one the frozen code keeps) goes to models/trained_budget/; models/trained/ is never written.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.blas import pin  # noqa: E402

if "numpy" not in sys.modules:   # run as a script: training keeps one BLAS thread per process, as the frozen training did
    pin(1)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
BUDGET = ROOT / "models/trained_budget"
PEAKS, EVERY = 600, 25
AUAD_CONFIG = (1e-7, 3000, 1000)             # the frozen selection (avaliacao/20261103-2051-training-auad-grid/run.json)


def configure(mod, model):
    """Set a training module to the budget check's settings (module globals the training functions read)."""
    mod.SEEDS = [1]
    mod.TRAINED = BUDGET
    if model == "jusup":
        mod.EPOCHS, mod.PATIENCE, mod.CKPT_EVERY, mod.LOG_START = 3000, 300, 100, True
        return mod
    mod.EPISODES = PEAKS
    mod.CHECKPOINTS = list(range(0, PEAKS + 1, EVERY))
    return mod


def table_changes(tables):
    """Change of the value table between consecutive checkpoints: Frobenius norm and largest absolute change."""
    out, prev = [], None
    for n in sorted(tables):
        V = tables[n]
        d = None if prev is None else V - prev
        out.append({"checkpoint": n, "frobenius": np.nan if d is None else float(np.linalg.norm(d)),
                    "max_abs": np.nan if d is None else float(np.abs(d).max()), "table_mean": float(V.mean())})
        prev = V
    return out


def run_xu(out, workers):
    from sim import train_xu as m
    configure(m, "xu")
    t0 = time.time()
    with Pool(workers) as pool:
        data = pool.map(m.collect, [(1, i) for i in range(PEAKS)])
    np.savez_compressed(out / "transitions.npz", **{f"t_{k}_{i}": t for k, i, t in data})
    tr = sorted([(i, t) for _, i, t in data])
    n_zones = m.ex().city.n_zones
    tables = {n: m.fit_value(np.vstack([t for _, t in tr[:n]]) if n else np.zeros((0, 5)), n_zones) for n in m.CHECKPOINTS}
    m.TRAINED.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(m.TRAINED / "xu_value_seed1.npz", V=tables[PEAKS], n_slots=m.N_SLOTS, episodes=PEAKS)
    for n, V in tables.items():
        np.savez_compressed(out / f"xu_value_seed1_ep{n}.npz", V=V)
    pd.DataFrame(table_changes(tables)).to_csv(out / "table_change.csv", index=False)
    with Pool(workers) as pool:
        curve = pool.map(m.evaluate, [(1, n, tables[n], case) for n in m.CHECKPOINTS for case in m.VALID])
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "xu", "training_seeds": [1], "episodes": PEAKS, "kept": "final",
                                              "total_wall_s": round(time.time() - t0, 1), "workers": workers}, indent=1))


def run_auad(out, workers):
    from sim import train_auad as m
    configure(m, "auad")
    m.TRAINED.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log = m.final_job((1, *AUAD_CONFIG, str(out)))
    pd.DataFrame(log).to_csv(out / "training.csv", index=False)
    t1 = time.time()
    with Pool(workers) as pool:
        curve = pool.map(m.evaluate, [(1, n, case, str(out)) for n in m.CHECKPOINTS for case in m.VALID])
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "auad", "stage": "budget", "alpha": AUAD_CONFIG[0],
                                              "mem": AUAD_CONFIG[1], "n_step": AUAD_CONFIG[2], "training_seeds": [1],
                                              "episodes": PEAKS, "kept": "theta_best (lowest gate cost)",
                                              "train_wall_s": round(t1 - t0, 1), "total_wall_s": round(time.time() - t0, 1)},
                                             indent=1))


def main():
    import os
    if any(os.environ.get(v) != "1" for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")):
        raise SystemExit("the budget retraining must run with one BLAS thread per process (sim/blas.py)")
    out = Path(sys.argv[2])
    model = sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    out.mkdir(parents=True, exist_ok=True)
    BUDGET.mkdir(parents=True, exist_ok=True)
    if model == "xu":
        run_xu(out, workers)
    elif model == "auad":
        run_auad(out, workers)
    else:
        import importlib
        m = configure(importlib.import_module({"li": "sim.train_li", "dqn": "sim.train_dqn", "jusup": "sim.train_jusup"}[model]), model)
        m.main()


if __name__ == "__main__":
    main()
