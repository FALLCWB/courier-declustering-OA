# Data for the courier declustering study

Step 2 of the plan, 2026-11-01. Raw files sit in `raw/`, files computed from them in `derived/`. Neither folder is ever published or sent anywhere: the papers release the simulator and the Curitiba scenarios only.

## Meituan (INFORMS TSL Data-Driven Research Challenge 2024)

- Source: https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge, downloaded 2026-11-01 (8 files, about 62 MB).
- License (`raw/meituan/License.txt`): CC BY-NC 4.0, non-commercial use only (academic research, teaching, scientific publishing). No distribution to third parties without Meituan's permission. Every publication carries this sentence in the acknowledgments: "This research was supported by data provided by Meituan."
- Data description: `TSL-Meituan challenge_background and data_20240321.pdf`, clarifications in `tsl_meituan_2024_data_report_20241015.pdf`, data paper by Wang et al. (2025) in the same folder.

| File | Rows | What it holds |
|---|---|---|
| `all_waybill_info_meituan_0322.csv.zip` | 654,343 waybills (568,546 orders) | Restaurant and customer coordinates, order, push, dispatch, grab, pickup and arrival times, estimated meal-ready time, promised time, and the courier position when the courier accepted the order (`grab_lat`, `grab_lng`) |
| `courier_wave_info_meituan.csv` | 206,748 waves | One wave per courier run: starts idle, accepts orders, delivers all of them, returns to idle |
| `dispatch_rider_meituan.csv` | 62,044 rows | Candidate couriers at 24 dispatch checkpoints: position and orders in hand |
| `dispatch_waybill_meituan.csv` | 15,921 rows | Orders waiting at those checkpoints |

Coordinates are shifted for privacy but not scaled, so distances hold (data report, section 2.1). A rejected waybill has zero grab time and position (section 2.4).

### Does it hold courier positions? Yes.

The position of every courier is known each time the courier accepts an order (568,546 positions, 4,955 couriers, 8 days in October 2022, 23 business areas, 4,962 restaurants). Combined with the waves, this gives the idle move: from the last drop-off of one wave to the position where the courier accepts the first order of the next wave. `scripts/profile_meituan.py` finds 177,825 such idle gaps from 4,776 couriers.

| Measure (from `derived/profile.txt`) | p10 | median | p90 |
|---|---|---|---|
| Idle gap between waves (min) | 1.8 | 10.9 | 114.0 |
| Distance moved while idle (m) | 72 | 1,070 | 2,959 |
| Restaurant to customer, straight line (m) | 466 | 1,469 | 2,796 |
| Order to door (min) | 16.0 | 28.5 | 49.0 |
| Order to estimated meal ready (min) | 0.2 | 12.2 | 18.2 |

Only 20% of idle gaps end within 300 m of the last drop-off and 53% end more than 1 km away, so couriers do move while idle. Whether they move back toward an area they prefer, toward restaurant clusters, or nowhere in particular is measured in step 6. Consequence for the plan: the return-to-area probability can be estimated from data instead of only swept (risk 1 in the plan is cleared).

Caveats: one Chinese city in October 2022, and the grab position is seen only when an order is accepted, so the path in between is unknown. Speed from pickup to arrival (median 6.3 km/h straight line) is low because couriers carry several orders at once; calibration in step 5 uses single-order waves for speed.

## Grubhub Meal Delivery Routing Problem instances

- Source: https://github.com/grubhub/mdrplib, downloaded 2026-11-01 (14.5 MB zip). Instances by Grubhub and Georgia Tech, described in `raw/grubhub/mdrplib-master/MDRPInstances.pdf`.
- License: the repository states none. Use for research with citation; the files are not redistributed.
- 240 instances from 10 historical days and cities. Coordinates in metres on a plane, perturbed within a grid cell; travel at 320 or 314 m/min (about 19 km/h) on straight lines; target click-to-door 40 min, maximum 90 min.

The ten base instances (`derived/grubhub_profile.txt`): 505 to 3,213 orders, 94 to 457 couriers, median preparation 15 to 17 min, city span 11 to 55 km. They serve as a second calibration target for order rates, preparation time and courier-to-order ratios; they hold no courier movement.

## Still to fetch (step 3)

- OpenStreetMap road network and restaurants for Curitiba (ODbL).
- IBGE 2022 census population for Curitiba at the finest public grid or census tract level.
