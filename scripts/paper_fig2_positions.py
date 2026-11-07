"""Courier positions for Paper A's Fig. 2 (FIGURES-SPEC.md, 2026-11-06): nearest courier and Jusup et al. (constrained
mean-field RL, 100% obedient) on the mixed start, normal supply, fitted behavior, seed 1001, at 17:00, 17:30 and
18:00, and the road network. One traced episode per model; the per-courier rows stay out of git and out of the
reviewer's folder (only the rendered map leaves).

Usage: python scripts/paper_fig2_positions.py <out_dir>
Writes fig2_positions.csv (model, minute, lng, lat, state) and fig2_roads.csv (lng1, lat1, lng2, lat2).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.blas import pin  # noqa: E402

pin()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(1)
from sim import video  # noqa: E402
from sim.run_extension import policy_kw  # noqa: E402
from sim.runner import Experiment  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MINUTES = (0, 30, 60)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    ex = Experiment(ROOT)
    rows = []
    for m, ob in (("nearest", None), ("jusup", 1.0)):
        _, sim = ex.episode("mixed", "normal", 1001, m, trace=True, obedience=ob, model_kw=policy_kw(m, 1001, ob))
        lng, lat, st = video.positions(ex.city, sim.legs, np.asarray(sim.fleet.start), np.array([60.0 * x for x in MINUTES]))
        for k, minute in enumerate(MINUTES):
            rows += [{"model": m, "minute": minute, "lng": float(a), "lat": float(b), "state": s}
                     for a, b, s in zip(lng[k], lat[k], st[k])]
    pd.DataFrame(rows).to_csv(out / "fig2_positions.csv", index=False)
    seg = video.road_segments(ROOT / "sim/city/curitiba")
    pd.DataFrame(seg.reshape(len(seg), 4), columns=["lng1", "lat1", "lng2", "lat2"]).to_csv(out / "fig2_roads.csv",
                                                                                          index=False)


if __name__ == "__main__":
    main()
