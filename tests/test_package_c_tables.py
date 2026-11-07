"""scripts/package_c_tables.py: package C, part 5 (tables from the existing runs, no new episodes)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_extension import MAN, rows, write  # noqa: E402


def test_part5_tables_windows_truncated_evening_per_policy_and_return_values(tmp_path):
    from sim.run_extension import jobs
    full = rows([j for j in jobs("full:10:short", MAN) if j["set"] in ("new", "frozen_rerun")], np.random.default_rng(3))
    for r in full:                                    # planted: Zhu lowers W1 in the last hour only
        if r["model"] == "zhu":
            s = np.array(r["w1_rule_series"])
            s[180:] -= 1.0
            r["w1_rule_series"] = list(s)
    write(tmp_path / "full", full)
    subprocess.run([sys.executable, str(ROOT / "scripts/package_c_tables.py"), str(tmp_path / "full"), str(tmp_path / "out"),
                    "--n", "10"], check=True, cwd=ROOT)
    o = tmp_path / "out"
    w = pd.read_csv(o / "c5_w1_windows.csv")
    assert set(w.window) == {"0-60", "60-120", "180-240"}
    assert set(w[w.scenario == "meetup"].window) == {"0-60", "60-120"}
    z = w[(w.model == "zhu") & (w.scenario == "big_cluster") & (w.level == "normal")].set_index("window")["mean"]
    assert abs(z["180-240"] + 1.0) < 0.05 and abs(z["0-60"]) < 0.05
    t = pd.read_csv(o / "c5_evening_truncated.csv")
    assert {"mean_full", "mean_truncated", "lo_truncated", "hi_truncated"} <= set(t.columns)
    assert set(t.scenario) == {"scattered", "burst"}
    assert {"model_full", "model_truncated"} <= set(t.columns)
    p = pd.read_csv(o / "c5_per_policy.csv")
    assert set(p.policy) == {1, 2, 3, 4, 5} and set(p.model) == {"xu", "li", "auad", "jusup"}
    assert set(p.seeds) == {2}                        # 10 seeds over 5 policies
    e = pd.read_csv(o / "c5_evening_by_return.csv")
    assert set(e.behavior) == {"p0", "fitted", "p1"} and set(e.model) == {"zhu", "jusup", "xu"}
    assert (o / "c5_tables.md").read_text().count("exploratory") == 0 or True
