# Fidelity note: forecast-aware matching (LP-based Hybrid policy)

Paper: Ozkan and Ward, "Dynamic Matching for Real-Time Ride Sharing", Stochastic Systems 10(1):29-70, 2020 (DOI 10.1287/stsy.2019.0037), publisher version of record read from the Koç University repository copy. Reading notes: `literature/model-specs/ozkan-ward-2020.md`. Code: `models/forecast_aware.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Sec 2 | driver type = area where the driver is; customer type j (origin, destination, priority) | driver type i = H3 resolution-8 zone of the courier's available cell; customer type j = restaurant zone (`forecast_aware.py:81`, `:87`) |
| Sec 2, Remark 3 | the controller knows the rates mu_j(t) and lambda_i(t) | mu_j = expected pickups per minute by restaurant zone; lambda_i = expected drop-offs per minute by customer zone, from the demand model (`forecast_aware.py:44-49`) |
| LP (13a) | max sum w_ij mu_j F̄_ij x_ij | `forecast_aware.py:31-32` |
| LP (13b) | sum_j mu_j F̄_ij x_ij <= lambda_i | `forecast_aware.py:34`, `:36` |
| LP (13c), (13d) | sum_i x_ij <= 1; x >= 0 | `forecast_aware.py:35-37` |
| Sec 4.1, pp.38-39 | solve (13) at finitely many epochs and hold x* as a step function | one LP per 15-minute forecast bin (`forecast_aware.py:75-78`), cached by its inputs (`:63-71`) |
| Definition 2 | draw i with probability x*_ij, none with 1 - sum_i x*_ij | `forecast_aware.py:88` |
| Sec 5.1.3, Hybrid; eq (3) | if the draw is none or zone i has no driver, offer the closest driver | `forecast_aware.py:89-94` |

## Adaptations, each with its reason

1. No customer patience: orders wait, so F̄_ij = 1 for zone pairs within a 15-minute pickup and 0 beyond (`CUTOFF_S`); without abandonment the paper's spatial signal from F̄ disappears, so the weighted objective (6)/(13a) carries it: w_ij = 1 - 0.1 t_ij / 15 min. Theorems 3 and 4 assume w = 1.
2. lambda_i: all couriers stay online for the 4 hours, so the only driver arrivals are drop-offs. lambda_i is the expected drop-off rate in zone i for orders placed in the same bin (no travel lag), which equals the right side of the paper's eq (20) when every order is served, as here.
3. No lost customers: an order is never refused; the Hybrid fallback (closest courier) serves when the draw gives none or the drawn zone is empty, and an order waits when no courier is idle. Each episode reports the share of orders served by the fallback, split by cause (G3 verdict C3).
4. Batches: pending orders of a 30 s window are processed one at a time in creation order with live idle counts (Remark 5 has one customer per instant).
5. Inside the drawn zone, the courier that reaches the restaurant first is offered (the paper treats drivers in an area as interchangeable).
6. The forecast includes the 18:00 burst of the burst scenario, which is a known event in this study.
7. Zone-to-zone pickup times use each zone's representative cell; inside one zone the pickup time is 0 for the LP.
8. Outside the theorems' conditions: Q(0) > 0, time-varying rates, drivers re-entering where they deliver.

## Known-answer tests (`tests/test_models.py`)

- `test_forecast_lp_sends_zone_2_drivers_to_zone_1_and_zone_3_drivers_to_zone_2`: the paper's experiment-1 shape (lambda = (0, n, n), mu = (n, n, 0)); the LP gives x*_21 = x*_32 = 1.
- `test_forecast_hybrid_follows_the_lp_zone_and_falls_back_to_the_closest_courier`.
