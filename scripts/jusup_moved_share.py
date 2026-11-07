"""G6 evidence (reviewer pre-note): share of free couriers that the trained Jusup et al. policy moves at each 20-minute
step, per training seed, on the validation seeds 95001 to 95003 (big cluster and scattered, normal supply, full
obedience). Usage: python scripts/jusup_moved_share.py <project_root> <training_dir>
Writes <training_dir>/moved_share.csv (one row per policy call) and prints the mean share and the policy's mean p."""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
import models.jusup_mf as jm  # noqa: E402
from sim.runner import Experiment  # noqa: E402
from sim.train_xu import SEEDS, VALID  # noqa: E402

ORIG = jm.JusupMF.relocate


def logged(self, v):
    cmds = ORIG(self, v)
    if v.t >= self.next_t - jm.STEP_S and (not self.log or self.log[-1][0] != v.t) and self.next_t - v.t == jm.STEP_S:
        self.log.append((v.t, len(v.couriers), len(cmds)))
    return cmds


def run(job):
    k, (scenario, level, seed) = job
    torch.set_num_threads(1)
    jm.JusupMF.relocate = logged
    jm.JusupMF.log = None
    e = Experiment(ROOT)
    holder = {}
    orig_init = jm.JusupMF.__init__

    def init(self, *a, **kw):
        orig_init(self, *a, **kw)
        self.log = []
        holder["pol"] = self
    jm.JusupMF.__init__ = init
    e.episode(scenario, level, seed, "jusup", obedience=1.0, light=True,
              model_kw={"weights_path": ROOT / f"models/trained/jusup_seed{k}.pt", "q": 1.0})
    return [{"training_seed": k, "scenario": scenario, "seed": seed, "t_min": t / 60.0, "free_obedient": n, "moved": m,
             "share": m / n if n else np.nan} for t, n, m in holder["pol"].log]


if __name__ == "__main__":
    with Pool(6) as pool:
        rows = [r for res in pool.map(run, [(k, c) for k in SEEDS for c in VALID]) for r in res]
    d = pd.DataFrame(rows)
    d.to_csv(Path(sys.argv[2]) / "moved_share.csv", index=False)
    print(d.groupby(["scenario", "training_seed"]).share.mean().unstack().round(3))
    print("overall mean share by scenario:", d.groupby("scenario").share.mean().round(3).to_dict())
    print("share by 20-min step (mean over seeds):")
    print(d.groupby(["scenario", "t_min"]).share.mean().unstack(0).round(3).to_string())
