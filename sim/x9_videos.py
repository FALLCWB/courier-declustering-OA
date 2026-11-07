"""X9: videos per arm for the big cluster, the meet-up and the scattered start (Paper A visual material).

Seed 1001 (the first evaluation seed), normal supply, fitted behavior; learned models run the policy of training seed
((1001 - 1) mod 5) + 1 = 1. Panels per arm: A, nearest courier and the three learned arm A models (the frozen three
are in the S9 video); B, nearest courier and Auad et al.; C, nearest courier, Zhu et al. and Jusup et al. at full
obedience, and Jusup et al. at 50%. Clock: 17:00 to 19:40 for the starts, 18:50 to 20:30 for the meet-up; 160x.
W1 counts an idle courier at the cell it is in; a relocating courier counts where it is along its route.

Usage: python sim/x9_videos.py <project_root> <out_dir> [workers]
A rerun keeps videos and stills already rendered. Stills: the ten models on the big cluster at 17:00 and 18:00
(panel_<model>_000.png and panel_<model>_060.png), arm C at 100%.
"""
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402
if __name__ == "__main__":
    pin()  # S8's BLAS threads, set before numpy loads (sim/blas.py)
import json
import time
from multiprocessing import Pool

ROOT = Path(sys.argv[1]).resolve() if __name__ == "__main__" else Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[2]) if __name__ == "__main__" and len(sys.argv) > 2 else Path(".")
SEED = 1001
NAMES = {"nearest": "Nearest courier", "foodmatch": "FoodMatch (bundling off)", "forecast": "Forecast-aware matching",
         "backpressure": "Mirror backpressure", "xu": "Xu et al. (value, KM)", "li": "Li et al. (mean-field AC)",
         "jahanshahi": "Jahanshahi et al. (DQN)", "auad": "Auad et al. (holding)", "zhu": "Zhu et al., 100% obedient",
         "jusup": "Jusup et al., 100% obedient"}
ARMS = {"A": [("nearest", None), ("xu", None), ("li", None), ("jahanshahi", None)],
        "B": [("nearest", None), ("auad", None)],
        "C": [("nearest", None), ("zhu", 1.0), ("jusup", 1.0), ("jusup", 0.5)]}
STARTS = {"big_cluster": (0.0, 9600.0, "big cluster at 17:00"), "meetup": (6600.0, 12600.0, "meet-up at 19:00"),
          "scattered": (0.0, 9600.0, "scattered start")}
STILL_MINUTES = (0, 60)   # stills at 17:00 and 18:00 (instructions of 2026-11-05, section 4)
_EX = {}


def still_panels():
    """The ten models on the big cluster for the stills, arm C at 100% obedience."""
    return [(m, 1.0 if m in ("zhu", "jusup") else None) for m in
            ("nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup")]


def videos():
    """(file, start, [(model, obedience)], clock window, title) for the nine videos."""
    out = []
    for arm, panels in ARMS.items():
        for s, (t0, t1, label) in STARTS.items():
            out.append((f"arm_{arm}_{s}_seed{SEED}.mp4", s, panels, t0, t1, f"Arm {arm}, {label}, seed {SEED}"))
    return out


def trace(args):
    model, scenario, obedience = args
    from sim.run_extension import policy_kw
    if "ex" not in _EX:
        import torch
        torch.set_num_threads(1)
        from sim.runner import Experiment
        _EX["ex"] = Experiment(ROOT)
    row, sim = _EX["ex"].episode(scenario, "normal", SEED, model, trace=True, obedience=obedience,
                                 model_kw=policy_kw(model, SEED, obedience))
    return (model, scenario, obedience), {"legs": sim.legs, "start": sim.fleet.start,
                                          "snapshots": [{"t": s["t"], "w1_min": s["w1_min"]} for s in sim.snapshots]}


def render(spec):
    from sim import video
    from sim.runner import Experiment
    name, scenario, panels, t0, t1, title, traces = spec
    ex = Experiment(ROOT)
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    demand = ex.demand[scenario]
    started = time.time()
    pan = [{"name": NAMES[m] if not (m == "jusup" and o == 0.5) else "Jusup et al., 50% obedient", **traces[(m, scenario, o)]}
           for m, o in panels]
    frames = video.render(OUT / name, ex.city, seg, pan, ex.city.rest, lambda t: demand.expected_pickups(t, t + 1800.0),
                          start_s=t0, end_s=t1, title=title)
    return name, frames, round(time.time() - started, 1)


def still(spec):
    """One model's panel on the big cluster at 17:00 and 18:00, in the style of the Part 1 stills."""
    from sim import video
    from sim.runner import Experiment
    m, o, tr = spec
    ex = Experiment(ROOT)
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    demand = ex.demand["big_cluster"]
    return video.stills(OUT / f"panel_{m}_{{minute:03d}}.png", ex.city, seg, [{"name": NAMES[m], **tr}], ex.city.rest,
                        lambda t: demand.expected_pickups(t, t + 1800.0), minutes=STILL_MINUTES)


def main():
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [v for v in videos() if not (OUT / v[0]).exists()]
    stills_todo = [(m, o) for m, o in still_panels() if not (OUT / f"panel_{m}_060.png").exists()]
    need = sorted({(m, v[1], o) for v in todo for m, o in v[2]} | {(m, "big_cluster", o) for m, o in stills_todo}, key=str)
    with Pool(workers) as pool:
        traces = dict(pool.map(trace, need, chunksize=1))
        pool.map(still, [(m, o, traces[(m, "big_cluster", o)]) for m, o in stills_todo], chunksize=1)
        done = pool.map(render, [(*v, traces) for v in todo], chunksize=1)
    log = OUT / "run.json"
    old = json.loads(log.read_text())["videos"] if log.exists() else []
    log.write_text(json.dumps({"seed": SEED, "level": "normal", "behavior": "fitted", "policy_training_seed": 1,
                               "videos": old + [{"file": n, "frames": f, "seconds": s} for n, f, s in done]}, indent=1))


if __name__ == "__main__":
    main()
