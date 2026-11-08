"""Mean-field multi-agent order dispatch (Li et al., WWW 2019), COD: a shared actor scores each idle courier's order pool
and samples by a Boltzmann softmax (Eq. 6); a shared critic sees the mean-field response a_bar (couriers nearby over
orders available) and learns the mean-field target (Eqs. 9 and 10).

Fidelity note: models/fidelity/li_meanfield.md; reading note: literature/model-specs/li-2019.md (arXiv 1901.11454v1).
"""
from pathlib import Path

import numpy as np

from sim.nn import MLP

POOL_S = 600.0                # order pool: restaurants within 10 min of the courier (the paper's radius r; ours)
NEIGH_S = 1200.0              # neighborhood for a_bar: twice the pool radius (Fig. 1b)
MAX_POOL = 20                 # candidates kept per courier (nearest first; ours, for fixed-size storage)
GAMMA = 0.95                  # p.7
ALPHA1, ALPHA2 = 0.01, -0.1   # destination potential (grid simulator) and pick-up minutes (coordinate simulator), p.7
CRITIC = (512, 256, 128, 64)  # p.7
ACTOR = (256, 128, 64)        # p.7
LR_CRITIC, LR_ACTOR = 1e-4, 1e-3
BATCH, UPDATE_EVERY, MEMORY = 2048, 3000, 500_000
N_OBS, N_ACT = 3, 4           # observation: courier x, y, time; action: destination x, y, pick-up and trip minutes


def obs_features(city, cell, t):
    lat0, lng0 = city.lat.mean(), city.lng.mean()
    return np.column_stack([(city.lng[cell] - lng0) * 10.0, (city.lat[cell] - lat0) * 10.0,
                            np.full(len(cell), t / 14400.0)])


class Memory:
    def __init__(self, size=MEMORY, seed=0):
        self.size, self.n, self.i = size, 0, 0
        self.x = np.zeros((size, N_OBS + 1 + N_ACT))                 # critic input of the taken action
        self.r = np.zeros(size)
        self.nx = np.zeros((size, MAX_POOL, N_OBS + 1 + N_ACT))       # critic inputs of the next pool
        self.nlogit = np.zeros((size, MAX_POOL))                       # target actor scores of the next pool
        self.nmask = np.zeros((size, MAX_POOL), bool)
        self.ax = np.zeros((size, MAX_POOL, N_OBS + N_ACT))           # actor inputs of the pool where it acted
        self.amask = np.zeros((size, MAX_POOL), bool)
        self.a = np.zeros(size, int)
        self.rng = np.random.default_rng(seed)

    def add(self, x, r, ax, amask, a, nx, nmask):
        i = self.i
        self.x[i], self.r[i], self.ax[i], self.amask[i], self.a[i] = x, r, ax, amask, a
        self.nmask[i] = False
        if nx is not None:
            self.nx[i, :len(nx)] = nx
            self.nmask[i, :len(nx)] = True
        self.i = (i + 1) % self.size
        self.n = min(self.n + 1, self.size)


class Learner:
    """COD training: critic regression to r + gamma v_MF(o'), v_MF = sum over the next pool of pi(a'|o') Q(o', a');
    actor: likelihood-ratio step toward the actions whose Q exceeds the pool's expected Q (the paper's deterministic
    policy gradient through a discrete action embedding is replaced by this standard actor-critic step; adaptation)."""

    def __init__(self, seed=0):
        self.critic = MLP([N_OBS + 1 + N_ACT, *CRITIC, 1], seed=seed, lr=LR_CRITIC)
        self.actor = MLP([N_OBS + N_ACT, *ACTOR, 1], seed=seed + 1, lr=LR_ACTOR)
        self.mem = Memory(seed=seed)
        self.pending = {}                 # courier -> (x, r, ax, amask, a) waiting for its next pool
        self.since, self.beta, self.losses = 0, 1.0, []
        self.actor_losses, self.rewards, self.ep_reward = [], [], 0.0   # logs only (training-budget check)

    def act(self, c, x, r, ax, amask, a, next_inputs):
        """Courier c acted; its previous transition (if any) gets this pool as next state."""
        self.ep_reward += float(r)
        if c in self.pending:
            px, pr, pax, pam, pa = self.pending.pop(c)
            self.mem.add(px, pr, pax, pam, pa, next_inputs, None)
            self.since += 1
        self.pending[c] = (x, r, ax, amask, a)
        if self.since >= UPDATE_EVERY and self.mem.n >= BATCH:
            self.update()
            self.since = 0

    def end_episode(self):
        for px, pr, pax, pam, pa in self.pending.values():
            self.mem.add(px, pr, pax, pam, pa, None, None)
        self.pending = {}
        self.rewards.append(self.ep_reward)
        self.ep_reward = 0.0

    def update(self):
        idx = self.mem.rng.integers(0, self.mem.n, BATCH)
        m = self.mem.nmask[idx]
        nq = self.critic.forward(self.mem.nx[idx].reshape(-1, N_OBS + 1 + N_ACT)).reshape(BATCH, MAX_POOL)
        nlog = self.actor.forward(self.mem.nx[idx][:, :, [0, 1, 2, 4, 5, 6, 7]].reshape(-1, N_OBS + N_ACT)).reshape(BATCH, MAX_POOL)
        w = np.where(m, np.exp(self.beta * (nlog - np.where(m, nlog, -np.inf).max(axis=1, keepdims=True))), 0.0)
        w = w / np.maximum(w.sum(axis=1, keepdims=True), 1e-12)
        v_next = np.where(m.any(axis=1), (w * np.where(m, nq, 0.0)).sum(axis=1), 0.0)
        y = self.mem.r[idx] + GAMMA * v_next
        q = self.critic.forward(self.mem.x[idx], keep=True).ravel()
        gW, gb = self.critic.grads((2.0 * (q - y) / BATCH)[:, None])
        self.critic.step(gW, gb)
        am, ax = self.mem.amask[idx], self.mem.ax[idx]
        logits = self.actor.forward(ax.reshape(-1, N_OBS + N_ACT), keep=True).reshape(BATCH, MAX_POOL)
        pi = np.where(am, np.exp(self.beta * (logits - np.where(am, logits, -np.inf).max(axis=1, keepdims=True))), 0.0)
        pi = pi / np.maximum(pi.sum(axis=1, keepdims=True), 1e-12)
        qa = q                                                          # Q of the taken action
        crit_in = np.concatenate([ax[:, :, :N_OBS], np.zeros((BATCH, MAX_POOL, 1)), ax[:, :, N_OBS:]], axis=2)
        crit_in[:, :, N_OBS] = self.mem.x[idx][:, N_OBS][:, None]       # same a_bar for the whole pool
        qpool = self.critic.forward(crit_in.reshape(-1, N_OBS + 1 + N_ACT)).reshape(BATCH, MAX_POOL)
        adv = qa - (pi * np.where(am, qpool, 0.0)).sum(axis=1)
        onehot = np.zeros_like(pi)
        onehot[np.arange(BATCH), self.mem.a[idx]] = 1.0
        dlogit = -(adv[:, None] * self.beta * (onehot - pi)) * am / BATCH   # gradient ascent on adv * log pi
        gW, gb = self.actor.grads(dlogit.reshape(-1, 1))
        self.actor.step(gW, gb)
        self.losses.append(float(np.mean((q - y) ** 2)))
        pa = pi[np.arange(BATCH), self.mem.a[idx]]                     # actor loss: -mean(adv x log pi(a)), a log only
        self.actor_losses.append(float(-np.mean(adv * np.log(np.maximum(pa, 1e-12)))))


class LiMeanField:
    """Every 30 s, idle couriers in random order sample one order from their pool (restaurants within POOL_S), by the
    softmax of the shared actor's scores; an order taken by an earlier courier leaves the later pools (asynchronous
    re-choice, p.5). Couriers whose pool is empty wait. Evaluation uses the final temperature (beta = 100, i.e. 0.01)."""
    name = "li"

    def __init__(self, seed=0, actor=None, weights_path=None, beta=100.0, learner=None):
        if actor is None:
            path = weights_path or Path(__file__).parent / "trained" / "li_seed1.npz"
            actor = MLP.from_state(dict(np.load(path)))
        self.actor, self.beta, self.learner = actor, beta, learner
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 14]))

    def assign(self, v):
        city, p = v.city, v.sim.params
        approach = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf               # [orders, couriers]
        trip = city.T[v.rest, v.cust] * v.sf + p.door_overhead_s
        in_pool = approach <= POOL_S
        near_c = (city.T[np.ix_(v.cell, v.cell)] * v.sf <= NEIGH_S)                          # couriers within 2r
        exp = v.sim.demand.expected_pickups(v.t, v.t + 1800.0)
        zone_dem = np.bincount(city.zone, weights=exp, minlength=city.n_zones)
        zone_sup = np.bincount(city.zone[v.cell], minlength=city.n_zones)
        dest_x = obs_features(city, v.cust, v.t)[:, :2]
        o = obs_features(city, v.cell, v.t)
        taken = np.zeros(len(v.orders), bool)
        pairs = []
        for c in self.rng.permutation(len(v.couriers)):
            pool = np.flatnonzero(in_pool[:, c] & ~taken)
            if not len(pool):
                continue
            pool = pool[np.argsort(approach[pool, c], kind="stable")[:MAX_POOL]]
            act = np.column_stack([dest_x[pool], approach[pool, c] / 600.0, trip[pool] / 600.0])
            ax = np.column_stack([np.repeat(o[c][None, :], len(pool), axis=0), act])
            logits = self.actor.forward(ax).ravel()
            z = self.beta * (logits - logits.max())
            pi = np.exp(z) / np.exp(z).sum()
            j = int(self.rng.choice(len(pool), p=pi))
            oi = pool[j]
            taken[oi] = True
            pairs.append((v.orders[oi], v.couriers[c]))
            if self.learner is not None:
                a_bar = near_c[c].sum() / len(pool)                       # couriers nearby over orders available (p.5)
                dz = city.zone[v.cust[oi]]
                dp = (zone_dem[dz] - zone_sup[dz]) if a_bar < 1.0 else 0.0  # destination potential only if orders exceed drivers
                r = 1.0 + ALPHA1 * dp + ALPHA2 * approach[oi, c] / 60.0
                x = np.concatenate([o[c], [a_bar], act[j]])
                xin = np.column_stack([np.repeat(o[c][None, :], len(pool), axis=0), np.full(len(pool), a_bar), act])
                pad_ax = np.zeros((MAX_POOL, N_OBS + N_ACT))
                pad_ax[:len(pool)] = ax
                am = np.zeros(MAX_POOL, bool)
                am[:len(pool)] = True
                self.learner.act(int(v.couriers[c]), x, r, pad_ax, am, j, xin)
        # An order with no courier within the pool radius is not lost here (orders are never refused): it goes to the
        # closest courier left, as in the other models' fallbacks.
        busy = {int(c) for _, c in pairs}
        free = np.array([int(c) not in busy for c in v.couriers])
        for oi in np.argsort(v.placed, kind="stable"):
            if taken[oi] or in_pool[oi].any() or not free.any():
                continue
            c = int(np.argmin(np.where(free, approach[oi], np.inf)))
            pairs.append((v.orders[oi], v.couriers[c]))
            free[c] = False
        return pairs
