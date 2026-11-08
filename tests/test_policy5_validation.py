"""Policy 5 validation check (DECISIONS.md, declared at 5a15a35): the run on seeds 95501 to 95503 and its report."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.argv = ["x", str(ROOT), "/tmp/unused"]


def _pv():
    from sim import policy5_validation as pv
    return pv


def test_jobs_cover_the_declared_design():
    pv = _pv()
    js = pv.jobs()
    assert len(js) == 8 * 6 * 4 + 4 * 6 * 4 == 288
    assert {j["model"] for j in js} == {"xu", "li", "jahanshahi", "auad"}
    assert {j["seed"] for j in js} == {95501, 95502, 95503}
    assert {(j["scenario"], j["level"]) for j in js} == {("big_cluster", "normal"), ("scattered", "normal")}
    p5 = [j for j in js if j["policy"] == 5]
    assert sorted({j["checkpoint"] for j in p5}) == [25, 50, 75, 100, 125, 150, 175, 200] and len(p5) == 8 * 6 * 4
    assert {j["checkpoint"] for j in js if j["policy"] != 5} == {200} and {j["policy"] for j in js} == {1, 2, 3, 4, 5}
    trained = {90000 + 1000 * k + i for k in range(1, 6) for i in range(200)} | set(range(91000, 91600))
    assert not {j["seed"] for j in js} & (trained | {95001, 95002, 95003} | set(range(97001, 97006)))


class FakeEx:
    def __init__(self):
        self.calls = []

    def episode(self, scenario, level, seed, model, **kw):
        self.calls.append((scenario, level, seed, model, kw))
        return {"w1_rule_min": 1.0, "p90_c2d_min": 2.0, "unassigned_over_30min_share": 0.0}, None


def test_evaluate_runs_the_training_codes_own_evaluation(tmp_path, monkeypatch):
    pv = _pv()
    fake = FakeEx()
    monkeypatch.setattr(pv, "experiment", lambda: fake)
    monkeypatch.setitem(pv.TRAIN, "li", tmp_path / "li")
    r = pv.evaluate({"model": "li", "policy": 5, "checkpoint": 25, "scenario": "scattered", "level": "normal", "seed": 95502})
    assert fake.calls[-1][:4] == ("scattered", "normal", 95502, "li")
    assert fake.calls[-1][4]["model_kw"] == {"weights_path": tmp_path / "li" / "li_seed5_ep25.npz"}
    assert (r["model"], r["training_seed"], r["episodes"], r["seed"], r["w1_rule_min"]) == ("li", 5, 25, 95502, 1.0)
    assert r["blas_threads"] >= 0
    monkeypatch.setitem(pv.TRAIN, "jahanshahi", tmp_path / "dqn")
    pv.evaluate({"model": "jahanshahi", "policy": 2, "checkpoint": 200, "scenario": "big_cluster", "level": "normal", "seed": 95501})
    assert fake.calls[-1][4]["model_kw"] == {"weights_path": tmp_path / "dqn" / "jahanshahi_seed2_ep200.npz"}
    (tmp_path / "auad").mkdir()
    np.savez_compressed(tmp_path / "auad" / "auad_seed5_ep50.npz", theta=np.arange(3.0), theta_learned=np.zeros(3))
    monkeypatch.setitem(pv.TRAIN, "auad", tmp_path / "auad")
    monkeypatch.setattr(pv, "auad_cost", lambda sim: 123.0)
    r = pv.evaluate({"model": "auad", "policy": 5, "checkpoint": 50, "scenario": "scattered", "level": "normal", "seed": 95503})
    assert fake.calls[-1][3] == "auad" and fake.calls[-1][4]["light"] is False and fake.calls[-1][4]["model_kw"]["cap"] is None
    assert list(fake.calls[-1][4]["model_kw"]["theta"]) == [0.0, 1.0, 2.0] and r["cost"] == 123.0


def _same_call(a, b):
    assert a[:4] == b[:4] and a[4].keys() == b[4].keys()
    for x in a[4]:
        if x == "model_kw":
            assert a[4][x].keys() == b[4][x].keys()
            for y in a[4][x]:
                assert np.array_equal(a[4][x][y], b[4][x][y]) if isinstance(a[4][x][y], np.ndarray) else a[4][x][y] == b[4][x][y]
        else:
            assert a[4][x] == b[4][x]


def test_evaluate_makes_the_same_episode_call_as_the_training_code(tmp_path, monkeypatch):
    pv = _pv()
    from sim import train_auad, train_dqn, train_li, train_xu
    fake = FakeEx()
    monkeypatch.setattr(pv, "experiment", lambda: fake)
    for mod in (train_xu, train_li, train_dqn, train_auad):
        monkeypatch.setitem(mod._EX, "ex", fake)
    case = ("scattered", "normal", 95502)
    job = {"policy": 5, "checkpoint": 50, "scenario": case[0], "level": case[1], "seed": case[2]}
    for m, mod in (("li", train_li), ("jahanshahi", train_dqn)):
        monkeypatch.setitem(pv.TRAIN, m, tmp_path / m)
        monkeypatch.setattr(sys, "argv", ["x", str(ROOT), str(tmp_path / m)])
        pv.evaluate({"model": m, **job})
        mod.evaluate((5, 50, case))
        _same_call(fake.calls[-2], fake.calls[-1])
    (tmp_path / "auad").mkdir()
    np.savez_compressed(tmp_path / "auad" / "auad_seed5_ep50.npz", theta=np.arange(3.0), theta_learned=np.zeros(3))
    monkeypatch.setitem(pv.TRAIN, "auad", tmp_path / "auad")
    monkeypatch.setattr(pv, "auad_cost", lambda sim: 1.0)
    monkeypatch.setattr(train_auad, "episode_cost", lambda sim: 1.0)
    pv.evaluate({"model": "auad", **job})
    train_auad.evaluate((5, 50, case, str(tmp_path / "auad")))
    _same_call(fake.calls[-2], fake.calls[-1])
    V = np.full((2, 2), 50.0)
    monkeypatch.setattr(pv, "xu_table", lambda k, n, *a, **kw: V)
    pv.evaluate({"model": "xu", **job})
    train_xu.evaluate((5, 50, V, case))
    _same_call(fake.calls[-2], fake.calls[-1])


def test_xu_checkpoints_are_refit_from_the_first_n_recorded_peaks(tmp_path, monkeypatch):
    pv = _pv()
    from models.xu_value import fit_value
    rng = np.random.default_rng(1)
    peaks = {i: np.column_stack([rng.integers(0, 4, 6), rng.integers(0, 3, 6), rng.normal(size=6), rng.integers(0, 4, 6),
                                 np.full(6, 5)]).astype(float) for i in range(4)}
    np.savez_compressed(tmp_path / "transitions.npz", **{f"t_5_{i}": t for i, t in peaks.items()})
    V = pv.xu_table(5, 2, tmp_path / "transitions.npz", n_zones=4, n_peaks=4)
    assert np.array_equal(V, fit_value(np.vstack([peaks[0], peaks[1]]), 4))
    fake = FakeEx()
    monkeypatch.setattr(pv, "experiment", lambda: fake)
    monkeypatch.setattr(pv, "xu_table", lambda k, n, *a, **kw: np.full((2, 2), float(n)))
    pv.evaluate({"model": "xu", "policy": 5, "checkpoint": 75, "scenario": "scattered", "level": "normal", "seed": 95501})
    assert fake.calls[-1][3] == "xu" and fake.calls[-1][4]["model_kw"]["value"][0, 0] == 75.0
    pv.evaluate({"model": "xu", "policy": 3, "checkpoint": 200, "scenario": "scattered", "level": "normal", "seed": 95501})
    kept = np.load(ROOT / "models/trained/xu_value_seed3.npz")["V"]
    assert np.array_equal(fake.calls[-1][4]["model_kw"]["value"], kept)


def test_the_run_keeps_one_blas_thread_like_the_curve_rows():
    import os
    code = "import sys; sys.argv=['x', '.', '/tmp/unused']; import sim.policy5_validation, os; print(os.environ['OPENBLAS_NUM_THREADS'])"
    env = {k: v for k, v in os.environ.items() if k not in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["1"]


def _rows(model, k, n, seeds, w1, p90, cost=None):
    return [{"model": model, "training_seed": k, "episodes": n, "scenario": s, "seed": v, "w1_rule_min": w1,
             "p90_c2d_min": p90, **({} if cost is None else {"cost": cost})} for s in ("big_cluster", "scattered") for v in seeds]


def test_report_applies_the_declared_reading_rule(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import policy5_report as rep
    old, new = (95001, 95002, 95003), (95501, 95502, 95503)
    o, n = [], []
    for m in ("xu", "li", "jahanshahi", "auad"):
        c = 100.0 if m == "auad" else None
        for k in range(1, 5):                                    # policies 1 to 4: gaps 0.1 * k in W1, 0.2 in p90
            o += _rows(m, k, 200, old, 5.0 + 0.1 * k, 40.2, c)
            n += _rows(m, k, 200, new, 5.0, 40.0, c)
        gap5 = 0.75 if m == "li" else 0.45                       # li: outside 0.1 to 0.4 widened by 0.10
        for ck in range(25, 201, 25):
            o += _rows(m, 5, ck, old, 5.0 + gap5, 40.2, c)
            n += _rows(m, 5, ck, new, 5.0 + (0.3 if ck == 125 else 0.0), 40.0, c)
    g = rep.gaps(pd.DataFrame(o), pd.DataFrame(n))
    w = g[g.metric == "w1_rule_min"].set_index("model")
    assert abs(w.loc["xu", "gap_policy5"] - 0.45) < 1e-12 and abs(w.loc["xu", "range_lo"] - 0.1) < 1e-12
    assert abs(w.loc["xu", "widened_hi"] - 0.5) < 1e-12 and bool(w.loc["xu", "within"]) and not bool(w.loc["li", "within"])
    assert abs(w.loc["xu", "beyond_range"] - 0.05) < 1e-12 and abs(w.loc["li", "beyond_range"] - 0.35) < 1e-12
    assert g[g.metric == "p90_c2d_min"].beyond_range.eq(0).all()               # inside the range: 0, before widening
    assert rep.outside_count(g) == (4, 8)                                      # W1 of every model lies above 0.1 to 0.4
    assert set(g.metric) == {"w1_rule_min", "p90_c2d_min", "cost"} and g[g.metric == "cost"].model.tolist() == ["auad"]
    assert g[g.metric == "cost"].within.isna().all()
    assert rep.verdict(g) == "affected"
    assert rep.verdict(g[g.model != "li"]) == "unaffected"
    cu = rep.curve(pd.DataFrame(o), pd.DataFrame(n))
    mv = rep.largest_move(cu)
    assert abs(mv.loc["xu", "largest_w1_move_new"] - 0.3) < 1e-12 and mv.loc["xu", "at_checkpoint_new"] == 125


def test_report_writes_the_paper_numbers(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    old, new = (95001, 95002, 95003), (95501, 95502, 95503)
    tr = tmp_path / "train"
    for m, d in (("xu", "xu"), ("li", "li"), ("jahanshahi", "dqn"), ("auad", "auad")):
        (tr / d).mkdir(parents=True)
        c = 100.0 if m == "auad" else None
        o = [r for k in range(1, 6) for ck in range(25, 201, 25) for r in _rows(m, k, ck, old, 5.0, 40.0, c)]
        pd.DataFrame(o).drop(columns="model").to_csv(tr / d / "curve.csv", index=False)
    rows = [r for m in ("xu", "li", "jahanshahi", "auad") for k in range(1, 6) for ck in ([25, 50, 75, 100, 125, 150, 175, 200] if k == 5 else [200])
            for r in _rows(m, k, ck, new, 5.0, 40.0, 100.0 if m == "auad" else None)]
    run = tmp_path / "run"
    run.mkdir()
    (run / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    cal = tmp_path / "cal"
    cal.mkdir()
    (cal / "report.json").write_text(json.dumps({"quantiles": {"c2d_min": {"sim": [1, 2, 3, 4, 35.8957],
                                                                            "meituan_single_order_waves": [1, 2, 3, 4, 41.1]}},
                                                "quantile_levels": [0.1, 0.25, 0.5, 0.75, 0.9]}))
    pd.DataFrame({"level": ["normal"] * 2 + ["tight"], "seed": [201, 202, 201], "p90_c2d_min": [35.0, 36.0, 50.0]}).to_csv(
        cal / "validation_episodes.csv", index=False)
    full = tmp_path / "episodes.jsonl"
    full.write_text("".join(json.dumps({"model": "nearest", "scenario": "scattered", "level": "normal", "behavior": "fitted",
                                        "seed": s, "set": "frozen_rerun", "p90_c2d_min": 35.0 + (s % 2)}) + "\n" for s in range(1001, 1151)))
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/policy5_report.py"), str(out), "--run", str(run), "--train-xu", str(tr / "xu"),
                        "--train-li", str(tr / "li"), "--train-dqn", str(tr / "dqn"), "--train-auad", str(tr / "auad"),
                        "--calibration", str(cal), "--full-episodes", str(full)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for f in ("p5_kept.csv", "p5_gap.csv", "p5_curve.csv", "p5_curve_move.csv", "p5_p90_sources.csv"):
        assert (out / f).exists(), f
    assert len(pd.read_csv(out / "p5_kept.csv")) == 4 * 5 * 2
    t = (out / "paper-numbers-policy5.md").read_text()
    assert "This research was supported by data provided by Meituan." in t and "5a15a35" in t
    assert "Policy 5 reads as **unaffected**" in t
    assert "Checkpoints 25 to 200 give identical rows for Xu et al., Li et al., Deep Q-network and Auad et al." in t
    s = pd.read_csv(out / "p5_p90_sources.csv").set_index("source")
    assert abs(s.loc["calibration, mean of per-episode p90", "value"] - 35.5) < 1e-12
    assert abs(s.loc["study runs, mean of per-episode p90", "value"] - 35.5) < 1e-12
    assert abs(s.loc["calibration, p90 of pooled orders", "value"] - 35.8957) < 1e-12
