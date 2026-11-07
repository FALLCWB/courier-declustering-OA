"""Five-agent review (S8), behavior finding 5: the preferred-area pull against the nearest hotspot, with the two
targets at a similar distance from the drop-off (within 500 m of each other), so the random-direction null is
comparable. Meituan, all day, gaps starting more than 2 km from both targets.

Usage: python scripts/pull_check_matched.py <project_root> <behavior_out_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
import sim.behavior_fit as bf  # noqa: E402
from sim.core import idle_moments as im  # noqa: E402

R, MATCH_M = 2000.0, 500.0


def main():
    out = Path(sys.argv[2])
    idle, xy, hot_xy = bf.meituan_gaps(ROOT)
    _, (D, G, H) = bf.meituan_prepare(idle, xy)
    rng = np.random.default_rng(20261104)
    dh = np.linalg.norm(hot_xy[None, :, :] - H[:, None, :], axis=2)
    dd = np.linalg.norm(hot_xy[None, :, :] - D[:, None, :], axis=2)
    d_home = np.linalg.norm(D - H, axis=1)
    # the hotspot outside both 2 km areas whose distance from D is closest to D's distance from home
    cand = np.where((dh > R) & (dd > R), np.abs(dd - d_home[:, None]), np.inf)
    j = cand.argmin(axis=1)
    ok = (cand[np.arange(len(D)), j] <= MATCH_M) & (d_home > R)
    X = hot_xy[j]
    move = np.linalg.norm(G - D, axis=1)
    theta = rng.uniform(0, 2 * np.pi, (len(D), im.NULL_DRAWS))
    Gn = D[:, None, :] + move[:, None, None] * np.stack([np.cos(theta), np.sin(theta)], axis=-1)
    ret_h = np.linalg.norm(G - H, axis=1) <= R
    ret_x = np.linalg.norm(G - X, axis=1) <= R
    exc_h = ret_h - (np.linalg.norm(Gn - H[:, None, :], axis=2) <= R).mean(axis=1)
    exc_x = ret_x - (np.linalg.norm(Gn - X[:, None, :], axis=2) <= R).mean(axis=1)
    d = pd.DataFrame({"c": idle.courier_id.to_numpy()[ok], "home": exc_h[ok], "hot": exc_x[ok], "ret_home": ret_h[ok],
                      "ret_hot": ret_x[ok], "dist_home": d_home[ok], "dist_hot": dd[np.arange(len(D)), j][ok]})
    res = bf.cluster_means(d, ["home", "hot", "ret_home", "ret_hot", "dist_home", "dist_hot"], rng, diff=("home", "hot"))
    res["match_m"] = MATCH_M
    (out / "pull_check_matched.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
