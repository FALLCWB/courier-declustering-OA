"""scripts/preview_figures.py: Python previews of the G8 figures, marked preview (instructions of 2026-11-05, section 4)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_paper_numbers import analysed  # noqa: E402


def test_previews_render_every_g8_figure_marked_preview(tmp_path, monkeypatch):
    d = analysed(tmp_path, monkeypatch)
    rows = []
    for s in ("big_cluster", "meetup", "scattered"):
        for m in ("nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"):
            for t in range(240):
                rows.append({"start": s, "model": m, "minute": t, "mean": 5 + np.sin(t / 30), "lo": 4.5, "hi": 6.5})
    rows += [{**r, "start": "reference_scattered"} for r in rows if r["start"] == "scattered" and r["model"] == "nearest"]
    (d / "w1").mkdir()
    pd.DataFrame(rows).to_csv(d / "w1" / "w1_over_time_extension.csv", index=False)
    out = d / "figures"
    res = subprocess.run([sys.executable, str(ROOT / "scripts/preview_figures.py"), str(d / "out"), str(d / "w1"), str(out)],
                         cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr[-2000:]
    names = {p.name for p in out.glob("*.png")}
    assert names == {"preview_forest_e1_w1.png", "preview_forest_e1_p90.png", "preview_forest_e2_w1_60.png",
                     "preview_forest_e2_p90.png", "preview_forest_e2_fresh_frozen3.png", "preview_w1_over_time_extension.png"}
    assert "preview" in (out / "README.md").read_text().lower()
