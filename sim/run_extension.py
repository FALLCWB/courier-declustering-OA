"""Run the extension's episodes on FE-SIM-1, as fixed in preregistration-extension.md (frozen at 8e082e3).

Usage: python sim/run_extension.py <project_root> <out_dir> <plan> [workers] [part m:r1,r2 (seeds by remainder mod m)]
  plan  pilot      seeds 1 to 30: every new cell of section 3, arm C also at 0% obedience (identity check), the frozen
                   four (nearest courier and the frozen three) in the 15 fitted start cells and nearest courier in the 60
                   sweep start cells, rerun because their S7 rows lack the Q2 fields (W1 over 60 min, per-minute series);
                   used only for sigma_d, the smallest effects and runtime
        full:<n>   seeds 1001 to 1000 + n: every new cell and every frozen cell (frozen four x 15 start cells x 5
                   settings), rerun by the same code so that all frozen rows carry the Q2 fields, and the exploratory
                   meet-up; in Filipe's order (2026-11-04): E1 and E2, the meet-ups, E5, then E3 and E4 (`phase`).
                   R4 (2026-11-05): the frozen four in the ten Q2 cells and on the scattered start, on the fresh block
                   5001 to 5000 + n (set fresh_q2), right after the other phase-1 jobs
        head       the phase-1 jobs at seeds 1001 to 1030 (every full plan holds them), run on idle cores during the pilot
        full:<n>:short  the same with the return sweep cut to 0 and 1, used only if the total estimate passes 48 h
        explore    the exploratory meet-up (meetup_median), the ten models, seeds 1001 to 1030
        zhu_ties   post-freeze sensitivity: Zhu with random partition ties on the big cluster, the meet-up and the
                   scattered start, normal supply, seeds 1001 to 1030 (outside every family)
One row per episode is appended to <out_dir>/episodes.jsonl as it finishes, with its per-minute W1 series; a rerun skips
the jobs already there, so a stopped run resumes where it was (the worker count changes no value).
Learned models run the policy of training seed ((s - 1) mod 5) + 1. Arm C models run at their obedience level; every
other model has obedience None.
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
if __name__ == "__main__":   # run as the experiment, not imported (tests import jobs and policy_kw)
    pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import json
import os
import time
from multiprocessing import Pool

ROOT = Path(sys.argv[1]).resolve() if __name__ == "__main__" else Path(__file__).resolve().parents[1]

FROZEN = ["nearest", "foodmatch", "forecast", "backpressure"]
ROWS_5_TO_8 = ["xu", "li", "jahanshahi", "auad"]
ARM_C = ["zhu", "jusup"]
TEN = FROZEN + ROWS_5_TO_8 + ARM_C
SETTINGS = ["fitted", "p0", "p0.25", "p0.5", "p1"]
OBEDIENCE = [0.25, 0.5, 0.75, 1.0]
WEIGHTS = {"xu": ("value_path", "xu_value_seed{k}.npz"), "li": ("weights_path", "li_seed{k}.npz"),
           "jahanshahi": ("weights_path", "jahanshahi_seed{k}.npz"), "auad": ("theta_path", "auad_seed{k}.npz"),
           "jusup": ("weights_path", "jusup_seed{k}.pt")}
KEY = ["set", "scenario", "level", "behavior", "model", "obedience", "seed"]
FRESH0 = 5001   # R4 (Filipe, 2026-11-05): the frozen four's Q2 cells on seeds 5001 to 5000 + n, never used before
Q2_STARTS = ("big_cluster", "three_clusters", "mixed")
SLOW = {"zhu": 0, "xu": 1, "li": 2}                           # long episodes first, so none straggles at the end
_EX = {}


def policy_kw(model, seed, obedience, set_=None):
    """The trained policy of the seed's training seed; the training-budget check (set "budget") reads the retrained
    policies in models/trained_budget/ (preregistration-addendum-budget.md)."""
    k = (seed - 1) % 5 + 1
    kw = {}
    if model in WEIGHTS:
        key, fname = WEIGHTS[model]
        kw[key] = ROOT / ("models/trained_budget" if set_ == "budget" else "models/trained") / fname.format(k=k)
    if model == "jusup":
        kw["q"] = obedience
    return kw


def phase(j):
    """Run order of the full runs (Filipe, 2026-11-04): 1 = the cells of E1 and E2 (fitted behavior, arm C at 100%, with
    the DQN and the scattered references), 2 = the exploratory and ride meet-ups (and the Zhu tie sensitivity),
    3 = E5 (arm C at 25 to 75%), 4 = E3 and E4 (the return sweep)."""
    if j["set"] in ("explore", "ride", "zhu_random_ties"):
        return 2
    if j["behavior"] != "fitted":
        return 4
    if j["model"] in ARM_C and j["obedience"] not in (None, 1.0):
        return 3
    return 1


def episode_kw(j):
    """Episode options: package C part 4 gives four policies noisy demand input (preregistration-addendum-C.md)."""
    return {"demand_noise": 0.2} if j["set"] == "noise" else {}


def job_kw(j):
    """Model options beyond the policy file: the post-freeze Zhu sensitivity runs random partition ties."""
    return {"tie": "random"} if j["set"] == "zhu_random_ties" else {}


def jobs(plan, man):
    kind, _, rest = plan.partition(":")
    n, _, variant = rest.partition(":")
    settings = SETTINGS if variant != "short" else ["fitted", "p0", "p1"]     # "short": only past the 48-h estimate
    combos = [(s, lvl) for s in man["scenarios"] for lvl in man["levels"]] + [("meetup", "normal")]
    cells = []
    if kind in ("pilot", "full"):
        cells += [("new", s, lvl, b, m, None) for s, lvl in combos for b in settings for m in ROWS_5_TO_8]
        cells += [("new", "meetup", "normal", b, m, None) for b in settings for m in FROZEN]
        cells += [("new", s, lvl, "fitted", m, o) for s, lvl in combos for m in ARM_C for o in OBEDIENCE]
        cells += [("new", s, lvl, b, m, 1.0) for s, lvl in combos for m in ARM_C for b in settings[1:]]
        cells += [("ride", "meetup_ride", "normal", "fitted", m, 1.0 if m in ARM_C else None) for m in TEN]
        starts = [(s, lvl) for s in man["scenarios"] for lvl in man["levels"]]
        if kind == "pilot":
            cells += [("identity", s, lvl, "fitted", m, 0.0) for s, lvl in combos for m in ARM_C]
            cells += [("frozen_rerun", s, lvl, "fitted", m, None) for s, lvl in starts for m in FROZEN]
            # nearest courier in the sweep start cells: the smallest effect of every cell comes from the pilot (section 6)
            cells += [("frozen_rerun", s, lvl, b, "nearest", None) for s, lvl in starts for b in settings[1:]]
        else:
            cells += [("frozen_rerun", s, lvl, b, m, None) for s, lvl in starts for b in settings for m in FROZEN]
        seeds = list(range(1, 31)) if kind == "pilot" else list(range(1001, 1001 + int(n)))
        if kind == "full":                               # the exploratory meet-up rides along at seeds 1001 to 1030
            out = [dict(zip(KEY, (*c, seed))) for seed in seeds for c in cells]
            out += jobs("explore", man)
            # R4: the frozen four in the Q2 cells, and on the scattered start (the time-to-undo reference), on the fresh
            # block; phase 1, after the other phase-1 jobs and before the meet-ups
            fresh = [("fresh_q2", s, lvl, "fitted", m, None) for s in Q2_STARTS for lvl in man["levels"] for m in FROZEN]
            fresh += [("fresh_q2", "meetup", "normal", "fitted", m, None) for m in FROZEN]
            fresh += [("fresh_q2", "scattered", lvl, "fitted", m, None) for lvl in man["levels"] for m in FROZEN]
            out += [dict(zip(KEY, (*c, seed))) for seed in range(FRESH0, FRESH0 + int(n)) for c in fresh]
            return sorted(out, key=lambda j: (phase(j), j["set"] == "fresh_q2", SLOW.get(j["model"], 9)))
    elif kind == "explore":
        cells = [("explore", "meetup_median", "normal", "fitted", m, 1.0 if m in ARM_C else None) for m in TEN]
        seeds = list(range(1001, 1031))
    elif kind == "head":    # E1 and E2 cells at seeds 1001 to 1030, held by every full plan since n >= 30 (section 6)
        return [j for j in jobs("full:30", man) if phase(j) == 1 and j["set"] != "fresh_q2"]
    elif kind.startswith("c_"):                         # package C (preregistration-addendum-C.md)
        levels = man["levels"]
        clustered = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in levels]
        primary = [(s, lvl) for s in ("scattered", "burst") for lvl in levels] + clustered + [("meetup", "normal")]
        ob = lambda m: 1.0 if m in ARM_C else None
        if kind == "c_e6":                              # E6: preferred areas independent of the start
            cells = [("e6", s, lvl, "indep", m, ob(m)) for s, lvl in clustered for m in TEN]
            seeds = list(range(1001, 1151))
        elif kind == "c_stay":                          # part 2: stay without commands, 100% obedience
            cells = [("stay", s, lvl, "fitted", "stay", 1.0) for s, lvl in primary]
            seeds = list(range(1001, 1151))
        elif kind == "c_noise":                         # part 4: noisy demand input
            cells = [("noise", s, lvl, "fitted", m, ob(m)) for s, lvl in primary for m in ("forecast", "li", "zhu", "jusup")]
            seeds = list(range(1001, 1031))
        elif kind == "c_ashkrof":                       # part 3: Ashkrof-coherent behavior, recalibrated
            cells = [("ashkrof", s, lvl, "ashkrof", m, ob(m)) for s, lvl in primary for m in TEN]
            seeds = list(range(1001, 1031))
        elif kind == "c_ashkrof_wide":                  # part 3 again at the wide-grid recalibration
            cells = [("ashkrof_wide", s, lvl, "ashkrofw", m, ob(m)) for s, lvl in primary for m in TEN]
            seeds = list(range(1001, 1031))
        elif kind == "c_budget":                        # training-budget check: retrained policy 1, its 30 seeds
            cells = [("budget", s, lvl, "fitted", m, ob(m)) for s, lvl in primary for m in ("xu", "li", "jahanshahi", "auad", "jusup")]
            seeds = list(range(1001, 1147, 5))
        elif kind == "c_resid":                         # C6 (exploratory, after E6 was seen): homes at the drop-offs
            cells = [("resid", s, lvl, "resid", m, ob(m)) for s, lvl in clustered for m in TEN]
            seeds = list(range(1001, 1031))
        else:
            raise SystemExit(f"unknown plan {plan}")
    elif kind == "zhu_ties":                             # post-freeze sensitivity, outside every family
        cells = [("zhu_random_ties", s, "normal", "fitted", "zhu", 1.0) for s in ("big_cluster", "meetup", "scattered")]
        seeds = list(range(1001, 1031))
    else:
        raise SystemExit(f"unknown plan {plan}")
    out = [dict(zip(KEY, (*c, seed))) for seed in seeds for c in cells]
    return sorted(out, key=lambda j: (phase(j), SLOW.get(j["model"], 9)))   # stable: seeds interleaved within a class


def in_part(j, part):
    """True when job j belongs to `part` = "m:r1,r2" (its seed mod m is one of the remainders); None takes every job.
    Two machines given complementary parts never run the same job (Filipe, 2026-11-05: the PC shares the run)."""
    if not part:
        return True
    m, rs = part.split(":")
    return j["seed"] % int(m) in {int(r) for r in rs.split(",")}


def key(j):
    return tuple(str(j[k]) for k in KEY)


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


def run(j):
    if "ex" not in _EX:
        import torch                                             # every worker the same way (torch changes no value:
        torch.set_num_threads(1)                                 # DECISIONS.md, 2026-11-04)
        from sim.runner import Experiment
        _EX["ex"] = Experiment(ROOT)
    t0 = time.time()
    row, _ = _EX["ex"].episode(j["scenario"], j["level"], j["seed"], j["model"], setting=j["behavior"],
                               obedience=j["obedience"],
                               model_kw={**policy_kw(j["model"], j["seed"], j["obedience"], j["set"]), **job_kw(j)},
                               **episode_kw(j))
    row.update({k: j[k] for k in KEY})
    row["policy_training_seed"] = (j["seed"] - 1) % 5 + 1 if j["model"] in WEIGHTS else None
    row["seconds"] = round(time.time() - t0, 2)
    row["worker"] = os.getpid()
    return row


def only_models(js, models):
    """Jobs of the listed models only ("xu,auad"), or all; the training-budget check evaluates each retrained model as
    soon as its retraining ends (a later run of the whole plan skips the episodes already done)."""
    if not models:
        return js
    keep = set(models.split(","))
    return [j for j in js if j["model"] in keep]


def main():
    out = Path(sys.argv[2])
    plan = sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    part = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "-" else None   # e.g. "3:0" on one machine, "3:1,2" on the other
    models = sys.argv[6] if len(sys.argv) > 6 else None            # e.g. "xu,auad"
    out.mkdir(parents=True, exist_ok=True)
    man = json.loads((ROOT / "scenarios/manifest.json").read_text())
    todo = only_models(jobs(plan, man), models)
    path = out / "episodes.jsonl"
    done = read_done(path)
    todo = [j for j in todo if key(j) not in done and in_part(j, part)]
    print(f"{plan}: {len(todo)} episodes to run, {len(done)} already done, {workers} workers, part {part}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, path.open("a") as fh:
        for i, row in enumerate(pool.imap_unordered(run, todo, chunksize=1)):
            fh.write(json.dumps(row, default=float) + "\n")
            fh.flush()
            if (i + 1) % 200 == 0:
                el = time.time() - t0
                print(f"  {i + 1}/{len(todo)} in {el / 60:.1f} min, {el / (i + 1):.2f} s per episode wall", flush=True)
    runs = out / f"run_{plan.replace(':', '_')}.json"
    log = json.loads(runs.read_text()) if runs.exists() else {"segments": []}
    log["segments"].append({"episodes": len(todo), "workers": workers, "wall_seconds": round(time.time() - t0, 1)})
    runs.write_text(json.dumps(log, indent=1))
    print("done", round((time.time() - t0) / 60, 1), "min", flush=True)


if __name__ == "__main__":
    main()
