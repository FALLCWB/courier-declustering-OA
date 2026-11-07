"""Event-driven simulator of one service period: orders arrive, couriers are assigned, ride, deliver, idle.

One order per courier at a time (no bundling in Part 1). The dispatch policy is the only lever: every
DISPATCH event it sees the pending orders and the available couriers and returns (order, courier) pairs.
An idle courier is available while parked or while moving between cells; a moving courier first
completes its current hop.
"""
import heapq
from dataclasses import dataclass, field

import numpy as np

from .metrics import concentration, w1

# Event kinds double as priorities for events at the same instant.
ARRIVAL, FREE, HOP, DECIDE, MEETUP, DISPATCH, SNAPSHOT = range(7)   # ties at one instant run in this order: the meet-up
# precedes that instant's dispatch and snapshot, as a start precedes 17:00's (the other kinds keep their relative order)
IDLE, BUSY = 0, 1


def next_steps(city, tgt):
    """Next cell from every cell toward `tgt`: the neighbor closest to tgt in road time if it is closer than the
    current cell, else tgt itself (first such neighbor on ties). Cached per city and target."""
    cache = city.__dict__.setdefault("_next", {})
    if tgt not in cache:
        nb = city.nbr
        valid = nb >= 0
        tn = np.where(valid, city.T[np.where(valid, nb, 0), tgt], np.inf)
        j = np.argmin(tn, axis=1)
        rows = np.arange(city.n)
        better = valid.any(axis=1) & (tn[rows, j] < city.T[:, tgt])
        cache[tgt] = np.where(better, nb[rows, j], tgt).astype(np.int32)
    return cache[tgt]


@dataclass
class Params:
    horizon_s: float = 4 * 3600.0     # orders are placed in [0, horizon)
    drain_s: float = 3 * 3600.0       # time after the horizon to finish open orders
    dispatch_s: float = 30.0          # Meituan dispatches in batches every 30 s or 1 min (TSL 2024 background)
    immediate: bool = False           # dispatch at every arrival and every release instead (tests)
    snapshot_s: float = 60.0
    lookahead_s: float = 1800.0       # expected-demand window of the concentration metric
    pickup_service_s: float = 240.0   # Grubhub MDRP instances: 4 min
    dropoff_service_s: float = 240.0  # Grubhub MDRP instances: 4 min; time after the door before the courier is free
    door_overhead_s: float = 0.0      # parking, walking and hand-over counted before the door time (Meituan arrive_time)
    pickup_overlaps_wait: bool = False  # True: leave at max(arrival + service, ready); False: max(arrival, ready) + service
    exp_service: bool = False         # exponential pickup service, no drop-off service (M/M/c test)
    speed_factor: float = 1.0         # multiplies free-flow road times; calibrated in step 5
    cover_s: float = 300.0            # demand counts as covered with an idle courier this close
    soon_s: float = 0.0               # > 0: also measure W1 with busy couriers free within soon_s, at their drop-off
    meetup_s: float = -1.0            # >= 0: at this time a share of the idle couriers rides to meetup_cell (extension)
    meetup_share: float = 0.2
    meetup_cell: int = -1
    meetup_jump: bool = False         # True: the chosen couriers are at the meet-up cell at once (already gathered)


@dataclass
class Fleet:
    start: np.ndarray       # start cell per courier
    home: np.ndarray        # preferred cell per courier
    full_time: np.ndarray   # bool per courier
    obedient: np.ndarray = None   # bool per courier: follows the policy's relocation commands (arm C); None = nobody


@dataclass
class View:
    """What a policy sees at a dispatch event."""
    t: float
    orders: np.ndarray      # pending order ids
    rest: np.ndarray
    cust: np.ndarray
    placed: np.ndarray
    ready: np.ndarray
    due: np.ndarray
    couriers: np.ndarray    # available courier ids
    cell: np.ndarray        # cell where each available courier can start from
    delay: np.ndarray       # seconds until it is there (rest of the current hop)
    sim: object = field(repr=False, default=None)

    @property
    def city(self):
        return self.sim.city

    @property
    def sf(self):
        return self.sim.params.speed_factor


class Simulator:
    def __init__(self, city, demand, orders, fleet, policy, behavior, params, seed=0, trace=False):
        self.city, self.demand, self.orders, self.fleet = city, demand, orders, fleet
        self.policy, self.behavior, self.params = policy, behavior, params
        n, m = len(fleet.start), len(orders)
        self.pos = fleet.start.astype(np.int32).copy()
        self.hop_to = np.full(n, -1, np.int32)
        self.hop_end = np.zeros(n)
        self.target = self.pos.copy()
        self.state = np.full(n, IDLE, np.int8)
        self.version = np.zeros(n, np.int64)
        self.idle_since = np.zeros(n)
        self.trips = np.zeros(n, np.int64)
        self.km_idle, self.km_dead, self.km_loaded = np.zeros(n), np.zeros(n), np.zeros(n)
        self.o_assigned = np.full(m, np.nan)
        self.o_from = np.full(m, -1, np.int32)        # cell the courier starts the order from
        self.o_courier = np.full(m, -1, np.int64)
        self.o_at_rest = np.full(m, np.nan)
        self.o_pickup = np.full(m, np.nan)
        self.o_door = np.full(m, np.nan)
        self.o_free = np.full(m, np.nan)
        self.pending = []
        self.snapshots = []
        # Idle gaps, measured like the Meituan moments: (courier, drop-off time, next acceptance time, drop-off cell,
        # cell the courier starts the next order from, whether it moved in between)
        self.gaps = []
        self.last_free = np.full(n, np.nan)
        self.moved = np.zeros(n, bool)
        self.pos_free = np.full(n, -1, np.int32)
        self.cur = np.full(n, -1, np.int64)              # order a busy courier carries
        self.legs = [] if trace else None
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 3]))
        self.seed = seed
        self.obedient = (np.zeros(n, bool) if fleet.obedient is None else np.asarray(fleet.obedient, bool))
        self.commands = hasattr(policy, "relocate") and self.obedient.any()
        self.meetup_couriers = []
        self.heap, self.seq = [], 0

    def push(self, t, kind, a=-1, b=-1):
        heapq.heappush(self.heap, (t, kind, self.seq, a, b))
        self.seq += 1

    # ---- run -------------------------------------------------------------------------------
    def run(self):
        p, n = self.params, len(self.pos)
        for o, t in enumerate(self.orders.placed):
            self.push(t, ARRIVAL, o)
        if not p.immediate:
            self.push(0.0, DISPATCH)
        for t in np.arange(0.0, p.horizon_s, p.snapshot_s):
            self.push(t, SNAPSHOT)
        if p.meetup_s >= 0:
            self.push(p.meetup_s, MEETUP)
        epoch = self.behavior.p.epoch_s
        for c, u in enumerate(self.rng.uniform(0, 1, n)):
            self.push(min(u * epoch, p.horizon_s), DECIDE, c, self.version[c])
        end = p.horizon_s + p.drain_s
        while self.heap:
            t, kind, _, a, b = heapq.heappop(self.heap)
            if t > end:
                break
            if kind == ARRIVAL:
                self.pending.append(a)
                if p.immediate:
                    self.dispatch(t)
            elif kind == FREE:
                self.release(a, b, t)
                if p.immediate:
                    self.dispatch(t)
            elif kind == HOP:
                if b == self.version[a]:
                    self.arrive_hop(a, t)
            elif kind == DECIDE:
                if b == self.version[a] and self.state[a] == IDLE and self.hop_to[a] < 0:
                    self.decide(a, t)
            elif kind == DISPATCH:
                self.dispatch(t)
                if self.commands:
                    self.relocate(t)
                open_orders = self.pending or (self.state == BUSY).any() or t < p.horizon_s
                if open_orders:
                    self.push(t + p.dispatch_s, DISPATCH)
            elif kind == SNAPSHOT:
                self.snapshot(t)
            elif kind == MEETUP:
                self.meetup(t)
        return self

    # ---- courier movement while idle -------------------------------------------------------
    def decide(self, c, t):
        if self.commands and self.obedient[c]:
            return                                        # the platform moves obedient couriers (arm C); no own choice
        b = self.behavior
        tgt = b.decide(c, int(self.pos[c]), int(self.fleet.home[c]), bool(self.fleet.full_time[c]), t,
                       self.idle_since[c], 0.0, int(self.trips[c]))
        self.target[c] = tgt
        if tgt == self.pos[c]:
            if not getattr(b, "gap_decided", lambda *a: False)(c, self.idle_since[c]):
                self.push(t + b.p.epoch_s, DECIDE, c, self.version[c])
        else:
            self.next_hop(c, t)

    def next_hop(self, c, t):
        T, cur, tgt = self.city.T, int(self.pos[c]), int(self.target[c])
        step = int(next_steps(self.city, tgt)[cur])
        dt = float(T[cur, step]) * self.params.speed_factor
        self.hop_to[c], self.hop_end[c] = step, t + dt
        self.moved[c] = True
        self.km_idle[c] += self.city.Dm[cur, step] / 1000.0
        if self.legs is not None:
            self.legs.append((c, t, t + dt, cur, step, "idle"))
        self.push(t + dt, HOP, c, self.version[c])

    def arrive_hop(self, c, t):
        self.pos[c], self.hop_to[c] = self.hop_to[c], -1
        if self.pos[c] == self.target[c]:
            if not getattr(self.behavior, "gap_decided", lambda *a: False)(c, self.idle_since[c]):
                self.push(t + self.behavior.p.epoch_s, DECIDE, c, self.version[c])
        else:
            self.next_hop(c, t)

    def send(self, c, tgt, t):
        """Point an idle courier at cell tgt: a parked one leaves now; a moving one finishes its hop first."""
        self.target[c] = int(tgt)
        if self.hop_to[c] >= 0:
            return
        self.version[c] += 1                               # cancels its pending own decision
        if self.pos[c] != self.target[c]:
            self.next_hop(c, t)

    def relocate(self, t):
        """Relocation commands of an arm C policy, followed by obedient idle couriers only."""
        idle = np.flatnonzero((self.state == IDLE) & self.obedient)
        if not len(idle):
            return
        cell = np.where(self.hop_to[idle] >= 0, self.hop_to[idle], self.pos[idle])
        view = View(t, np.empty(0, np.int64), np.empty(0, np.int32), np.empty(0, np.int32), np.empty(0), np.empty(0),
                    np.empty(0), idle, cell, np.zeros(len(idle)), self)
        for c, tgt in self.policy.relocate(view):
            c = int(c)
            if self.obedient[c] and self.state[c] == IDLE:
                self.send(c, tgt, t)

    def meetup(self, t):
        """Meet-up scenario: a share of the couriers idle at time t ride to one cell and wait there; their preferred
        areas stay as they were, so the next decision after a delivery can take them home."""
        p = self.params
        idle = np.flatnonzero(self.state == IDLE)
        k = int(round(p.meetup_share * len(idle)))
        rng = np.random.default_rng(np.random.SeedSequence([self.seed, 12]))
        chosen = np.sort(rng.choice(idle, size=k, replace=False)) if k else np.empty(0, int)
        decided = getattr(self.behavior, "_decided_gap", None)
        for c in chosen:
            if decided is not None:
                decided[int(c)] = self.idle_since[c]       # this gap's move is the meet-up
            if p.meetup_jump:                               # variant: already gathered at time t
                if self.legs is not None:                   # drawn as a zero-length leg (trace only)
                    self.legs.append((int(c), t, t, int(self.pos[c]), p.meetup_cell, "idle"))
                self.version[c] += 1
                self.pos[c] = self.target[c] = p.meetup_cell
                self.hop_to[c] = -1
            else:
                self.send(int(c), p.meetup_cell, t)
        self.meetup_couriers = chosen.tolist()

    # ---- dispatch and delivery -------------------------------------------------------------
    def dispatch(self, t):
        if not self.pending:
            return
        avail = np.flatnonzero(self.state == IDLE)
        if not len(avail):
            return
        hopping = self.hop_to[avail] >= 0
        cell = np.where(hopping, self.hop_to[avail], self.pos[avail])
        delay = np.where(hopping, self.hop_end[avail] - t, 0.0)
        ids = np.array(self.pending, dtype=np.int64)
        o = self.orders
        view = View(t, ids, o.rest[ids], o.cust[ids], o.placed[ids], o.ready[ids], o.due[ids],
                    avail, cell, delay, self)
        pairs = self.policy.assign(view)
        where = {int(c): i for i, c in enumerate(avail)}
        taken = set()
        for oid, c in pairs:
            oid, c = int(oid), int(c)
            assert self.state[c] == IDLE and np.isnan(self.o_assigned[oid]), "policy assigned a busy courier or an assigned order"
            i = where[c]
            self.assign(oid, c, t, int(cell[i]), float(delay[i]))
            taken.add(oid)
        if taken:
            self.pending = [x for x in self.pending if x not in taken]

    def assign(self, oid, c, t, cell, delay):
        p, T, D, o = self.params, self.city.T, self.city.Dm, self.orders
        self.pos[c], self.hop_to[c] = cell, -1          # a moving courier completes its hop first
        self.version[c] += 1
        self.state[c] = BUSY
        r, k = int(o.rest[oid]), int(o.cust[oid])
        if not np.isnan(self.last_free[c]):
            self.gaps.append((c, float(self.last_free[c]), float(t), int(self.pos_free[c]), cell, bool(self.moved[c])))
        at_rest = t + delay + float(T[cell, r]) * p.speed_factor * o.approach_mult[oid]
        service = self.rng.exponential(p.pickup_service_s) if p.exp_service else p.pickup_service_s
        if p.pickup_overlaps_wait:
            pickup = max(at_rest + service, o.ready[oid])
        else:
            pickup = max(at_rest, o.ready[oid]) + service
        door = pickup + (float(T[r, k]) * p.speed_factor + p.door_overhead_s) * o.ride_mult[oid]
        free = door + (0.0 if p.exp_service else p.dropoff_service_s)
        self.km_dead[c] += D[cell, r] / 1000.0
        self.km_loaded[c] += D[r, k] / 1000.0
        self.o_assigned[oid], self.o_courier[oid] = t, c
        self.cur[c] = oid
        self.o_from[oid] = cell
        self.o_at_rest[oid], self.o_pickup[oid], self.o_door[oid], self.o_free[oid] = at_rest, pickup, door, free
        if self.legs is not None:
            self.legs += [(c, t + delay, at_rest, cell, r, "to_pickup"), (c, at_rest, pickup, r, r, "wait"),
                          (c, pickup, door, r, k, "loaded"), (c, door, free, k, k, "drop")]
        self.push(free, FREE, c, oid)

    def release(self, c, oid, t):
        self.state[c] = IDLE
        self.pos[c] = self.target[c] = self.orders.cust[oid]
        self.idle_since[c] = t
        self.last_free[c], self.pos_free[c], self.moved[c] = t, self.pos[c], False
        self.trips[c] += 1
        self.decide(c, t)

    # ---- measurement -----------------------------------------------------------------------
    def snapshot(self, t):
        p = self.params
        idle = np.flatnonzero(self.state == IDLE)
        exp = self.demand.expected_pickups(t, t + p.lookahead_s)
        row = concentration(self.city, self.pos[idle], exp, p.speed_factor, p.cover_s)
        row["t"] = t
        if p.soon_s > 0:
            busy = np.flatnonzero(self.state == BUSY)
            soon = busy[self.o_free[self.cur[busy]] <= t + p.soon_s]
            cells = np.concatenate([self.pos[idle], self.orders.cust[self.cur[soon]]])
            row["n_soon"] = int(len(soon))
            row["w1_soon_min"], row["emd_warning_soon"] = w1(self.city, cells, exp, p.speed_factor, with_warning=True)
        row["n_busy"] = int((self.state == BUSY).sum())
        row["n_pending"] = len(self.pending)
        self.snapshots.append(row)
