"""Extension plan, design decision 4: the meet-up scenario's cell and settings, written to scenarios/manifest.json.

Rule of 2026-11-04 (G6 verdict ruling 4, approved by Filipe): among H3 resolution-9 cells at least 3 km (straight line)
from the three cluster hubs and with resident population above zero, the cell with the fewest expected pickups within
2 km (straight line) over 19:00 to 20:00. At 19:00 (7,200 s into the episode) 20% of the idle couriers on the
scattered start at normal supply are at that cell (jump variant, primary; riding there is the sensitivity scenario
`meetup_ride`). The share becomes 40% if the training-seed check (scripts/meetup_share_check.py) says so.
The retired rule (most populated cell at least 3 km from the hubs) and its cell stay in the manifest under "retired".
Usage: python scripts/add_meetup.py <project_root>
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
cal = load_calibration()
city = load(ROOT / "sim/city/curitiba", layout=man["layout"])
demand = make_demand(city, cal, orders_4h=man["orders_4h"])
hubs = [int(city.cell_index[c]) for c in man["cluster"]["hub_cells"]]
cell, near = meetup_point(city, demand, hubs, T0, T1)
old = man.get("meetup", {})
retired = old.get("retired") or {k: old[k] for k in ("cell", "cell_population", "km_from_hubs", "rule") if k in old}
retired["retired_on"] = "2026-11-04"
exp = demand.expected_pickups(T0, T1)
man["meetup"] = {"time_s": T0, "share": old.get("share", 0.2) if old.get("share_checked") else 0.2,
                 "share_checked": bool(old.get("share_checked", False)), "level": "normal", "start": "scattered",
                 "jump": True, "cell": str(city.cell[cell]), "cell_population": float(city.pop[cell]),
                 "expected_pickups_within_2km_19_20": round(near, 3),
                 "km_from_hubs": [round(float(city.straight_m(h, cell)) / 1000, 2) for h in hubs],
                 "km_from_centre": round(float(city.straight_m(city.centre, cell)) / 1000, 2),
                 "rule": "among cells at least 3 km from the three cluster hubs with resident population above zero, the "
                         "cell with the fewest expected pickups within 2 km (straight line) over 19:00 to 20:00; jump "
                         "variant primary, riding there is the sensitivity scenario meetup_ride",
                 "retired": retired}
# context for the reader: the same 2 km sum over every populated cell (median), and at the retired cell
sums = [exp[city.straight_m(int(c), np.arange(city.n)) <= 2000.0].sum() for c in np.flatnonzero(city.pop > 0)]
man["meetup"]["median_populated_cell_expected_pickups_within_2km_19_20"] = round(float(np.median(sums)), 3)
r = int(city.cell_index[retired["cell"]])
retired["expected_pickups_within_2km_19_20"] = round(float(exp[city.straight_m(r, np.arange(city.n)) <= 2000.0].sum()), 3)
path.write_text(json.dumps(man, indent=1, default=float))
print(json.dumps(man["meetup"], indent=1))
