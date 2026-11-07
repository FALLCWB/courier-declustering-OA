"""Summarize the ten Grubhub MDRP base instances (o100, s1, t100, p100)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
rows = []
for d in sorted(ROOT.glob("*o100t100s1p100")):
    o = pd.read_csv(d / "orders.txt", sep="\t")
    c = pd.read_csv(d / "couriers.txt", sep="\t")
    r = pd.read_csv(d / "restaurants.txt", sep="\t")
    p = pd.read_csv(d / "instance_parameters.txt", sep="\t")
    rows.append(dict(instance=d.name, orders=len(o), restaurants=len(r), couriers=len(c),
                     courier_hours=round(((c.off_time - c.on_time) / 60).sum(), 1),
                     horizon_min=int(o.placement_time.max()),
                     prep_median_min=(o.ready_time - o.placement_time).median(),
                     span_km=round(max(o.x.max() - o.x.min(), o.y.max() - o.y.min()) / 1000, 1),
                     m_per_min=int(p.iloc[0, 0])))
t = pd.DataFrame(rows)
print(t.to_string(index=False))
