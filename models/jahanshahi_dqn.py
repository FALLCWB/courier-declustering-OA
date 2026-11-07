"""Deep Q-network courier assignment for meal delivery (Jahanshahi et al., Knowledge-Based Systems 2022), assignment action
only: double DQN with rank-based prioritized replay and hard target updates (the variant the paper selects).

Fidelity note: models/fidelity/jahanshahi_dqn.md; reading note: literature/model-specs/jahanshahi-2022.md (arXiv v2).
State of an assignment: the expected delivery time delta_co = d_o + max{pi_o, tau_c + d(c, o)} (Eq. 1; tau_c = 0 with one
order per courier); reward 45 - delta (Eq. 3); one shared network scores each candidate courier (the paper's
single-courier policy shared by all couriers, p.22, extended to a large fleet).
"""
from pathlib import Path

import numpy as np

from sim.nn import MLP

K_CAND = 30                    # candidates per order: the idle couriers nearest by time (adaptation)
LIMIT_MIN = 45.0               # reward 45 - delta (Eq. 3)
GAMMA = 0.9                    # Table 6
BATCH = 128                    # Table 6
MEMORY = 20_000                # Table 6
UPDATE_EVERY = 100             # hard target update (Table 6)
ALPHA, BETA0 = 0.6, 0.4        # rank-based prioritized replay (p.15-16)
HIDDEN = (64, 128, 128, 64)    # Table 2
LR = 1e-3                      # not found in the paper (ours)
SCALE = 1.0 / LIMIT_MIN        # rewards divided by 45 inside the network (ours; argmax unchanged)
TRAIN_EVERY = 4                # one update every 4 decisions (the paper gives no frequency; ours, for the 12 h budget)


def deltas(v):
    """[orders, couriers] expected delivery time in minutes, Eq. 1 with tau_c = 0."""
    city, p = v.city, v.sim.params
    approach = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf
    prep_left = np.maximum(v.ready - v.t, 0.0)[:, None]
    ride = (city.T[v.rest, v.cust] * v.sf + p.door_overhead_s)[:, None]
    return (ride + np.maximum(prep_left, approach)) / 60.0, approach


class Replay:
    """Rank-based prioritized replay (Schaul et al.; the paper's PER): P(i) proportional to (1/rank)^alpha, importance
    weights (M P(i))^-beta normalized by their maximum; ranks re-sorted at every target update."""

    def __init__(self, size=MEMORY, k=K_CAND, seed=0):
        self.s = np.zeros(size)
        self.r = np.zeros(size)
        self.next = np.zeros((size, k))
        self.mask = np.zeros((size, k), bool)
        self.prio = np.zeros(size)
        self.n, self.i, self.size = 0, 0, size
        self.rng = np.random.default_rng(seed)
        self.order = None
        self._pr_n, self._pr = 0, None

    def add(self, s, r, nxt):
        i = self.i
        self.s[i], self.r[i] = s, r
        self.mask[i] = False
        if nxt is not None:
            self.next[i, :len(nxt)] = nxt
            self.mask[i, :len(nxt)] = True
        self.prio[i] = self.prio[:self.n].max() if self.n else 1.0
        self.i = (i + 1) % self.size
        self.n = min(self.n + 1, self.size)
        self.order = None

    def sample(self, batch, beta):
        if self.order is None or len(self.order) != self.n:
            self.order = np.argsort(-self.prio[:self.n], kind="stable")
        if self._pr_n != self.n:                           # rank probabilities depend only on n
            self._pr = (1.0 / np.arange(1, self.n + 1)) ** ALPHA
            self._pr /= self._pr.sum()
            self._pr_n = self.n
        pr = self._pr
        ranks = self.rng.choice(self.n, size=batch, p=pr)
        idx = self.order[ranks]
        w = (self.n * pr[ranks]) ** (-beta)
        return idx, w / w.max()


class Learner:
    """Double DQN on the replay: y = r + gamma Q_target(s', argmax_a Q(s', a)), one update per decision."""

    def __init__(self, net, seed=0, total_updates=1_000_000):
        self.net, self.target = net, MLP([1, *HIDDEN, 1], seed=seed + 1)
        self.target.copy_from(net)
        self.mem = Replay(seed=seed)
        self.pending = None
        self.updates, self.total = 0, total_updates
        self.losses = []

    def observe(self, candidates, s, r):
        """A decision: its candidate features complete the previous transition (as its next state), then the chosen
        pair's feature s and reward r wait for the next decision."""
        if self.pending is not None:
            self.mem.add(self.pending[0], self.pending[1], candidates)
            self.decisions = getattr(self, "decisions", 0) + 1
            if self.decisions % TRAIN_EVERY == 0:
                self.update()
        self.pending = (s, r)

    def end_episode(self):
        if self.pending is not None:
            self.mem.add(self.pending[0], self.pending[1], None)
            self.pending = None

    def update(self):
        if self.mem.n < BATCH:
            return
        beta = BETA0 + (1.0 - BETA0) * min(1.0, self.updates / self.total)
        idx, w = self.mem.sample(BATCH, beta)
        m, nxt = self.mem.mask[idx], self.mem.next[idx]
        q_on = self.net.forward(nxt.reshape(-1, 1)).reshape(BATCH, -1)
        q_on = np.where(m, q_on, -np.inf)
        best = np.argmax(q_on, axis=1)
        q_tg = self.target.forward(nxt[np.arange(BATCH), best][:, None]).ravel()
        has = m.any(axis=1)
        y = self.mem.r[idx] + GAMMA * np.where(has, q_tg, 0.0)
        q = self.net.forward(self.mem.s[idx][:, None], keep=True).ravel()
        err = q - y
        gW, gb = self.net.grads((2.0 * w * err / BATCH)[:, None])
        self.net.step(gW, gb)
        self.mem.prio[idx] = np.abs(err) + 1e-6
        self.mem.order = None if self.updates % UPDATE_EVERY == 0 else self.mem.order
        self.updates += 1
        if self.updates % UPDATE_EVERY == 0:
            self.target.copy_from(self.net)
        self.losses.append(float(np.mean(err ** 2)))


class JahanshahiDQN:
    """Orders in creation order (one decision per order, as in the paper): score the K nearest idle couriers by the
    shared network on delta, take the highest Q (epsilon-greedy in training). No order is refused; an order with no
    idle courier waits for the next epoch."""
    name = "jahanshahi"

    def __init__(self, seed=0, net=None, weights_path=None, epsilon=0.0, learner=None, k_cand=K_CAND):
        if net is None:
            path = weights_path or Path(__file__).parent / "trained" / "jahanshahi_seed1.npz"
            net = MLP.from_state(dict(np.load(path)))
        self.net, self.eps, self.learner, self.k = net, epsilon, learner, k_cand
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 13]))

    def assign(self, v):
        d, approach = deltas(v)
        free = np.ones(len(v.couriers), bool)
        pairs = []
        for o in np.argsort(v.placed, kind="stable"):
            if not free.any():
                break
            cand = np.flatnonzero(free)
            cand = cand[np.argsort(approach[o, cand], kind="stable")[:self.k]]
            feats = d[o, cand] / 60.0
            q = self.net.forward(feats[:, None]).ravel()
            j = int(np.argmax(q)) if self.rng.uniform() >= self.eps else int(self.rng.integers(len(cand)))
            c = int(cand[j])
            if self.learner is not None:
                self.learner.observe(feats, feats[j], (LIMIT_MIN - d[o, c]) * SCALE)
            pairs.append((v.orders[o], v.couriers[c]))
            free[c] = False
        return pairs
