"""Data behind Paper A's figures (FIGURES-SPEC.md, 2026-11-06), from the committed aggregates; the figures are drawn in
MATLAB (figures/paper/*.m). Fig. 2 (the fleet on the map) needs a traced episode: scripts/paper_fig2_positions.py.

Usage: python scripts/paper_figure_data.py <out_dir>
Writes fig1_w1_evening.csv, fig3_f1_forest.csv, fig4_q1_forest.csv and fig5_q2_forest.csv. Every row is an aggregate
over seeds. Groups follow the spec: untrained assignment (FoodMatch, forecast-aware matching, mirror backpressure),
learned assignment and holding (Xu, Li, Auad), moving idle couriers (Zhu, Jusup, at 100% obedience). The DQN is in no
figure (it stays within 0.1 min of nearest courier).
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
G8 = ROOT / "avaliacao/20261105-1405-g8-results"
FIRST = ROOT / "avaliacao/20261102-2130-part1-untrained/results"
GROUP = {"foodmatch": "untrained", "forecast": "untrained", "backpressure": "untrained", "xu": "learned", "li": "learned",
         "auad": "learned", "zhu": "moving", "jusup": "moving"}
COLS = ["group", "scenario", "level", "model", "metric", "mean", "lo", "hi", "delta", "established", "seeds"]


def forest(df, seeds):
    d = df.copy()
    d["group"] = d.model.map(GROUP)
    d["established"] = d.established.astype(str).str.lower().eq("true")
    d["seeds"] = d["seeds"] if "seeds" in d else seeds
    return d[COLS]


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    w = pd.read_csv(G8 / "w1/w1_over_time_extension.csv")
    w = w[w.start.isin(["big_cluster", "meetup", "reference_scattered"]) & (w.model != "jahanshahi")]
    w.to_csv(out / "fig1_w1_evening.csv", index=False)

    f1 = pd.read_csv(FIRST / "contrasts.csv")
    f1 = f1[f1.family == "F1"]
    forest(f1, "1001-1030").to_csv(out / "fig3_f1_forest.csv", index=False)

    con = pd.read_csv(G8 / "analysis/contrasts.csv")
    e1 = con[(con.family == "E1") & con.model.isin(["xu", "li", "auad", "zhu", "jusup"])]
    forest(e1, "1001-1150").to_csv(out / "fig4_q1_forest.csv", index=False)

    fr = pd.read_csv(G8 / "analysis/contrasts_e2_fresh.csv")          # R4: the frozen three from the fresh block
    frozen = fr[fr.model.isin(["foodmatch", "forecast", "backpressure"])]
    new = con[(con.family == "E2") & con.model.isin(["xu", "li", "auad", "zhu", "jusup"])]
    pd.concat([forest(frozen, "5001-5150"), forest(new, "1001-1150")]).to_csv(out / "fig5_q2_forest.csv", index=False)


if __name__ == "__main__":
    main()
