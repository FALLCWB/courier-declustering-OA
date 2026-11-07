"""Profile the Meituan TSL 2024 data: coverage, timing, and whether idle courier moves can be measured."""
import ast
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(sys.argv[1])
OUT = Path(sys.argv[2])


def haversine_m(lat1, lng1, lat2, lng2):
    r = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lng2 - lng1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


with zipfile.ZipFile(RAW / "all_waybill_info_meituan_0322.csv.zip") as z:
    with z.open("all_waybill_info_meituan_0322.csv") as f:
        wb = pd.read_csv(f, index_col=0)
for c in ["sender_lat", "sender_lng", "recipient_lat", "recipient_lng", "grab_lat", "grab_lng"]:
    wb[c] = wb[c].where(wb[c] != 0) / 1e6
wb.to_parquet(OUT / "waybills.parquet")

lines = []
say = lines.append
say(f"waybills: {len(wb):,}; orders: {wb.order_id.nunique():,}; couriers: {wb.courier_id.nunique():,}")
say(f"days: {sorted(wb.dt.unique().tolist())}")
say(f"area ids (da_id): {wb.da_id.nunique()}; restaurants (poi_id): {wb.poi_id.nunique():,}")
say(f"grabbed waybills: {(wb.is_courier_grabbed == 1).sum():,}; with grab position: {wb.grab_lat.notna().sum():,}")
say(f"lat range {wb.sender_lat.min():.4f} to {wb.sender_lat.max():.4f}; lng range {wb.sender_lng.min():.4f} to {wb.sender_lng.max():.4f}")

ok = wb[(wb.is_courier_grabbed == 1) & (wb.arrive_time > 0) & (wb.fetch_time > 0)].copy()
ok["dist_m"] = haversine_m(ok.sender_lat, ok.sender_lng, ok.recipient_lat, ok.recipient_lng)
ok["click_to_door_min"] = (ok.arrive_time - ok.platform_order_time) / 60
ok["prep_min"] = (ok.estimate_meal_prepare_time - ok.platform_order_time) / 60
ok["grab_to_fetch_m"] = haversine_m(ok.grab_lat, ok.grab_lng, ok.sender_lat, ok.sender_lng)
ok["ride_speed_kmh"] = ok.dist_m / 1000 / ((ok.arrive_time - ok.fetch_time) / 3600)
ok["hour"] = pd.to_datetime(ok.platform_order_time, unit="s", utc=True).dt.tz_convert("Asia/Shanghai").dt.hour
for col in ["dist_m", "click_to_door_min", "prep_min", "grab_to_fetch_m", "ride_speed_kmh"]:
    q = ok[col].replace([np.inf, -np.inf], np.nan).dropna().quantile([0.1, 0.5, 0.9])
    say(f"{col}: p10 {q[0.1]:.1f}, median {q[0.5]:.1f}, p90 {q[0.9]:.1f}")
say("orders per local hour: " + ", ".join(f"{h}:{n}" for h, n in ok.groupby("hour").size().items()))

# Idle moves between waves: last drop-off of wave k -> first grab position of wave k+1.
wv = pd.read_csv(RAW / "courier_wave_info_meituan.csv")
wv["order_ids"] = wv.order_ids.map(ast.literal_eval)
last_drop = ok.sort_values("arrive_time").groupby("order_id").last()
first_grab = ok.sort_values("grab_time").groupby("order_id").first()
rows = []
for (dt, cid), g in wv.sort_values("wave_start_time").groupby(["dt", "courier_id"]):
    g = g.reset_index(drop=True)
    for k in range(len(g) - 1):
        a = [o for o in g.order_ids[k] if o in last_drop.index]
        b = [o for o in g.order_ids[k + 1] if o in first_grab.index]
        if not a or not b:
            continue
        end = last_drop.loc[a].sort_values("arrive_time").iloc[-1]
        start = first_grab.loc[b].sort_values("grab_time").iloc[0]
        rows.append(dict(dt=dt, courier_id=cid, t_end=end.arrive_time, t_next=start.grab_time,
                         lat0=end.recipient_lat, lng0=end.recipient_lng, lat1=start.grab_lat, lng1=start.grab_lng))
idle = pd.DataFrame(rows)
idle["gap_min"] = (idle.t_next - idle.t_end) / 60
idle["move_m"] = haversine_m(idle.lat0, idle.lng0, idle.lat1, idle.lng1)
idle = idle[(idle.gap_min >= 0) & idle.lat1.notna()]
idle.to_parquet(OUT / "idle_moves.parquet")
say(f"waves: {len(wv):,}; usable idle gaps between consecutive waves: {len(idle):,} from {idle.courier_id.nunique():,} couriers")
for col in ["gap_min", "move_m"]:
    q = idle[col].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
    say(f"idle {col}: " + ", ".join(f"p{int(p*100)} {v:.1f}" for p, v in q.items()))
say(f"share of idle gaps with move under 300 m: {(idle.move_m < 300).mean():.3f}; over 1 km: {(idle.move_m > 1000).mean():.3f}")
dr = pd.read_csv(RAW / "dispatch_rider_meituan.csv", index_col=0)
say(f"dispatch_rider snapshots: {len(dr):,}; couriers: {dr.courier_id.nunique():,}; checkpoints: {dr.dispatch_time.nunique():,}; days: {sorted(dr.dt.unique().tolist())}")
(OUT / "profile.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
