"""scripts/package_c_analysis.py and scripts/paper_numbers_c.py: package C parts 1 to 4 (preregistration-addendum-C.md)."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_extension import MAN, rows, write  # noqa: E402

N = 10
CLUSTERED = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in MAN["levels"]]


def _plant(rs, model, field, by, cells=None, series_from=None):
    for r in rs:
        if r["model"] == model and (cells is None or (r["scenario"], r["level"]) in cells):
            if series_from is None:
                r[field] += by
            else:
                s = np.array(r[field])
                s[series_from:] += by
                r[field] = list(s)


@pytest.fixture(scope="module")
def dirs(tmp_path_factory):
    from sim.run_extension import jobs
    t = tmp_path_factory.mktemp("pkgc")
    rng = np.random.default_rng(5)
    full = rows([j for j in jobs(f"full:{N}:short", MAN) if j["set"] in ("new", "frozen_rerun")], rng)
    write(t / "full", full)
    near = pd.DataFrame([r for r in full if r["model"] == "nearest"])
    m = near.groupby(["scenario", "level", "behavior"])[["w1_rule_min", "w1_rule_60min_after_min"]].mean()
    m.columns = ["w1_rule_min_mean", "w1_rule_60min_after_min_mean"]
    m["w1_second_hour_mean"] = m["w1_rule_60min_after_min_mean"]
    (t / "pilot").mkdir()
    m.reset_index().to_csv(t / "pilot" / "pilot_nearest_means.csv", index=False)
    g8 = t / "g8"
    g8.mkdir()
    eight = ["xu", "li", "auad", "zhu", "jusup", "foodmatch", "forecast", "backpressure"]
    pd.DataFrame([{"question": "Q2", "scenario": s, "level": lvl, "model": mo, "class": "does not undo"}
                  for s, lvl in CLUSTERED for mo in eight[:5]]).to_csv(g8 / "classes.csv", index=False)
    pd.DataFrame([{"question": "Q2", "scenario": s, "level": lvl, "model": mo, "class": "does not undo"}
                  for s, lvl in CLUSTERED for mo in eight[5:]]).to_csv(g8 / "classes_e2_fresh.csv", index=False)
    pk = t / "pkgc"
    keep = lambda js: [j for j in js if j["seed"] <= 1000 + N]
    e6 = rows(keep(jobs("c_e6", MAN)), rng)
    _plant(e6, "xu", "w1_rule_60min_after_min", -2.0)                    # planted: Xu undoes under indep
    _plant(e6, "zhu", "w1_rule_series", -1.0, series_from=180)           # planted: Zhu's evening edge
    write(pk / "e6", e6)
    st = rows(keep(jobs("c_stay", MAN)), rng)
    _plant(st, "stay", "w1_rule_min", -1.0)                              # planted: stay lowers W1 by 1
    write(pk / "stay", st)
    no = rows(keep(jobs("c_noise", MAN)), rng)
    q1 = [(s, lvl) for s in ("scattered", "burst") for lvl in MAN["levels"]]
    _plant(no, "li", "w1_rule_min", -2.0, cells=q1)                      # planted: noisy Li prevents on Q1
    ref = {(r["scenario"], r["level"], r["seed"]): r for r in full if r["model"] == "forecast" and r["behavior"] == "fitted"}
    for r in no:                                                         # planted: forecast ignores the noise
        if r["model"] == "forecast":
            r.update({k: v for k, v in ref[(r["scenario"], r["level"], r["seed"])].items()
                      if k not in ("set", "seed", "scenario", "level", "model", "behavior", "obedience")})
    write(pk / "noise", no)
    ak = rows(keep(jobs("c_ashkrof", MAN)), rng)
    _plant(ak, "jusup", "w1_rule_60min_after_min", -2.0)                  # planted: Jusup undoes under ashkrof
    write(pk / "ashkrof", ak)
    rs = rows(keep(jobs("c_resid", MAN)), rng)
    rs = [r for r in rs if r["seed"] <= 1000 + N]
    _plant(rs, "xu", "w1_rule_60min_after_min", -2.0)                    # planted: Xu undoes under resid
    _plant(rs, "nearest", "w1_rule_60min_after_min", -1.0)               # planted: nearest itself lower under resid
    write(pk / "resid", rs)
    aw = rows(keep(jobs("c_ashkrof", MAN)), rng)
    for r in aw:
        r.update(set="ashkrof_wide", behavior="ashkrofw")
    _plant(aw, "li", "w1_rule_60min_after_min", -2.0)                   # planted: Li undoes at the wide-grid point
    write(pk / "ashkrof_wide", aw)
    fit = pk / "ashkrof_fit"
    fit.mkdir()
    (fit / "report.json").write_text(json.dumps({"variant": "ashkrof", "fit": {
        "params": {"p_return": 0.85, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": -2.5}, "objective": 900.0,
        "ci95": {"p_return": [0.75, 0.95], "epoch_s": [42.0, 42.0], "cruise_radius_m": [2000.0, 2000.0], "asc_stay": [-3.0, -2.0]}}}))
    pd.DataFrame({"moment": ["ret_1000_all", "stay_5"], "in_fit": [True, True], "meituan_peak": [0.36, 0.5],
                  "meituan_all_day": [0.41, 0.5], "simulated": [0.30, 0.45]}).to_csv(fit / "moments_table.csv", index=False)
    import shutil
    shutil.copytree(fit, pk / "ashkrof_fit_wide")
    w = json.loads((pk / "ashkrof_fit_wide" / "report.json").read_text())
    w["fit"]["params"]["asc_stay"] = -4.5
    (pk / "ashkrof_fit_wide" / "report.json").write_text(json.dumps(w))
    ref = t / "fitted_fit"
    c7 = pk / "c7_fit_wide"
    ref.mkdir()
    (ref / "report.json").write_text(json.dumps({"variant": "single", "fit": {
        "params": {"p_return": 0.75, "epoch_s": 42.0, "cruise_radius_m": 2000.0, "asc_stay": -3.0}, "objective": 2316.8,
        "ci95": {"p_return": [0.675, 0.825], "epoch_s": [29.4, 42.0], "cruise_radius_m": [2000.0, 2800.0], "asc_stay": [-3.5, -2.0]}}}))
    pd.DataFrame({"moment": ["ret_1000_all", "stay_5"], "in_fit": [True, True], "meituan_peak": [0.36, 0.5],
                  "meituan_all_day": [0.41, 0.5], "simulated": [0.26, 0.48]}).to_csv(ref / "moments_table.csv", index=False)
    shutil.copytree(ref, c7)
    w7 = json.loads((c7 / "report.json").read_text())
    w7["fit"]["ci95"]["asc_stay"] = [-6.0, -2.5]
    (c7 / "report.json").write_text(json.dumps(w7))
    return t


def run(dirs, part, out="out", n=N, extra=()):
    return subprocess.run([sys.executable, str(ROOT / "scripts/package_c_analysis.py"), part, str(dirs / out),
                           "--full", str(dirs / "full"), "--pkgc", str(dirs / "pkgc"), "--pilot", str(dirs / "pilot"),
                           "--g8", str(dirs / "g8"), "--fitted-fit", str(dirs / "fitted_fit"), "--n", str(n),
                           "--n-explore", str(N), *extra], cwd=ROOT, capture_output=True, text=True)


def test_e6_holds_144_contrasts_with_holm_classes_undo_and_the_evening(dirs):
    r = run(dirs, "e6")
    assert r.returncode == 0, r.stderr
    o = dirs / "out"
    con = pd.read_csv(o / "c1_e6_contrasts.csv")
    assert len(con) == 144 and set(con.family) == {"E6"} and set(con.behavior) == {"indep"}
    assert set(con.metric) == {"w1_rule_60min_after_min", "p90_c2d_min"} and "jahanshahi" not in set(con.model)
    assert {"p_holm", "established", "equivalence", "delta"} <= set(con.columns)
    cl = pd.read_csv(o / "c1_e6_classes.csv")
    assert len(cl) == 72 and {"e2_class", "e2_source", "changed"} <= set(cl.columns)
    assert set(cl[cl.model == "xu"]["class"]) == {"undoes at no delivery cost"}
    assert set(cl[cl.model == "foodmatch"]["class"]) == {"does not undo"}
    assert cl[cl.model == "xu"].changed.all() and not cl[cl.model == "li"].changed.any()
    assert set(cl[cl.model == "forecast"].e2_source) == {"E2-fresh (R4)"}
    ud = pd.read_csv(o / "c1_e6_undo.csv")
    assert len(ud) == 9 * 10 and set(ud[ud.model == "xu"].second_hour_check) <= {"holds after the first hour",
                                                                                   "undoes in the first hour, not after"}
    ev = pd.read_csv(o / "c1_e6_evening.csv")
    assert len(ev) == 9 * 9
    assert np.allclose(ev[ev.model == "zhu"]["mean"], -1.0, atol=0.05)
    assert "This research was supported by data provided by Meituan." in (o / "c1_e6.md").read_text()


def test_e6_stops_when_a_cell_is_incomplete(dirs):
    r = run(dirs, "e6", out="out_bad", n=N + 1)
    assert r.returncode != 0 and "not complete" in (r.stderr + r.stdout)


def test_stay_reports_three_contrasts_on_five_metrics_in_the_16_cells(dirs):
    r = run(dirs, "stay")
    assert r.returncode == 0, r.stderr
    st = pd.read_csv(dirs / "out" / "c2_stay.csv")
    assert len(st) == 16 * 3 * 5
    assert set(st.contrast) == {"stay - nearest", "zhu - stay", "jusup - stay"}
    assert set(st.metric) == {"w1_rule_min", "w1_rule_60min_after_min", "w1_2000_2059", "p90_c2d_min", "extra_km_per_order"}
    w = st[st.metric == "w1_rule_min"].groupby("contrast")["mean"].mean()
    assert abs(w["stay - nearest"] + 1.0) < 0.05 and abs(w["zhu - stay"] - 1.0) < 0.05


def test_noise_reads_classes_beside_the_true_input_and_lists_changes(dirs):
    r = run(dirs, "noise")
    assert r.returncode == 0, r.stderr
    o = dirs / "out"
    cl = pd.read_csv(o / "c4_noise_classes.csv")
    assert len(cl) == 4 * 16 and {"class_alt", "class_ref", "changed"} <= set(cl.columns)
    li = cl[(cl.model == "li") & cl.scenario.isin(["scattered", "burst"])]
    assert li.changed.all() and set(li.class_alt) == {"prevents at no delivery cost"}
    assert cl.changed.sum() == 6
    con = pd.read_csv(o / "c4_noise_contrasts.csv")
    sizes = con[con.input == "noisy"].groupby("holm_set").size().to_dict()
    assert sizes == {"E1-shaped": 48, "E2-shaped": 80}


def test_ashkrof_reads_eight_models_lists_changes_and_the_fit(dirs):
    r = run(dirs, "ashkrof")
    assert r.returncode == 0, r.stderr
    o = dirs / "out"
    cl = pd.read_csv(o / "c3_ashkrof_classes.csv")
    assert len(cl) == 8 * 16
    assert cl[cl.changed].model.unique().tolist() == ["jusup"] and cl.changed.sum() == 10
    con = pd.read_csv(o / "c3_ashkrof_contrasts.csv")
    assert con[con.input == "ashkrof"].groupby("holm_set").size().to_dict() == {"E1-shaped": 96, "E2-shaped": 160}
    fit = pd.read_csv(o / "c3_ashkrof_fit.csv")
    p = fit.set_index("parameter")
    assert p.loc["p_return", "ashkrof"] == 0.85 and p.loc["p_return", "fitted"] == 0.75
    assert p.loc["part_time_stay", "ashkrof"] == 0.0
    mo = pd.read_csv(o / "c3_ashkrof_moments.csv")
    assert {"meituan_peak", "simulated_fitted", "simulated_ashkrof"} <= set(mo.columns)


def test_paper_numbers_c_assembles_the_parts_with_the_addendum_hash(dirs):
    o = dirs / "out"
    (o / "c5_tables.md").write_text("# Package C, part 5\n\nThis research was supported by data provided by Meituan.\n\nrows\n")
    r = subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(o), "--addendum", "ed05df2"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    t = (o / "paper-numbers-C.md").read_text()
    assert "ed05df2" in t.split("\n\n")[1] or "ed05df2" in t[:400]
    assert t.count("This research was supported by data provided by Meituan.") >= 2
    for h in ("E6", "stay", "Ashkrof", "noisy", "part 5"):
        assert h.lower() in t.lower()


def test_paper_numbers_c_summarises_part5_from_its_csvs(tmp_path):
    cells = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in ("tight", "normal", "loose")]
    pd.DataFrame([{"scenario": s, "level": lvl, "window": w, "model": m, "mean": v, "lo": v - 0.1, "hi": v + 0.1}
                  for s, lvl in cells for m in ("zhu", "jusup", "xu") for w, v in (("0-60", -0.2), ("60-120", 0.3), ("180-240", -5.0))]
                 ).to_csv(tmp_path / "c5_w1_windows.csv", index=False)
    pd.DataFrame([{"behavior": b, "scenario": s, "level": lvl, "model": m, "mean": v, "lo": v - 0.1, "hi": v + 0.1}
                  for s, lvl in cells for m in ("zhu", "jusup", "xu") for b, v in (("p0", -0.4), ("fitted", -5.0), ("p1", -6.5))]
                 ).to_csv(tmp_path / "c5_evening_by_return.csv", index=False)
    pd.DataFrame([{"scenario": "scattered", "level": "normal", "model": "jusup", "mean_full": 2.0, "mean_truncated": 1.7}]
                 ).to_csv(tmp_path / "c5_evening_truncated.csv", index=False)
    pd.DataFrame([{"family": "E1", "model": "xu", "scenario": "burst", "level": "tight", "metric": "w1_rule_min", "policy": k,
                   "mean": -1.0 - 0.1 * k} for k in range(1, 6)]).to_csv(tmp_path / "c5_per_policy.csv", index=False)
    (tmp_path / "c5_tables.md").write_text("x\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(tmp_path), "--addendum", "ed05df2"], cwd=ROOT, check=True)
    s = (tmp_path / "paper-numbers-C.md").read_text().split("## Summary")[1].split("\n# ")[0]
    assert "zhu -0.20, +0.30, -5.00" in s
    assert "p0 -0.40, fitted -5.00, p1 -6.50" in s
    assert "jusup, scattered, normal: +2.00 to +1.70" in s
    assert "0.40 min" in s


def test_e6_stops_when_the_paper_a_class_of_a_cell_is_missing(dirs, tmp_path):
    import shutil
    bad = tmp_path / "g8"
    shutil.copytree(dirs / "g8", bad)
    fr = pd.read_csv(bad / "classes_e2_fresh.csv")
    fr.iloc[1:].to_csv(bad / "classes_e2_fresh.csv", index=False)
    r = subprocess.run([sys.executable, str(ROOT / "scripts/package_c_analysis.py"), "e6", str(tmp_path / "o"),
                        "--full", str(dirs / "full"), "--pkgc", str(dirs / "pkgc"), "--pilot", str(dirs / "pilot"),
                        "--g8", str(bad), "--n", str(N)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "Paper A class" in (r.stderr + r.stdout)


def test_e6_stops_on_a_missing_minute_in_a_series(dirs, tmp_path):
    import shutil
    pk = tmp_path / "pkgc"
    shutil.copytree(dirs / "pkgc" / "e6", pk / "e6")
    lines = (pk / "e6" / "episodes.jsonl").read_text().splitlines()
    r0 = json.loads(lines[0])
    r0["w1_rule_series"][10] = None
    lines[0] = json.dumps(r0)
    (pk / "e6" / "episodes.jsonl").write_text("\n".join(lines) + "\n")
    r = subprocess.run([sys.executable, str(ROOT / "scripts/package_c_analysis.py"), "e6", str(tmp_path / "o"),
                        "--full", str(dirs / "full"), "--pkgc", str(pk), "--pilot", str(dirs / "pilot"),
                        "--g8", str(dirs / "g8"), "--n", str(N)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "missing minute" in (r.stderr + r.stdout)


def test_noise_counts_episodes_equal_to_the_true_input_and_labels_say_which_w1(dirs):
    assert run(dirs, "noise").returncode == 0
    o = dirs / "out"
    idn = pd.read_csv(o / "c4_noise_identity.csv").set_index("model")
    assert idn.loc["forecast", "episodes_equal_to_true"] == 16 * N and idn.loc["li", "episodes_equal_to_true"] == 0
    t = (o / "c4_noise.md").read_text()
    assert "W1 over 60 min on Q2" in t and "share their bootstrap resamples" in t


def test_e6_markdown_states_the_sign_and_the_numbers_behind_each_class(dirs):
    assert run(dirs, "e6").returncode == 0
    t = (dirs / "out" / "c1_e6.md").read_text()
    assert "model minus nearest courier, in minutes; lower is better" in t
    assert "p90 upper 95%" in t and "nearest median" in t


def test_summary_skips_a_part_whose_markdown_is_missing(tmp_path):
    pd.DataFrame([{"established": True, "n": 150}]).to_csv(tmp_path / "c1_e6_contrasts.csv", index=False)
    pd.DataFrame([{"class": "undoes at no delivery cost", "model": "xu", "changed": True}]).to_csv(tmp_path / "c1_e6_classes.csv", index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(tmp_path), "--addendum", "ed05df2"], cwd=ROOT, check=True)
    s = (tmp_path / "paper-numbers-C.md").read_text().split("## Summary")[1].split("\n# ")[0]
    assert "E6" not in s
    (tmp_path / "c1_e6.md").write_text("x\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(tmp_path), "--addendum", "ed05df2"], cwd=ROOT, check=True)
    s = (tmp_path / "paper-numbers-C.md").read_text().split("## Summary")[1].split("\n# ")[0]
    assert "E6" in s and "n = 150" in s


def test_resid_reads_e6_tables_beside_e6_and_e2_at_the_same_seeds(dirs):
    r = run(dirs, "resid")
    assert r.returncode == 0, r.stderr
    o = dirs / "out"
    con = pd.read_csv(o / "c6_resid_contrasts.csv")
    assert con.groupby("setting").size().to_dict() == {"fitted": 144, "indep": 144, "resid": 144}
    cl = pd.read_csv(o / "c6_resid_classes.csv")
    assert len(cl) == 72 and {"class_resid", "class_indep", "class_fitted"} <= set(cl.columns)
    xu = cl[cl.model == "xu"]
    assert set(xu.class_resid) == {"undoes at no delivery cost"} and set(xu.class_fitted) == {"does not undo"}
    ne = pd.read_csv(o / "c6_resid_nearest.csv")
    assert len(ne) == 9 and {"resid", "indep", "fitted"} <= set(ne.columns)
    assert np.allclose(ne.resid - ne.fitted, -1.0, atol=0.05)
    ud = pd.read_csv(o / "c6_resid_undo.csv")
    assert set(ud.setting) == {"resid", "indep", "fitted"} and len(ud) == 3 * 9 * 10
    ev = pd.read_csv(o / "c6_resid_evening.csv")
    assert set(ev.setting) == {"resid", "indep", "fitted"} and len(ev) == 3 * 9 * 9
    t = (o / "c6_resid.md").read_text()
    assert "exploratory" in t and "declared after the E6 results were seen" in t


def test_paper_numbers_c_has_c6_and_the_wide_bands(tmp_path):
    k = dict(scenario="mixed", level="tight", model="xu")
    pd.DataFrame([{**k, "class_resid": "does not undo", "class_indep": "does not undo", "class_fitted": "undoes at no delivery cost"}]
                 ).to_csv(tmp_path / "c6_resid_classes.csv", index=False)
    (tmp_path / "c6_resid.md").write_text("## C6\n")
    pd.DataFrame([{"parameter": "asc_stay", "old_lo": -3.5, "old_hi": -2.0, "new_lo": -4.5, "new_hi": -2.0,
                   "new_touches_low": False, "new_touches_high": False, "old_point": -3.0, "new_point": -3.0, "point_moved": False}]
                 ).to_csv(tmp_path / "c7_bands.csv", index=False)
    (tmp_path / "c7_bands.md").write_text("## C7\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(tmp_path), "--addendum", "ed05df2"], cwd=ROOT, check=True)
    t = (tmp_path / "paper-numbers-C.md").read_text()
    s = t.split("## Summary")[1].split("\n# ")[0]
    assert "C6 (exploratory" in s and "undo in 0 of 1 under `resid`, 0 under `indep`, 1 under the fitted setting" in s
    assert "C7" in s and "stay constant (beta0) [-3.5, -2] to [-4.5, -2]" in s
    assert "# C6" in t and "# C7" in t


def test_ashkrof_wide_reads_part_3_again_at_the_wide_grid_point(dirs):
    r = run(dirs, "ashkrof_wide")
    assert r.returncode == 0, r.stderr
    o = dirs / "out"
    cl = pd.read_csv(o / "c3w_ashkrof_classes.csv")
    assert len(cl) == 8 * 16 and cl[cl.changed].model.unique().tolist() == ["li"] and cl.changed.sum() == 10
    fit = pd.read_csv(o / "c3w_ashkrof_fit.csv").set_index("parameter")
    assert fit.loc["asc_stay", "ashkrof"] == -4.5
    t = (o / "c3w_ashkrof.md").read_text()
    assert "wide-grid recalibration" in t


def test_review_fixes_of_the_extra_parts(dirs):
    assert run(dirs, "resid").returncode == 0
    o = dirs / "out"
    t = (o / "c6_resid.md").read_text()
    assert "Nearest courier's own W1 over the first 60 min (min" in t and "| fitted | big_cluster | tight | xu |" in t
    assert "scattered start under the fitted setting, for all three settings" in t and "The DQN row is descriptive" in t
    assert set(pd.read_csv(o / "c6_resid_contrasts.csv").family) == {"C6", "E6 at these seeds", "fitted, E6 cells at these seeds"}
    assert run(dirs, "ashkrof_wide").returncode == 0
    w = (o / "c3w_ashkrof.md").read_text()
    assert "beta0 from -2.5 to -4.5" in w and "c3_ashkrof" in w and "ashkrofw class" in w
    assert "eight tested models" in w
    f = pd.read_csv(o / "c3w_ashkrof_fit.csv").set_index("parameter")
    assert f.loc["asc_stay", "fitted_wide_ci_lo"] == -6.0
    assert run(dirs, "ashkrof").returncode == 0
    assert "eight tested models" in (o / "c3_ashkrof.md").read_text()
    subprocess.run([sys.executable, str(ROOT / "scripts/paper_numbers_c.py"), str(o), "--addendum", "ed05df2"], cwd=ROOT, check=True)
    s = (o / "paper-numbers-C.md").read_text().split("## Summary")[1].split("\n# ")[0]
    assert "Ashkrof, first recalibration (its grid cut the beta0 interval)" in s
    assert "Ashkrof, wide-grid recalibration" in s and "Ashkrof setting at the wide-grid recalibration" in s
