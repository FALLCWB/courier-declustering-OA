"""Published models with known answers on toy cities (one zone per cell, 60 s per cell unless stated)."""
from types import SimpleNamespace

import numpy as np
import pytest

from sim.core.city import toy_line
from sim.core.engine import Params, View
from sim.core.policies import NearestIdle
from models.foodmatch import FoodMatch
from models.forecast_aware import ForecastAware, solve_lp


def view(city, t, rest, placed, ready, cells, demand=None):
    sim = SimpleNamespace(city=city, params=Params(horizon_s=3600), demand=demand)
    n = len(rest)
    return View(t, np.arange(n), np.array(rest), np.zeros(n, int), np.array(placed, float), np.array(ready, float),
                np.full(n, 1e9), np.arange(len(cells)), np.array(cells), np.zeros(len(cells)), sim)


def test_foodmatch_minimizes_extra_delivery_time_where_nearest_is_greedy():
    # order 0 (oldest) at cell 5, food ready at 1000 s; order 1 at cell 0, ready now. Couriers at cells 1 and 9.
    # Nearest, oldest first: order 0 -> courier 0 (tie at 240 s, first index), order 1 -> courier 1 (540 s late).
    # FoodMatch: XDT(0, either) = 0 because both arrive before the food; XDT(1, courier 0) = 60 s, so 0 -> 1, 1 -> 0.
    city = toy_line(10, hop_s=60)
    v = view(city, 0.0, [5, 0], [0.0, 10.0], [1000.0, 0.0], [1, 9])
    assert sorted(NearestIdle().assign(v)) == [(0, 0), (1, 1)]
    assert sorted(FoodMatch(seed=1).assign(v)) == [(0, 1), (1, 0)]


def test_foodmatch_leaves_an_order_pending_when_the_first_mile_passes_45_min():
    city = toy_line(10, hop_s=600)                       # 5 cells = 3,000 s > 2,700 s
    v = view(city, 0.0, [5], [0.0], [0.0], [0])
    assert FoodMatch().assign(v) == []
    assert FoodMatch().assign(view(city, 0.0, [4], [0.0], [0.0], [0])) == [(0, 0)]   # 2,400 s is allowed


def test_forecast_lp_sends_zone_2_drivers_to_zone_1_and_zone_3_drivers_to_zone_2():
    # Ozkan and Ward Sec 5.2 experiment 1 shape: lambda = (0, n, n), mu = (n, n, 0); zones 1 and 3 too far apart
    n = 10.0
    t = np.array([[0.0, 60.0, 600.0], [60.0, 0.0, 60.0], [600.0, 60.0, 0.0]])
    x = solve_lp(np.array([n, n, 0.0]), np.array([0.0, n, n]), t, cutoff_s=300.0)
    expect = np.zeros((3, 3))
    expect[1, 0] = expect[2, 1] = 1.0                    # x*_21 = 1 and x*_32 = 1 (paper indices)
    assert np.allclose(x, expect, atol=1e-7)


def test_forecast_hybrid_follows_the_lp_zone_and_falls_back_to_the_closest_courier():
    city = toy_line(3, hop_s=60)
    pol = ForecastAware(seed=0)
    x = np.zeros((3, 3))
    x[1, 0] = 1.0                                        # every zone-0 order goes to a zone-1 driver
    pol._bin, pol._cx = 0, np.cumsum(x, axis=0)
    v = view(city, 0.0, [0], [0.0], [0.0], [0, 1])       # courier 0 is in zone 0 (nearest), courier 1 in zone 1
    assert pol.assign(v) == [(0, 1)]
    v = view(city, 0.0, [0], [0.0], [0.0], [0, 2])       # no zone-1 courier: closest driver
    assert pol.assign(v) == [(0, 0)]


def test_backpressure_scores_match_the_paper_example():
    from models.backpressure import choose, congestion, normalized
    q = np.array([9.0, 1.0, 0.0, 6.0])                   # m = 4, K = 16: qbar = (13, 5, 4, 10) / 32
    assert np.allclose(normalized(q, 4) * 32, [13, 5, 4, 10])
    assert np.allclose(congestion(normalized(q, 4), 4), [-3.13786, -5.05964, -5.65685, -3.57771], atol=1e-5)
    assert choose(q, [0, 1], [0.5, 0.5], 4) == 0        # the longer queue serves
    assert choose(q, [0, 1], [-1.0, 1.0], 4) == 1       # payoff beats supply: 1.51899 < 1.59721
    assert choose(q, [0, 1], [-0.9, 1.0], 4) == 0       # 1.61899 > 1.59721
    q2 = np.array([1.0, 1.0, 0.0, 14.0])
    assert choose(q2, [0, 2], [0.0, 1.0], 4) == 0       # the empty zone 2 would win the literal argmax; never chosen
    assert choose(q2, [2], [1.0], 4) == -1


def test_backpressure_takes_the_courier_from_the_fuller_neighbor_zone():
    from models.backpressure import MirrorBackpressure
    city = toy_line(6, hop_s=60)                         # zones = cells; neighbors i - 1 and i + 1
    v = view(city, 0.0, [1], [0.0], [0.0], [1, 2, 2, 2, 2, 2])
    assert NearestIdle().assign(v) == [(0, 0)]           # the courier already at the restaurant
    assert MirrorBackpressure().assign(v) == [(0, 1)]    # zone 2 holds five idle couriers: the first of them
    v = view(city, 0.0, [1], [0.0], [0.0], [4, 5])       # nobody within one zone: the closest courier
    assert MirrorBackpressure().assign(v) == [(0, 0)]


def test_foodmatch_breaks_ties_by_first_mile_but_never_trades_extra_delivery_time_for_it():
    from models.foodmatch import lexicographic_assignment
    xdt = np.array([[1.0, 0.0], [0.0, 0.0]])            # diagonal: 1 s of XDT and no first mile
    fm = np.array([[0.0, 2000.0], [2000.0, 0.0]])        # anti-diagonal: no XDT and 4,000 s of first mile
    assert sorted(lexicographic_assignment(xdt, fm)) == [(0, 1), (1, 0)]
    assert lexicographic_assignment(np.zeros((1, 2)), np.array([[100.0, 50.0]])) == [(0, 1)]   # tie: the closer


def test_foodmatch_takes_the_closer_of_two_couriers_that_both_beat_the_food():
    city = toy_line(10, hop_s=60)
    v = view(city, 0.0, [5], [0.0], [1000.0], [9, 4])    # both arrive before 1,000 s; courier 1 is 60 s away
    assert FoodMatch(seed=3).assign(v) == [(0, 1)]


def test_fallback_counts_split_by_cause():
    from models.backpressure import MirrorBackpressure
    city = toy_line(3, hop_s=60)
    pol = ForecastAware(seed=0)
    pol._bin, pol._cx = 0, np.cumsum(np.zeros((3, 3)), axis=0)    # every draw gives none
    pol.assign(view(city, 0.0, [0], [0.0], [0.0], [0, 1]))
    x = np.zeros((3, 3))
    x[1, 0] = 1.0
    pol._cx = np.cumsum(x, axis=0)                                  # draw zone 1, which is empty
    pol.assign(view(city, 0.0, [0], [0.0], [0.0], [0, 2]))
    assert pol.counts == {"orders": 2, "draw_none": 1, "zone_empty": 1}
    mbp = MirrorBackpressure()
    mbp.assign(view(toy_line(6, hop_s=60), 0.0, [1], [0.0], [0.0], [4, 5]))
    mbp.assign(view(toy_line(6, hop_s=60), 0.0, [1], [0.0], [0.0], [2, 5]))
    assert mbp.counts == {"orders": 2, "no_neighbor": 1}


def test_xu_value_dynamic_programming_matches_the_hand_computed_table():
    from models.xu_value import fit_value
    # zones A = 0, B = 1; slots 0..2 then terminal; gamma 0.9 (reading note, section 6)
    one = fit_value([(0, 0, 1.0 * 10, 1, 1)], n_zones=2, n_slots=3, gamma=0.9)       # (zone, slot, R, zone', slot')
    assert one[0, 0] == pytest.approx(10.0)
    two = fit_value([(0, 0, 10.0, 1, 2)], n_zones=2, n_slots=3, gamma=0.9)          # k = 2: 10 x 0.19 / 0.2
    assert two[0, 0] == pytest.approx(9.5)


def test_xu_planning_weight_is_the_td_error_and_kuhn_munkres_takes_the_larger():
    from models.xu_value import td_weight
    V = np.zeros((2, 4))
    V[0, 0], V[0, 1] = 9.5, 8.0
    assert td_weight(10.0, 1.0, 0.9, V[1, 1], V[0, 0]) == pytest.approx(0.5)          # o1: A to B
    assert td_weight(4.0, 1.0, 0.9, V[0, 1], V[0, 0]) == pytest.approx(1.7)           # o2: A to A, preferred


def test_xu_planner_prefers_the_courier_whose_destination_value_is_higher():
    from models.xu_value import XuValue
    city = toy_line(4, hop_s=60)                         # zones = cells
    sim = SimpleNamespace(city=city, params=Params(horizon_s=3600, pickup_overlaps_wait=True), demand=None)
    V = np.zeros((4, 49))
    V[1, :] = 5.0                                        # being in zone 1 is worth more than zone 0
    # one order at cell 0 to cell 3; couriers at cells 0 and 1: the courier at 0 is closer, but taking the order
    # from cell 1 gives up more value (V = 5), so the courier at 0 is chosen; both reach within 15 min
    v = View(0.0, np.arange(1), np.array([0]), np.array([3]), np.zeros(1), np.zeros(1), np.full(1, 1e9),
             np.arange(2), np.array([0, 1]), np.zeros(2), sim)
    assert XuValue(value=V).assign(v) == [(0, 0)]
    V2 = np.zeros((4, 49))
    V2[0, :] = 5.0
    assert XuValue(value=V2).assign(v) == [(0, 1)]       # now leaving zone 0 costs more


def test_jahanshahi_delta_and_reward_match_the_paper_example():
    # Fig. 1a, p.12: delivery 4, preparation 6, idle courier 7 away: delta = 4 + max(6, 7) = 11, reward 45 - 11 = 34
    from models.jahanshahi_dqn import LIMIT_MIN, deltas
    city = toy_line(12, hop_s=60)
    sim = SimpleNamespace(city=city, params=Params(horizon_s=3600, door_overhead_s=0.0), demand=None)
    v = View(0.0, np.arange(1), np.array([7]), np.array([11]), np.zeros(1), np.full(1, 360.0), np.full(1, 1e9),
             np.arange(2), np.array([0, 3]), np.zeros(2), sim)
    d, _ = deltas(v)
    assert d[0, 0] == pytest.approx(11.0) and LIMIT_MIN - d[0, 0] == pytest.approx(34.0)
    assert d[0, 1] == pytest.approx(4.0 + 6.0)                                    # 4 away: the food is the limit


def test_jahanshahi_with_a_q_decreasing_in_delta_picks_the_nearest_courier():
    # with delta as the only input, a Q that falls with delta ranks couriers like nearest courier (ties at the food's
    # ready time go to the nearer one, since candidates are ordered by time)
    from models.jahanshahi_dqn import JahanshahiDQN
    from sim.nn import MLP
    net = MLP([1, 1])
    net.W, net.b = [np.array([[-1.0]])], [np.array([0.0])]
    city = toy_line(12, hop_s=60)
    sim = SimpleNamespace(city=city, params=Params(horizon_s=3600), demand=None)
    v = view(city, 0.0, [5, 9], [0.0, 1.0], [600.0, 0.0], [0, 4, 8, 11])
    v.sim.params = Params(horizon_s=3600)
    assert sorted(JahanshahiDQN(net=net).assign(v)) == sorted(NearestIdle().assign(v))


def test_double_dqn_learns_to_prefer_the_lower_delta():
    from models.jahanshahi_dqn import BATCH, Learner
    from sim.nn import MLP
    net = MLP([1, 16, 1], seed=0, lr=1e-2)
    learn = Learner(net, seed=0, total_updates=5000)
    rng = np.random.default_rng(0)
    for _ in range(3000):                                # one-step choices, reward 1 - delta, gamma applies to the next
        cand = rng.uniform(0, 1, 5)
        j = int(rng.integers(5))
        learn.observe(cand, cand[j], 1.0 - cand[j])
    assert learn.mem.n >= BATCH and net.forward(np.array([[0.1]]))[0, 0] > net.forward(np.array([[0.9]]))[0, 0]


def li_view(city, cells, rest, placed=None):
    from sim.core.demand import Component, Demand
    sim = SimpleNamespace(city=city, params=Params(horizon_s=3600),
                          demand=Demand(city, [Component(np.ones(600), np.ones(city.n))]))
    n = len(rest)
    placed = np.zeros(n) if placed is None else np.array(placed, float)
    return View(0.0, np.arange(n), np.array(rest), np.array(rest), placed, np.zeros(n), np.full(n, 1e9),
                np.arange(len(cells)), np.array(cells), np.zeros(len(cells)), sim)


def test_li_softmax_matches_eq_6_and_one_courier_wins_a_contested_order():
    from models.li_meanfield import LiMeanField
    from sim.nn import MLP
    z = np.array([0.0, 1.0, 2.0])
    p = np.exp(z) / np.exp(z).sum()
    assert np.allclose(p, [0.0900, 0.2447, 0.6652], atol=1e-4)                      # Eq. 6 with beta = 1
    city = toy_line(6, hop_s=60)
    pol = LiMeanField(actor=MLP([7, 4, 1], seed=0), seed=1)
    pairs = pol.assign(li_view(city, [1, 2], [1]))                                  # two couriers, one order
    assert len(pairs) == 1 and pairs[0][0] == 0


def test_li_serves_an_order_outside_every_pool_by_the_closest_courier():
    from models.li_meanfield import LiMeanField
    from sim.nn import MLP
    city = toy_line(40, hop_s=60)                                                  # 30 cells = 30 min > 10 min pool
    pairs = LiMeanField(actor=MLP([7, 4, 1], seed=0)).assign(li_view(city, [0, 5], [35]))
    assert pairs == [(0, 1)]


def test_li_learner_stores_a_transition_when_the_courier_acts_again():
    from models.li_meanfield import LiMeanField, Learner
    city = toy_line(6, hop_s=60)
    learn = Learner(seed=0)
    pol = LiMeanField(actor=learn.actor, learner=learn, beta=1.0)
    pol.assign(li_view(city, [1], [1]))
    assert learn.mem.n == 0 and 0 in learn.pending
    pol.assign(li_view(city, [2], [2]))
    assert learn.mem.n == 1 and learn.mem.nmask[0].sum() == 1


def test_li_critic_and_actor_update_on_a_full_batch():
    from models.li_meanfield import BATCH, MAX_POOL, N_ACT, N_OBS, Learner
    learn = Learner(seed=0)
    rng = np.random.default_rng(0)
    mem = learn.mem
    for _ in range(BATCH + 10):
        k = int(rng.integers(1, MAX_POOL))
        ax = np.zeros((MAX_POOL, N_OBS + N_ACT))
        ax[:k] = rng.normal(size=(k, N_OBS + N_ACT))
        am = np.zeros(MAX_POOL, bool)
        am[:k] = True
        mem.add(rng.normal(size=N_OBS + 1 + N_ACT), 1.0, ax, am, 0, rng.normal(size=(k, N_OBS + 1 + N_ACT)), None)
    learn.update()
    assert len(learn.losses) == 1 and np.isfinite(learn.losses[0])


def test_zhu_sends_two_couriers_on_a_line_to_the_centres_of_their_halves():
    from models.zhu_coverage import ZhuCoverage
    from sim.core.demand import Component, Demand
    city = toy_line(9, hop_s=60, hop_m=300.0)                         # 2.4 km line, uniform demand
    demand = Demand(city, [Component(np.ones(240), np.ones(9))], gravity_s=1.0)
    sim = SimpleNamespace(city=city, params=Params(horizon_s=14400), demand=demand,
                          state=np.zeros(2, np.int8), hop_to=np.full(2, -1), pos=np.array([0, 8]))
    v = View(0.0, np.empty(0, int), np.empty(0, int), np.empty(0, int), np.empty(0), np.empty(0), np.empty(0),
             np.arange(2), np.array([0, 8]), np.zeros(2), sim)
    cmds = dict(ZhuCoverage(radius_m=5000.0).relocate(v))
    assert cmds == {0: 2, 1: 6}                                       # cells 0-4 and 5-8: weighted medians 2 and 6


def test_zhu_courier_with_no_demand_in_its_radius_takes_its_whole_part_centroid():
    """G7 verdict E1: a radius-limited part with no demand falls back to the whole graph Voronoi part (Eq. 18 without
    Eq. 19); a part with no demand at all gets no command."""
    from models.zhu_coverage import ZhuCoverage
    from sim.core.demand import Component, Demand
    city = toy_line(9, hop_s=60, hop_m=300.0)
    w = np.zeros(9)
    w[[2, 4]] = 1.0                                                   # demand only at cells 2 and 4
    demand = Demand(city, [Component(np.ones(240), w)], gravity_s=1e-3)   # exact zeros, as in the city
    sim = SimpleNamespace(city=city, params=Params(horizon_s=14400), demand=demand,
                          state=np.zeros(3, np.int8), hop_to=np.full(3, -1), pos=np.array([0, 8, 0]))
    v = View(0.0, np.empty(0, int), np.empty(0, int), np.empty(0, int), np.empty(0), np.empty(0), np.empty(0),
             np.arange(3), np.array([0, 8, 0]), np.zeros(3), sim)
    zhu = ZhuCoverage(radius_m=500.0)                                 # courier 0 reaches cells 0-1, courier 1 cells 7-8
    assert dict(zhu.relocate(v)) == {0: 3}                            # part 0-4 (tie at 4 to the lower index): centroid 3
    # courier 2 shares cell 0 with courier 0, so the lower-index tie rule leaves it no cell
    assert zhu.events == {"steps": 1, "commands": 1, "whole_part_commands": 1, "no_demand_in_part": 1, "owns_no_cell": 1}


def test_zhu_at_zero_obedience_is_nearest_courier():
    from models.zhu_coverage import ZhuCoverage
    from sim.core.behavior import StayBehavior
    from sim.core.demand import Component, Demand
    from sim.core.engine import Fleet, Simulator
    city = toy_line(12, hop_s=60)
    demand = Demand(city, [Component(np.full(60, 0.5), np.ones(12))])
    orders = demand.sample(4)
    def go(policy, obedient):
        fleet = Fleet(np.array([0, 5, 11]), np.array([0, 5, 11]), np.ones(3, bool), obedient=np.array(obedient))
        return Simulator(city, demand, orders, fleet, policy, StayBehavior(3), Params(horizon_s=3600, drain_s=3600), 0).run()
    a, b = go(ZhuCoverage(), [False] * 3), go(NearestIdle(), [False] * 3)
    assert np.array_equal(a.o_courier, b.o_courier) and np.allclose(a.o_door, b.o_door, equal_nan=True)
    c = go(ZhuCoverage(), [True] * 3)
    assert c.km_idle.sum() > 0                                       # obedient couriers are moved


def auad_view(city, cells, t=0.0, placed=0.0):
    sim = SimpleNamespace(city=city, params=Params(horizon_s=14400, pickup_overlaps_wait=True), demand=None,
                          pos=np.zeros(len(cells), int), pending=[0], state=np.zeros(len(cells), np.int8))
    return View(t, np.arange(1), np.array([5]), np.array([6]), np.array([placed]), np.array([placed]),
                np.array([placed + 2100.0]), np.arange(len(cells)), np.array(cells), np.zeros(len(cells)), sim)


def test_auad_holds_when_the_only_courier_is_far_and_offers_when_a_near_one_appears():
    from models.auad_holding import N_FEAT, AuadHolding
    city = toy_line(40, hop_s=60, hop_m=1000.0)                      # 1 km per cell
    theta = np.zeros(N_FEAT)
    theta[3] = 5.0                                                   # a held order costs 5 (phi_3 counts open orders)
    pol = AuadHolding(theta=theta)
    assert pol.assign(auad_view(city, [35])) == []                   # c0 = 30 + 1 km > 5: hold
    assert pol.assign(auad_view(city, [35, 5], t=60.0)) == [(0, 1)]  # courier 1 at the restaurant: c0 = 1 < 5
    assert AuadHolding(theta=np.zeros(N_FEAT)).assign(auad_view(city, [35])) == []   # theta = 0 prices no held order
    # maximum hold: lambda_lost = 2 h past the deadline (Table 6); the fixture's deadline is placed + 2,100 s
    assert pol.assign(auad_view(city, [35], t=2100.0 + 7200.0 - 30.0)) == []
    assert pol.assign(auad_view(city, [35], t=2100.0 + 7200.0)) == [(0, 0)]


def test_auad_features_are_the_papers_raw_counts():
    from models.auad_holding import features
    phi = features(n_active=10, n_on=4, n_open_left=3, buckets=np.arange(9.0), n_offered=2, rc_km_sum=5.0)
    assert phi.tolist() == [1.0, 2.5, 0.75, 3.0, *np.arange(9.0).tolist(), 2.0, 2.5]   # phi_13 = 4 - 2, phi_14 = 5 / 2
    assert features(10, 4, 3, np.zeros(9), 0, 0.0)[-1] == 0.0                          # no offer: phi_14 = 0


def test_auad_acts_with_theta_best_and_the_gate_replaces_it_only_when_cheaper():
    from models.auad_holding import AuadHolding, Learner
    city = toy_line(40, hop_s=60, hop_m=1000.0)
    learn = Learner(seed=0)
    learn.theta[3] = 5.0                                             # the learned theta would offer (c0 = 1 < 5) ...
    pol = AuadHolding(learner=learn)
    assert pol.assign(auad_view(city, [5], t=60.0)) == []           # ... but the policy acts with theta_best = 0: hold
    learn.best_cost = 100.0
    assert not learn.consider(120.0)                                 # Algorithm 1 lines 13-14: a costlier theta is kept out
    assert learn.consider(80.0) and learn.best_cost == 80.0
    assert AuadHolding(learner=learn, seed=1).assign(auad_view(city, [5], t=60.0)) == [(0, 0)]
    learn.theta[0] = np.nan
    assert not learn.consider(1.0)                                   # a diverged theta never replaces theta_best


def test_auad_episode_cost_is_lateness_distance_and_lost_orders():
    from models.auad_holding import K_DIST, K_LATE, K_LOST, episode_cost
    city = SimpleNamespace(Dm=np.array([[0.0, 2000.0], [2000.0, 0.0]]))
    orders = SimpleNamespace(placed=np.array([0.0, 0.0, 0.0, 20000.0]), due=np.array([1000.0, 1000.0, 1000.0, 21000.0]),
                             rest=np.array([0, 0, 0, 0]), cust=np.array([1, 1, 1, 1]))
    sim = SimpleNamespace(city=city, orders=orders, params=Params(horizon_s=14400.0, drain_s=10800.0),
                          o_door=np.array([900.0, 1600.0, np.nan, np.nan]), o_assigned=np.array([0.0, 0.0, np.nan, np.nan]),
                          km_dead=np.array([1.5, 0.5]), km_loaded=np.array([4.0]))
    late = (600.0 + (25200.0 - 1000.0)) / 60.0                       # order 1 ten minutes late; order 2 never delivered
    assert episode_cost(sim) == pytest.approx(K_LATE * late + K_DIST * (2.0 + 4.0) + K_LOST * 1)   # order 3 is outside


def test_auad_learner_target_is_the_discounted_cost_beyond_the_immediate_one():
    from models.auad_holding import GAMMA, N_FEAT, Learner
    learn = Learner(seed=0)
    phi = np.zeros(N_FEAT)
    phi[0] = 1.0
    for c in [2.0, 3.0, 5.0]:
        learn.hist.append((phi, c))
    learn._push(0, bootstrap=False)                                  # no bootstrap: the whole remaining episode
    assert learn.buf_y[0] == pytest.approx(2.0 + GAMMA * 3.0 + GAMMA ** 2 * 5.0 - 2.0)


def test_auad_vectorized_decisions_equal_the_order_by_order_loop():
    """The policy decides all orders up to the next offer at once; the pairs must equal the plain loop over orders."""
    from models.auad_holding import LAMBDA_LOST_S, N_FEAT, AuadHolding, features
    city = toy_line(40, hop_s=60, hop_m=1000.0)
    rng = np.random.default_rng(5)
    for trial in range(30):
        n_o, n_c = int(rng.integers(1, 25)), int(rng.integers(1, 12))
        placed = rng.uniform(0, 3000, n_o)
        due = placed + rng.uniform(600, 3600, n_o)
        t = 3000.0 + (LAMBDA_LOST_S + 3600.0 if trial % 5 == 0 else 0.0)        # some trials have lost orders
        sim = SimpleNamespace(city=city, params=Params(horizon_s=14400, pickup_overlaps_wait=True), demand=None,
                              pos=np.zeros(30, int), pending=list(range(n_o)), state=np.zeros(30, np.int8))
        v = View(t, np.arange(n_o) + 100, rng.integers(0, 40, n_o), rng.integers(0, 40, n_o), placed, placed + 300.0, due,
                 np.arange(n_c) + 7, rng.integers(0, 40, n_c), np.zeros(n_c), sim)
        theta = rng.normal(0, 3, N_FEAT)
        got = AuadHolding(theta=theta, seed=trial).assign(v)
        # reference: the plain loop, same permutation
        ref = AuadHolding(theta=theta, seed=trial)
        perm = ref.rng.permutation(n_o)
        p = sim.params
        at_rest = v.t + v.delay[None, :] + city.T[np.ix_(v.cell, v.rest)].T * v.sf
        door = np.maximum(at_rest + p.pickup_service_s, v.ready[:, None]) + (city.T[v.rest, v.cust] * v.sf)[:, None]
        km = (city.Dm[np.ix_(v.cell, v.rest)].T + city.Dm[v.rest, v.cust][:, None]) / 1000.0
        rc = city.Dm[v.rest, v.cust] / 1000.0
        c0 = 1.0 * km + 4.0 * np.maximum(door - v.due[:, None], 0.0) / 60.0
        b = np.clip(((v.due - v.t) // 1200.0).astype(int), 0, 8)
        buckets = np.bincount(b, minlength=9).astype(float)
        n_open, rc_sum, n_off, free, want = n_o, 0.0, 0, np.ones(n_c, bool), []
        for o in perm:
            if not free.any():
                break
            c = int(np.argmin(np.where(free, c0[o], np.inf)))
            b_off = buckets.copy()
            b_off[b[o]] -= 1
            hold = theta @ features(n_o, 30, n_open, buckets, n_off, rc_sum)
            off = c0[o, c] + theta @ features(n_o, 30, n_open - 1, b_off, n_off + 1, rc_sum + rc[o])
            if off <= hold + 1e-9 or v.t >= v.due[o] + LAMBDA_LOST_S:
                want.append((v.orders[o], v.couriers[c]))
                free[c] = False
                n_open, rc_sum, n_off, buckets = n_open - 1, rc_sum + rc[o], n_off + 1, b_off
        assert got == want, trial


def test_auad_capped_run_stops_once_the_cost_lower_bound_passes_the_cap():
    from models.auad_holding import K_LATE, N_FEAT, AuadHolding, CostCapExceeded, cost_lower_bound
    city = toy_line(40, hop_s=60, hop_m=1000.0)
    v = auad_view(city, [35], t=2100.0 + 600.0)                      # the open order is 10 min past its deadline
    v.sim.o_door = np.array([np.nan])
    v.sim.orders = SimpleNamespace(due=np.array([2100.0]))
    v.sim.km_dead, v.sim.km_loaded = np.zeros(1), np.zeros(1)
    assert cost_lower_bound(v) == pytest.approx(K_LATE * 10.0)
    assert AuadHolding(theta=np.zeros(N_FEAT), cap=50.0).assign(v) == []          # bound 40 <= 50: the run goes on
    with pytest.raises(CostCapExceeded):
        AuadHolding(theta=np.zeros(N_FEAT), cap=30.0).assign(v)


def test_zhu_random_partition_ties_give_co_located_couriers_their_own_cells():
    """Post-freeze sensitivity (Filipe, 2026-11-04): tie="random" sends each tied cell to a random closest courier, from
    the episode's own stream; the default keeps the lower-index rule, under which a co-located courier owns no cell."""
    from models.zhu_coverage import ZhuCoverage
    from sim.core.demand import Component, Demand
    city = toy_line(9, hop_s=60, hop_m=300.0)
    demand = Demand(city, [Component(np.ones(240), np.ones(9))], gravity_s=60.0)
    sim = SimpleNamespace(city=city, params=Params(horizon_s=14400), demand=demand,
                          state=np.zeros(3, np.int8), hop_to=np.full(3, -1), pos=np.array([0, 8, 0]))
    v = View(0.0, np.empty(0, int), np.empty(0, int), np.empty(0, int), np.empty(0), np.empty(0), np.empty(0),
             np.arange(3), np.array([0, 8, 0]), np.zeros(3), sim)
    lower = ZhuCoverage(radius_m=5000.0)
    lower.relocate(v)
    assert lower.events["owns_no_cell"] == 1                          # courier 2 shares cell 0 with courier 0
    rand = ZhuCoverage(seed=3, radius_m=5000.0, tie="random")
    cmds = dict(rand.relocate(v))
    assert rand.events["owns_no_cell"] == 0 and set(cmds) == {0, 1, 2}
    again = ZhuCoverage(seed=3, radius_m=5000.0, tie="random")
    assert dict(again.relocate(v)) == cmds                            # fixed seed: the same draw
