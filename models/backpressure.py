"""Mirror backpressure, assignment only (Kanoria and Qian, Management Science 2024; arXiv 1903.02764v4).

Fidelity note: models/fidelity/backpressure.md; reading notes: literature/model-specs/kanoria-qian-2024.md.
Nodes are the H3 resolution-8 zones; q_i counts idle couriers available in zone i; the pickup neighborhood P(j) of
an order at restaurant zone j is j and the zones that share a boundary with it (Sec 6.1); D(j, k) = {k}.
"""
import numpy as np

MIN_PICKUP_S = 120.0     # pickup time max{travel, 2 min} (App F.1, footnote 20)


def congestion(qbar, m):
    """Eq (8): f(qbar) = -sqrt(m) qbar^(-1/2)."""
    return -np.sqrt(m) / np.sqrt(qbar)


def normalized(q, m):
    """Eq (9) with K = the number of available couriers: qbar = (q + sqrt(K)) / (K + m sqrt(K))."""
    K = float(q.sum())
    d = np.sqrt(K)
    return (q + d) / (K + m * d)


def choose(q, cand, w, m):
    """Eq (10) over pickup-compatible zones `cand` that have an idle courier; the destination term is the same for
    every candidate (D = {k}) and is left out. Returns the chosen zone or -1 when no candidate has a courier."""
    cand = np.asarray(cand)
    ok = q[cand] > 0
    if not ok.any():
        return -1
    s = np.asarray(w, float) + congestion(normalized(q, m)[cand], m)
    s[~ok] = -np.inf
    return int(cand[int(np.argmax(s))])


def zone_adjacency(city):
    """Zones that share a boundary: some cell of one has a neighbor cell in the other (plus the zone itself)."""
    adj = [{z} for z in range(city.n_zones)]
    for c in range(city.n):
        for nb in city.nbr[c]:
            if nb >= 0:
                adj[city.zone[c]].add(int(city.zone[nb]))
    return [np.array(sorted(a)) for a in adj]


class MirrorBackpressure:
    """Per order, in creation order (one demand per period, Sec 2): take a courier from the pickup-compatible zone
    with the highest score w_ij + f(qbar_i), w_ij = -pickup time / longest pickup time in P(j) (pickup cost folded
    into the payoff, normalized to |w| <= 1); inside the zone, the courier that arrives first. Orders are never
    refused (assignment is the only lever); with no idle courier in P(j), the closest courier serves."""
    name = "backpressure"

    def __init__(self, seed=0):
        self.seed = seed
        self.counts = {"orders": 0, "no_neighbor": 0}   # closest-courier fallbacks (G3 C3)

    def assign(self, v):
        city = v.city
        if getattr(city, "_zone_adj", None) is None:
            city._zone_adj = zone_adjacency(city)
        adj, m = city._zone_adj, city.n_zones
        zone_c = city.zone[v.cell]
        q = np.bincount(zone_c, minlength=m).astype(float)
        eta = v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf                       # [orders, couriers]
        free = np.ones(len(v.couriers), bool)
        pairs = []
        for o in np.argsort(v.placed, kind="stable"):
            if not free.any():
                break
            j = city.zone[v.rest[o]]
            cand = adj[j]
            pick = np.maximum(city.T[city.zone_rep[cand], city.zone_rep[j]] * v.sf, MIN_PICKUP_S)
            w = -pick / pick.max()
            i = choose(q, cand, w, m)
            self.counts["orders"] += 1
            self.counts["no_neighbor"] += int(i < 0)
            mask = free & (zone_c == i) if i >= 0 else free
            c = int(np.argmin(np.where(mask, eta[o], np.inf)))
            pairs.append((v.orders[o], v.couriers[c]))
            free[c] = False
            q[zone_c[c]] -= 1
        return pairs
