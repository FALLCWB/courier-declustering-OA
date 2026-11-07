"""What an idle courier does: return to its preferred area, stay, move to the nearest hotspot, or cruise.

Fitted structure (S3, `avaliacao/20261102-1146-behavior-single-final`): one decision per gap between two orders,
made one decision interval after the drop-off. With probability p_return a courier outside its preferred area
(2 km around its start cell) heads back to it (the drift-back test); otherwise it picks stay, hotspot or cruise by a
multinomial logit whose coefficient names and values, except the stay constant, follow Ashkrof et al. (2024),
Transportation Letters, Table 3. Then it waits where it went until its next order. The defaults below are the fitted
values; `single_decision=False` gives the re-deciding structure of the first fit, `one_move_per_gap` the second.
"""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class BehaviorParams:
    p_return: float = 0.75            # fitted, 95% interval 0.675 to 0.825
    home_radius_m: float = 2000.0
    epoch_s: float = 42.0             # fitted, 29.4 to 42 s: delay before the decision after a drop-off
    hotspot_quantile: float = 0.95
    cruise_radius_m: float = 2000.0   # fitted, 2,000 to 2,800 m
    centre_radius_m: float = 1500.0
    coef: dict = field(default_factory=lambda: {
        "asc_stay": -3.0, "wait_min_stay": -0.022, "centre_stay": 0.322, "part_time_stay": 0.393,   # asc_stay fitted, -3.5 to -2
        "drive_min_hotspot": -0.025, "trips_hotspot": 0.080,
        "begin_shift_cruise": -0.764, "familiar_cruise": -0.312,
    })
    begin_shift_s: float = 3600.0
    one_move_per_gap: bool = False    # True: at most one stay/hotspot/cruise move between two orders (returns repeat)
    single_decision: bool = True      # one decision per gap, one interval after the drop-off; then it waits
    no_hotspot: bool = False          # exploratory only (G4 verdict V3): the logit drops the hotspot alternative


class Behavior:
    """Idle decisions. `rngs[c]` is courier c's own random stream, so draws stay aligned across policies."""

    def __init__(self, city, params, pickup_share, speed_factor, seed, n_couriers):
        self.city, self.p, self.sf = city, params, speed_factor
        cut = np.quantile(pickup_share[pickup_share > 0], params.hotspot_quantile) if (pickup_share > 0).any() else 0
        self.hotspots = np.flatnonzero(pickup_share >= cut) if cut > 0 else np.flatnonzero(city.rest > 0)
        self.rngs = [np.random.default_rng(s) for s in np.random.SeedSequence([seed, 2]).spawn(n_couriers)]
        self.seed = seed
        self._near = {}
        self._inside = {}
        self._moved_gap = {}              # courier -> idle_since of the gap in which it already made its move
        self._decided_gap = {}            # courier -> idle_since of the gap in which it already decided
        hot_t = city.T[:, self.hotspots] * speed_factor           # nearest hotspot of every cell, computed once
        self.nearest_hot = self.hotspots[np.argmin(hot_t, axis=1)]
        self.hot_min = hot_t.min(axis=1)
        self.in_centre = city.straight_m(city.centre, np.arange(city.n)) <= params.centre_radius_m

    def _within(self, i, radius_m):
        key = (i, radius_m)
        if key not in self._near:
            self._near[key] = np.flatnonzero(self.city.straight_m(i, np.arange(self.city.n)) <= radius_m)
        return self._near[key]

    def gap_decided(self, c, idle_since):
        """True once a courier has made the one decision of its current gap (single_decision): no more DECIDE events."""
        return self.p.single_decision and self._decided_gap.get(c) == idle_since

    def decide(self, c, pos, home, full_time, t, idle_since, shift_start, trips):
        """Return the target cell for courier c, now parked at `pos`. Returning `pos` means stay."""
        rng, p, k = self.rngs[c], self.p, self.p.coef
        if home not in self._inside:
            self._inside[home] = self.city.straight_m(home, np.arange(self.city.n)) <= p.home_radius_m
        inside_home = bool(self._inside[home][pos])
        if p.single_decision:
            if t <= idle_since or self._decided_gap.get(c) == idle_since:
                return pos
            self._decided_gap[c] = idle_since
            # The one decision of the gap after delivery `trips` uses its own draws, so a courier decides the same way
            # under every model whatever the waiting before (common random numbers; five-agent review, S8).
            gap_rng = np.random.default_rng(np.random.SeedSequence([self.seed, 2, c, trips]))
            u_return, u_choice, u_cell = gap_rng.uniform(size=3)
        else:
            u_return, u_choice, u_cell = rng.uniform(size=3)
        if not inside_home and u_return < p.p_return:
            return home
        if p.one_move_per_gap and self._moved_gap.get(c) == idle_since:
            return pos
        nearest_hot = self.nearest_hot[pos]
        v_stay = (k["asc_stay"] + k["wait_min_stay"] * (t - idle_since) / 60 + k["centre_stay"] * self.in_centre[pos]
                  + k["part_time_stay"] * (not full_time))
        v_hot = k["drive_min_hotspot"] * self.hot_min[pos] / 60 + k["trips_hotspot"] * trips
        v_cruise = k["begin_shift_cruise"] * (t - shift_start < p.begin_shift_s) + k["familiar_cruise"] * inside_home
        if p.no_hotspot:
            v_hot = -np.inf
        v = np.array([v_stay, v_hot, v_cruise])
        prob = np.exp(v - v.max())
        prob /= prob.sum()
        choice = int(np.searchsorted(np.cumsum(prob), u_choice))
        if choice == 0 or (choice == 1 and nearest_hot == pos):
            return pos
        if choice == 1:
            self._moved_gap[c] = idle_since
            return int(nearest_hot)
        ring = self._within(pos, p.cruise_radius_m)
        ring = ring[ring != pos]
        if not len(ring):
            return pos
        self._moved_gap[c] = idle_since
        return int(ring[min(int(u_cell * len(ring)), len(ring) - 1)])


class StayBehavior:
    """Couriers never move while idle (used by tests and as the no-movement reference)."""

    def __init__(self, n_couriers=0, epoch_s=1e12):
        self.p = BehaviorParams(epoch_s=epoch_s)

    def decide(self, c, pos, *args):
        return pos
