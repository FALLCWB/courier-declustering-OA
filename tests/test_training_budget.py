"""Training-budget check (preregistration-addendum-budget.md): the training scripts keep their frozen behavior by default,
and the budget driver retrains policy 1 with 600 peaks into models/trained_budget/ without touching models/trained/."""
import importlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))


def _mod(name):
    sys.argv = ["x", str(ROOT), "/tmp/unused"]
    return importlib.import_module(name)


def test_trainers_default_to_the_frozen_settings():
    xu, li, dqn, auad, jus = (_mod(f"sim.train_{m}") for m in ("xu", "li", "dqn", "auad", "jusup"))
    for m in (xu, li, dqn, auad, jus):
        assert m.TRAINED == ROOT / "models/trained"
    assert li.EPISODES == li.ANNEAL == 200 and dqn.EPISODES == dqn.ANNEAL == 200
    assert 0 not in li.CHECKPOINTS and 0 not in dqn.CHECKPOINTS and 0 not in auad.CHECKPOINTS
    assert (jus.EPOCHS, jus.PATIENCE, jus.CKPT_EVERY, jus.LOG_START) == (1000, 100, None, False)


def test_li_temperature_holds_its_final_value_after_the_anneal_horizon():
    li = _mod("sim.train_li")
    old = lambda i: 1.0 + (0.01 - 1.0) * i / (200 - 1)                       # the frozen formula, 200 peaks
    assert all(li.temperature(i) == old(i) for i in range(200))
    assert li.temperature(199) == li.temperature(450) == li.temperature(599)


def test_li_learner_logs_the_actor_loss_and_the_episode_reward():
    from models.li_meanfield import BATCH, MAX_POOL, N_ACT, N_OBS, Learner
    lr = Learner(seed=3)
    x, ax = np.zeros(N_OBS + 1 + N_ACT), np.zeros((MAX_POOL, N_OBS + N_ACT))
    am = np.zeros(MAX_POOL, bool)
    am[:3] = True
    lr.act(0, x, 1.5, ax, am, 0, None)
    lr.act(1, x, 2.0, ax, am, 1, None)
    lr.end_episode()
    assert lr.rewards == [3.5]
    rng = np.random.default_rng(0)
    n = BATCH
    m = lr.mem
    m.x[:n] = rng.normal(size=(n, N_OBS + 1 + N_ACT))
    m.r[:n] = rng.normal(size=n)
    m.ax[:n] = rng.normal(size=(n, MAX_POOL, N_OBS + N_ACT))
    m.amask[:n, :4] = True
    m.nx[:n] = rng.normal(size=(n, MAX_POOL, N_OBS + 1 + N_ACT))
    m.nmask[:n, :4] = True
    m.n = n
    lr.update()
    assert len(lr.losses) == len(lr.actor_losses) == 1 and np.isfinite(lr.actor_losses[0])


def test_dqn_learner_logs_the_episode_reward():
    from models.jahanshahi_dqn import HIDDEN, Learner
    from sim.nn import MLP
    lr = Learner(MLP([1, *HIDDEN, 1], seed=1), seed=1, total_updates=10)
    lr.observe(np.array([0.1, 0.2]), 0.1, 30.0)
    lr.observe(np.array([0.3]), 0.3, 12.0)
    lr.end_episode()
    assert lr.rewards == [42.0]


def test_budget_driver_retrains_policy_1_for_600_peaks_into_its_own_folder():
    sys.argv = ["x", str(ROOT), "/tmp/unused"]
    from sim import train_budget as tb
    li = _mod("sim.train_li")
    tb.configure(li, "li")
    assert li.SEEDS == [1] and li.EPISODES == 600 and li.ANNEAL == 200
    assert li.CHECKPOINTS == list(range(0, 601, 25)) and li.TRAINED == ROOT / "models/trained_budget"
    jus = _mod("sim.train_jusup")
    tb.configure(jus, "jusup")
    assert (jus.SEEDS, jus.EPOCHS, jus.PATIENCE, jus.CKPT_EVERY, jus.LOG_START) == ([1], 3000, 300, 100, True)
    assert jus.TRAINED == ROOT / "models/trained_budget"
    importlib.reload(li)
    importlib.reload(jus)                                                   # the defaults come back for other tests


def test_value_table_change_between_checkpoints():
    sys.argv = ["x", str(ROOT), "/tmp/unused"]
    from sim import train_budget as tb
    V0, V1, V2 = np.zeros((2, 3)), np.ones((2, 3)), np.ones((2, 3)) * 1.5
    ch = tb.table_changes({0: V0, 25: V1, 50: V2})
    assert [c["checkpoint"] for c in ch] == [0, 25, 50]
    assert np.isnan(ch[0]["frobenius"]) and ch[1]["max_abs"] == 1.0 and abs(ch[2]["frobenius"] - np.sqrt(6 * 0.25)) < 1e-12


def test_budget_plan_runs_the_retrained_policy_1_of_the_five_models_at_the_seeds_of_policy_1():
    from test_analysis_extension import MAN
    from sim.run_extension import jobs, policy_kw
    js = jobs("c_budget", MAN)
    seeds = list(range(1001, 1147, 5))
    assert len(seeds) == 30 and len(js) == 5 * 16 * 30
    assert {j["model"] for j in js} == {"xu", "li", "jahanshahi", "auad", "jusup"} and {j["set"] for j in js} == {"budget"}
    assert sorted({j["seed"] for j in js}) == seeds and {j["behavior"] for j in js} == {"fitted"}
    assert {j["obedience"] for j in js if j["model"] == "jusup"} == {1.0}
    kw = policy_kw("li", 1006, None, "budget")
    assert kw["weights_path"] == ROOT / "models/trained_budget/li_seed1.npz"
    assert policy_kw("li", 1006, None)["weights_path"] == ROOT / "models/trained/li_seed1.npz"


def test_budget_driver_trains_with_one_blas_thread_like_the_frozen_training():
    import subprocess
    code = "import sys; sys.argv=['x', '.', '/tmp/unused']; import sim.train_budget, os; print(os.environ['OPENBLAS_NUM_THREADS'], os.environ['OMP_NUM_THREADS'])"
    env = {k: v for k, v in __import__("os").environ.items() if k not in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["1", "1"]


def test_a_run_can_be_limited_to_some_models():
    from test_analysis_extension import MAN
    from sim.run_extension import jobs, only_models
    js = jobs("c_budget", MAN)
    sel = only_models(js, "xu,auad")
    assert {j["model"] for j in sel} == {"xu", "auad"} and len(sel) == 2 * 16 * 30
    assert only_models(js, None) == js
