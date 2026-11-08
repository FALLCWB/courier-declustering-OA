"""X4: train the constrained mean-field rebalancing policy of Jusup et al. by back-propagation through the mean-field
model (MFC-style, Sec. 4.1 and Algorithm 1 without the learned matcher), under the paper's settings (Table 3).

Usage: python sim/train_jusup.py <project_root> <out_dir>
One process per training seed k = 1 to 5 (4 torch threads each, 20 cores; evaluation afterwards on 4 workers): up to 1,000 epochs (Table 3) with early stopping
(patience 100 on the validation objective); each epoch draws a start and supply level from the 15 combinations and an
obedient share from {0.25, 0.5, 0.75, 1}, takes the start's courier mass by zone (episode seeds 98000 + 1000 k + epoch,
clear of the validation seeds 95001 to 95003; the first trainings used 90000 + 1000 k + epoch)
and the expected orders per zone for each 20-minute step divided by the fleet, and maximizes the summed reward plus the
barrier (Eq. 23a) with AdamW (weight decay 5e-4, the authors' training config) and gradient clipping. Validation: big cluster and scattered starts at normal supply, seeds
95001 to 95003, obedient share 1. Afterwards the final policies run in the simulator on the validation seeds at full
obedience. Outputs models/trained/jusup_seed<k>.pt and <out_dir>/training.csv, curve.csv, run.json.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from models.jusup_mf import LR, STEP_S, Geometry, Policy, rollout  # noqa: E402
from sim import scenarios as sc  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import COMBOS, SEEDS, VALID  # noqa: E402

EPOCHS, PATIENCE = 1000, 100
CKPT_EVERY, LOG_START = None, False   # budget check: checkpoints every CKPT_EVERY epochs and the epoch-0 objective
TRAINED = ROOT / "models/trained"     # the budget check retrains into models/trained_budget (sim/train_budget.py)
THREADS, EVAL_WORKERS = 4, 4   # 24-core limit on FE-SIM-1: 5 seeds x 4 threads, then 4 evaluation workers
TRAIN_BASE = 98000            # episode seeds TRAIN_BASE + 1000 k + epoch (G6 verdict: clear of the validation seeds)
WEIGHT_DECAY = 5e-4           # authors' configs/training/*_mfc_1ot_50pct_run1.yaml (policy_cfg.weight_decay)
QS = [0.25, 0.5, 0.75, 1.0]
_EX = {}


def ex():
    if "ex" not in _EX:
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def case(e, scenario, level, seed):
    """Start mass by zone and demand per 20-minute step (expected orders per zone / fleet size)."""
    city, n = e.city, e.man["fleets"][level]
    start = sc.starts(city, e.base, scenario, n, seed, e.hubs)
    mu0 = torch.tensor(np.bincount(city.zone[start], minlength=city.n_zones), dtype=torch.float32)
    dem = e.demand[scenario]
    steps = [torch.tensor(np.bincount(city.zone, weights=dem.expected_pickups(t, t + STEP_S), minlength=city.n_zones) / n,
                          dtype=torch.float32) for t in np.arange(0.0, 4 * 3600.0, STEP_S)]
    return mu0, steps


def train(k):
    torch.set_num_threads(THREADS)
    e = ex()
    geo = Geometry(e.city, e.base)
    pol = Policy(geo.Z, seed=4000 + k)
    opt = torch.optim.AdamW(pol.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    valid = [case(e, s, l, seed) for s, l, seed in VALID]
    best, best_state, since, log, t0 = -np.inf, None, 0, [], time.time()
    out = Path(sys.argv[2])
    if LOG_START:                                # the untrained policy's validation objective (epoch 0)
        with torch.no_grad():
            vals = [rollout(pol, geo, m, s, 1.0) for m, s in valid]
        log.append({"training_seed": k, "epoch": 0, "scenario": None, "q": None, "train_objective": np.nan,
                    "valid_objective": float(np.mean([float(a + b) for a, b in vals])),
                    "valid_reward": float(np.mean([float(a) for a, _ in vals])), "wall_s": 0.0})
    if CKPT_EVERY:
        torch.save(pol.state_dict(), out / f"jusup_seed{k}_ep0.pt")
    for ep in range(EPOCHS):
        rng = np.random.default_rng(np.random.SeedSequence([k, ep, 78]))
        scenario, level = COMBOS[rng.integers(len(COMBOS))]
        q = QS[rng.integers(len(QS))]
        mu0, steps = case(e, scenario, level, TRAIN_BASE + 1000 * k + ep)
        total, barrier = rollout(pol, geo, mu0, steps, q)
        loss = -(total + barrier)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(pol.parameters(), 1.0)
        opt.step()
        with torch.no_grad():
            vals = [rollout(pol, geo, m, s, 1.0) for m, s in valid]
        v_obj = float(np.mean([float(a + b) for a, b in vals]))
        v_rew = float(np.mean([float(a) for a, _ in vals]))
        log.append({"training_seed": k, "epoch": ep + 1, "scenario": scenario, "q": q, "train_objective": -float(loss),
                    "valid_objective": v_obj, "valid_reward": v_rew, "wall_s": round(time.time() - t0, 1)})
        if CKPT_EVERY and (ep + 1) % CKPT_EVERY == 0:
            torch.save(pol.state_dict(), out / f"jusup_seed{k}_ep{ep + 1}.pt")
        if v_obj > best:
            best, since = v_obj, 0
            best_state = {kk: vv.clone() for kk, vv in pol.state_dict().items()}
        else:
            since += 1
            if since >= PATIENCE:
                break
    torch.save(best_state, TRAINED / f"jusup_seed{k}.pt")
    return log


def evaluate(job):
    k, (scenario, level, seed) = job
    torch.set_num_threads(1)
    row, _ = ex().episode(scenario, level, seed, "jusup", obedience=1.0,
                          model_kw={"weights_path": TRAINED / f"jusup_seed{k}.pt", "q": 1.0})
    near, _ = ex().episode(scenario, level, seed, "nearest")
    return {"training_seed": k, "scenario": scenario, "seed": seed, "w1_rule_min": row["w1_rule_min"],
            "p90_c2d_min": row["p90_c2d_min"], "idle_km_per_order": row["idle_km_per_order"],
            "nearest_w1_rule_min": near["w1_rule_min"], "nearest_p90_c2d_min": near["p90_c2d_min"]}


def evaluate_ckpt(job):
    """A checkpoint of the budget check (every CKPT_EVERY epochs) on one validation case."""
    k, n, (scenario, level, seed) = job
    torch.set_num_threads(1)
    row, _ = ex().episode(scenario, level, seed, "jusup", obedience=1.0,
                          model_kw={"weights_path": Path(sys.argv[2]) / f"jusup_seed{k}_ep{n}.pt", "q": 1.0})
    return {"training_seed": k, "epochs": n, "scenario": scenario, "seed": seed, "w1_rule_min": row["w1_rule_min"],
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
    with Pool(EVAL_WORKERS) as pool:
        curve = pool.map(evaluate, [(k, c) for k in SEEDS for c in VALID])
    pd.DataFrame(curve).to_csv(out / "curve.csv", index=False)
    if CKPT_EVERY:
        ck = sorted({(k, int(f.stem.split("_ep")[1])) for k in SEEDS for f in out.glob(f"jusup_seed{k}_ep*.pt")})
        with Pool(EVAL_WORKERS) as pool:
            cc = pool.map(evaluate_ckpt, [(k, n, c) for k, n in ck for c in VALID])
        pd.DataFrame(cc).to_csv(out / "curve_checkpoints.csv", index=False)
    (out / "run.json").write_text(json.dumps({"model": "jusup", "training_seeds": SEEDS, "max_epochs": EPOCHS, "patience": PATIENCE,
                                              "train_wall_s": round(t1 - t0, 1), "total_wall_s": round(time.time() - t0, 1)},
                                             indent=1))
    print(pd.DataFrame(curve).groupby("scenario")[["w1_rule_min", "nearest_w1_rule_min", "p90_c2d_min",
                                                   "nearest_p90_c2d_min"]].mean().round(3))


if __name__ == "__main__":
    main()
