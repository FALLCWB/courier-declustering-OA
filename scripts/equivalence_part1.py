"""R3 addendum: the equivalence reading applied to the first round's (Part 1) contrasts, labelled post hoc.

The Part 1 results were seen before the addendum, so this reading is post hoc (preregistration-extension-addendum-R3.md).
Every Part 1 family (F1 to F4) is read: a contrast that is not established is "equivalent within delta" when its 95%
bootstrap interval lies inside (-delta, +delta), with delta the pre-registered smallest effect of the row (10% of
nearest courier's mean W1 in the cell; 1.0 min for p90), else "inconclusive"; an established contrast gets no reading.

Usage: python scripts/equivalence_part1.py <first_round_results_dir> <out_dir>
Writes equivalence_part1_post_hoc.csv and equivalence_part1_post_hoc.md in out_dir.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.analysis_extension import equivalence  # noqa: E402


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    con = pd.read_csv(src / "contrasts.csv")
    con["established"] = con.established.astype(str).str.lower() == "true"
    con["equivalence"] = equivalence(con)
    con["reading"] = "post hoc"
    cols = [c for c in ["family", "scenario", "level", "behavior", "layout", "scale", "time_mult", "model", "metric",
                        "delta", "n", "mean", "lo", "hi", "p_holm", "established", "equivalence", "reading"] if c in con]
    con[cols].to_csv(out / "equivalence_part1_post_hoc.csv", index=False)
    t = con.assign(label=con.equivalence.replace("", "established")).pivot_table(
        index=["family", "metric"], columns="label", values="model", aggfunc="count", fill_value=0)
    L = ["# Part 1 contrasts, equivalence reading (post hoc)", "",
         "This research was supported by data provided by Meituan.", "",
         "Post hoc: the Part 1 results were seen before the R3 addendum (`preregistration-extension-addendum-R3.md`). "
         "A contrast that is not established reads \"equivalent within delta\" when its 95% bootstrap interval lies inside "
         "(-delta, +delta), with delta the row's pre-registered smallest effect (10% of nearest courier's mean W1 in the "
         "cell; 1.0 min for p90), else \"inconclusive\". It changes no class and no Holm result.", "",
         "| Family | Metric | " + " | ".join(t.columns) + " |", "|---|---|" + "---|" * len(t.columns)]
    L += [f"| {f} | {m} | " + " | ".join(str(int(v)) for v in r) + " |" for (f, m), r in t.iterrows()]
    (out / "equivalence_part1_post_hoc.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
