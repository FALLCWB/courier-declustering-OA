"""Render the S2 calibration report (report.md) from report.json written by sim/calibrate.py.

Usage: python scripts/calibration_report.py <calibration_out_dir> [previous_out_dir]

With a previous run, the report opens with the before and after numbers that the G1 fixes asked for.
"""
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
r = json.loads((out / "report.json").read_text())
prev = json.loads((Path(sys.argv[2]) / "report.json").read_text()) if len(sys.argv) > 2 else None
cal, mt, gt = r["calibration"], r["meituan"], r["grubhub"]
fa, bd, ut = r["fleet_anchor"], r["bands"], r["utilization"]
L = []
say = L.append


def f(x, d=2):
    return f"{x:,.{d}f}"


say(f"# Calibration report (S2), {out.name}")
say("")
say("This research was supported by data provided by Meituan. Meituan rows never leave `data/`; this report and "
    "`sim/params/calibration.json` hold fitted parameters and aggregates only.")
say("")
sw = mt["single_order_waves"]


def headline(x):
    u = x["utilization"]["normal"]
    return (x["ks"]["c2d_vs_meituan_single_order_waves"]["D"], u["p90_c2d_min"], u["late_rate"],
            x["quantiles"]["order_to_pickup_min"]["sim"])


if prev is not None:
    b, a = headline(prev), headline(r)
    say(f"## Before and after the G1 fixes (normal supply, 10 episodes; before = `{Path(sys.argv[2]).name}`)")
    say("")
    say("| Quantity | Before | After | Meituan orders delivered alone |")
    say("|---|---|---|---|")
    say(f"| KS D, order to door | {f(b[0], 3)} | {f(a[0], 3)} | |")
    say(f"| p90 order to door (min) | {f(b[1], 1)} | {f(a[1], 1)} | {f(r['quantiles']['c2d_min']['meituan_single_order_waves'][4], 1)} |")
    say(f"| Late rate | {f(100 * b[2], 1)}% | {f(100 * a[2], 1)}% | {f(100 * sw['late_share'], 1)}% |")
    say(f"| Order to pickup p10, median, p90 (min) | {', '.join(f(x, 1) for x in (b[3][0], b[3][2], b[3][4]))} | "
        f"{', '.join(f(x, 1) for x in (a[3][0], a[3][2], a[3][4]))} | "
        f"{', '.join(f(sw['order_to_fetch_q10_25_50_75_90'][i], 1) for i in (0, 2, 4))} |")
    say("")
say("## Parameters and their sources")
say("")
say("| Parameter | Value | Source and method |")
say("|---|---|---|")
ride = mt["ride"]
say(f"| Ride time, pickup to door | {f(ride['intercept_min'])} min + {f(ride['per_km_min'])} min per straight km "
    f"(95% CI intercept {f(ride['ci95'][0][0])} to {f(ride['ci95'][1][0])}, slope {f(ride['ci95'][0][1])} to "
    f"{f(ride['ci95'][1][1])}) | Meituan single-order waves placed 17:00 to 20:59, {ride['orders']:,} orders from "
    f"{ride['couriers']:,} couriers; OLS; courier bootstrap (300 resamples). Median straight speed incl. fixed part "
    f"{f(ride['median_straight_kmh'], 1)} km/h |")
say(f"| Speed factor on free-flow road times | {f(cal['speed_factor'], 3)} | Ratio of sums: Meituan slope times straight km "
    f"over simulated free-flow road minutes, 200,000 simulated restaurant-customer pairs in different cells |")
say(f"| Door overhead (park, walk, hand over) | {f(cal['door_overhead_s'] / 60)} min | Meituan ride intercept |")
say(f"| Travel-time noise | lognormal factors with mean 1, sigma {f(cal['ride_sigma'], 3)}: one on each order's pickup-to-door "
    f"time (ride plus door overhead), one on the courier's approach to the restaurant | Meituan single-order rides around "
    f"the fitted line: log-residual SD {f(ride['log_residual_sd'], 3)}, robust (1.4826 x MAD) {f(ride['log_residual_sigma_robust'], 3)}, "
    f"the robust value is used and never tuned to the order-to-door test. Both factors come from the order stream, so every "
    f"model sees the same ones for a seed; policies plan on expected times |")
ph = mt["pickup_handling"]
say(f"| Pickup service | {f(cal['pickup_service_s'] / 60)} min, overlapping the wait for food (leave at max(arrival + "
    f"service, ready)) | Meituan: fetch minus accept time when the courier was within 100 m of the restaurant and the "
    f"food was estimated ready ({ph['orders']:,} orders; p25 {f(ph['quantiles_10_25_50_75_90'][1])}, p75 "
    f"{f(ph['quantiles_10_25_50_75_90'][3])} min). Grubhub MDRP uses 4 min |")
say(f"| Drop-off service after the door | {f(cal['dropoff_service_s'] / 60)} min | Hand-over is in the door overhead |")
say(f"| Intra-cell trip | {f(r['intra_cell_trip']['t_s'], 1)} s, {f(r['intra_cell_trip']['d_m'], 0)} m | Hexagon mean "
    f"distance times median neighbor detour at median neighbor speed (free flow, before the speed factor) |")
say(f"| Gravity scale of restaurant choice | {f(cal['gravity_s'], 0)} s of free-flow road time | Minimum two-sample KS distance "
    f"to Meituan restaurant-to-customer straight distance (`gravity_search.csv`) |")
prep = cal["prep"]
say(f"| Preparation time | {prep['dist']} with parameters {', '.join(f(x, 3) for x in prep['params'])} (minutes) | "
    f"Lowest one-sample KS among lognormal, gamma and Weibull on Meituan estimates of 1 to 60 min; "
    f"{100 * mt['prep_excluded_share']:.1f}% of peak estimates excluded (under 1 min or over 60 min); orders with an "
    f"estimate under 1 min are fetched {f(mt['prep_under_1min_order_to_fetch_median_min'], 1)} min after the order "
    f"(median), like the others ({f(mt['prep_valid_order_to_fetch_median_min'], 1)} min), so those estimates are "
    f"placeholders, not ready food |")
say(f"| Promised time | max({f(cal['promise']['floor_s'] / 60)}, {f(cal['promise']['intercept_s'] / 60)} + "
    f"{f(cal['promise']['per_km_s'] / 60)} x km) min | Meituan estimated arrival minus order time, OLS on straight km; "
    f"floor = 1st percentile. Meituan late share {100 * mt['promise']['late_share']:.1f}% |")
say(f"| Arrival shape | 16 shares of 15 min, peak bin {f(100 * max(cal['arrival_shape_15min']), 1)}% | Meituan orders per "
    f"15 min, 17:00 to 20:59, mean of {mt['days']} days |")
say(f"| Orders in the 4 hours | {f(cal['orders_4h'], 0)} | The load that the normal one-order fleet carries at "
    f"Meituan's busiest-hour utilization, not Curitiba's demand: volume at which the normal fleet reaches the normal "
    f"utilization (`fleet_search.csv`) |")
say(f"| Fleets: tight, normal, loose | {cal['fleet']['tight']:,}, {cal['fleet']['normal']:,}, {cal['fleet']['loose']:,} "
    f"couriers | Normal from IBGE PNAD 2022 ({fa['pnad_delivery_workers_brazil']:,} delivery-app workers in Brazil, "
    f"Census population {fa['brazil_pop_2022']:,}) scaled to Curitiba ({f(fa['curitiba_pop_in_grid'], 0)} residents): "
    f"{f(fa['curitiba_delivery_workers'], 0)} workers, times Meituan shares working a given day "
    f"({f(fa['share_working_a_given_day'], 3)}) and active in the busiest hour ({f(fa['share_active_busiest_hour'], 3)}): "
    f"all delivery apps under one dispatcher; tight and loose by bisection to their band centres |")
say(f"| Restaurant layout | {cal['layout']} | CNPJ registry density, seed 0 (S1) |")
say("")
say("## Supply bands (busiest-hour utilization, 18:00 to 19:00)")
say("")
say("| Level | Centre | Band | Source |")
say("|---|---|---|---|")
c = bd["centres"]
say(f"| Tight | {f(c['tight'], 3)} | {f(bd['bands']['tight'][0], 3)} to {f(bd['bands']['tight'][1], 3)} | Near saturation, "
    f"by design. Context only: Grubhub median peak orders per courier-hour {f(gt['och_peak_median'])} (range "
    f"{f(gt['och_peak_range'][0])} to {f(gt['och_peak_range'][1])}) times simulated busy hours per order "
    f"{f(bd['busy_hours_per_order_at_normal'], 3)} = {f(bd['grubhub_och_peak_times_busy_hours_context_only'], 3)}; Grubhub "
    f"instances allow bundles, the same reason Meituan's orders per courier-hour are set aside |")
say(f"| Normal | {f(c['normal'], 3)} | {f(bd['bands']['normal'][0], 3)} to {f(bd['bands']['normal'][1], 3)} | Meituan "
    f"share of courier time in a wave, busiest hour ({mt['busiest_hour']}:00) |")
say(f"| Loose | {f(c['loose'], 3)} | {f(bd['bands']['loose'][0], 3)} to {f(bd['bands']['loose'][1], 3)} | Meituan "
    f"share of courier time in a wave, lowest peak hour |")
say("")
say("Meituan peak hours (means over days):")
say("")
say("| Hour | Couriers active | Orders | Orders per courier-hour | Wave-time share |")
say("|---|---|---|---|---|")
for h in mt["hourly"]:
    say(f"| {int(h['hour'])}:00 | {f(h['couriers'], 0)} | {f(h['orders'], 0)} | {f(h['och'])} | {f(h['wave_share'], 3)} |")
say("")
say("## Utilization check (10 validation episodes per level, seeds 201 to 210)")
say("")
say("| Level | Couriers | Utilization, mean (95% CI) | Band | Inside | p90 order to door (min) | Late rate | "
    "Pending orders at peak | Seconds per episode |")
say("|---|---|---|---|---|---|---|---|---|")
for lvl in ["tight", "normal", "loose"]:
    u = ut[lvl]
    say(f"| {lvl} | {u['couriers']:,} | {f(u['mean'], 3)} ({f(u['ci95'][0], 3)} to {f(u['ci95'][1], 3)}) | "
        f"{f(u['band'][0], 3)} to {f(u['band'][1], 3)} | {'yes' if u['inside'] else 'no'} | {f(u['p90_c2d_min'], 1)} | "
        f"{f(100 * u['late_rate'], 1)}% | {f(u['pending_peak_mean'], 1)} | {f(u['episode_seconds'], 1)} |")
say("")
say(f"Speed: Meituan's marginal straight-line speed beyond the fixed part is {f(ride['marginal_straight_kmh'], 1)} km/h "
    f"(e-bikes), and the simulator follows it; the 10 Grubhub MDRP base instances use {f(gt['meters_per_minute_range'][0], 0)} "
    f"to {f(gt['meters_per_minute_range'][1], 0)} m/min, {f(gt['speed_kmh_range'][0], 1)} to {f(gt['speed_kmh_range'][1], 1)} "
    f"km/h (`instance_parameters.txt`); the x0.75 time check below gives "
    f"{f(ride['marginal_straight_kmh'] / 0.75, 1)} km/h, the motorcycle end. Curitiba couriers mostly ride motorcycles; "
    f"S8 runs the faster-riding robustness family (D1).")
say("")
say("Speed sensitivity at the normal fleet (3 episodes each):")
say("")
say("| Speed factor x | Utilization | p90 order to door (min) |")
say("|---|---|---|")
say(f"| 1.00 | {f(ut['normal']['mean'], 3)} | {f(ut['normal']['p90_c2d_min'], 1)} |")
for m, v in r["speed_sensitivity"].items():
    say(f"| {float(m):.2f} | {f(v['util_peak'], 3)} | {f(v['p90_c2d_min'], 1)} |")
say("")
say("## Two-sample KS tests (simulated orders of the 10 normal-level episodes against the data)")
say("")
say("With samples this large, any small difference gives p near 0; D is the size of the largest gap between the two "
    "cumulative distributions.")
say("")
say("| Quantity | Against | D | p | n simulated | n observed |")
say("|---|---|---|---|---|---|")
names = {"c2d_vs_meituan": ("Order to door", "Meituan 17:00 to 20:59, all orders"),
         "c2d_vs_meituan_single_order_waves": ("Order to door", "Meituan 17:00 to 20:59, orders delivered alone "
                                               f"({100 * mt['share_peak_orders_in_single_order_waves']:.1f}% of orders)"),
         "distance_vs_meituan": ("Restaurant to customer, straight", "Meituan 17:00 to 20:59"),
         "distance_vs_grubhub": ("Restaurant to customer, straight", "Grubhub MDRP, 10 base instances"),
         "prep_vs_meituan_valid": ("Preparation", "Meituan estimates 1 to 60 min"),
         "prep_vs_meituan_all": ("Preparation", "Meituan estimates, all"),
         "prep_vs_grubhub": ("Preparation", "Grubhub MDRP"),
         "order_to_pickup_vs_meituan": ("Order to pickup", "Meituan 17:00 to 20:59, all orders"),
         "order_to_pickup_vs_meituan_single_order_waves": ("Order to pickup", "Meituan 17:00 to 20:59, orders delivered alone")}
for k, (q, a) in names.items():
    t = r["ks"][k]
    say(f"| {q} | {a} | {f(t['D'], 3)} | {t['p']:.2g} | {t['n_sim']:,} | {t['n_obs']:,} |")
say("")
say("Meituan order to door by the number of orders in the courier's wave (p10, p25, p50, p75, p90, min): "
    + "; ".join(f"{'4 or more' if k == '4' else k}: {', '.join(f(x, 1) for x in v)}"
                for k, v in mt["c2d_by_wave_size_q10_25_50_75_90"].items())
    + ". The simulator delivers one order at a time, so its comparable target is the single-order waves.")
say("")
say("Quantiles " + ", ".join(f"p{int(100 * x)}" for x in r["quantile_levels"]) + ":")
say("")
say("| Quantity | Series | Values |")
say("|---|---|---|")
for qn, series in r["quantiles"].items():
    for s, v in series.items():
        say(f"| {qn} | {s} | {', '.join(f(x, 1) for x in v)} |")
say("")
def q3(v):
    return ", ".join(f(v[i], 1) for i in (0, 2, 4))


say("## Comparable targets and stated limits")
say("")
say(f"Meituan orders delivered alone ({sw['orders']:,} peak orders): late share {f(100 * sw['late_share'], 1)}% "
    f"(simulation, normal supply: {f(100 * ut['normal']['late_rate'], 1)}%); order to fetch p10, median, p90 "
    f"{q3(sw['order_to_fetch_q10_25_50_75_90'])} min (simulation order to pickup: "
    f"{q3(r['quantiles']['order_to_pickup_min']['sim'])} min).")
say("")
say("Limits of the comparison:")
say("")
say(f"1. Meituan couriers accept an order delivered alone a median {f(sw['accept_after_order_q10_25_50_75_90'][2], 1)} min "
    f"after it is placed (p90 {f(sw['accept_after_order_q10_25_50_75_90'][4], 1)} min); the simulator assigns at the "
    f"next 30 s dispatch when a courier is free.")
say(f"2. {f(100 * sw['fetched_before_estimated_ready_share'], 0)}% of orders delivered alone are fetched before the "
    f"estimated ready time (fetch minus estimate: median {f(sw['fetch_minus_estimated_ready_q10_25_50_75_90'][2], 1)}, "
    f"p10 {f(sw['fetch_minus_estimated_ready_q10_25_50_75_90'][0], 1)} min), so the preparation time is the "
    f"platform's estimate, an imperfect proxy for when the food is ready.")
say("3. Meituan's utilization counts couriers with a wave in the hour; the simulator's counts every online courier.")
say("")
say("Figure: `calibration.png` (its order-to-door panel compares with Meituan orders delivered alone). Episodes: "
    "`validation_episodes.csv`. Search traces: `gravity_search.csv`, `fleet_search.csv`.")
(out / "report.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
