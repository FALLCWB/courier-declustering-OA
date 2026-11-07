"""Checks of the calibration helpers with known answers."""
import numpy as np
import pytest
from scipy import stats

from sim.config import prep_sample_s, rate_per_min


def test_rate_per_min_spreads_the_4h_volume_by_the_15min_shape():
    shape = np.r_[np.full(8, 1.0), np.full(8, 3.0)]
    r = rate_per_min(shape, 3200.0)
    assert len(r) == 240 and r.sum() == pytest.approx(3200.0)
    assert r[-1] == pytest.approx(3 * r[0])


def test_prep_sample_follows_the_fitted_distribution():
    s = prep_sample_s({"dist": "lognorm", "params": [0.4, 0.0, 12.0]})
    assert np.median(s) == pytest.approx(12.0 * 60, rel=1e-3)
    assert stats.kstest(s / 60, "lognorm", args=(0.4, 0.0, 12.0)).statistic < 0.001


def test_bisection_refuses_an_unbracketed_target_and_reports_the_root():
    import pytest
    from sim.calibrate import solve
    with pytest.raises(ValueError):
        solve(None, lambda x: x / 10.0, 0, 10, 2.0)       # f(0) = 0, f(10) = 1: 2 is out of reach
    x, fx, _ = solve(None, lambda x: x / 10.0, 0, 10, 0.5, tol=0.01)
    assert abs(fx - 0.5) <= 0.01
