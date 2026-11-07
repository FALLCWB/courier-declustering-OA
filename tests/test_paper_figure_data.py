"""scripts/paper_figure_data.py: the data behind Paper A's Figs. 1 and 3 to 5 (FIGURES-SPEC.md, 2026-11-06), from the
committed aggregates; Fig. 2's positions come from a traced episode and are not tested here."""
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_figure_data_hold_every_cell_and_model_of_the_spec(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_figure_data.py"), str(tmp_path)], check=True, cwd=ROOT)
    f1 = pd.read_csv(tmp_path / "fig1_w1_evening.csv")
    assert set(f1.start) == {"big_cluster", "meetup", "reference_scattered"} and "jahanshahi" not in set(f1.model)
    assert set(f1[f1.start == "big_cluster"].model) == {"nearest", "foodmatch", "forecast", "backpressure", "xu", "li",
                                                        "auad", "zhu", "jusup"}
    f3 = pd.read_csv(tmp_path / "fig3_f1_forest.csv")
    assert len(f3) == 3 * 2 * 15 and set(f3.metric) == {"W1", "p90"}
    f4 = pd.read_csv(tmp_path / "fig4_q1_forest.csv")
    assert len(f4) == 5 * 2 * 6 and set(f4.model) == {"xu", "li", "auad", "zhu", "jusup"}
    f5 = pd.read_csv(tmp_path / "fig5_q2_forest.csv")
    assert len(f5) == 8 * 2 * 10
    assert set(f5[f5.model.isin(["foodmatch", "forecast", "backpressure"])].seeds) == {"5001-5150"}
    for f in (f3, f4, f5):
        assert {"scenario", "level", "model", "metric", "mean", "lo", "hi", "delta", "established", "group"} <= set(f.columns)
        assert set(f.established.astype(str)) <= {"True", "False"}
