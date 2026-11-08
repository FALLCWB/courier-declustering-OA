This research was supported by data provided by Meituan.

## Part 3 again, at the wide-grid recalibration (exploratory, no test)

The first recalibration's grid cut the beta0 interval. The wide-grid recalibration (`ashkrof_fit_wide/`, setting `ashkrofw`) moved beta0 from -3 to -4.5, with the band [-6.5, -2.7375]; the first runs at beta0 -3 lie inside it and stay beside these (`c3_ashkrof_*`). The objective is flat in beta0, so the two points fit the moments about equally well. Part 3 ran again at the new values; everything else as in part 3. The fitted columns `fitted_wide_ci_*` are the fitted behavior's bands on its own wide grid (C7).

Recalibrated values beside the fitted behavior (95% bootstrap intervals over the Meituan moments):

| parameter | fitted | fitted_ci_lo | fitted_ci_hi | fitted_wide_ci_lo | fitted_wide_ci_hi | ashkrof | ashkrof_ci_lo | ashkrof_ci_hi | ashkrof_note |
|---|---|---|---|---|---|---|---|---|---|
| p_return | 0.750 | 0.675 | 0.825 | 0.675 | 0.825 | 0.750 | 0.675 | 0.850 | recalibrated |
| asc_stay | -3.000 | -3.500 | -2.000 | -6.000 | -2.500 | -4.500 | -6.500 | -2.738 | recalibrated |
| epoch_s | 42.000 | 29.400 | 42.000 | 29.400 | 42.000 | 42.000 | 42.000 | 42.000 | fixed at the fitted value |
| cruise_radius_m | 2000.000 | 2000.000 | 2800.000 | 1979.000 | 2800.000 | 2000.000 | 2000.000 | 2000.000 | fixed at the fitted value |
| part_time_stay | nan | nan | nan | nan | nan | 0.000 | nan | nan | set to 0 (Scenario 1 Primary otherwise) |
| objective | 2316.829 | nan | nan | nan | nan | 2484.122 | nan | nan |  |

Moments (Meituan peak hours, the fitted behavior and the Ashkrof setting):

| moment | in_fit | meituan_peak | meituan_all_day | simulated_fitted | simulated_ashkrof |
|---|---|---|---|---|---|
| exc_1000_15-30 | False | 0.431 | 0.443 | 0.494 | 0.497 |
| exc_1000_5-15 | False | 0.335 | 0.345 | 0.129 | 0.131 |
| exc_1000_<5 | False | 0.087 | 0.088 | 0.010 | 0.009 |
| exc_1000_>=30 | False | 0.391 | 0.448 | 0.594 | 0.588 |
| exc_1000_all | False | 0.285 | 0.323 | 0.200 | 0.199 |
| exc_2000_15-30 | True | 0.514 | 0.521 | 0.606 | 0.607 |
| exc_2000_5-15 | True | 0.420 | 0.427 | 0.269 | 0.274 |
| exc_2000_<5 | True | 0.098 | 0.105 | 0.049 | 0.048 |
| exc_2000_>=30 | True | 0.490 | 0.539 | 0.695 | 0.690 |
| exc_2000_all | False | 0.369 | 0.406 | 0.308 | 0.307 |
| exc_3000_15-30 | False | 0.501 | 0.522 | 0.587 | 0.584 |
| exc_3000_5-15 | False | 0.399 | 0.414 | 0.242 | 0.251 |
| exc_3000_<5 | False | 0.086 | 0.088 | 0.051 | 0.052 |
| exc_3000_>=30 | False | 0.528 | 0.559 | 0.687 | 0.689 |
| exc_3000_all | False | 0.386 | 0.424 | 0.312 | 0.313 |
| move_mean | nan | nan | nan | nan | 1169.973 |
| move_q10 | True | 43.393 | 73.282 | 0.000 | 0.000 |
| move_q25 | True | 312.686 | 427.585 | 263.037 | 287.888 |
| move_q50 | True | 910.804 | 1070.989 | 678.874 | 692.966 |
| move_q75 | True | 1751.876 | 1961.133 | 1515.168 | 1522.629 |
| move_q90 | True | 2748.672 | 2959.550 | 2864.637 | 2862.038 |
| ret_1000_15-30 | False | 0.532 | 0.551 | 0.595 | 0.598 |
| ret_1000_5-15 | False | 0.433 | 0.448 | 0.212 | 0.217 |
| ret_1000_<5 | False | 0.130 | 0.131 | 0.035 | 0.034 |
| ret_1000_>=30 | False | 0.484 | 0.555 | 0.687 | 0.681 |
| ret_1000_all | False | 0.366 | 0.413 | 0.263 | 0.263 |
| ret_2000_15-30 | True | 0.690 | 0.705 | 0.788 | 0.787 |
| ret_2000_5-15 | True | 0.600 | 0.611 | 0.402 | 0.411 |
| ret_2000_<5 | True | 0.162 | 0.171 | 0.085 | 0.086 |
| ret_2000_>=30 | True | 0.653 | 0.719 | 0.850 | 0.845 |
| ret_2000_all | False | 0.516 | 0.564 | 0.416 | 0.416 |
| ret_3000_15-30 | False | 0.711 | 0.736 | 0.798 | 0.794 |
| ret_3000_5-15 | False | 0.606 | 0.627 | 0.384 | 0.400 |
| ret_3000_<5 | False | 0.158 | 0.160 | 0.093 | 0.095 |
| ret_3000_>=30 | False | 0.728 | 0.768 | 0.876 | 0.876 |
| ret_3000_all | False | 0.563 | 0.610 | 0.438 | 0.440 |
| stay_15-30 | True | 0.035 | 0.040 | 0.038 | 0.026 |
| stay_5-15 | True | 0.093 | 0.082 | 0.069 | 0.053 |
| stay_<5 | True | 0.628 | 0.612 | 0.563 | 0.553 |
| stay_>=30 | True | 0.030 | 0.031 | 0.041 | 0.028 |

### Contrasts and classes

All ten models ran, seeds 1001 to 1030; the eight tested models are read against nearest courier, beside the fitted behavior's full-run rows at the same seeds, read the same way. Smallest effects per behavior: 10% of nearest courier's mean under that behavior (the fitted pilot for the fitted rows; seeds 1001 to 1030 of this part for `ashkrofw`, which had no pilot). Holm within the E1-shaped and E2-shaped sets of each behavior, as a reading device. The DQN is a descriptive row (mean differences, no interval). Contrasts: `c3w_ashkrof_contrasts.csv`; classes: `c3w_ashkrof_classes.csv`; DQN: `c3w_ashkrof_dqn.csv`.

W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model minus nearest courier, in minutes; lower is better.

| input | holm_set | contrasts | established |
|---|---|---|---|
| ashkrofw | E1-shaped | 96 | 85 |
| ashkrofw | E2-shaped | 160 | 134 |
| fitted | E1-shaped | 96 | 85 |
| fitted | E2-shaped | 160 | 132 |

Classes by model (cells):

| model | class | ashkrofw | fitted |
|---|---|---|---|
| auad | does not undo | 10 | 10 |
| auad | does not prevent | 6 | 6 |
| backpressure | does not undo | 10 | 10 |
| backpressure | does not prevent | 4 | 4 |
| backpressure | prevents at no delivery cost | 2 | 2 |
| foodmatch | does not undo | 10 | 10 |
| foodmatch | does not prevent | 6 | 6 |
| forecast | does not undo | 10 | 10 |
| forecast | prevents at no delivery cost | 4 | 4 |
| forecast | does not prevent | 2 | 2 |
| jusup | does not prevent | 6 | 6 |
| jusup | does not undo | 6 | 6 |
| jusup | undoes at no delivery cost | 4 | 4 |
| li | does not undo | 10 | 10 |
| li | prevents at no delivery cost | 4 | 4 |
| li | does not prevent | 2 | 2 |
| xu | does not undo | 6 | 6 |
| xu | does not prevent | 4 | 4 |
| xu | undoes at no delivery cost | 2 | 2 |
| xu | undoes at a delivery cost | 2 | 2 |
| xu | prevents at a delivery cost | 1 | 1 |
| xu | prevents at no delivery cost | 1 | 1 |
| zhu | does not undo | 10 | 10 |
| zhu | does not prevent | 6 | 6 |

Classes that change: 0 of 128.

None.

This research was supported by data provided by Meituan.
