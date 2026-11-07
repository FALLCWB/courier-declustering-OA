"""Learning and planning (Xu et al., KDD 2018): an offline tabular value of (zone, time slot) and online Kuhn-Munkres
on the temporal-difference error of each courier-order pair.

Fidelity note: models/fidelity/xu_value.md; reading note: literature/model-specs/xu-2018.md (KDD 2018 full text, printed
pages 905-913): value table by Algorithm 1 (p.908), edge weight Eq. 8 (p.909), Kuhn-Munkres under at-most-one
constraints (Eqs. 6-7), so a pair with a negative weight is not matched and its order waits for a later round.
"""
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

GAMMA = 0.95          # per 5-minute slot (our choice; Xu's value not found)
SLOT_S = 300.0        # time slot of the value table
N_SLOTS = 48          # 17:00 to 21:00; slot 48 is terminal (V = 0)
WAIT_FALLBACK_S = 1800.0   # an order unassigned for 30 min goes to the closest courier (orders are never refused; ours)
REWARD = 1.0          # one delivered order (no fare in food delivery)


def discounted_reward(R, k, gamma):
    """R spread uniformly over k slots and discounted: R (gamma^k - 1) / (k (gamma - 1)) (Tang et al. 2019, Sec 2)."""
    k = np.asarray(k, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(k > 0, R * (gamma ** k - 1.0) / (k * (gamma - 1.0)), R)
    return out


def td_weight(R, k, gamma, v_next, v_now):
    """Edge weight, Eq. 8 (p.909): R_gamma + gamma^dt V(s') - V(s), the TD error of serving the order."""
    return discounted_reward(R, k, gamma) + gamma ** np.asarray(k, float) * v_next - v_now


def fit_value(transitions, n_zones, n_slots=N_SLOTS, gamma=GAMMA):
    """One backward dynamic-programming pass over slots. transitions: (zone, slot, R, zone2, slot2) with slot2 > slot;
    slot2 >= n_slots is the terminal (V = 0). V(z, s) = mean over transitions from (z, s) of the discounted reward plus
    gamma^k V(z2, s2); unvisited (zone, slot) states take the mean of the visited states of their slot."""
    V = np.zeros((n_zones, n_slots + 1))
    if not len(transitions):
        return V
    t = np.asarray(transitions, float)
    z, s, R, z2, s2 = t[:, 0].astype(int), t[:, 1].astype(int), t[:, 2], t[:, 3].astype(int), np.minimum(t[:, 4], n_slots).astype(int)
    k = s2 - s
    if (k <= 0).any():
        raise ValueError("every transition must end in a later slot")
    for slot in range(n_slots - 1, -1, -1):
        m = s == slot
        if m.any():
            target = discounted_reward(R[m], k[m], gamma) + gamma ** k[m] * V[z2[m], s2[m]]
            tot = np.bincount(z[m], weights=target, minlength=n_zones)
            cnt = np.bincount(z[m], minlength=n_zones)
            seen = cnt > 0
            V[seen, slot] = tot[seen] / cnt[seen]
            V[~seen, slot] = V[seen, slot].mean()
    return V


def transitions_from(sim, slot_s=SLOT_S, n_slots=N_SLOTS):
    """Training data from one simulated peak: every delivered order (courier zone at acceptance to customer zone at the
    door, reward 1) and every idle gap of at least one slot (drop-off zone to the zone of the next acceptance, reward 0)."""
    city, o = sim.city, sim.orders
    done = ~np.isnan(sim.o_door) & ~np.isnan(sim.o_assigned)
    s1 = np.floor(sim.o_assigned[done] / slot_s).astype(int)
    s2 = np.maximum(np.floor(sim.o_door[done] / slot_s).astype(int), s1 + 1)
    keep = s1 < n_slots
    rows = [np.column_stack([city.zone[sim.o_from[done]][keep], s1[keep], np.full(keep.sum(), REWARD),
                             city.zone[o.cust[done]][keep], s2[keep]])]
    if sim.gaps:
        g = np.array(sim.gaps, float)
        a = np.floor(g[:, 1] / slot_s).astype(int)
        b = np.floor(g[:, 2] / slot_s).astype(int)
        m = (b > a) & (a < n_slots)
        rows.append(np.column_stack([city.zone[g[m, 3].astype(int)], a[m], np.zeros(m.sum()),
                                     city.zone[g[m, 4].astype(int)], b[m]]))
    return np.vstack(rows)


class XuValue:
    """Every 30 s: Kuhn-Munkres over pending orders and idle couriers maximizing the sum of Eq. 8 weights, keeping only
    pairs with a positive weight (at most one courier per order and order per courier, Eqs. 6-7: a negative pair adds
    nothing, so the order waits); the trip's dt runs from now to the expected door time, including pickup (p.907). An
    order unassigned for 30 min goes to the closest courier left, since orders are never refused here."""
    name = "xu"

    def __init__(self, seed=0, value=None, value_path=None, gamma=GAMMA):
        if value is None:
            value = np.load(value_path or Path(__file__).parent / "trained" / "xu_value_seed1.npz")["V"]
        self.V, self.gamma = np.asarray(value, float), gamma
        self.n_slots = self.V.shape[1] - 1

    def assign(self, v):
        city, p = v.city, v.sim.params
        approach = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf               # [orders, couriers]
        at_rest = v.t + approach
        ready = v.ready[:, None]
        if p.pickup_overlaps_wait:
            pickup = np.maximum(at_rest + p.pickup_service_s, ready)
        else:
            pickup = np.maximum(at_rest, ready) + p.pickup_service_s
        door = pickup + (city.T[v.rest, v.cust] * v.sf + p.door_overhead_s)[:, None]
        k = (door - v.t) / SLOT_S
        s_now = min(int(v.t // SLOT_S), self.n_slots)
        s_end = np.minimum((door // SLOT_S).astype(int), self.n_slots)
        v_next = self.V[city.zone[v.cust][:, None], s_end]
        v_now = self.V[city.zone[v.cell], s_now][None, :]
        rho = td_weight(REWARD, k, self.gamma, v_next, v_now)
        rows, cols = linear_sum_assignment(-rho)
        pairs = [(i, j) for i, j in zip(rows, cols) if rho[i, j] > 0.0]
        used_o, used_c = {i for i, _ in pairs}, {j for _, j in pairs}
        free = np.array([j not in used_c for j in range(len(v.couriers))])
        for i in np.argsort(v.placed, kind="stable"):
            if i in used_o or v.t - v.placed[i] < WAIT_FALLBACK_S or not free.any():
                continue
            j = int(np.argmin(np.where(free, approach[i], np.inf)))
            pairs.append((i, j))
            free[j] = False
        return [(v.orders[i], v.couriers[j]) for i, j in pairs]
