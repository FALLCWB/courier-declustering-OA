"""scripts/fit_bands_report.py: C7 and the Ashkrof interval, old bands against wide-grid bands."""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
K = ["p_return", "epoch_s", "cruise_radius_m", "asc_stay"]


def fit_dir(d, params, ci, grid, extra=None):
    d.mkdir(parents=True)
    (d / "report.json").write_text(json.dumps({"fit": {"params": params, "ci95": ci, "objective": 1.0}, **(extra or {})}))
    pd.DataFrame(grid).to_csv(d / "grid.csv", index=False)


def test_bands_report_lists_old_and_new_bands_touching_ends_moves_and_reproduction(tmp_path):
    p0 = {"p_return": 0.75, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": -3.0}
    g_old = [{**p0, "ret_2000_<5": 0.1, "stay_<5": 0.5}, {**p0, "asc_stay": -2.5, "ret_2000_<5": 0.2, "stay_<5": 0.4}]
    fit_dir(tmp_path / "old", p0, {"p_return": [0.675, 0.825], "epoch_s": [29.4, 42.0], "cruise_radius_m": [2000.0, 2800.0],
                                   "asc_stay": [-3.5, -2.0]}, g_old)
    p1 = {**p0, "asc_stay": -3.5}
    g_new = [{**p0, "ret_2000_<5": 0.1, "stay_<5": 0.5}, {**p0, "asc_stay": -2.5, "ret_2000_<5": 0.25, "stay_<5": 0.4},
             {**p1, "ret_2000_<5": 0.3, "stay_<5": 0.3}]
    fit_dir(tmp_path / "new", p1, {"p_return": [0.6, 0.9], "epoch_s": [21.0, 60.0], "cruise_radius_m": [1428.571, 3920.0],
                                   "asc_stay": [-4.5, -2.0]}, g_new,
            {"explored_range": {"p_return": [0.45, 0.975], "epoch_s": [15.0, 117.6], "cruise_radius_m": [714.286, 7056.0],
                                "asc_stay": [-4.5, -0.5]},
             "bands_touch_grid": {"p_return": [False, False], "epoch_s": [False, False], "cruise_radius_m": [False, False],
                                  "asc_stay": [True, False]}, "band_rounds": 8})
    out = tmp_path / "c7_bands"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/fit_bands_report.py"), str(tmp_path / "old"), str(tmp_path / "new"),
                        str(out), "--title", "C7. Fitted behavior", "--note", "The runs keep the frozen values."],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    t = pd.read_csv(f"{out}.csv").set_index("parameter")
    assert list(t.index) == K
    assert t.loc["asc_stay", "old_lo"] == -3.5 and t.loc["asc_stay", "new_lo"] == -4.5
    assert bool(t.loc["asc_stay", "new_touches_low"]) and not bool(t.loc["p_return", "new_touches_low"])
    assert t.loc["asc_stay", "old_point"] == -3.0 and t.loc["asc_stay", "new_point"] == -3.5 and bool(t.loc["asc_stay", "point_moved"])
    assert not bool(t.loc["p_return", "point_moved"])
    md = Path(f"{out}.md").read_text()
    assert "1 of 2 grid points shared with the earlier fit reproduce its moments exactly" in md
    assert "This research was supported by data provided by Meituan." in md
    assert "still touches" in md and "8 rounds" in md
    assert "Point estimate: moved for stay constant (beta0). The runs keep the frozen values." in md


def test_bands_report_marks_fixed_parameters_missing_records_edges_and_sparse_tails(tmp_path):
    p0 = {"p_return": 0.75, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": -3.0}
    ci_old = {"p_return": [0.65, 0.85], "epoch_s": [42.0, 42.0], "cruise_radius_m": [2000.0, 2000.0], "asc_stay": [-4.0, -2.0]}
    fit_dir(tmp_path / "old", p0, ci_old, [{**p0, "stay_<5": 0.5}])
    grid = [{**p0, "p_return": p, "asc_stay": a, "stay_<5": 0.5} for p in (0.65, 0.75, 0.85) for a in (-5.0, -4.5, -4.0, -3.5, -3.0, -2.5)]
    grid += [{**p0, "asc_stay": -5.5, "stay_<5": 0.5}]                     # a tail value tried at one combination only
    ci = {"p_return": [0.65, 0.85], "epoch_s": [42.0, 42.0], "cruise_radius_m": [2000.0, 2000.0], "asc_stay": [-5.0, -3.5]}
    fit_dir(tmp_path / "a", p0, ci, grid, {"explored_range": {"p_return": [0.65, 0.85], "epoch_s": [42.0, 42.0],
            "cruise_radius_m": [2000.0, 2000.0], "asc_stay": [-5.5, -2.5]}, "band_rounds": 1,
            "bands_touch_grid": {"p_return": [False, False], "asc_stay": [False, False]}})
    fit_dir(tmp_path / "b", p0, ci, grid)                                   # an older report: no touch record
    for d in ("a", "b"):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/fit_bands_report.py"), str(tmp_path / "old"), str(tmp_path / d),
                            str(tmp_path / f"out_{d}"), "--title", "T"], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    ta = pd.read_csv(tmp_path / "out_a.csv").set_index("parameter")
    assert ta.loc["epoch_s", "touches"] == "fixed" and ta.loc["asc_stay", "touches"] == "no"
    assert ta.loc["asc_stay", "low_end_one_value_from_edge"] and not ta.loc["asc_stay", "high_end_one_value_from_edge"]
    assert ta.loc["asc_stay", "points_at_lowest_value"] == 1
    tb = pd.read_csv(tmp_path / "out_b.csv").set_index("parameter")
    assert tb.loc["asc_stay", "touches"] == "not recorded"
    ma = (tmp_path / "out_a.md").read_text()
    assert "one value from the edge" in ma and "not comparable across fits" in ma and "Filipe" not in ma
