"""Run experiment episodes on FE-SIM-1: the pilot (S7) and the full runs (S8), as fixed in preregistration.md.

Usage: python sim/run_cells.py <project_root> <out_dir> <plan> [workers]
  plan  pilot          F1 and F2 cells (5 starts x 3 levels x 5 behavior settings x 4 models), seeds 1 to 30
        full:<n>       the same cells, seeds 1001 to 1000 + n
        f3:<n>         layouts s1 to s4 and osm, big cluster, normal supply, fitted behavior, 4 models, seeds 1001 on
        f4:<n>         half scale and travel times x0.75, big cluster, normal supply, fitted behavior, 4 models
One row per episode is appended to <out_dir>/episodes.jsonl as it finishes (models report different extra fields); a rerun skips the jobs already there, so a
stopped run resumes where it was.
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
if __name__ == "__main__":   # run as the experiment, not imported (tests import read_done)
    pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim.runner import Experiment  # noqa: E402

MODELS = ["nearest", "foodmatch", "forecast", "backpressure"]
SETTINGS = ["fitted", "p0", "p0.25", "p0.5", "p1"]
KEY = ["family", "scenario", "level", "behavior", "layout", "scale", "time_mult", "seed", "model"]
_EX = {}


def jobs(plan, man):
    kind, _, n = plan.partition(":")
    seeds = list(range(1, 31)) if kind == "pilot" else list(range(1001, 1001 + int(n)))
    out = []
    if kind in ("pilot", "full"):
        for seed in seeds:
            for s in man["scenarios"]:
                for lvl in man["levels"]:
                    for b in SETTINGS:
                        for m in MODELS:
                            out.append({"family": "F1" if b == "fitted" else "F2", "scenario": s, "level": lvl,
                                        "behavior": b, "layout": man["layout"], "scale": 1.0, "time_mult": 1.0,
                                        "seed": seed, "model": m})
    elif kind == "f3":
        for layout in ["s1", "s2", "s3", "s4", "osm"]:
            for seed in seeds:
                for m in MODELS:
                    out.append({"family": "F3", "scenario": "big_cluster", "level": "normal", "behavior": "fitted",
                                "layout": layout, "scale": 1.0, "time_mult": 1.0, "seed": seed, "model": m})
    elif kind == "f4":
        for scale, tm in [(0.5, 1.0), (1.0, 0.75)]:
            for seed in seeds:
                for m in MODELS:
                    out.append({"family": "F4", "scenario": "big_cluster", "level": "normal", "behavior": "fitted",
                                "layout": man["layout"], "scale": scale, "time_mult": tm, "seed": seed, "model": m})
    else:
        raise SystemExit(f"unknown plan {plan}")
    return out


def read_done(path):
    """Keys of the finished episodes; a last line cut by a stop is dropped and the file truncated to the last newline."""
    if not path.exists():
        return set()
    raw = path.read_bytes()
    cut = raw.rfind(b"\n") + 1
    if cut < len(raw):
        with path.open("r+b") as f:
            f.truncate(cut)
    return {key(json.loads(line)) for line in raw[:cut].decode().splitlines() if line.strip()}


def key(j):
    return tuple(str(j[k]) for k in KEY)


def run(j):
    if j["layout"] not in _EX:
        _EX.clear()                                            # one layout per worker at a time (memory)
        _EX[j["layout"]] = Experiment(ROOT, layout=j["layout"])
    t0 = time.time()
    row, _ = _EX[j["layout"]].episode(j["scenario"], j["level"], j["seed"], j["model"], setting=j["behavior"],
                                      scale=j["scale"], time_mult=j["time_mult"])
    row.update({k: j[k] for k in KEY})
    row["seconds"] = round(time.time() - t0, 2)
    row["worker"] = os.getpid()
    return row


def main():
    out = Path(sys.argv[2])
    plan = sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    out.mkdir(parents=True, exist_ok=True)
    man = json.loads((ROOT / "scenarios/manifest.json").read_text())
    todo = jobs(plan, man)
    path = out / "episodes.jsonl"
    done = read_done(path)
    todo = [j for j in todo if key(j) not in done]
    print(f"{plan}: {len(todo)} episodes to run, {len(done)} already done", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, path.open("a") as fh:
        for i, row in enumerate(pool.imap_unordered(run, todo, chunksize=1)):
            fh.write(json.dumps(row, default=float) + "\n")
            fh.flush()
            if (i + 1) % 100 == 0:
                el = time.time() - t0
                print(f"  {i + 1}/{len(todo)} in {el / 60:.1f} min, {el / (i + 1):.2f} s per episode wall", flush=True)
    (out / f"run_{plan.replace(':', '_')}.json").write_text(json.dumps({
        "plan": plan, "episodes": len(todo), "workers": workers, "wall_seconds": round(time.time() - t0, 1)}))
    print("done", round((time.time() - t0) / 60, 1), "min", flush=True)


if __name__ == "__main__":
    main()
