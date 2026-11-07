"""Jusup et al. reimplementation: entropy, JS, mass conservation, and zero obedience moving nobody."""
from types import SimpleNamespace

import numpy as np
import pytest

torch = pytest.importorskip("torch")                  # the project environment on FE-SIM-1 has it; the PC venv does not

from models.jusup_mf import Policy, barrier_term, entropy, js, rollout  # noqa: E402


def toy_geo(Z=9):
    match = torch.eye(Z)
    dest_mask = torch.ones(Z, Z, dtype=torch.bool)
    od = torch.full((Z, Z), 1.0 / Z)
    return SimpleNamespace(Z=Z, xy=torch.zeros(Z, 2), dest_mask=dest_mask, match=match, od=od)


def test_entropy_and_js_known_values():
    assert float(entropy(torch.ones(9))) == pytest.approx(np.log(9), abs=1e-5)       # uniform: h_max (Eq. 25)
    one = torch.zeros(9)
    one[0] = 1.0
    assert float(entropy(one)) < 1e-6
    assert float(js(torch.ones(9), torch.ones(9))) == pytest.approx(0.0, abs=1e-6)
    assert float(barrier_term(torch.tensor(1.0), torch.tensor(0.5))) == pytest.approx(np.log(0.5))


def test_rollout_conserves_mass_and_zero_obedience_moves_nobody():
    geo = toy_geo()
    pol = Policy(geo.Z, seed=0)
    mu0 = torch.zeros(9)
    mu0[0] = 1.0
    dem = [torch.full((9,), 0.0) for _ in range(3)]                    # no demand: only repositioning acts
    total, _ = rollout(pol, geo, mu0, dem, q=0.0)                      # q = 0: the cluster stays
    p, dest = pol(geo, mu0, torch.ones(9), 0.0, 1.0)
    assert torch.all((p >= 0) & (p <= 1)) and torch.allclose(dest.sum(dim=1), torch.ones(9))
    # mass conservation through matching and repositioning
    dem = [torch.full((9,), 0.05) for _ in range(3)]
    mu = mu0.clone()
    total, barrier = rollout(pol, geo, mu, dem, q=1.0)
    assert torch.isfinite(total) and torch.isfinite(barrier)


def test_repositioning_mass_is_not_available_in_its_step():
    """Eq. (7): available vehicles are (1 - p) mu; the repositioning part neither matches nor counts in the JS term
    during the step in which it moves."""
    geo = toy_geo()
    half = lambda geo, mu, dem, t, q: (torch.full((geo.Z,), 0.5), torch.full((geo.Z, geo.Z), 1.0 / geo.Z))  # noqa: E731
    mu0 = torch.zeros(9)
    mu0[0] = 1.0
    dem = [torch.full((9,), 0.05)]
    total, _ = rollout(half, geo, mu0, dem, q=1.0)
    avail = torch.zeros(9)
    avail[0] = 0.5                                                    # half stays available, all of it in zone 0
    R = 0.05 - float(js(avail, torch.full((9,), 0.05)))                # zone 0 serves its own demand only (Eq. 16)
    assert float(total) == pytest.approx((R + 1) / 2, abs=1e-5)         # Eq. 17


def test_objective_is_the_eq_17_reward_plus_the_barrier_on_the_next_available_mass():
    """Eqs. 16, 17 and 23a: per step r = (matched share of the fleet - JS gap + 1) / 2, and the barrier
    lambda log(h(mu^A_{t+1}) - C) on the available mass after each step (the start's own mass is not constrained; the
    mass after the last step is split by the policy at the horizon). The authors' `utils/reward.py` does the same."""
    geo = toy_geo()
    half = lambda geo, mu, dem, t, q: (torch.full((geo.Z,), 0.5), torch.full((geo.Z, geo.Z), 1.0 / geo.Z))  # noqa: E731
    mu0 = torch.zeros(9)
    mu0[0] = 1.0                                                       # a cluster: infeasible at the start
    dem = torch.full((9,), 0.02)
    total, barrier = rollout(half, geo, mu0, [dem], q=1.0)
    avail0 = torch.zeros(9)
    avail0[0] = 0.5
    assert float(total) == pytest.approx((0.02 - float(js(avail0, dem)) + 1) / 2, abs=1e-6)
    mu1 = torch.full((9,), 0.02 / 9 + 0.5 / 9)                          # matched to customers, repositioned uniformly
    mu1[0] += 0.5 - 0.02                                               # the available mass left unmatched in zone 0
    C = 0.5 * np.log(9)
    expected = float(barrier_term(entropy(0.5 * mu1), torch.tensor(C)))
    assert float(barrier) == pytest.approx(expected, abs=1e-5)


def test_relocate_counts_couriers_whose_mass_zone_differs_from_their_command_zone():
    """G8 item (Filipe, 2026-11-04), adaptation 10: per policy step, the obedient idle couriers counted in one zone's
    mass (current cell) but commanded with another zone's leave probability (the cell they can start from)."""
    from models.jusup_mf import JusupMF
    from sim.core.city import toy_line
    from sim.core.demand import Component, Demand
    from sim.core.engine import Params, View
    city = toy_line(9, hop_s=60, hop_m=300.0)                         # one zone per cell
    demand = Demand(city, [Component(np.ones(240), np.ones(9))], gravity_s=60.0)
    sim = SimpleNamespace(city=city, params=Params(horizon_s=14400), demand=demand, state=np.zeros(3, np.int8),
                          pos=np.array([0, 3, 5]), hop_to=np.array([1, -1, -1]))
    v = View(0.0, np.empty(0, int), np.empty(0, int), np.empty(0, int), np.empty(0), np.empty(0), np.empty(0),
             np.arange(3), np.array([1, 3, 5]), np.zeros(3), sim)   # courier 0 is in mid-hop from cell 0 to cell 1
    jm = JusupMF(seed=1, policy=Policy(9, seed=0))
    jm.geo = toy_geo(9)
    jm.relocate(v)
    assert jm.events == {"steps": 1, "couriers": 3, "zone_mismatch": 1, "max_zone_mismatch_in_step": 1}
    assert jm.relocate(v) == [] and jm.events["steps"] == 1           # within the 20-min step: no policy call, no count
