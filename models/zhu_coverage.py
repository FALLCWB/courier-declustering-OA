"""Coverage control of idle couriers (Zhu, Sirmatel, Ferrari-Trecate and Geroliminis, IEEE TCST 2024), graph version
(CVR-graph): every idle courier is sent to the demand-weighted centroid of its radius-limited graph Voronoi cell; orders
go to the nearest idle courier (the paper's assignment rule). Arm C: only obedient couriers follow the commands.

Fidelity note: models/fidelity/zhu_coverage.md; reading note: literature/model-specs/zhu-2024.md (arXiv 2311.11716v1).
"""
import numpy as np

from sim.core.policies import NearestIdle

R_G_M = np.sqrt(2.0) * 1000.0    # graph radius r_G = sqrt(2) r, r = 1000 m (p.8)


class ZhuCoverage(NearestIdle):
    """relocate(): partition the cells among all idle couriers by road distance (Eq. 18), limit each part to R_G_M
    (Eq. 19), and send each obedient courier to the cell minimizing sum over its part of d(cell, q)^2 phi(q)
    (Eq. 22 as read in the reading note), phi = the static pickup density of the day (Eq. 12). A radius-limited part
    with no demand falls back to the whole part (G7 verdict E1); a part with no demand at all gets no command."""
    name = "zhu"

    def __init__(self, seed=0, radius_m=R_G_M, tie="lower"):
        """tie: "lower" (the frozen rule: a tied cell goes to the lower courier index) or "random" (post-freeze
        sensitivity, Filipe 2026-11-04: each tied cell goes to a random closest courier, from the episode's own stream)."""
        self.radius = radius_m
        self.phi = None
        self.tie = tie
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 17])) if tie == "random" else None
        # per episode: control steps with obedient idle couriers; commands sent; of those, sent by the empty-part rule;
        # couriers left without a command because their whole part holds no demand, or because they own no cell
        self.events = {"steps": 0, "commands": 0, "whole_part_commands": 0, "no_demand_in_part": 0, "owns_no_cell": 0}

    def relocate(self, v):
        city, sim = v.city, v.sim
        self.events["steps"] += 1
        if self.phi is None:
            share = sim.demand.expected_pickups(0.0, sim.params.horizon_s)
            self.phi = share / share.sum()
            # the city build stores Dm column-major, so a row gather jumps 17 KB per value; a row-major copy holds the
            # same values and makes the per-step gather about four times faster (DECISIONS.md, X7)
            self.Dm = np.ascontiguousarray(city.Dm)
        idle = np.flatnonzero(sim.state == 0)
        pos = np.where(sim.hop_to[idle] >= 0, sim.hop_to[idle], sim.pos[idle])
        D = self.Dm[pos]                                              # [idle couriers, cells] road metres
        owner = np.argmin(D, axis=0)                                  # graph Voronoi (Eq. 18), ties to the lower index
        if self.tie == "random":                                      # sensitivity only: a random closest courier
            tied = D == D[owner, np.arange(city.n)]
            multi = np.flatnonzero(tied.sum(axis=0) > 1)
            if len(multi):
                r = self.rng.random((len(idle), len(multi)))
                r[~tied[:, multi]] = np.inf
                owner[multi] = np.argmin(r, axis=0)
        reach = D[owner, np.arange(city.n)] <= self.radius            # r-limited part (Eq. 19)
        # cells grouped by owner once per step, ascending within each part (stable sort): the same arrays as
        # np.flatnonzero(owner == i) per courier, without a scan of every cell per courier
        order = np.argsort(owner, kind="stable")
        bounds = np.searchsorted(owner[order], np.arange(len(idle) + 1))
        where = {int(c): i for i, c in enumerate(idle)}
        cmds = []
        for c in v.couriers:
            i = where[int(c)]
            part = order[bounds[i]:bounds[i + 1]]
            if not len(part):                                          # shares its cell with a lower-index courier
                self.events["owns_no_cell"] += 1
                continue
            cand = part[reach[part]]                                   # candidate cells: the courier's part
            q = cand[self.phi[cand] > 0]
            whole = not len(q)
            if whole:                                                  # empty-part rule (G7 verdict E1): no demand
                cand = part                                            # within r_G, so the whole part (Eq. 18 alone)
                q = cand[self.phi[cand] > 0]
                if not len(q):
                    self.events["no_demand_in_part"] += 1
                    continue
            cost = (self.Dm[np.ix_(cand, q)].astype(float) ** 2 * self.phi[q][None, :]).sum(axis=1)
            cmds.append((int(c), int(cand[np.argmin(cost)])))           # ties to the lower cell index
            self.events["commands"] += 1
            self.events["whole_part_commands"] += whole
        return cmds
