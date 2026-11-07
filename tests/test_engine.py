"""Simulator checks with known answers: exact single-order times, conservation, M/M/c waiting, determinism."""
import math

import numpy as np
import pytest

from sim.core.behavior import StayBehavior
from sim.core.city import toy_line
from sim.core.demand import Component, Demand, Orders
from sim.core.engine import Fleet, Params, Simulator
from sim.core.metrics import concentration, gini, summarize
from sim.core.policies import BatchMatching, NearestIdle


def one_order(placed, rest, cust, ready, due=1e9):
    return Orders(np.array([placed]), np.array([rest]), np.array([cust]), np.array([ready]), np.array([due]))


def run(city, orders, starts, policy=None, params=None, demand=None, seed=0):
    n = len(starts)
    fleet = Fleet(np.array(starts), np.array(starts), np.ones(n, bool))
    demand = demand or Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    params = params or Params(horizon_s=3600, drain_s=7200)
    return Simulator(city, demand, orders, fleet, policy or NearestIdle(), StayBehavior(n), params, seed).run()


@pytest.mark.parametrize("ready, expect", [(100.0, 180 + 240 + 240), (900.0, 900 + 240 + 240)])
def test_single_order_time_equals_routed_time(ready, expect):
    # courier at cell 0, restaurant cell 3, customer cell 7, 60 s per cell, 240 s pickup service
    city = toy_line(10, hop_s=60)
    sim = run(city, one_order(0.0, 3, 7, ready), [0])
    assert sim.o_door[0] == pytest.approx(expect, abs=1e-9)
    assert sim.o_free[0] == pytest.approx(expect + 240, abs=1e-9)
    assert sim.km_dead[0] == pytest.approx(0.9) and sim.km_loaded[0] == pytest.approx(1.2)


def test_order_waits_for_next_dispatch_cycle():
    city = toy_line(10, hop_s=60)
    sim = run(city, one_order(10.0, 0, 1, 0.0), [0])
    assert sim.o_assigned[0] == 30.0   # dispatch every 30 s


@pytest.mark.parametrize("policy", [NearestIdle(), BatchMatching()])
def test_conservation_every_order_delivered_once(policy):
    city = toy_line(30, hop_s=45)
    rng = np.random.default_rng(1)
    m = 150
    placed = np.sort(rng.uniform(0, 3600, m))
    orders = Orders(placed, rng.integers(0, 30, m), rng.integers(0, 30, m), placed + rng.uniform(0, 900, m),
                    placed + 2400)
    sim = run(city, orders, list(rng.integers(0, 30, 40)), policy=policy)
    assert np.isfinite(sim.o_door).all() and (sim.o_courier >= 0).all()
    assert sim.trips.sum() == m
    for c in range(40):          # one order at a time per courier
        mine = np.flatnonzero(sim.o_courier == c)
        mine = mine[np.argsort(sim.o_assigned[mine])]
        assert (sim.o_assigned[mine][1:] >= sim.o_free[mine][:-1] - 1e-9).all()
    assert (sim.o_assigned >= placed).all() and (sim.o_pickup >= sim.orders.ready).all()


def erlang_c_wait(lam, mu, c):
    a = lam / mu
    top = a ** c / math.factorial(c) * c / (c - a)
    p_wait = top / (sum(a ** k / math.factorial(k) for k in range(c)) + top)
    return p_wait / (c * mu - lam)


def test_waiting_time_matches_mmc_theory():
    # zero travel, zero preparation, exponential service: an M/M/c queue served first come first served
    city = toy_line(1)
    lam, mean_s, c = 0.8 / 60, 600.0, 10              # load 0.8 per courier
    rng = np.random.default_rng(7)
    placed = np.cumsum(rng.exponential(1 / lam, 40000))
    orders = Orders(placed, np.zeros(len(placed), int), np.zeros(len(placed), int), placed, placed + 1e9)
    params = Params(horizon_s=placed[-1] + 1, drain_s=36000, immediate=True, exp_service=True,
                    pickup_service_s=mean_s, snapshot_s=1e9)
    sim = run(city, orders, [0] * c, params=params)
    wait = (sim.o_assigned - placed)[2000:]               # drop the warm-up
    batches = wait[: len(wait) // 40 * 40].reshape(40, -1).mean(axis=1)
    half = 2.023 * batches.std(ddof=1) / math.sqrt(40)    # t quantile, 39 degrees of freedom
    theory = erlang_c_wait(lam, 1 / mean_s, c)
    assert abs(batches.mean() - theory) < half, (batches.mean(), theory, half)


def test_same_seed_same_result():
    city = toy_line(20, hop_s=50)
    comp = Component(np.full(60, 3.0), np.ones(20))
    demand = Demand(city, [comp], prep_s=np.array([300.0, 600.0]))
    orders = demand.sample(seed=5)
    a = summarize(run(city, orders, list(range(0, 20, 2)), demand=demand))
    b = summarize(run(city, demand.sample(seed=5), list(range(0, 20, 2)), demand=demand))
    assert a == b
    assert not np.array_equal(orders.placed, demand.sample(seed=6).placed)


def test_concentration_metric_known_values():
    city = toy_line(5, hop_s=60)
    demand = np.array([0, 0, 0, 0, 1.0])
    all_at_0 = concentration(city, np.array([0, 0]), demand, 1.0, 180)   # 4 min away, 3 min cover
    assert all_at_0["w1_min"] == pytest.approx(4.0)        # every courier is 4 cells (4 min) away
    assert all_at_0["tv"] == pytest.approx(1.0)
    assert all_at_0["uncovered"] == pytest.approx(1.0)
    matched = concentration(city, np.array([4]), demand, 1.0, 180)
    assert matched["w1_min"] == pytest.approx(0.0) and matched["uncovered"] == 0.0
    assert gini([1, 1, 1, 1]) == pytest.approx(0.0) and gini([0, 0, 0, 4]) == pytest.approx(0.75)


def test_intra_cell_trip_takes_time_and_w1_stays_zero_when_matched():
    city = toy_line(5, hop_s=60)
    city.set_intra_cell(t_s=25.0, d_m=150.0)
    assert city.T[2, 2] == pytest.approx(25.0) and city.Dm[2, 2] == pytest.approx(150.0)
    assert city.T[1, 2] == pytest.approx(60.0)                       # off-diagonal untouched
    sim = run(city, one_order(0.0, 3, 3, 0.0), [3])                  # restaurant and customer in the same cell
    assert sim.o_door[0] == pytest.approx(25 + 240 + 25.0)           # dispatch at 0 s, ride in cell, service, ride
    matched = concentration(city, np.array([4]), np.array([0, 0, 0, 0, 1.0]), 1.0, 180)
    assert matched["w1_min"] == pytest.approx(0.0)


def test_hex_mean_distance_matches_known_constant():
    from sim.core.city import hex_mean_distance
    assert hex_mean_distance() == pytest.approx(0.8262, abs=0.003)   # regular hexagon of side 1


def test_door_overhead_counts_before_the_door_time():
    city = toy_line(10, hop_s=60)
    params = Params(horizon_s=3600, drain_s=7200, door_overhead_s=250.0, dropoff_service_s=0.0)
    sim = run(city, one_order(0.0, 3, 7, 100.0), [0], params=params)
    assert sim.o_door[0] == pytest.approx(180 + 240 + 240 + 250)    # to restaurant, service, ride, park and hand over
    assert sim.o_free[0] == pytest.approx(sim.o_door[0])


def test_promise_grows_with_distance_and_has_a_floor():
    city = toy_line(10, hop_s=60, hop_m=1000.0)
    comp = Component(np.full(60, 5.0), np.ones(10))
    demand = Demand(city, [comp], promise_s=1000.0, promise_per_km_s=300.0, promise_floor_s=1500.0)
    o = demand.sample(seed=3)
    km = city.straight_m(o.rest, o.cust) / 1000.0
    assert np.allclose(o.due - o.placed, np.maximum(1500.0, 1000.0 + 300.0 * km))
    assert (km > 2).any() and (km < 1).any()


@pytest.mark.parametrize("ready, pickup", [(100.0, 180 + 240), (900.0, 900.0)])
def test_pickup_service_overlaps_the_wait_for_food(ready, pickup):
    # courier at cell 0, restaurant cell 3 (180 s), customer cell 7 (240 s ride); parking and walking in happen
    # while the food is prepared, so the courier leaves at max(arrival + service, ready)
    city = toy_line(10, hop_s=60)
    params = Params(horizon_s=3600, drain_s=7200, pickup_overlaps_wait=True)
    sim = run(city, one_order(0.0, 3, 7, ready), [0], params=params)
    assert sim.o_pickup[0] == pytest.approx(pickup)
    assert sim.o_door[0] == pytest.approx(pickup + 240)


def test_travel_noise_scales_the_approach_and_the_pickup_to_door_time():
    # courier at cell 0, restaurant cell 3 (180 s free flow), customer cell 7 (240 s), 250 s door overhead;
    # approach factor 2 doubles the 180 s, ride factor 0.5 halves ride plus door overhead
    city = toy_line(10, hop_s=60)
    o = one_order(0.0, 3, 7, 100.0)
    o.approach_mult, o.ride_mult = np.array([2.0]), np.array([0.5])
    params = Params(horizon_s=3600, drain_s=7200, door_overhead_s=250.0, dropoff_service_s=0.0)
    sim = run(city, o, [0], params=params)
    assert sim.o_at_rest[0] == pytest.approx(360.0)
    assert sim.o_pickup[0] == pytest.approx(360.0 + 240.0)
    assert sim.o_door[0] == pytest.approx(600.0 + 0.5 * (240.0 + 250.0))


def test_travel_noise_has_mean_one_and_is_the_same_for_every_policy():
    city = toy_line(30, hop_s=45)
    comp = Component(np.full(60, 3.0), np.ones(30))
    noisy = Demand(city, [comp], ride_sigma=0.31)
    o = noisy.sample(seed=5)
    big = Demand(city, [Component(np.full(600, 60.0), np.ones(30))], ride_sigma=0.31).sample(seed=1)
    for m in (big.approach_mult, big.ride_mult):
        assert m.mean() == pytest.approx(1.0, abs=0.01)
        assert np.log(m).std() == pytest.approx(0.31, abs=0.01)
    assert abs(np.corrcoef(big.approach_mult, big.ride_mult)[0, 1]) < 0.02
    plain = Demand(city, [comp]).sample(seed=5)          # the noise never shifts the order stream
    for f in ("placed", "rest", "cust", "ready", "due"):
        assert np.array_equal(getattr(plain, f), getattr(o, f))
    assert (plain.approach_mult == 1.0).all() and (plain.ride_mult == 1.0).all()
    again = noisy.sample(seed=5)
    assert np.array_equal(again.ride_mult, o.ride_mult) and np.array_equal(again.approach_mult, o.approach_mult)
    starts = list(np.random.default_rng(2).integers(0, 30, 25))
    ride = {}
    for policy in (NearestIdle(), BatchMatching()):
        sim = run(city, o, starts, policy=policy, demand=noisy)
        ride[type(policy).__name__] = sim.o_door - sim.o_pickup
        expect = (city.T[o.rest, o.cust] * sim.params.speed_factor + sim.params.door_overhead_s) * o.ride_mult
        assert np.allclose(sim.o_door - sim.o_pickup, expect)
    assert np.allclose(ride["NearestIdle"], ride["BatchMatching"])


def test_idle_gaps_are_logged_from_drop_off_to_next_acceptance():
    # one courier at cell 0: order 0 (restaurant 3, customer 7) ends at 180 + 240 + 240 + 240 = 900 s (door 660,
    # drop-off service 240); order 1 placed at 1000 s is accepted at the 1020 s dispatch; the courier stayed at 7
    city = toy_line(10, hop_s=60)
    placed = np.array([0.0, 1000.0])
    orders = Orders(placed, np.array([3, 5]), np.array([7, 2]), placed + 100.0, placed + 1e9)
    sim = run(city, orders, [0])
    assert sim.gaps == [(0, 900.0, 1020.0, 7, 7, False)]


def test_idle_gap_records_the_move_of_a_courier_heading_home():
    from sim.core.behavior import Behavior, BehaviorParams
    # home is cell 0; the drop-off at cell 9 is 2,700 m away, outside the 2 km preferred area; p_return 1 sends it home
    city = toy_line(10, hop_s=60)
    placed = np.array([0.0, 3000.0])
    orders = Orders(placed, np.array([0, 1]), np.array([9, 0]), placed, placed + 1e9)
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    fleet = Fleet(np.array([0]), np.array([0]), np.ones(1, bool))
    bp = BehaviorParams(p_return=1.0)
    bp.coef["asc_stay"] = 50.0                     # once home it stays
    beh = Behavior(city, bp, np.ones(city.n), 1.0, 0, 1)
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), beh, Params(horizon_s=3600, drain_s=7200), 0).run()
    (c, t_free, t_acc, d_cell, g_cell, moved), = sim.gaps
    assert (c, d_cell, g_cell, moved) == (0, 9, 0, True) and t_acc - t_free > 540


def test_soon_free_supply_counts_couriers_free_within_5_min_at_their_drop_off():
    # the courier is busy until 900 s (see the idle-gap test); with soon_s = 300 it counts as supply at its drop-off
    # cell 7 from the 600 s snapshot on, and at 900 s it is idle again
    from sim.core.metrics import concentration
    city = toy_line(10, hop_s=60)
    demand = Demand(city, [Component(np.ones(600), np.ones(city.n))])
    params = Params(horizon_s=3600, drain_s=7200, soon_s=300.0)
    sim = run(city, one_order(0.0, 3, 7, 100.0), [0], params=params, demand=demand)
    snap = {s["t"]: s for s in sim.snapshots}
    assert snap[540.0]["n_soon"] == 0 and snap[600.0]["n_soon"] == 1 and snap[840.0]["n_soon"] == 1
    assert snap[900.0]["n_soon"] == 0 and snap[900.0]["n_idle"] == 1
    exp = demand.expected_pickups(600.0, 600.0 + params.lookahead_s)
    assert snap[600.0]["w1_soon_min"] == pytest.approx(concentration(city, np.array([7]), exp, 1.0, 300.0)["w1_min"])
    assert np.isnan(snap[600.0]["w1_min"])                 # nobody idle at 600 s


def test_one_move_per_gap_lets_a_courier_choose_a_logit_move_only_once_between_orders():
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(20, hop_s=60)
    bp = BehaviorParams(p_return=0.0, cruise_radius_m=3000.0, one_move_per_gap=True, single_decision=False)
    bp.coef = dict(bp.coef, asc_stay=-50.0, drive_min_hotspot=-50.0)     # always cruise
    hot = np.zeros(city.n)
    hot[0] = 1.0                                                         # the only hotspot, 10 min away
    beh = Behavior(city, bp, hot, 1.0, 0, 1)
    first = beh.decide(0, 10, 10, True, 100.0, 100.0, 0.0, 0)
    assert first != 10                                                   # cruises after the drop-off
    assert beh.decide(0, first, 10, True, 400.0, 100.0, 0.0, 0) == first  # same gap: stays where it went
    assert beh.decide(0, first, 10, True, 900.0, 800.0, 0.0, 1) != first  # next gap: may move again
    free = Behavior(city, BehaviorParams(p_return=0.0, cruise_radius_m=3000.0, coef=bp.coef, single_decision=False), hot,
                    1.0, 0, 1)
    a = free.decide(0, 10, 10, True, 100.0, 100.0, 0.0, 0)
    assert free.decide(0, a, 10, True, 400.0, 100.0, 0.0, 0) != a        # without the rule it keeps wandering


def test_single_decision_waits_one_interval_then_decides_once_per_gap():
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(20, hop_s=60)
    bp = BehaviorParams(p_return=0.0, cruise_radius_m=3000.0, epoch_s=120.0, single_decision=True)
    bp.coef = dict(bp.coef, asc_stay=-50.0, drive_min_hotspot=-50.0)     # always cruise when it decides
    hot = np.zeros(city.n)
    hot[0] = 1.0
    beh = Behavior(city, bp, hot, 1.0, 0, 1)
    assert beh.decide(0, 10, 10, True, 100.0, 100.0, 0.0, 0) == 10      # at the drop-off: waits
    target = beh.decide(0, 10, 10, True, 220.0, 100.0, 0.0, 0)
    assert target != 10                                                   # one interval later: its one decision
    assert beh.decide(0, target, 10, True, 600.0, 100.0, 0.0, 0) == target  # then it waits where it went
    bp2 = BehaviorParams(p_return=1.0, single_decision=True, epoch_s=120.0)
    beh2 = Behavior(city, bp2, hot, 1.0, 0, 1)
    assert beh2.decide(0, 19, 0, True, 220.0, 100.0, 0.0, 0) == 0         # outside its area: the decision is to return
    assert beh2.decide(0, 12, 0, True, 400.0, 100.0, 0.0, 0) == 12        # no second return in the same gap


def test_undelivered_orders_enter_order_to_door_at_the_end_of_the_drain():
    # one courier, 600 s per cell: order 0 (restaurant and customer at cell 9) keeps it busy past the drain end
    # (5,400 s), so order 1 placed at 100 s is never assigned and counts at 5,400 - 100 s, a lower bound
    city = toy_line(10, hop_s=600)
    placed = np.array([0.0, 100.0])
    orders = Orders(placed, np.array([9, 0]), np.array([9, 1]), placed, placed + 600.0)
    sim = run(city, orders, [0], params=Params(horizon_s=3600, drain_s=1800))
    assert np.isnan(sim.o_door[1]) and sim.o_door[0] == pytest.approx(5640.0)
    s = summarize(sim)
    # order 0 is scheduled to reach the door at 5,640 s, after the drain's end, so it is not delivered by the end of
    # the drain either and also enters at 5,400 s (preregistration section 7, G3 verdict C2)
    c2d = np.array([5400.0, 5300.0]) / 60
    assert s["delivered"] == 0 and s["undelivered"] == 2
    assert s["p90_c2d_min"] == pytest.approx(np.percentile(c2d, 90))
    assert s["mean_c2d_min"] == pytest.approx(c2d.mean()) and s["late_rate"] == 1.0


def test_gini_of_idle_couriers_is_undefined_when_nobody_is_idle():
    city = toy_line(5, hop_s=60)
    row = concentration(city, np.array([], dtype=int), np.ones(5), 1.0, 300.0)
    assert np.isnan(row["gini_idle"]) and np.isnan(row["w1_min"])
    row = concentration(city, np.array([0, 4]), np.ones(5), 1.0, 300.0)
    assert row["emd_warning"] == 0 and row["gini_idle"] == pytest.approx(0.6)


def test_single_decision_draws_depend_only_on_seed_courier_and_gap():
    # the decision of courier 0 in its gap after delivery k must not depend on how many times it was asked before
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(20, hop_s=60)
    hot = np.zeros(city.n)
    hot[0] = 1.0
    bp = BehaviorParams(p_return=0.5, cruise_radius_m=3000.0, epoch_s=42.0)
    a = Behavior(city, bp, hot, 1.0, 7, 2)
    b = Behavior(city, bp, hot, 1.0, 7, 2)
    for t in (100.0, 142.0, 184.0, 226.0):                 # b is asked four more times in an earlier gap
        b.decide(0, 10, 10, True, t, 100.0, 0.0, 2)
    assert a.decide(0, 15, 3, True, 942.0, 900.0, 0.0, 3) == b.decide(0, 15, 3, True, 942.0, 900.0, 0.0, 3)


def test_single_decision_stops_asking_once_the_gap_is_decided():
    from sim.core.behavior import Behavior, BehaviorParams
    calls = []

    class Counting(Behavior):
        def decide(self, c, *args):
            calls.append(args[3])                        # t
            return super().decide(c, *args)

    city = toy_line(10, hop_s=60)
    bp = BehaviorParams(p_return=0.0, epoch_s=42.0)
    bp.coef = dict(bp.coef, asc_stay=50.0)                # it decides to stay
    orders = Orders(np.array([0.0]), np.array([1]), np.array([2]), np.array([0.0]), np.array([1e9]))
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    fleet = Fleet(np.array([0]), np.array([0]), np.ones(1, bool))
    beh = Counting(city, bp, np.ones(city.n), 1.0, 0, 1)
    Simulator(city, demand, orders, fleet, NearestIdle(), beh, Params(horizon_s=3600, drain_s=3600), 0).run()
    after = [t for t in calls if t >= 300.0]              # the delivery ends before 300 s
    assert len(after) == 2                                # at the drop-off, then the one decision 42 s later


def test_without_the_hotspot_alternative_a_courier_never_heads_to_a_hotspot():
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(20, hop_s=60)
    hot = np.zeros(city.n)
    hot[0] = 1.0
    coef = dict(BehaviorParams().coef, asc_stay=-50.0, drive_min_hotspot=0.0, trips_hotspot=50.0)   # hotspot dominates
    with_hot = Behavior(city, BehaviorParams(p_return=0.0, coef=coef), hot, 1.0, 1, 1)
    no_hot = Behavior(city, BehaviorParams(p_return=0.0, coef=coef, no_hotspot=True), hot, 1.0, 1, 1)
    assert with_hot.decide(0, 10, 10, True, 200.0, 100.0, 0.0, 1) == 0                  # the only hotspot
    assert no_hot.decide(0, 10, 10, True, 200.0, 100.0, 0.0, 1) not in (0, 10)         # cruises instead


class HoldThenNearest:
    """Holds every order until t >= 120 s, then assigns by nearest courier (a model that may hold, arm B)."""
    def assign(self, v):
        return [] if v.t < 120.0 else NearestIdle().assign(v)


def test_a_held_order_waits_for_a_later_epoch_and_the_wait_counts():
    city = toy_line(10, hop_s=60)
    sim = run(city, one_order(0.0, 1, 2, 0.0), [0], policy=HoldThenNearest(),
              params=Params(horizon_s=3600, drain_s=7200, pickup_overlaps_wait=True, dropoff_service_s=0.0))
    assert sim.o_assigned[0] == 120.0                                 # held through the 0, 30, 60 and 90 s epochs
    assert sim.o_door[0] == pytest.approx(120.0 + 60.0 + 240.0 + 60.0)  # to restaurant, service, ride


class SendAllTo9(NearestIdle):
    """Assigns by nearest courier and orders every idle courier to cell 9 (an arm C model)."""
    def relocate(self, v):
        return [(c, 9) for c in v.couriers]


def test_only_obedient_couriers_follow_relocation_and_zero_obedience_equals_nearest():
    city = toy_line(10, hop_s=60)
    orders = Orders(np.array([1000.0]), np.array([0]), np.array([1]), np.array([1000.0]), np.array([1e9]))
    params = Params(horizon_s=3600, drain_s=3600)
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    def go(policy, obedient):
        fleet = Fleet(np.array([0, 0]), np.array([0, 0]), np.ones(2, bool), obedient=np.array(obedient))
        return Simulator(city, demand, orders, fleet, policy, StayBehavior(2), params, 0).run()
    mixed = go(SendAllTo9(), [True, False])
    assert mixed.o_courier[0] == 1                                    # courier 0 left for cell 9, courier 1 stayed
    assert mixed.km_idle[0] > 0 and mixed.km_idle[1] == 0
    none = go(SendAllTo9(), [False, False])
    base = go(NearestIdle(), [False, False])
    assert none.o_courier[0] == base.o_courier[0] and none.o_door[0] == base.o_door[0] and none.km_idle.sum() == 0


def test_meetup_sends_the_chosen_share_of_idle_couriers_to_one_cell_where_they_wait():
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(12, hop_s=60)
    orders = Orders(np.array([5000.0]), np.array([0]), np.array([1]), np.array([5000.0]), np.array([1e9]))
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    bp = BehaviorParams()
    bp.coef = dict(bp.coef, asc_stay=50.0)                            # they would otherwise stay where they are
    fleet = Fleet(np.array([0, 2, 4, 6]), np.array([0, 2, 4, 6]), np.ones(4, bool))
    params = Params(horizon_s=7200, drain_s=600, meetup_s=600.0, meetup_share=0.5, meetup_cell=11)
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), Behavior(city, bp, np.ones(city.n), 1.0, 3, 4),
                    params, 3).run()
    at_meet = np.flatnonzero(sim.pos == 11)
    assert len(at_meet) == 2 and sim.meetup_couriers == sorted(at_meet.tolist())


def test_meetup_jump_variant_places_the_couriers_at_once():
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(12, hop_s=60)
    orders = Orders(np.array([5000.0]), np.array([0]), np.array([1]), np.array([5000.0]), np.array([1e9]))
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    fleet = Fleet(np.array([0, 2, 4, 6]), np.array([0, 2, 4, 6]), np.ones(4, bool))
    params = Params(horizon_s=7200, drain_s=600, meetup_s=600.0, meetup_share=0.5, meetup_cell=11, meetup_jump=True)
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), StayBehavior(4), params, 3).run()
    assert sorted(np.flatnonzero(sim.pos == 11).tolist()) == sim.meetup_couriers and sim.km_idle.sum() == 0


def test_fewer_snapshots_leave_the_simulation_unchanged():
    """The runner's light mode (training) takes one snapshot instead of one per minute; snapshots only read state."""
    from sim.core.behavior import Behavior, BehaviorParams
    city = toy_line(30, hop_s=60)
    rng = np.random.default_rng(3)
    placed = np.sort(rng.uniform(0, 3600, 40))
    orders = Orders(placed, rng.integers(0, 30, 40), rng.integers(0, 30, 40), placed + 300.0, placed + 2400.0)
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    out = []
    for snap in (60.0, 3600.0):
        start = np.array([0, 10, 20, 29])
        fleet = Fleet(start, np.zeros(4, int), np.ones(4, bool))     # every home at cell 0: couriers ride back
        beh = Behavior(city, BehaviorParams(p_return=1.0), np.ones(city.n), 1.0, 0, 4)
        out.append(Simulator(city, demand, orders, fleet, NearestIdle(), beh,
                             Params(horizon_s=3600, drain_s=7200, snapshot_s=snap), 0).run())
    a, b = out
    assert len(a.snapshots) == 60 and len(b.snapshots) == 1
    assert a.km_idle.sum() > 0                                       # the behavior moved idle couriers
    for f in ("o_door", "o_assigned", "o_courier", "km_idle", "km_dead", "km_loaded", "trips"):
        np.testing.assert_array_equal(getattr(a, f), getattr(b, f))


def test_meetup_jump_is_drawn_as_a_zero_length_leg_to_the_point():
    from sim.video import positions
    city = toy_line(12, hop_s=60)
    orders = Orders(np.array([5000.0]), np.array([0]), np.array([1]), np.array([5000.0]), np.array([1e9]))
    demand = Demand(city, [Component(np.zeros(600), np.ones(city.n))])
    fleet = Fleet(np.array([0, 2, 4, 6]), np.array([0, 2, 4, 6]), np.ones(4, bool))
    params = Params(horizon_s=7200, drain_s=600, meetup_s=600.0, meetup_share=0.5, meetup_cell=11, meetup_jump=True)
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), StayBehavior(4), params, 3, trace=True).run()
    lng, _, _ = positions(city, sim.legs, sim.fleet.start, np.array([599.0, 601.0]))
    chosen = sim.meetup_couriers
    assert np.allclose(lng[1, chosen], city.lng[11]) and np.allclose(lng[0, chosen], city.lng[sim.fleet.start[chosen]])


def test_meetup_happens_before_the_dispatch_and_snapshot_of_its_instant():
    # an order waiting at cell 11 is dispatched at 600 s, the meet-up instant: the couriers placed at cell 11 must
    # already be there (no km to the restaurant), and the 600 s snapshot must count them at the point
    city = toy_line(12, hop_s=60)
    orders = Orders(np.array([599.0]), np.array([11]), np.array([10]), np.array([599.0]), np.array([1e9]))
    demand = Demand(city, [Component(np.full(600, 0.01), np.ones(city.n))])            # expected pickups for W1
    fleet = Fleet(np.array([0, 2, 4, 6]), np.array([0, 2, 4, 6]), np.ones(4, bool))
    params = Params(horizon_s=7200, drain_s=600, meetup_s=600.0, meetup_share=0.5, meetup_cell=11, meetup_jump=True)
    sim = Simulator(city, demand, orders, fleet, NearestIdle(), StayBehavior(4), params, 3).run()
    assert sim.o_assigned[0] == 600.0 and int(sim.o_courier[0]) in sim.meetup_couriers and sim.km_dead.sum() == 0
    snap = next(s for s in sim.snapshots if s["t"] == 600.0)
    before = next(s for s in sim.snapshots if s["t"] == 540.0)
    assert np.isfinite(before["w1_min"]) and snap["w1_min"] != before["w1_min"]
