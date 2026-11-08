"""Policy 5 validation check (DECISIONS.md, declared at 5a15a35): the curve code's validation cases on seeds 95501 to
95503, disjoint from every training seed, for Xu et al., Li et al., the deep Q-network and Auad et al.

Usage: python sim/policy5_validation.py <project_root> <out_dir> [workers]
Policy 5 runs at every checkpoint (25 to 200 peaks), policies 1 to 4 at the kept state (200 peaks): 288 episodes. Each
episode is the call the training code's own `evaluate` makes (sim/train_xu.py, train_li.py, train_dqn.py,
train_auad.py), with the checkpoint files of the frozen training folders; Xu's checkpoint tables are refit from the
recorded transitions (the frozen training kept only the 200-peak table), and its kept tables come from models/trained/.
One BLAS thread per process, as the training processes that wrote the rows for 95001 to 95003. Rows go to
<out_dir>/rows.jsonl as each episode ends; a restart skips the episodes already written.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.blas import pin, threads  # noqa: E402

if "numpy" not in sys.modules:   # run as a script: one BLAS thread, as the curve rows on 95001 to 95003
    pin(1)
import numpy as np  # noqa: E402

SEEDS = (95501, 95502, 95503)
CASES = [(s, "normal", v) for s in ("big_cluster", "scattered") for v in SEEDS]
CHECKPOINTS = [25, 50, 75, 100, 125, 150, 175, 200]
KEPT = 200
MODELS = ("xu", "li", "jahanshahi", "auad")
TRAIN = {"xu": ROOT / "avaliacao/20261103-1021-training-xu", "li": ROOT / "avaliacao/20261103-1449-training-li",
         "jahanshahi": ROOT / "avaliacao/20261103-1449-training-dqn", "auad": ROOT / "avaliacao/20261103-2154-training-auad"}
_EX = {}


def jobs():
    out = []
    for m in MODELS:
        for k in range(1, 6):
            for n in (CHECKPOINTS if k == 5 else [KEPT]):
                out += [{"model": m, "policy": k, "checkpoint": n, "scenario": s, "level": lvl, "seed": v} for s, lvl, v in CASES]
    return out


def key(j):
    return (j["model"], j["policy"], j["checkpoint"], j["scenario"], j["seed"])


def row_key(r):
    return (r["model"], r["training_seed"], r["episodes"], r["scenario"], r["seed"])


def experiment():
    if "ex" not in _EX:
        from sim.runner import Experiment
        _EX["ex"] = Experiment(ROOT)
    return _EX["ex"]


def auad_cost(sim):
    from models.auad_holding import episode_cost
    return episode_cost(sim)


def xu_table(k, n, transitions=None, n_zones=None, n_peaks=200):
    """The value table fitted on the first n recorded peaks of training seed k, as sim/train_xu.py fits it."""
    from models.xu_value import fit_value
    z = np.load(transitions or TRAIN["xu"] / "transitions.npz")
    tr = sorted([(i, z[f"t_{k}_{i}"]) for i in range(n_peaks)])
    return fit_value(np.vstack([t for _, t in tr[:n]]), n_zones if n_zones is not None else experiment().city.n_zones)


def evaluate(job):
    m, k, n, s, lvl, v = job["model"], job["policy"], job["checkpoint"], job["scenario"], job["level"], job["seed"]
    ex = experiment()
    extra = {}
    if m == "xu":
        V = np.load(ROOT / f"models/trained/xu_value_seed{k}.npz")["V"] if n == KEPT else xu_table(k, n)
        row, _ = ex.episode(s, lvl, v, "xu", model_kw={"value": V})
    elif m in ("li", "jahanshahi"):
        row, _ = ex.episode(s, lvl, v, m, model_kw={"weights_path": TRAIN[m] / f"{m}_seed{k}_ep{n}.npz"})
    else:
        theta = np.load(TRAIN["auad"] / f"auad_seed{k}_ep{n}.npz")["theta"]
        row, sim = ex.episode(s, lvl, v, "auad", model_kw={"theta": np.array(theta, float), "cap": None}, light=False)
        extra = {"cost": auad_cost(sim), "unassigned_over_30min_share": row["unassigned_over_30min_share"]}
    return {"model": m, "training_seed": k, "episodes": n, "scenario": s, "seed": v, **extra,
            "w1_rule_min": row["w1_rule_min"], "p90_c2d_min": row["p90_c2d_min"], "blas_threads": threads()}


def main():
    import os
    if any(os.environ.get(v) != "1" for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")):
        raise SystemExit("the policy 5 check runs with one BLAS thread per process, as the curve rows it is compared with")
    out = Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    out.mkdir(parents=True, exist_ok=True)
    rows = out / "rows.jsonl"
    done = {row_key(json.loads(x)) for x in rows.read_text().splitlines()} if rows.exists() else set()
    todo = [j for j in jobs() if key(j) not in done]
    todo.sort(key=lambda j: j["model"] != "auad")           # Auad's episodes are the longest: start them first
    t0 = time.time()
    print(f"{len(todo)} of {len(jobs())} episodes to run, {workers} workers", flush=True)
    with Pool(workers) as pool, rows.open("a") as f:
        for i, r in enumerate(pool.imap_unordered(evaluate, todo), 1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            if i % 12 == 0 or i == len(todo):
                print(f"{i}/{len(todo)} {round(time.time() - t0)} s", flush=True)
    (out / "run.json").write_text(json.dumps({"episodes": len(jobs()), "workers": workers, "seeds": list(SEEDS),
                                              "declared_at": "5a15a35", "wall_s": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
