"""Assignment with holding (Auad, Lagos and Lagos, Transportation Science 2026), bundling and courier rejection off: the
n-step SARSA policy with a linear value of the joint decision, Q(s, x) = c0(s, x) + theta . phi(s, x) (Eq. 1), where an
order may be held for a later 30 s epoch. Arm B.

Fidelity note: models/fidelity/auad_holding.md; reading note: literature/model-specs/auad-2026.md (manuscript, Oct 2025).
Features are the paper's raw counts (p.13-14); alpha, the buffer m and n come from the paper's grid (p.29), chosen on
training-range seeds by sim/train_auad.py; the policy acts with theta_best, which Algorithm 1 (lines 13-14) replaces only
when a Monte Carlo episode of the learned theta costs less.
"""
from pathlib import Path

import numpy as np

K_DIST, K_LATE, K_LOST = 1.0, 4.0, 16.0  # Table 6; K_late per minute late (the paper states no unit; ours)
GAMMA = 0.999                    # Table 6
LAMBDA_LOST_S = 7200.0           # Table 6: an order unassigned 2 h past its deadline is lost; here it is booked as lost
                                 # (K_lost) and offered to the cheapest courier, since no order is refused (ours)
GRID = {"alpha": (1e-7, 1e-6, 1e-5), "mem": (3000, 5000, 9000), "n_step": (2, 1000, 3000)}   # p.29
ALPHA, MEM, N_STEP = 1e-6, 3000, 1000   # defaults until the grid choice is recorded in DECISIONS.md
BATCH = 20                       # b (p.29)
BUCKET_S, N_BUCKETS = 1200.0, 8  # deadline buckets (p.13-14)
N_FEAT = 15                      # bias + 14 features (p.13-14)


def features(n_active, n_on, n_open_left, buckets, n_offered, rc_km_sum):
    """phi_0..phi_14 of a joint decision (p.13-14), raw as printed: phi_1 active orders per courier, phi_2 open orders
    not offered per courier, phi_3 their count, phi_4..phi_12 their deadline buckets, phi_13 on-duty couriers receiving
    no offer, phi_14 mean restaurant-to-customer km of the offered orders (0 when none is offered)."""
    n1 = max(n_on, 1)
    return np.concatenate([[1.0, n_active / n1, n_open_left / n1, float(n_open_left)], np.asarray(buckets, float),
                           [float(n_on - n_offered), rc_km_sum / n_offered if n_offered else 0.0]])


def episode_cost(sim):
    """The paper's total cost of a finished episode (rewards, p.10): K_late x minutes late (an order never delivered
    counts at the drain's end) + K_dist x km ridden toward and with an order + K_lost x orders lost (unassigned 2 h past
    the deadline; here they were offered then)."""
    p, o = sim.params, sim.orders
    inside = o.placed < p.horizon_s
    end = p.horizon_s + p.drain_s
    door = np.where(np.isnan(sim.o_door) | (sim.o_door > end), end, sim.o_door)[inside]
    late_min = float(np.maximum(door - o.due[inside], 0.0).sum() / 60.0)
    assigned = np.where(np.isnan(sim.o_assigned), end, sim.o_assigned)[inside]
    lost = int((assigned >= o.due[inside] + LAMBDA_LOST_S).sum())
    return K_LATE * late_min + K_DIST * float(sim.km_dead.sum() + sim.km_loaded.sum()) + K_LOST * lost


class Learner:
    """n-step SARSA (Algorithm 1): target for theta . phi(s_t, x_t) is sum_{i<n-1} gamma^i c_{t+i} + gamma^(n-1)
    Q(s_{t+n-1}, x_{t+n-1}) - c0_t, stored in a ring buffer of m; each epoch one SGD step on b samples. The cost c_t of
    an epoch is booked when its offers are made (planned c0, plus K_lost for an order offered at the lost limit). An
    n longer than the episode gives the Monte Carlo return to the episode's end. theta_best acts; consider() is
    lines 13-14."""

    def __init__(self, seed=0, alpha=ALPHA, mem=MEM, n_step=N_STEP):
        self.alpha, self.mem, self.n_step = alpha, mem, n_step
        self.theta = np.zeros(N_FEAT)
        self.theta_best, self.best_cost = np.zeros(N_FEAT), np.inf
        self.buf_x, self.buf_y = np.zeros((mem, N_FEAT)), np.zeros(mem)
        self.n, self.i = 0, 0
        self.hist = []
        self.rng = np.random.default_rng(seed)
        self.errors = []

    def record(self, phi, c0):
        self.hist.append((phi, c0))
        if len(self.hist) >= self.n_step:
            self._push(len(self.hist) - self.n_step, bootstrap=True)
        self._step()

    def _push(self, t0, bootstrap):
        seg = self.hist[t0:t0 + self.n_step]
        g = sum(GAMMA ** i * c for i, (_, c) in enumerate(seg[:-1] if bootstrap else seg))
        if bootstrap:
            phi_n, c_n = seg[-1]
            g += GAMMA ** (len(seg) - 1) * (c_n + self.theta @ phi_n)
        self.buf_x[self.i], self.buf_y[self.i] = self.hist[t0][0], g - self.hist[t0][1]
        self.i = (self.i + 1) % self.mem
        self.n = min(self.n + 1, self.mem)

    def end_episode(self):
        start = max(0, len(self.hist) - self.n_step + 1)
        for t0 in range(start, len(self.hist)):
            self._push(t0, bootstrap=False)
        self.hist = []

    def _step(self):
        if self.n < BATCH:
            return
        idx = self.rng.integers(0, self.n, BATCH)
        x, y = self.buf_x[idx], self.buf_y[idx]
        err = y - x @ self.theta
        self.theta += self.alpha * (err[:, None] * x).mean(axis=0)
        self.errors.append(float(np.mean(err ** 2)))

    def diverged(self):
        return not np.all(np.isfinite(self.theta))

    def consider(self, cost):
        """Algorithm 1 lines 13-14: theta_best <- theta when the Monte Carlo cost of theta is lower."""
        if self.diverged() or not cost < self.best_cost:
            return False
        self.theta_best, self.best_cost = self.theta.copy(), float(cost)
        return True


class CostCapExceeded(Exception):
    """Raised during a capped Monte Carlo run once a lower bound of the episode's total cost passes the cap."""


def cost_lower_bound(v):
    """A lower bound of episode_cost at time v.t: lateness already incurred by delivered orders and by orders still
    open (they reach the door no earlier than now), plus the kilometres already ridden toward and with orders."""
    sim, t = v.sim, v.t
    door, due = sim.o_door, sim.orders.due
    done = ~np.isnan(door) & (door <= t)
    late = np.maximum(door[done] - due[done], 0.0).sum() + np.maximum(t - v.due, 0.0).sum()
    return K_LATE * late / 60.0 + K_DIST * float(sim.km_dead.sum() + sim.km_loaded.sum())


class AuadHolding:
    """Each epoch, orders in random order (the simple policy's permutation): the free idle courier with the lowest
    immediate cost c0 (Eq. 2 for an empty route: K_dist km + K_late minutes late) is offered the order if
    Q(offer) = c0 + theta . phi(offer) is at most Q(hold) = theta . phi(hold), else the order is held (our reading of
    the offer test; the paper's 'offer only if Q <= 0' would hold everything at theta = 0, as does this one). An order
    still open 2 h past its deadline is offered (lambda_lost). With a learner, the policy acts with theta_best."""
    name = "auad"

    def __init__(self, seed=0, theta=None, theta_path=None, epsilon=0.0, learner=None, cap=None):
        if theta is None and learner is None:
            theta = np.load(theta_path or Path(__file__).parent / "trained" / "auad_seed1.npz")["theta"]
        self.theta = None if learner is not None else np.asarray(theta, float)
        self.eps, self.learner, self.cap = epsilon, learner, cap
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 15]))

    def assign(self, v):
        city, sim, p = v.city, v.sim, v.sim.params
        if self.cap is not None and cost_lower_bound(v) > self.cap:
            raise CostCapExceeded
        theta = self.learner.theta_best if self.learner is not None else self.theta
        approach = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf
        at_rest = v.t + approach
        ready = v.ready[:, None]
        pickup = np.maximum(at_rest + p.pickup_service_s, ready) if p.pickup_overlaps_wait else np.maximum(at_rest, ready) + p.pickup_service_s
        door = pickup + (city.T[v.rest, v.cust] * v.sf + p.door_overhead_s)[:, None]
        km = (city.Dm[np.ix_(v.cell, v.rest)].T + city.Dm[v.rest, v.cust][:, None]) / 1000.0
        rc = city.Dm[v.rest, v.cust] / 1000.0
        c0 = K_DIST * km + K_LATE * np.maximum(door - v.due[:, None], 0.0) / 60.0
        lost = v.t >= v.due + LAMBDA_LOST_S
        n_on = len(sim.pos)
        n_active = len(sim.pending) + int((sim.state == 1).sum())
        b = np.clip(((v.due - v.t) // BUCKET_S).astype(int), 0, N_BUCKETS)
        buckets = np.bincount(b, minlength=N_BUCKETS + 1).astype(float)
        n_open, rc_sum, n_off, cost = len(v.orders), 0.0, 0, 0.0
        free = np.ones(len(v.couriers), bool)
        pairs = []
        perm = self.rng.permutation(len(v.orders))
        if self.eps:                                        # exploration draws, one per order in the permutation
            explore = self.rng.uniform(size=len(perm)) < self.eps
            coin = self.rng.integers(2, size=len(perm)) == 1
        best = c0.argmin(axis=1)                            # cheapest courier per order; c0 columns of taken couriers
        cbest = c0[np.arange(len(best)), best]              # become inf, and only orders that lost theirs are redone
        pos = 0
        # Orders are decided in the permutation's order; the state (open count, buckets, offers, free couriers) changes
        # only at an offer, so all orders up to the next offer are decided at once under the same state.
        while pos < len(perm) and free.any():
            rem = perm[pos:]
            q_hold = theta @ features(n_active, n_on, n_open, buckets, n_off, rc_sum)
            base = theta @ features(n_active, n_on, n_open - 1, buckets, n_off + 1, 0.0)
            q_off = cbest[rem] + base - theta[4 + b[rem]] + theta[14] * (rc_sum + rc[rem]) / (n_off + 1)
            offer = (q_off <= q_hold) | lost[rem]
            if self.eps:
                offer = np.where(explore[pos:], coin[pos:] | lost[rem], offer)
            hits = np.flatnonzero(offer)
            if not len(hits):
                break
            j = int(hits[0])
            o = int(rem[j])
            c = int(best[o])
            pairs.append((v.orders[o], v.couriers[c]))
            cost += c0[o, c] + (K_LOST if lost[o] else 0.0)
            free[c] = False
            c0[:, c] = np.inf
            stale = np.flatnonzero(best == c)
            best[stale] = c0[stale].argmin(axis=1)
            cbest[stale] = c0[stale, best[stale]]
            buckets = buckets.copy()
            buckets[b[o]] -= 1
            n_open, rc_sum, n_off = n_open - 1, rc_sum + rc[o], n_off + 1
            pos += j + 1
        if self.learner is not None:
            self.learner.record(features(n_active, n_on, n_open, buckets, n_off, rc_sum), cost)
        return pairs
