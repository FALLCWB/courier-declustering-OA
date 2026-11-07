# Behavior fit report (S3), 20261102-1146-behavior-single-final, structure "single"

This research was supported by data provided by Meituan. Meituan rows never leave `data/`; this report holds fitted parameters and aggregates only.

## Fitted parameters (grid-limited bootstrap bands, conditional on the structure: the grid points picked by refitting on 100 bootstrap replicates of the targets and of each grid point; not coverage intervals)

| Parameter | Fitted | 95% interval | Grid searched |
|---|---|---|---|
| Return probability per decision outside the 2 km area | 0.75 | 0.675 to 0.825 | 0.6, 0.675, 0.75, 0.825, then +/-0.075 |
| Decision interval while idle (s) | 42 | 29.4 to 42 | 30, 42, 60, then x0.7 and x1.4 |
| Cruise radius (m) | 2000 | 2000 to 2800 | 2000, 2800, 3600, then x0.7 and x1.4 |
| Stay constant of the logit | -3 | -3.5 to -2 | -3, -2.5, -2, then +/-0.5 |

Distance at the fit 2,316.8 over 17 moments; 177 grid points; 1 grid points within 9.49 (chi-square, 4 degrees of freedom, 95%) of the best; the bootstrap refits picked 19 distinct points.

## Simulated against observed moments

Meituan targets: idle gaps between waves whose last drop-off falls between 17:00 and 20:59 local time. The shared definition reproduces the handed-over all-day moments to 1.1e-16. Simulation: 10 validation episodes (seeds 311 to 320), nearest courier, normal supply, scattered start, fitted behavior. Moments outside the fit (radii 1 and 3 km, all gap lengths pooled) are out-of-sample checks.

| Moment | In fit | Meituan 17:00 to 21:00 | Meituan all day | Simulated |
|---|---|---|---|---|
| ret_1000_all | no | 0.366 | 0.413 | 0.263 |
| exc_1000_all | no | 0.285 | 0.323 | 0.200 |
| ret_1000_<5 | no | 0.130 | 0.131 | 0.035 |
| exc_1000_<5 | no | 0.087 | 0.088 | 0.010 |
| ret_1000_5-15 | no | 0.433 | 0.448 | 0.212 |
| exc_1000_5-15 | no | 0.335 | 0.345 | 0.129 |
| ret_1000_15-30 | no | 0.532 | 0.551 | 0.595 |
| exc_1000_15-30 | no | 0.431 | 0.443 | 0.494 |
| ret_1000_>=30 | no | 0.484 | 0.555 | 0.687 |
| exc_1000_>=30 | no | 0.391 | 0.448 | 0.594 |
| ret_2000_all | no | 0.516 | 0.564 | 0.416 |
| exc_2000_all | no | 0.369 | 0.406 | 0.308 |
| ret_2000_<5 | yes | 0.162 | 0.171 | 0.085 |
| exc_2000_<5 | yes | 0.098 | 0.105 | 0.049 |
| ret_2000_5-15 | yes | 0.600 | 0.611 | 0.402 |
| exc_2000_5-15 | yes | 0.420 | 0.427 | 0.269 |
| ret_2000_15-30 | yes | 0.690 | 0.705 | 0.788 |
| exc_2000_15-30 | yes | 0.514 | 0.521 | 0.606 |
| ret_2000_>=30 | yes | 0.653 | 0.719 | 0.850 |
| exc_2000_>=30 | yes | 0.490 | 0.539 | 0.695 |
| ret_3000_all | no | 0.563 | 0.610 | 0.438 |
| exc_3000_all | no | 0.386 | 0.424 | 0.312 |
| ret_3000_<5 | no | 0.158 | 0.160 | 0.093 |
| exc_3000_<5 | no | 0.086 | 0.088 | 0.051 |
| ret_3000_5-15 | no | 0.606 | 0.627 | 0.384 |
| exc_3000_5-15 | no | 0.399 | 0.414 | 0.242 |
| ret_3000_15-30 | no | 0.711 | 0.736 | 0.798 |
| exc_3000_15-30 | no | 0.501 | 0.522 | 0.587 |
| ret_3000_>=30 | no | 0.728 | 0.768 | 0.876 |
| exc_3000_>=30 | no | 0.528 | 0.559 | 0.687 |
| stay_<5 | yes | 0.628 | 0.612 | 0.563 |
| stay_5-15 | yes | 0.093 | 0.082 | 0.069 |
| stay_15-30 | yes | 0.035 | 0.040 | 0.038 |
| stay_>=30 | yes | 0.030 | 0.031 | 0.041 |
| move_q10 | yes | 43 | 73 | 0 |
| move_q25 | yes | 313 | 428 | 263 |
| move_q50 | yes | 911 | 1,071 | 679 |
| move_q75 | yes | 1,752 | 1,961 | 1,515 |
| move_q90 | yes | 2,749 | 2,960 | 2,865 |

## Checks

Preferred area against the nearest hotspot outside it (Meituan, all day, gaps starting more than 2 km from both; 84,152 gaps, 4,449 couriers; 95% courier-bootstrap intervals): excess over random direction toward the preferred area 0.406 (0.399 to 0.412), toward the hotspot 0.020 (0.016 to 0.024), difference 0.386 (0.376 to 0.395). Mean start distance 3.27 km to the preferred area and 4.65 km to the hotspot.

Same check with the two targets at a similar distance from the drop-off (within 500 m; `pull_check_matched.json`; 28,201 gaps, 3,804 couriers): excess toward the preferred area 0.337 (0.328 to 0.346), toward the hotspot -0.035 (-0.040 to -0.030), difference 0.372 (0.359 to 0.384); mean distance 3.34 and 3.37 km.

Returns within the courier's business district against across districts (gaps starting more than 2 km from the preferred area; district = `da_id` of the last drop-off against the courier's most frequent `da_id` on other days):

| Start | Gaps | Couriers | Return share | Excess over random direction |
|---|---|---|---|---|
| inside the home district | 53,666 | 4,281 | 0.649 (0.640 to 0.658) | 0.465 (0.459 to 0.472) |
| in another district | 30,486 | 3,052 | 0.415 (0.405 to 0.425) | 0.301 (0.293 to 0.310) |

Idle kilometres per order (simulation, 10 episodes): 2.59 km idle; 3.34 km without an order (idle plus the ride to the restaurant). Allen et al. 2021 (London, Table 1): about 2.1 km per job without an order. Busiest-hour utilization 0.714; p90 order to door 35.8 min; mean episode 18.7 s.

Mean straight move per idle gap (same definition; `scripts/move_per_gap.py`, `move_per_gap.json`): simulated 1.16 km (1.15 to 1.17; 97,570 gaps, seeds 311 to 320), Meituan 17:00 to 21:00 1.23 km (1.20 to 1.25), all day 1.38 km. The simulator carries one order per gap, Meituan 3.8, so km per order differ while the move per gap matches; 3.34 km without an order per order is a stated limit (G2 ruling 2).

Figures: `behavior_fit.png`. Tables: `moments_table.csv`, `grid.csv`, `validation_episodes.csv`.
