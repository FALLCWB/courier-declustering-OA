"""Build the simulator inputs from the fitted parameters in sim/params/calibration.json (written by sim/calibrate.py).

The JSON holds fitted parameters only, never Meituan rows, so it is safe to publish.
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats

from sim.core.demand import Component, Demand
from sim.core.engine import Params

CALIBRATION = Path(__file__).parent / "params" / "calibration.json"
PREP_GRID = 10000


def load_calibration(path=CALIBRATION):
    return json.loads(Path(path).read_text())


def prep_sample_s(prep):
    """Deterministic quantile grid of the fitted preparation-time distribution, in seconds."""
    dist = getattr(stats, prep["dist"])(*prep["params"])
    return dist.ppf((np.arange(PREP_GRID) + 0.5) / PREP_GRID) * 60.0


def rate_per_min(shape_15min, orders_4h):
    """Expected orders per minute over the 240 minutes, from the 15-minute shape (shares that sum to one)."""
    shape = np.asarray(shape_15min, float)
    return np.repeat(shape / shape.sum() * orders_4h / 15.0, 15)


def make_demand(city, cal, orders_4h=None, gravity_s=None, extra=()):
    """Base demand (population-weighted customers, Meituan shape) plus optional extra components (the burst)."""
    rate = rate_per_min(cal["arrival_shape_15min"], orders_4h if orders_4h is not None else cal["orders_4h"])
    p = cal["promise"]
    return Demand(city, [Component(rate, city.pop), *extra], gravity_s=gravity_s or cal["gravity_s"],
                  prep_s=prep_sample_s(cal["prep"]), promise_s=p["intercept_s"],
                  promise_per_km_s=p["per_km_s"], promise_floor_s=p["floor_s"], ride_sigma=cal["ride_sigma"])


def make_params(cal, **over):
    kw = dict(horizon_s=4 * 3600.0, speed_factor=cal["speed_factor"], door_overhead_s=cal["door_overhead_s"],
              pickup_service_s=cal["pickup_service_s"], dropoff_service_s=cal["dropoff_service_s"],
              pickup_overlaps_wait=cal["pickup_overlaps_wait"])
    kw.update(over)
    return Params(**kw)
