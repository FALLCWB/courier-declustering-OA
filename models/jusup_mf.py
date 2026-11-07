"""Constrained mean-field rebalancing (Jusup, Zhang, Hu, Pasztor, Krause and Corman, Transportation Research Part C 2026),
reimplemented on the zone graph: a policy for a representative idle courier in each zone gives a repositioning share p
and a distribution over destination zones; it is trained by back-propagation through a differentiable mean-field model
of the fleet over the evening, maximizing the matched fraction minus the Jensen-Shannon gap between available couriers
and demand (Eq. 16) with a log-barrier on the entropy of available couriers (Eqs. 18, 19, 23a). Arm C: only obedient
couriers follow; the obedient share q is a policy input and scales the controllable mass.

Fidelity note: models/fidelity/jusup_mf.md; reading note: literature/model-specs/jusup-2026.md (arXiv v3). The authors'
code (BSD-3) assumes a square grid with Euclidean moves, so the method is reimplemented from the paper.
"""
from pathlib import Path

import numpy as np
import torch

STEP_S = 1200.0              # 20-minute steps (Sec. 5.1)
HIDDEN = (512, 256, 256, 64)  # Table 3
LR = 5e-4                    # AdamW, Table 3
LAMBDA = 1.0                 # barrier weight (Sec. 5.2.3)
P_ENTROPY = 0.5              # C = p h_max (Eq. 25); p = 0.5 (ours, within the paper's 0 to 0.85)
EPS = 1e-10                  # entropy smoothing (Eq. 18)
NEIGH_M = 3000.0             # destinations: zones within 3 km of the zone (adaptation of the continuous move u)
MATCH_M = 1500.0             # matching reach in the mean-field model (the paper's OT radius r; ours)


def entropy(mu):
    """Eq. 18 with unit weights on the normalized available mass."""
    m = mu / mu.sum().clamp_min(1e-12)
    return -(m * torch.log(m + EPS)).sum()


def js(a, b):
    a = a / a.sum().clamp_min(1e-12)
    b = b / b.sum().clamp_min(1e-12)
    m = 0.5 * (a + b)
    return 0.5 * ((a * torch.log((a + EPS) / (m + EPS))).sum() + (b * torch.log((b + EPS) / (m + EPS))).sum())


class Geometry:
    """Zone graph data for the mean-field model: representative-cell coordinates, destination masks within NEIGH_M,
    the matching kernel within MATCH_M and the origin-to-destination kernel of orders."""

    def __init__(self, city, demand):
        rep = city.zone_rep
        D = city.Dm[np.ix_(rep, rep)].astype(float)
        self.Z = len(rep)
        self.xy = torch.tensor(np.column_stack([city.lng[rep] - city.lng.mean(), city.lat[rep] - city.lat.mean()]) * 10.0,
                               dtype=torch.float32)
        self.dest_mask = torch.tensor(D <= NEIGH_M)
        k = (D <= MATCH_M).astype(float)
        self.match = torch.tensor(k / k.sum(axis=1, keepdims=True), dtype=torch.float32)      # supply reach
        cw = demand.components[0].cust_weight / demand.components[0].cust_weight.sum()
        A = np.zeros((city.n, self.Z))
        A[np.arange(city.n), city.zone] = 1.0                                                   # cell -> zone
        B = A[demand.rest_cells]                                                                # restaurant cell -> zone
        joint = (B.T @ (cw[:, None] * demand.choice).T @ A)                                     # [rest zone, cust zone]
        joint = joint / np.maximum(joint.sum(axis=1, keepdims=True), 1e-12)
        self.od = torch.tensor(joint, dtype=torch.float32)


class Policy(torch.nn.Module):
    """Representative courier of each zone: input (zone coordinates, available mass of all zones, demand of all zones,
    time, obedient share); output p in [0, 1] and logits over destination zones (masked to NEIGH_M)."""

    def __init__(self, Z, seed=0):
        super().__init__()
        torch.manual_seed(seed)
        dims = [2 + 2 * Z + 2, *HIDDEN]
        layers = []
        for a, b in zip(dims[:-1], dims[1:]):
            layers += [torch.nn.Linear(a, b), torch.nn.LeakyReLU()]
        self.body = torch.nn.Sequential(*layers)
        self.p_head = torch.nn.Linear(HIDDEN[-1], 1)
        self.dest_head = torch.nn.Linear(HIDDEN[-1], Z)

    def forward(self, geo, mu, dem, t, q):
        Z = geo.Z
        g = torch.cat([mu / mu.sum().clamp_min(1e-12), dem / dem.sum().clamp_min(1e-12), torch.tensor([t, q])])
        x = torch.cat([geo.xy, g.unsqueeze(0).expand(Z, -1)], dim=1)
        h = self.body(x)
        p = torch.sigmoid(self.p_head(h)).squeeze(1)
        logits = self.dest_head(h).masked_fill(~geo.dest_mask, -1e9)
        return p, torch.softmax(logits, dim=1)


def barrier_term(h, C, delta=0.05):
    """Log-barrier on h - C (Eq. 23a), extended linearly below delta so that an infeasible start (a cluster, where the
    paper needs a feasible one, p.11) still yields a gradient toward more entropy (adaptation)."""
    gap = h - C
    return torch.where(gap > delta, torch.log(gap.clamp_min(delta)), np.log(delta) + (gap - delta) / delta)


def rollout(policy, geo, mu0, demand_steps, q, c_frac=P_ENTROPY):
    """Differentiable mean-field evening. mu = courier mass (sums to 1); demand_steps = expected orders per zone and step
    divided by the fleet size. Each step (Eqs. 7, 10, 11, 14): the obedient repositioning mass q p mu leaves for the
    policy's destinations and is not available in this step; the available mass (Eq. 7) matches demand within MATCH_M;
    at the step's end matched couriers are at customer zones (OD kernel), repositioning couriers at their destinations,
    and the rest stay. Returns the summed reward of Eq. 17, r = (R + 1) / 2 with R = matched share of the fleet minus
    the JS gap between available couriers and demand (Eq. 16), and the barrier of Eq. 23a, lambda log(h(mu^A_{t+1}) - C),
    on the entropy of the available mass after each step (Eqs. 18, 19): the start's own mass is not constrained (the
    paper needs a feasible start only for t > 0, p.11), and the mass after the last step is split by the policy at the
    horizon, fed the last step's demand. The authors' `utils/reward.py` computes the same terms."""
    mu = mu0 / mu0.sum()
    h_max = torch.log(torch.tensor(float(geo.Z)))
    C = c_frac * h_max
    total, barrier = torch.tensor(0.0), torch.tensor(0.0)
    T = len(demand_steps)
    for t, dem in enumerate(demand_steps):
        p, dest = policy(geo, mu, dem, t / T, q)
        move = q * p * mu                                                  # repositioning mass
        avail = mu - move                                                  # Eq. 7: available vehicles
        if t > 0:                                                          # Eq. 23a: h of mu^A_{t+1} for step t - 1
            barrier = barrier + LAMBDA * barrier_term(entropy(avail), C)
        reach = avail @ geo.match                                          # available supply reaching each zone
        served = torch.minimum(reach, dem)                                 # matched mass (dem is per fleet member)
        take = avail * ((served / reach.clamp_min(1e-12)) @ geo.match.T).clamp(max=1.0)   # matched mass by origin zone
        total = total + (served.sum() - js(avail, dem) + 1) / 2            # Eqs. 16, 17
        mu = avail - take + served @ geo.od + move @ dest                  # Eq. 14: cruising, matched, repositioned
    p, _ = policy(geo, mu, demand_steps[-1], 1.0, q)                       # the last step's mu^A_{t+1}
    barrier = barrier + LAMBDA * barrier_term(entropy(mu - q * p * mu), C)
    return total, barrier


class JusupMF:
    """Arm C: assignment by nearest courier; relocate() every STEP_S applies the trained policy: each obedient idle
    courier in zone z leaves with probability p_z (the policy's share for the observed mass) for a destination zone
    drawn from the policy's distribution, at that zone's representative cell."""
    name = "jusup"

    def __init__(self, seed=0, policy=None, weights_path=None, q=1.0):
        from sim.core.policies import NearestIdle
        self._nearest = NearestIdle()
        self.policy = policy
        self.path = weights_path or Path(__file__).parent / "trained" / "jusup_seed1.pt"
        self.q = q
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 16]))
        self.geo, self.next_t = None, 0.0
        # adaptation 10, counted per policy step (G8 item, Filipe 2026-11-04): obedient idle couriers whose current cell
        # (counted in the mass) and start cell (whose zone's leave probability applies) lie in different zones
        self.events = {"steps": 0, "couriers": 0, "zone_mismatch": 0, "max_zone_mismatch_in_step": 0}

    def assign(self, v):
        return self._nearest.assign(v)

    def relocate(self, v):
        if v.t < self.next_t:
            return []
        self.next_t = v.t + STEP_S
        city, sim = v.city, v.sim
        if self.geo is None:
            self.geo = Geometry(city, sim.demand)
            if self.policy is None:
                self.policy = Policy(self.geo.Z)
                self.policy.load_state_dict(torch.load(self.path))
            self.policy.eval()
        idle = np.flatnonzero(sim.state == 0)
        mu = torch.tensor(np.bincount(city.zone[sim.pos[idle]], minlength=city.n_zones), dtype=torch.float32)
        dem = torch.tensor(np.bincount(city.zone, weights=sim.demand.expected_pickups(v.t, v.t + STEP_S),
                                       minlength=city.n_zones), dtype=torch.float32)
        with torch.no_grad():
            p, dest = self.policy(self.geo, mu.clamp_min(0) + 1e-9, dem + 1e-9, v.t / sim.params.horizon_s, self.q)
        p, dest = p.numpy(), dest.numpy()
        mism = int(np.count_nonzero(city.zone[sim.pos[v.couriers]] != city.zone[v.cell]))
        self.events["steps"] += 1
        self.events["couriers"] += len(v.couriers)
        self.events["zone_mismatch"] += mism
        self.events["max_zone_mismatch_in_step"] = max(self.events["max_zone_mismatch_in_step"], mism)
        cmds = []
        for c, cell in zip(v.couriers, v.cell):
            z = city.zone[cell]
            if self.rng.uniform() < p[z]:
                dz = int(self.rng.choice(len(dest[z]), p=dest[z] / dest[z].sum()))
                cmds.append((int(c), int(city.zone_rep[dz])))
        return cmds
