"""R3 addendum (preregistration-extension-addendum-R3.md): equivalence reading of the contrasts that are not established."""
import pandas as pd


def test_equivalence_reads_only_contrasts_that_are_not_established_against_their_smallest_effect():
    from sim.analysis_extension import equivalence
    con = pd.DataFrame({"established": [True, False, False, False, False],
                        "lo": [-0.5, -0.2, -0.6, -0.4, 0.1],
                        "hi": [-0.1, 0.3, 0.2, 0.5, 0.49],
                        "delta": [0.5, 0.5, 0.5, 0.5, 0.5]})
    # established: no reading; inside (-delta, +delta): equivalent; touching or crossing a bound: inconclusive
    assert list(equivalence(con)) == ["", "equivalent within delta", "inconclusive", "inconclusive",
                                      "equivalent within delta"]


def test_part1_equivalence_is_labelled_post_hoc_and_reads_every_family(tmp_path):
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    pd.DataFrame([{"family": "F1", "scenario": "big_cluster", "level": "tight", "model": "foodmatch", "metric": "W1",
                   "delta": 1.0, "mean": 0.1, "lo": -0.2, "hi": 0.4, "p_holm": 0.6, "established": False},
                  {"family": "F2", "scenario": "big_cluster", "level": "tight", "model": "forecast", "metric": "p90",
                   "delta": 1.0, "mean": -2.0, "lo": -2.5, "hi": -1.5, "p_holm": 0.001, "established": True}]
                 ).to_csv(tmp_path / "contrasts.csv", index=False)
    subprocess.run([sys.executable, str(root / "scripts/equivalence_part1.py"), str(tmp_path), str(tmp_path / "out")],
                   check=True, cwd=root)
    eq = pd.read_csv(tmp_path / "out" / "equivalence_part1_post_hoc.csv", keep_default_na=False)
    assert list(eq.equivalence) == ["equivalent within delta", ""]
    assert set(eq.reading) == {"post hoc"}
    assert "post hoc" in (tmp_path / "out" / "equivalence_part1_post_hoc.md").read_text()


def test_equivalence_reads_the_established_flag_from_csv_strings():
    from sim.analysis_extension import equivalence
    con = pd.DataFrame({"established": ["True", "False", "false"], "lo": [-0.5, -0.2, -0.6], "hi": [-0.1, 0.3, 0.2],
                        "delta": [0.5, 0.5, 0.5]})
    assert list(equivalence(con)) == ["", "equivalent within delta", "inconclusive"]
