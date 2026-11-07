# Pre-registration: Part 1, untrained dispatch models from identical clustered starts

Plan: `plans/2026-11-01-first-simulation.md`, step S6, objective E5. Written 2026-11-02 before any comparison run; changes C1 to C6 of the G3 verdict applied; frozen by the commit recorded on the last line of `reviews/G3-verdict.md` and in `DECISIONS.md`. Every later change goes to Filipe as a choice (rerun, narrower claim, limitation) and into the plan's "Changes to the plan". This research was supported by data provided by Meituan.

## 1. Question and unit

Do three published dispatch models that need no training keep idle couriers closer to where orders are expected than nearest-courier dispatch? Each run starts every model from the same clustered start, with couriers who drift back to their preferred areas. Each model is also charged its cost in delivery time.

- **Unit:** one episode, a simulated evening peak of Curitiba from 17:00 to 21:00 with its own seed. Orders placed in the 4 hours are followed until delivery, with up to 3 hours of drain.
- **Common random numbers.** For a given scenario, supply level and seed, all four models see the same:
  - orders: times, restaurants, customers, ready times, promises and travel-time factors;
  - start cells and preferred areas;
  - full-time flags;
  - per-courier behavior random streams.
- **Pairing.** Comparisons are paired by seed within a cell. A cell is start x supply level x behavior setting x model.

## 2. Inputs (fixed at the freeze commit)

- City and restaurants: `sim/city/build.py` (4,311 H3 resolution-9 cells, 670 resolution-8 zones), main layout s0 from the CNPJ registry density (S1).
- Calibration: `sim/params/calibration.json` (S2 with the G1 fixes). Timing follows Meituan. Lognormal travel-time noise has sigma 0.314.
- Volume and fleet: 12,184 orders in the 4 hours. This is the load that the normal one-order fleet carries at Meituan's busiest-hour utilization; it is not Curitiba's demand. The fleet stands for all delivery apps under one dispatcher.
- Courier behavior: defaults of `sim/core/behavior.py` (S3, `avaliacao/20261102-1146-behavior-single-final`):
  - one decision per gap between orders, 42 s after the drop-off;
  - return to the preferred area (2 km around the start cell) with probability 0.75;
  - otherwise stay, nearest hotspot or cruise within 2,000 m, by a logit with stay constant -3;
  - 40% of couriers are full-time.
- Scenarios and fleets: `scenarios/manifest.json` (S4).

## 3. Design

| Factor | Levels |
|---|---|
| Start (5) | big cluster (all couriers uniform over the cells within 1.5 km of the busiest pickup zone); three clusters (a third around each of the three busiest zones at least 4 km apart); scattered (start cells in proportion to pickups expected in the first 30 min); mixed (half big cluster, half scattered); burst (scattered start plus, from 18:00 to 18:30, 10% of the city's expected half-hour orders in one zone 6.4 km from the busiest hub with few couriers; a known event, part of the expected demand) |
| Supply level (3) | tight 1,978 couriers (busiest-hour utilization 0.925, near saturation, by design; Grubhub is context only); normal 2,495 (Meituan's busiest-hour share 0.709); loose 3,196 (Meituan's lowest peak-hour share 0.554); each inside its band of plus or minus 0.05 |
| Behavior setting (5) | fitted (return probability 0.75); sweep of the return probability at 0, 0.25, 0.5 and 1 with the other fitted values. The plan's sixth setting, sweep value 0.75, equals the fitted setting, so it is not run twice |
| Model (4) | nearest courier (baseline, `sim/core/policies.py`); FoodMatch with bundling off (Joshi et al. 2021); forecast-aware LP-based Hybrid matching (Ozkan and Ward 2020); mirror backpressure, assignment only, eq (8) (Kanoria and Qian 2024). Implementation choices: `models/fidelity/` |

All couriers stay online for the 4 hours. Each courier carries one order at a time. Every model dispatches on the same 30 s clock.

## 4. Metrics (per episode)

**Primary: W1, in minutes.** It is the earth mover's distance between two distributions over H3 resolution-8 zones:

- supply: the idle couriers plus the busy couriers who will be free within 5 min, the latter counted at their drop-off cell;
- demand: the pickups expected in the next 30 min.

The ground cost is the riding time between the zones' representative cells (free flow times the speed factor), with no cost inside a zone. W1 is measured every 60 s from 17:00 to 20:59 (240 snapshots) and averaged. Counting soon-free couriers is the few-idle rule chosen in S4, by the lower between-seed coefficient of variation (0.0311 against 0.0324 for idle-weighting; `avaliacao/20261102-1156-scenarios`).

**Co-primary: p90 order to door.** The 90th percentile of order-to-door time, in minutes, over the orders placed from 17:00 to 20:59. With this co-primary, a model that spreads couriers but delays food cannot win.

**Secondary** (descriptive, 95% intervals, no confirmatory claim):
- W1 over the first 30 min;
- total variation distance between the two shares;
- Gini of idle couriers across zones;
- share of expected demand with no idle courier within 5 min;
- late rate (door after the promised time);
- km without an order per order;
- idle km per order;
- Gini of deliveries per courier;
- mean order to door;
- share of orders unassigned for more than 30 min;
- food waiting for the courier (pickup minus ready time), mean and p90 (G1 verdict; kept secondary and descriptive at G3);
- W1 with idle couriers only, weighted by the number of idle couriers per snapshot (the other few-idle rule; G3 verdict C3);
- for forecast-aware matching and backpressure, the share of orders served by the closest-courier fallback, split by cause: the draw gave none, the drawn zone was empty, or no courier was idle in the neighborhood (G3 verdict C3).

## 5. Hypothesis families and tests

Each contrast is a model against nearest-courier in one cell, on one metric. Its estimate is the mean over seeds of the paired difference, model minus nearest. Lower is better for both primary metrics.

| Family | Contrasts | Number |
|---|---|---|
| F1, primary | 3 models x 2 metrics x 5 starts x 3 supply levels, fitted behavior | 90 |
| F2, behavior sweep | the same at return probability 0, 0.25, 0.5 and 1 | 360 |
| F3, robustness layouts | 3 models x 2 metrics x layouts s1, s2, s3, s4 and OpenStreetMap; big-cluster start, normal supply, fitted behavior; same fleets and volume | 30 |
| F4, D1 robustness | 3 models x 2 metrics x {half scale: fleet and orders x0.5; faster riding: travel times x0.75}; big-cluster start, normal supply, fitted behavior; run only if the S7 runtime estimate with it stays under 24 h | 12 |

- **Intervals:** 95% percentile bootstrap over seeds, 10,000 resamples, generator seed 20261103.
- **p-values:** two-sided paired t-test. A bootstrap p-value cannot resolve the smallest Holm thresholds of F2 (0.05/360).
- **Multiplicity:** Holm step-down at alpha 0.05 within each family, never across families.
- **"Established" contrast:** Holm-adjusted p below 0.05. An established effect smaller than the smallest effect of interest is reported as smaller than that threshold.

**Joint reading of the co-primaries (G3 verdict C1).** Each model in each F1 cell falls in exactly one class:

| Class | W1 | p90 order to door |
|---|---|---|
| declusters at no delivery cost | established lower (Holm), estimate at least the smallest effect | upper end of the 95% interval below +1.0 min |
| declusters at a delivery cost | as above | established higher (Holm), estimate at least +1.0 min |
| declusters, cost unresolved | as above | every other case |
| does not decluster | any other result; an established increase is reported as such | any |

Paper A reports the count of cells per class and model, and makes no other combined claim.

## 6. Smallest effects of interest and sample size

- **Smallest effects of interest:**
  - W1: 10% of nearest-courier's mean W1 in the same cell, from the pilot;
  - p90 order to door: 1.0 min.
- **Pilot (S7):**
  - every cell of F1 and F2 with seeds 1 to 30;
  - used only for the standard deviation sigma_d of each paired difference and for runtime;
  - never reused in the main analysis.
- **Sample-size rule:**
  - n_c = ceil(((z_(1 - alpha*/2) + z_0.80) x sigma_d / delta)^2), with alpha* = 0.05/90 (Holm's first threshold in F1) and 80% power;
  - n = the largest n_c over the F1 contrasts, at least 30, rounded up to a multiple of 10;
  - the same n holds for every cell of every family;
  - full runs use seeds 1001 to 1000 + n.
- **Runtime limit:** if the runtime estimate for F1 to F4 on 24 cores of FE-SIM-1 exceeds 24 hours, Filipe chooses between fewer sweep values and fewer episodes in F2 to F4. F4 runs only within the limit.

## 7. Exclusions and checks

- No episode is excluded.
- An order not delivered by the end of the drain enters order to door at the drain's end (21:00 plus 3 hours), a lower bound, in p90, in the mean, in the late rate and in every other order-time metric; the number of such orders is reported per model (G3 verdict C2). W1 snapshots where no courier counts as supply are left out of the episode mean, and their number is reported per model.
- Before the full runs, the five-agent review of the scripts that produce numbers (S8) can change code only to fix a defect. Every number that changes is rerun and reported.

## 8. What the analysis does not do

- No learned models: they belong to the next plan.
- No bundling, courier rejection, shift changes, nudges or prices.
- No claim about any company's operations.
- No test across families, and no post hoc subgroup.
