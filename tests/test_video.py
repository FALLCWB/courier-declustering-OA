"""Video positions with known answers: straight-line interpolation along legs and the state colors."""
import numpy as np
import pytest

from sim.core.city import toy_line
from sim.video import positions


def test_courier_moves_halfway_and_parks_idle_after_its_last_leg():
    city = toy_line(5, hop_s=60)
    legs = [(0, 100.0, 200.0, 0, 2, "to_pickup"), (0, 200.0, 260.0, 2, 2, "wait"), (0, 260.0, 380.0, 2, 4, "loaded")]
    lng, lat, st = positions(city, legs, np.array([0, 3]), np.array([50.0, 150.0, 230.0, 320.0, 500.0]))
    assert lng[0, 0] == city.lng[0] and st[0, 0] == "idle"                 # before its first leg: at the start cell
    assert lng[1, 0] == pytest.approx(city.lng[1]) and st[1, 0] == "pickup"
    assert lng[2, 0] == pytest.approx(city.lng[2]) and st[2, 0] == "pickup"
    assert lng[3, 0] == pytest.approx(city.lng[3]) and st[3, 0] == "loaded"
    assert lng[4, 0] == pytest.approx(city.lng[4]) and st[4, 0] == "idle"
    assert (lng[:, 1] == city.lng[3]).all() and (st[:, 1] == "idle").all()  # a courier with no legs never moves
