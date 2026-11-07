"""X5 end-to-end check of the extension: all ten models on one shared big-cluster start and on the meet-up (seed 501,
normal supply, fitted behavior), each also from the scattered start for the time to undo; the metrics table; one 60 s
four-panel video per arm, and a meet-up check video.

Seed 501 is outside the pilot (1 to 30), full-run (from 1001), training (90000 up) and check (96001 up) seeds.
Learned models run the policy of training seed ((501 - 1) mod 5) + 1 = 1 (the G6 reviewer's rule, fixed in X6).
Arm C models run at full obedience (upper bound) and, as a check, at 0%, where they must equal nearest courier.
W1 counts an idle courier at the cell it is in: a courier relocating counts where it is along its route, hop by hop,
not at its destination; a jumped meet-up courier counts at the point from 19:00.

Videos (big cluster from 17:00, 160x, 60 s, 1920x1080):
  arm A: nearest courier and the three learned arm A models (the four frozen ones are in the S9 video);
  arm B: nearest courier and Auad et al., each from the big cluster and from the scattered start (arm B has one model);
  arm C: nearest courier, Zhu et al. and Jusup et al. at full obedience, and Jusup et al. at 50% obedience;
  meet-up: nearest courier with the jump variant and the ride variant, 18:50 to 20:30.

Usage: python sim/e2e_extension.py <project_root> <out_dir> [workers]
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
sys.path.insert(0, str(ROOT))
from sim import video  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.stats import time_to_undo  # noqa: E402

SEED = 501
ARM = {"nearest": "A", "foodmatch": "A", "forecast": "A", "backpressure": "A", "xu": "A", "li": "A", "jahanshahi": "A",
       "auad": "B", "zhu": "C", "jusup": "C"}
NAMES = {"nearest": "Nearest courier", "foodmatch": "FoodMatch (bundling off)", "forecast": "Forecast-aware",
         "backpressure": "Mirror backpressure", "xu": "Xu et al. (value, KM)", "li": "Li et al. (mean-field AC)",
         "jahanshahi": "Jahanshahi et al. (DQN)", "auad": "Auad et al. (holding)", "zhu": "Zhu et al. (coverage)",
         "jusup": "Jusup et al. (constrained MF)"}
WEIGHTS = {"xu": ("value_path", "xu_value_seed{k}.npz"), "li": ("weights_path", "li_seed{k}.npz"),
           "jahanshahi": ("weights_path", "jahanshahi_seed{k}.npz"), "auad": ("theta_path", "auad_seed{k}.npz"),
           "jusup": ("weights_path", "jusup_seed{k}.pt")}
COLS = ["model", "arm", "scenario", "obedience", "w1_rule_min", "w1_rule_60min_after_min", "time_to_undo_min",
        "p90_c2d_min", "mean_c2d_min", "late_rate", "unassigned_over_30min_share", "undelivered", "orders",
        "idle_km_per_order", "extra_km_per_order", "food_wait_p90_min", "seconds"]
TRACE = {("nearest", "big_cluster", 1.0), ("xu", "big_cluster", 1.0), ("li", "big_cluster", 1.0),
         ("jahanshahi", "big_cluster", 1.0), ("auad", "big_cluster", 1.0), ("nearest", "scattered", 1.0),
         ("auad", "scattered", 1.0), ("zhu", "big_cluster", 1.0), ("jusup", "big_cluster", 1.0),
         ("jusup", "big_cluster", 0.5), ("nearest", "meetup", 1.0), ("nearest", "meetup_ride", 1.0)}
_EX = {}


def policy_kw(model, seed, obedience):
    k = (seed - 1) % 5 + 1
    kw = {}
    if model in WEIGHTS:
        key, fname = WEIGHTS[model]
        kw[key] = ROOT / "models/trained" / fname.format(k=k)
    if model == "jusup":
        kw["q"] = obedience
    return kw


def job(args):
    model, scenario, obedience = args
    if "ex" not in _EX:
        import torch
        torch.set_num_threads(1)
        _EX["ex"] = Experiment(ROOT)
    t0 = time.time()
    trace = (model, scenario, obedience) in TRACE
    row, sim = _EX["ex"].episode(scenario, "normal", SEED, model, trace=trace,
                                 obedience=obedience if ARM[model] == "C" else None,
                                 model_kw=policy_kw(model, SEED, obedience))
    row["seconds"] = round(time.time() - t0, 1)
    row["arm"] = ARM[model]
    row["obedience"] = obedience if ARM[model] == "C" else np.nan
    panel = None
    if trace:
        panel = {"legs": sim.legs, "start": sim.fleet.start,
                 "snapshots": [{"t": s["t"], "w1_min": s["w1_min"]} for s in sim.snapshots]}
    return (model, scenario, obedience), row, panel


def render(spec):
    name, panels, start_s, end_s, title = spec
    ex = Experiment(ROOT)
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    demand = ex.demand["big_cluster"]
    t0 = time.time()
    frames = video.render(OUT / name, ex.city, seg, panels, ex.city.rest, lambda t: demand.expected_pickups(t, t + 1800.0),
                          start_s=start_s, end_s=end_s, title=title)
    return name, frames, round(time.time() - t0, 1)


OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")


def main():
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(m, s, 1.0) for m in ARM for s in ("big_cluster", "meetup", "scattered")]
    jobs += [(m, s, 0.0) for m in ("zhu", "jusup") for s in ("big_cluster", "meetup", "scattered")]   # 0% identity check
    jobs += [("jusup", s, 0.5) for s in ("big_cluster", "scattered")] + [("nearest", "meetup_ride", 1.0)]
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    rows = {k: r for k, r, _ in res}
    panels = {k: p for k, _, p in res if p is not None}
    for (m, s, o), r in rows.items():       # reference: the same model at the same obedience from the scattered start
        if s in ("big_cluster", "meetup"):
            ref = rows[(m, "scattered", o)]["w1_rule_series"]
            r["time_to_undo_min"] = time_to_undo(r["w1_rule_series"], ref, start_min=120 if s == "meetup" else 0)
        else:                                # the ride variant gathers after 19:00, so a time from 19:00 means nothing
            r["time_to_undo_min"] = np.nan
    table = pd.DataFrame(list(rows.values()))
    table.drop(columns=["w1_rule_series"]).to_csv(OUT / "metrics.csv", index=False)
    series = pd.DataFrame({f"{m}|{s}|{o}": r["w1_rule_series"] for (m, s, o), r in rows.items()})
    series.insert(0, "minute_from_1700", np.arange(len(series)))
    series.to_csv(OUT / "w1_series.csv", index=False)
    t = table[COLS].copy()
    t["order"] = t["model"].map({m: i for i, m in enumerate(ARM)})
    t = t.sort_values(["scenario", "obedience", "order"], na_position="first").drop(columns="order")
    md = ["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    md += ["| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in t.to_numpy()]
    (OUT / "metrics.md").write_text("\n".join(md) + "\n")
    checks = {}
    for s in ("big_cluster", "meetup", "scattered"):
        near = rows[("nearest", s, 1.0)]
        for m in ("zhu", "jusup"):
            zero = rows[(m, s, 0.0)]
            checks[f"{m}_0pct_equals_nearest_{s}"] = all(      # the scattered start has no time to undo: NaN on both
                zero[k] == near[k] or (pd.isna(zero[k]) and pd.isna(near[k])) for k in ("w1_rule_min", "w1_rule_60min_after_min", "time_to_undo_min", "p90_c2d_min",
                                             "delivered", "idle_km_per_order")) and np.array_equal(zero["w1_rule_series"], near["w1_rule_series"], equal_nan=True)
    print(json.dumps(checks), flush=True)
    t1 = time.time()

    def pan(m, s, o, label=None):
        return {"name": label or NAMES[m], **panels[(m, s, o)]}

    specs = [
        ("arm_A_big_cluster_60s.mp4", [pan("nearest", "big_cluster", 1.0), pan("xu", "big_cluster", 1.0),
                                       pan("li", "big_cluster", 1.0), pan("jahanshahi", "big_cluster", 1.0)],
         0.0, 9600.0, "Arm A, big cluster"),
        ("arm_B_big_cluster_and_scattered_60s.mp4",
         [pan("nearest", "big_cluster", 1.0, "Nearest courier, big cluster"), pan("auad", "big_cluster", 1.0, "Auad et al., big cluster"),
          pan("nearest", "scattered", 1.0, "Nearest courier, scattered"), pan("auad", "scattered", 1.0, "Auad et al., scattered")],
         0.0, 9600.0, "Arm B"),
        ("arm_C_big_cluster_60s.mp4", [pan("nearest", "big_cluster", 1.0), pan("zhu", "big_cluster", 1.0, "Zhu et al., 100% obedient"),
                                       pan("jusup", "big_cluster", 1.0, "Jusup et al., 100% obedient"),
                                       pan("jusup", "big_cluster", 0.5, "Jusup et al., 50% obedient")],
         0.0, 9600.0, "Arm C, big cluster"),
        ("meetup_check_nearest_jump_and_ride.mp4", [pan("nearest", "meetup", 1.0, "Nearest courier, meet-up (jump)"),
                                                    pan("nearest", "meetup_ride", 1.0, "Nearest courier, meet-up (ride)")],
         6600.0, 12600.0, "Meet-up at 19:00"),
    ]
    todo = [sp for sp in specs if not (OUT / sp[0]).exists()]      # a rerun keeps videos already rendered
    with Pool(max(len(todo), 1)) as pool:
        vids = pool.map(render, todo, chunksize=1)
    old = OUT / "run.json"
    if old.exists():
        vids += [tuple(v.values()) for v in json.loads(old.read_text()).get("videos", []) if v["file"] not in {n for n, _, _ in vids}]
    (OUT / "run.json").write_text(json.dumps({"seed": SEED, "level": "normal", "behavior": "fitted",
                                              "policy_training_seed": (SEED - 1) % 5 + 1, "episodes": len(jobs),
                                              "episode_wall_s": round(t1 - t0, 1), "checks": checks,
                                              "videos": [{"file": n, "frames": f, "seconds": s} for n, f, s in vids],
                                              "total_wall_s": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
