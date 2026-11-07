"""FoodMatch with order batching off (Joshi et al., ICDE 2021; arXiv 2008.12905v1): windowed Kuhn-Munkres on extra
delivery time. Fidelity note: models/fidelity/foodmatch.md; reading notes: literature/model-specs/foodmatch-2021.md.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

OMEGA_S = 7200.0          # rejection penalty Omega (Sec V-B)
FIRST_MILE_CAP_S = 2700.0 # first mile over 45 min costs Omega (Sec V-B; code 2700 s)
K_MULT = 200.0            # k = 200 |O| / |V| candidate orders per vehicle (Sec V-B; code)
XDT_RESOLUTION_S = 0.01   # XDT differences under 0.01 s count as ties


def lexicographic_assignment(xdt, first_mile):
    """Kuhn-Munkres on total XDT, ties broken by total first mile (G3 verdict C4): every assignment chosen this way is
    optimal for the paper's objective. XDT is counted in whole hundredths of a second and the first mile, capped at the
    45-minute rule, enters as a fraction below one hundredth in total, so it never outweighs any XDT difference."""
    n = min(xdt.shape)
    scale = FIRST_MILE_CAP_S * max(n, 1) + 1.0
    cost = np.round(xdt / XDT_RESOLUTION_S) + np.minimum(first_mile, FIRST_MILE_CAP_S) / scale
    rows, cols = linear_sum_assignment(cost)
    return list(zip(rows.tolist(), cols.tolist()))


class FoodMatch:
    """One order per courier: build the FoodGraph of pending orders and idle couriers, sparsify it to the k nearest
    orders per courier (Alg. 2, Lemma 1), solve Kuhn-Munkres, assign pairs below Omega; the rest carry over.

    With MAXO = 1 the courier is empty, so mCost = XDT(o, v) (Eq. 3-4), and Eq. 2 with Def. 6-7 gives
    XDT = max(t + firstMile, o_t + o_p) + lastMile - (o_t + o_p + lastMile) = max(0, t + firstMile - ready).
    """
    name = "foodmatch"

    def __init__(self, seed=0, k_mult=K_MULT, ties="first_mile"):
        """ties: "first_mile" (frozen design, G3 C4) or "shuffle" (the S5 variant: arbitrary courier among equal XDT)."""
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 9]))
        self.k_mult, self.ties = k_mult, ties

    def assign(self, v):
        n_o, n_c = len(v.orders), len(v.couriers)
        first_mile = v.city.T[np.ix_(v.cell, v.rest)].T * v.sf                    # [orders, couriers], seconds
        arrive = v.t + v.delay[None, :] + first_mile                             # t_v + firstMile (Alg. 2 uses loc(v, t))
        w = np.minimum(np.maximum(0.0, arrive - v.ready[:, None]), OMEGA_S)      # Eq. 2, Def. 5-7, w(o, v) Sec IV-A
        w[first_mile > FIRST_MILE_CAP_S] = OMEGA_S                               # 45-minute first-mile rule, Sec V-B
        k = max(1, int(self.k_mult * n_o / n_c))                                 # Sec V-B
        if k < n_o:                                                              # Alg. 2 l.8 and l.19, Lemma 1
            far = np.argsort(first_mile, axis=0, kind="stable")[k:, :]
            np.put_along_axis(w, far, OMEGA_S, axis=0)
        if self.ties == "shuffle":
            perm = self.rng.permutation(n_c)                                     # arbitrary vehicle order for ties
            rows, cols = linear_sum_assignment(w[:, perm])                       # Kuhn-Munkres, Sec IV-A
            return [(v.orders[i], v.couriers[perm[j]]) for i, j in zip(rows, cols) if w[i, perm[j]] < OMEGA_S]
        pairs = lexicographic_assignment(w, first_mile)                          # Kuhn-Munkres, Sec IV-A; ties: C4
        return [(v.orders[i], v.couriers[j]) for i, j in pairs if w[i, j] < OMEGA_S]
