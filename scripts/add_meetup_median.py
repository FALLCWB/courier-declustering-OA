"""G7 verdict E2(c): the exploratory meet-up point, written to scenarios/manifest.json under "meetup_median".

Rule, fixed before any comparison: among the meet-up's eligible cells (at least 3 km in a straight line from the three
cluster hubs, resident population above zero), the cell whose expected pickups within 2 km over 19:00 to 20:00 is
closest to the median over those cells; ties go to the cell closest to the city centre. The run uses the primary
meet-up's time (19:00), share (20%) and jump variant; it is pre-registered as exploratory, outside every family.
Usage: python scripts/add_meetup_median.py <project_root>
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.config import load_calibration, make_demand  # noqa: E402
from sim.core.city import load  # noqa: E402
from sim.scenarios import meetup_point  # noqa: E402

T0, T1 = 7200.0, 10800.0
path = ROOT / "scenarios/manifest.json"
man = json.loads(path.read_text())
city = load(ROOT / "sim/city/curitiba", layout=man["layout"])
demand = make_demand(city, load_calibration(), orders_4h=man["orders_4h"])
hubs = [int(city.cell_index[c]) for c in man["cluster"]["hub_cells"]]
cell, near = meetup_point(city, demand, hubs, T0, T1, target="median")
allc = np.arange(city.n)
ok = (city.pop > 0) & np.all([city.straight_m(h, allc) >= 3000.0 for h in hubs], axis=0)
exp = demand.expected_pickups(T0, T1)
sums = [exp[city.straight_m(int(c), allc) <= 2000.0].sum() for c in np.flatnonzero(ok)]
man["meetup_median"] = {
    "cell": str(city.cell[cell]), "cell_population": float(city.pop[cell]),
    "expected_pickups_within_2km_19_20": round(near, 3),
    "median_eligible_cells_expected_pickups_within_2km_19_20": round(float(np.median(sums)), 3),
    "eligible_cells": int(ok.sum()),
    "km_from_hubs": [round(float(city.straight_m(h, cell)) / 1000, 2) for h in hubs],
    "km_from_centre": round(float(city.straight_m(city.centre, cell)) / 1000, 2),
    "rule": "among the meet-up's eligible cells, the cell whose expected pickups within 2 km (straight line) over 19:00 "
            "to 20:00 is closest to the median over those cells; ties to the cell closest to the city centre",
    "uses": "time_s, share and jump of 'meetup'",
    "status": "exploratory, pre-registered, outside every family (G7 verdict E2(c))"}
path.write_text(json.dumps(man, indent=1, default=float))
print(json.dumps(man["meetup_median"], indent=1))
