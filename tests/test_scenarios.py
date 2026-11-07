"""Starting scenarios with known answers on a toy line city (cells 300 m apart, one zone per cell)."""
import numpy as np

from sim.core.city import toy_line
from sim.core.demand import Component, Demand
from sim import scenarios as sc


def setup(n=60):
    city = toy_line(n, hop_s=60, hop_m=300.0)
    pop = np.ones(n)
    pop[10] = 50.0                                    # busiest pickup area around cell 10, then 40, then 25
    pop[40], pop[25] = 30.0, 20.0
    demand = Demand(city, [Component(np.full(240, 10.0), pop)], gravity_s=60.0)
    return city, demand


def test_three_busiest_zones_are_far_enough_apart():
    city, demand = setup()
    hubs = sc.busiest_zones(city, demand, 3, 4000.0)
    reps = [int(city.zone_rep[z]) for z in hubs]
    assert reps[0] == 10 and all(city.straight_m(a, b) >= 4000.0 for i, a in enumerate(reps) for b in reps[i + 1:])


def test_cluster_starts_stay_within_1_5_km_and_split_by_thirds():
    city, demand = setup()
    hubs = [int(city.zone_rep[z]) for z in sc.busiest_zones(city, demand, 3, 4000.0)]
    big = sc.starts(city, demand, "big_cluster", 300, 7, hubs)
    assert (city.straight_m(hubs[0], big) <= 1500.0).all()
    three = sc.starts(city, demand, "three_clusters", 300, 7, hubs)
    for h, part in zip(hubs, np.array_split(three, 3)):
        assert len(part) == 100 and (city.straight_m(h, part) <= 1500.0).all()
    mixed = sc.starts(city, demand, "mixed", 300, 7, hubs)
    assert (city.straight_m(hubs[0], mixed[:150]) <= 1500.0).all()
    assert np.array_equal(mixed[150:], sc.starts(city, demand, "scattered", 300, 7, hubs)[150:])


def test_burst_starts_like_scattered_and_adds_its_orders_in_one_zone_at_18h():
    city, demand = setup()
    hubs = [10, 40, 25]
    assert np.array_equal(sc.starts(city, demand, "burst", 200, 3, hubs), sc.starts(city, demand, "scattered", 200, 3, hubs))
    comp = sc.burst_component(city, demand, zone=55)
    on = np.flatnonzero(comp.rate_per_min > 0)
    assert on[0] == 60 and on[-1] == 89 and (np.flatnonzero(comp.cust_weight) == [55]).all()
    expected = demand.expected_pickups(3600, 5400).sum()
    assert abs(comp.rate_per_min.sum() - 0.10 * expected) < 1e-9


def test_meetup_point_is_the_far_populated_cell_with_the_fewest_pickups_within_2_km():
    # hub at cell 5; cells 0 to 11 have no restaurants (fewest pickups, but within 3 km of the hub); cells 52 to 59
    # have no residents and no restaurants (excluded); among the rest the window of +-2 km (6 cells) reaching into the
    # empty end is the emptiest, so cell 51 wins
    n = 60
    pop, rest = np.ones(n), np.ones(n)
    rest[:12] = 0.0
    pop[52:], rest[52:] = 0.0, 0.0
    city = toy_line(n, hop_s=60, hop_m=300.0, pop=pop, rest=rest)
    demand = Demand(city, [Component(np.full(240, 10.0), pop)], gravity_s=60.0)
    cell, near = sc.meetup_point(city, demand, [5], 7200.0, 10800.0)
    assert cell == 51
    exp = demand.expected_pickups(7200.0, 10800.0)
    assert near == exp[45:52].sum()
    assert exp[52:].sum() == 0 and exp[:12].sum() == 0                    # the excluded cells were emptier still


def test_meetup_point_ties_go_to_the_cell_closest_to_the_city_centre():
    # no restaurants at either end of the line: cells 0 to 3 and 56 to 59 all have zero pickups within 2 km; the hub
    # sits at the centre (cell 30), so both ends are eligible; cell 56 is the tied cell closest to the centre
    n = 60
    rest = np.ones(n)
    rest[:10], rest[50:] = 0.0, 0.0
    city = toy_line(n, hop_s=60, hop_m=300.0, rest=rest)
    demand = Demand(city, [Component(np.full(240, 10.0), np.ones(n))], gravity_s=60.0)
    cell, near = sc.meetup_point(city, demand, [30], 7200.0, 10800.0)
    assert near == 0.0 and cell == 56


def test_meetup_point_median_target_takes_the_cell_closest_to_the_median():
    # G7 verdict E2(c): customers rise along the line, so pickups within 2 km rise from cell to cell; the hub at cell 0
    # and no residents from cell 47 on leave cells 10 to 46 eligible (37 cells), and the median of their 2 km sums is
    # the sum at the middle cell, 28; the primary rule (fewest pickups) keeps cell 10
    n = 60
    pop = np.ones(n)
    pop[47:] = 0.0
    city = toy_line(n, hop_s=60, hop_m=300.0, pop=pop)
    demand = Demand(city, [Component(np.full(240, 10.0), np.arange(1.0, n + 1))], gravity_s=60.0)
    exp = demand.expected_pickups(7200.0, 10800.0)
    cell, near = sc.meetup_point(city, demand, [0], 7200.0, 10800.0, target="median")
    assert cell == 28 and near == exp[city.straight_m(28, np.arange(n)) <= 2000.0].sum()
    assert sc.meetup_point(city, demand, [0], 7200.0, 10800.0)[0] == 10
