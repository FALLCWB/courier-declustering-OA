"""Sanity run: one Curitiba episode, one seed, the two baseline policies, from one big cluster.

Usage: python sanity_run.py <project_root> <out_dir>
Parameters here are provisional (calibration is step 5, behavior step 6); the run checks that the
pipeline works end to end and that the numbers are plausible, not what they are.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(ROOT))
from sim.core.behavior import Behavior, BehaviorParams  # noqa: E402
from sim.core.city import load  # noqa: E402
from sim.core.demand import Component, Demand  # noqa: E402
from sim.core.engine import Fleet, Params, Simulator  # noqa: E402
from sim.core.metrics import summarize  # noqa: E402
from sim.core.policies import BatchMatching, NearestIdle  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
SEED, N_COURIERS, PEAK_PER_H = 1, 300, 600
city = load(ROOT / "sim/city/curitiba")

# Meituan orders per local hour, 17:00 to 20:59 (data/derived/profile.txt), scaled to the peak volume.
hourly = np.array([52621, 65520, 45474, 29702], float)
rate = np.repeat(hourly / hourly.max() * PEAK_PER_H / 60.0, 60)
wb = pd.read_parquet(ROOT / "data/derived/waybills.parquet", columns=["platform_order_time", "estimate_meal_prepare_time"])
prep = (wb.estimate_meal_prepare_time - wb.platform_order_time).to_numpy(float)
prep = prep[(prep >= 0) & (prep <= 3600)]
demand = Demand(city, [Component(rate, city.pop)], gravity_s=600.0, prep_s=prep)
orders = demand.sample(SEED)

# Scenario: one big cluster. Every courier starts within 1.5 km of the busiest pickup cell and prefers that area.
share = demand.pickup_share[0]
hub = int(np.argmax(share))
near = np.flatnonzero(city.straight_m(hub, np.arange(city.n)) <= 1500)
rng = np.random.default_rng(np.random.SeedSequence([SEED, 4]))
start = rng.choice(near, N_COURIERS)
fleet = Fleet(start=start, home=start.copy(), full_time=rng.uniform(size=N_COURIERS) < 0.4)
params = Params(horizon_s=4 * 3600.0)

rows = []
for policy in [NearestIdle(), BatchMatching()]:
    beh = Behavior(city, BehaviorParams(p_return=0.5), share, params.speed_factor, SEED, N_COURIERS)
    t0 = time.time()
    sim = Simulator(city, demand, orders, fleet, policy, beh, params, seed=SEED).run()
    row = {"policy": policy.name, "seconds": round(time.time() - t0, 1), **summarize(sim)}
    rows.append(row)
    snaps = pd.DataFrame(sim.snapshots)
    snaps.to_csv(OUT / f"snapshots_{policy.name}.csv", index=False)
    print(json.dumps(row), flush=True)
    print(snaps.iloc[::30][["t", "n_idle", "n_busy", "n_pending", "w1_min", "tv", "gini_idle", "uncovered"]]
          .round(3).to_string(index=False), flush=True)
pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
(OUT / "setup.json").write_text(json.dumps({
    "seed": SEED, "couriers": N_COURIERS, "peak_orders_per_h": PEAK_PER_H, "orders": len(orders),
    "hub_cell": str(city.cell[hub]), "start_cells_within_m": 1500, "behavior": "p_return 0.5, placeholder logit",
    "speed_factor": params.speed_factor, "note": "provisional parameters; calibration is step 5"}, indent=1))
