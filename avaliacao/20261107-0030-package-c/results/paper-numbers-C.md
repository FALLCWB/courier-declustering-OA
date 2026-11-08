# Paper numbers, package C

Pre-registration addendum C (`preregistration-addendum-C.md`) committed at ed05df2, before any episode of parts 1 to 4. Part 1 (E6) is confirmatory; parts 2 to 5 are exploratory or descriptive, with no test.

This research was supported by data provided by Meituan.

## Summary

- E6 (confirmatory, n = 150): 141 of 144 contrasts established (Holm within E6); 0 of 72 cell-model pairs undo the cluster (none); 8 classes differ from those Paper A quotes.
- Stay (exploratory): on the 10 Q2 cells, W1 over 60 min falls below nearest courier's in 6 cells; Zhu et al. falls below `stay` in 8 and Jusup et al. in 8 (95% intervals below 0).
- Ashkrof setting at the first recalibration (exploratory): 0 of 128 classes change.
- Noisy demand (exploratory): 0 of 64 classes change.
- Ashkrof setting at the wide-grid recalibration (exploratory): 0 of 128 classes change.
- Ashkrof, first recalibration (its grid cut the beta0 interval): return probability 0.75 [0.65, 0.85] (fitted 0.75); stay constant -3 [-4, -2] (fitted -3).
- Ashkrof, wide-grid recalibration: return probability 0.75 [0.675, 0.85] (fitted 0.75); stay constant -4.5 [-6.5, -2.74] (fitted -3).
- Part 5, W1 by window after the cluster appears (0-60, 60-120, 180-240 min; model minus nearest courier, mean of the nine clustered cells): zhu -0.10, -0.16, -3.34; jusup -1.77, +0.76, -2.02; xu -0.48, +0.89, -0.70.
- Part 5, W1 over 20:00 to 20:59 by return probability (mean of the nine clustered cells): zhu p0 -0.21, fitted -3.34, p1 -4.19; jusup p0 +1.12, fitted -2.02, p1 -2.86; xu p0 +0.53, fitted -0.70, p1 +0.29.
- Part 5, Q1 W1 without 20:30 to 21:00: the largest shift is jusup, scattered, normal: +2.01 to +1.68.
- Part 5, per training policy: the largest spread between the five policy means of one contrast is 7.59 min (auad, E2, big_cluster, tight, p90_c2d_min).
- C6 (exploratory, homes at the drop-offs, seeds 1001 to 1030): cell-model pairs that undo the cluster: undo in 0 of 72 under `resid`, 0 under `indep`, 7 under the fitted setting.
- C7, fitted behavior, bands on a wider grid: return probability [0.675, 0.825] to [0.675, 0.825]; decision delay (s) [29.4, 42] to [29.4, 42]; cruise radius (m) [2000, 2800] to [1979, 2800] (point 2000 to 2800); stay constant (beta0) [-3.5, -2] to [-6, -2.5] (point -3 to -3.5). Point estimate moved for cruise radius (m), stay constant (beta0).
- Ashkrof variant, bands on a wider grid: return probability [0.65, 0.85] to [0.675, 0.85]; stay constant (beta0) [-4, -2] to [-6.5, -2.738] (point -3 to -4.5). Point estimate moved for stay constant (beta0).

# Part 1, E6

## Part 1. E6: clustered starts with preferred areas independent of the start (confirmatory)

Behavior `indep`, seeds 1001 to 1150 (n = 150), arm C at 100% obedience. 144 contrasts, Holm at 0.05 within E6; smallest effects as in E2. Differences are model minus nearest courier, in minutes; lower is better.

| contrasts | established | established decrease of at least delta | established increase | equivalent within delta (R3) | inconclusive (R3) |
|---|---|---|---|---|---|
| 144 | 141 | 8 | 93 | 3 | 0 |

141 established contrasts. Classes by model:

| model | does not undo |
|---|---|
| auad | 9 |
| backpressure | 9 |
| foodmatch | 9 |
| forecast | 9 |
| jusup | 9 |
| li | 9 |
| xu | 9 |
| zhu | 9 |

Cells whose class differs from the class Paper A quotes (E2, or E2-fresh for the frozen three): 8 of 72.

| cell | model | W1 over 60 min [95% CI] | p_Holm | p90 | p90 upper 95% | p90 p_Holm | E6 class | Paper A class (source) |
|---|---|---|---|---|---|---|---|---|
| mixed, tight | xu | -1.18 [-1.21, -1.14] | 5.31e-114 | +0.02 | +0.44 | 1 | does not undo | undoes at no delivery cost (E2) |
| mixed, normal | xu | -1.05 [-1.08, -1.03] | 9.96e-123 | +3.15 | +3.18 | 1.12e-188 | does not undo | undoes at no delivery cost (E2) |
| mixed, loose | xu | -0.90 [-0.92, -0.88] | 6.79e-131 | +3.20 | +3.22 | 4.56e-196 | does not undo | undoes at a delivery cost (E2) |
| three_clusters, normal | jusup | +1.79 [+1.74, +1.83] | 1.43e-118 | +1.95 | +2.01 | 8.02e-107 | does not undo | undoes at no delivery cost (E2) |
| three_clusters, loose | jusup | +1.40 [+1.37, +1.45] | 2.3e-114 | +0.57 | +0.60 | 7.66e-90 | does not undo | undoes at no delivery cost (E2) |
| mixed, tight | jusup | +2.97 [+2.91, +3.02] | 3.65e-141 | +9.24 | +9.54 | 1.89e-102 | does not undo | undoes at no delivery cost (E2) |
| mixed, normal | jusup | +2.51 [+2.46, +2.55] | 1.53e-144 | +1.20 | +1.24 | 1.05e-100 | does not undo | undoes at no delivery cost (E2) |
| mixed, loose | jusup | +1.89 [+1.85, +1.93] | 3.21e-132 | +0.27 | +0.29 | 6.3e-58 | does not undo | undoes at no delivery cost (E2) |

Every cell: `c1_e6_classes.csv`; every contrast with its R3 reading: `c1_e6_contrasts.csv`.

### Time to undo and the second-hour check (cells classed as undoing, and nearest courier)

Against the same model, obedience, supply level and seed from the scattered start (fitted rows of the full runs).

| scenario | level | model | class | time_to_undo_median | time_to_undo_q25 | time_to_undo_q75 | censored_count | nearest median | second-hour W1 | nearest second-hour W1 | second_hour_check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| big_cluster | tight | nearest | nearest courier | 55.000 | 54.000 | 58.000 | 0 | 55.000 | 5.660 | 5.660 |  |
| big_cluster | normal | nearest | nearest courier | 91.000 | 88.000 | 96.000 | 0 | 91.000 | 7.510 | 7.510 |  |
| big_cluster | loose | nearest | nearest courier | 132.000 | 120.000 | 146.750 | 1 | 132.000 | 8.070 | 8.070 |  |
| three_clusters | tight | nearest | nearest courier | 65.000 | 63.000 | 67.000 | 0 | 65.000 | 5.350 | 5.350 |  |
| three_clusters | normal | nearest | nearest courier | 132.500 | 119.000 | 145.000 | 2 | 132.500 | 8.850 | 8.850 |  |
| three_clusters | loose | nearest | nearest courier | 159.000 | 133.250 | 192.500 | 18 | 159.000 | 7.200 | 7.200 |  |
| mixed | tight | nearest | nearest courier | 59.000 | 56.000 | 63.000 | 0 | 59.000 | 5.570 | 5.570 |  |
| mixed | normal | nearest | nearest courier | 66.000 | 63.000 | 69.000 | 0 | 66.000 | 4.570 | 4.570 |  |
| mixed | loose | nearest | nearest courier | 72.000 | 68.000 | 77.000 | 0 | 72.000 | 4.160 | 4.160 |  |

### DQN (descriptive)

| scenario | level | model | w1_60_minus_nearest | p90_minus_nearest |
|---|---|---|---|---|
| big_cluster | tight | jahanshahi | -0.015 | -0.074 |
| big_cluster | normal | jahanshahi | -0.036 | 0.007 |
| big_cluster | loose | jahanshahi | -0.018 | 0.029 |
| three_clusters | tight | jahanshahi | -0.001 | -0.121 |
| three_clusters | normal | jahanshahi | -0.018 | 0.011 |
| three_clusters | loose | jahanshahi | -0.014 | 0.024 |
| mixed | tight | jahanshahi | -0.064 | 0.004 |
| mixed | normal | jahanshahi | -0.044 | 0.047 |
| mixed | loose | jahanshahi | -0.031 | 0.032 |

### Pre-registered secondary: W1 over 20:00 to 20:59, model minus nearest courier

| model | big_cluster, loose | big_cluster, normal | big_cluster, tight | mixed, loose | mixed, normal | mixed, tight | three_clusters, loose | three_clusters, normal | three_clusters, tight |
|---|---|---|---|---|---|---|---|---|---|
| auad | +0.45 [+0.43, +0.48] | +0.00 [-0.02, +0.03] | -0.40 [-0.44, -0.37] | +0.15 [+0.13, +0.17] | -0.03 [-0.05, -0.00] | -0.08 [-0.12, -0.04] | +0.50 [+0.47, +0.52] | +0.39 [+0.36, +0.42] | -0.41 [-0.45, -0.38] |
| backpressure | -0.93 [-0.96, -0.91] | +0.23 [+0.20, +0.26] | -0.14 [-0.17, -0.11] | -0.19 [-0.21, -0.16] | -0.11 [-0.13, -0.08] | +0.15 [+0.11, +0.18] | -0.63 [-0.65, -0.60] | -0.45 [-0.48, -0.42] | -0.11 [-0.14, -0.07] |
| foodmatch | +0.35 [+0.33, +0.37] | +0.46 [+0.42, +0.50] | -0.62 [-0.66, -0.59] | +0.11 [+0.09, +0.14] | -0.06 [-0.08, -0.03] | -0.07 [-0.11, -0.03] | +0.43 [+0.40, +0.45] | +0.13 [+0.10, +0.16] | -0.66 [-0.70, -0.63] |
| forecast | +1.49 [+1.47, +1.52] | -0.25 [-0.29, -0.20] | -0.38 [-0.41, -0.35] | +0.52 [+0.48, +0.56] | -0.42 [-0.48, -0.37] | -0.23 [-0.26, -0.19] | +0.17 [+0.14, +0.20] | -0.10 [-0.13, -0.07] | -0.43 [-0.46, -0.40] |
| jahanshahi | -0.22 [-0.24, -0.20] | +0.03 [+0.01, +0.06] | -0.01 [-0.04, +0.02] | -0.08 [-0.10, -0.06] | -0.02 [-0.04, +0.00] | -0.03 [-0.05, -0.01] | -0.13 [-0.15, -0.11] | -0.18 [-0.20, -0.15] | -0.02 [-0.05, +0.01] |
| jusup | +4.96 [+4.90, +5.03] | +5.06 [+5.00, +5.11] | +0.80 [+0.76, +0.85] | +5.85 [+5.79, +5.91] | +4.14 [+4.08, +4.19] | +1.63 [+1.57, +1.69] | +8.30 [+8.24, +8.36] | +6.20 [+6.11, +6.29] | +0.97 [+0.92, +1.02] |
| li | -1.29 [-1.33, -1.25] | -0.08 [-0.11, -0.04] | -0.61 [-0.65, -0.56] | -0.56 [-0.59, -0.54] | -0.48 [-0.51, -0.45] | -0.33 [-0.36, -0.30] | -1.23 [-1.26, -1.19] | -0.88 [-0.91, -0.85] | -0.86 [-0.91, -0.82] |
| xu | +1.05 [+1.02, +1.09] | +0.45 [+0.41, +0.49] | -1.10 [-1.16, -1.04] | +0.68 [+0.65, +0.72] | +0.04 [-0.00, +0.08] | -0.79 [-0.85, -0.74] | +0.93 [+0.89, +0.97] | +0.81 [+0.76, +0.86] | -1.27 [-1.32, -1.21] |
| zhu | +1.06 [+1.01, +1.11] | +5.30 [+5.24, +5.36] | +0.43 [+0.39, +0.48] | +4.63 [+4.56, +4.71] | +2.22 [+2.12, +2.32] | +1.16 [+1.10, +1.22] | +7.56 [+7.49, +7.62] | +3.05 [+2.96, +3.14] | +0.55 [+0.50, +0.60] |

# Part 2, stay

## Part 2. Stay without commands: suppression against repositioning (exploratory, no test)

Fitted behavior, seeds 1001 to 1150 (n = 150); `stay` and arm C at 100% obedience. Rows are cells, columns the contrasts; every number with its interval is in `c2_stay.csv`.

### W1

| cell | stay - nearest | zhu - stay | jusup - stay |
|---|---|---|---|
| scattered, tight | +1.05 [+1.02, +1.09] | -0.35 [-0.37, -0.33] | +0.11 [+0.09, +0.13] |
| scattered, normal | +1.61 [+1.59, +1.64] | -0.46 [-0.46, -0.45] | +0.39 [+0.37, +0.41] |
| scattered, loose | +1.24 [+1.22, +1.25] | -0.29 [-0.30, -0.29] | +0.32 [+0.30, +0.34] |
| burst, tight | +0.40 [+0.38, +0.41] | -0.20 [-0.21, -0.18] | +0.07 [+0.06, +0.09] |
| burst, normal | +1.71 [+1.69, +1.74] | -0.48 [-0.49, -0.47] | +0.33 [+0.32, +0.35] |
| burst, loose | +1.41 [+1.39, +1.43] | -0.32 [-0.33, -0.31] | +0.32 [+0.30, +0.34] |
| big_cluster, tight | +0.04 [+0.02, +0.05] | -0.09 [-0.10, -0.07] | +0.14 [+0.12, +0.16] |
| big_cluster, normal | -0.49 [-0.52, -0.45] | -0.33 [-0.34, -0.32] | +0.45 [+0.41, +0.48] |
| big_cluster, loose | -4.22 [-4.24, -4.19] | -0.23 [-0.24, -0.22] | +2.16 [+2.11, +2.20] |
| three_clusters, tight | +0.12 [+0.11, +0.14] | -0.08 [-0.09, -0.07] | -0.01 [-0.03, +0.01] |
| three_clusters, normal | -0.67 [-0.71, -0.63] | -0.12 [-0.14, -0.10] | +1.73 [+1.66, +1.80] |
| three_clusters, loose | -1.22 [-1.24, -1.20] | -0.26 [-0.27, -0.25] | -1.24 [-1.29, -1.19] |
| mixed, tight | +0.23 [+0.21, +0.24] | -0.10 [-0.12, -0.09] | -0.12 [-0.14, -0.10] |
| mixed, normal | -0.43 [-0.49, -0.36] | -0.28 [-0.29, -0.27] | +0.85 [+0.80, +0.90] |
| mixed, loose | -1.31 [-1.33, -1.29] | -0.18 [-0.19, -0.18] | -1.40 [-1.47, -1.33] |
| meetup, normal | +1.25 [+1.23, +1.27] | -0.41 [-0.42, -0.40] | +0.38 [+0.36, +0.40] |

### W1 over the first 60 min

| cell | stay - nearest | zhu - stay | jusup - stay |
|---|---|---|---|
| scattered, tight | -0.52 [-0.53, -0.50] | -0.15 [-0.15, -0.14] | +0.28 [+0.26, +0.30] |
| scattered, normal | -0.78 [-0.79, -0.76] | -0.09 [-0.09, -0.09] | +0.28 [+0.26, +0.30] |
| scattered, loose | -1.06 [-1.07, -1.05] | -0.04 [-0.04, -0.04] | +0.33 [+0.31, +0.34] |
| burst, tight | -0.49 [-0.51, -0.48] | -0.15 [-0.16, -0.14] | +0.28 [+0.26, +0.30] |
| burst, normal | -0.73 [-0.74, -0.72] | -0.09 [-0.09, -0.08] | +0.28 [+0.26, +0.30] |
| burst, loose | -0.99 [-1.00, -0.98] | -0.04 [-0.04, -0.04] | +0.32 [+0.31, +0.34] |
| big_cluster, tight | -0.15 [-0.16, -0.14] | -0.01 [-0.01, -0.00] | +0.59 [+0.55, +0.63] |
| big_cluster, normal | -0.20 [-0.21, -0.19] | -0.02 [-0.02, -0.02] | -0.45 [-0.49, -0.41] |
| big_cluster, loose | -0.11 [-0.12, -0.10] | -0.02 [-0.02, -0.02] | -1.85 [-1.88, -1.81] |
| three_clusters, tight | -0.15 [-0.17, -0.14] | +0.04 [+0.03, +0.04] | -0.65 [-0.71, -0.59] |
| three_clusters, normal | -0.06 [-0.07, -0.04] | -0.09 [-0.10, -0.09] | -2.60 [-2.63, -2.56] |
| three_clusters, loose | +0.08 [+0.07, +0.10] | -0.14 [-0.15, -0.13] | -3.07 [-3.10, -3.04] |
| mixed, tight | -0.04 [-0.06, -0.03] | -0.00 [-0.01, +0.00] | -1.60 [-1.65, -1.54] |
| mixed, normal | +0.01 [+0.00, +0.02] | -0.02 [-0.03, -0.02] | -2.83 [-2.87, -2.79] |
| mixed, loose | +0.05 [+0.04, +0.06] | -0.03 [-0.03, -0.02] | -2.86 [-2.89, -2.83] |
| meetup, normal | +1.92 [+1.89, +1.95] | -0.53 [-0.55, -0.51] | +0.44 [+0.41, +0.47] |

### W1 over 20:00 to 20:59

| cell | stay - nearest | zhu - stay | jusup - stay |
|---|---|---|---|
| scattered, tight | +3.20 [+3.14, +3.27] | -0.72 [-0.74, -0.69] | -0.16 [-0.19, -0.13] |
| scattered, normal | +3.80 [+3.76, +3.83] | -0.70 [-0.71, -0.69] | +0.28 [+0.26, +0.30] |
| scattered, loose | +3.17 [+3.14, +3.20] | -0.45 [-0.45, -0.44] | +0.24 [+0.20, +0.27] |
| burst, tight | +1.83 [+1.78, +1.88] | -0.52 [-0.55, -0.49] | -0.13 [-0.16, -0.10] |
| burst, normal | +3.95 [+3.91, +3.99] | -0.76 [-0.77, -0.75] | +0.05 [+0.03, +0.07] |
| burst, loose | +3.41 [+3.38, +3.44] | -0.51 [-0.51, -0.50] | +0.15 [+0.12, +0.18] |
| big_cluster, tight | +0.33 [+0.28, +0.39] | -0.34 [-0.37, -0.30] | +0.03 [-0.00, +0.07] |
| big_cluster, normal | -4.54 [-4.63, -4.46] | -0.65 [-0.66, -0.64] | -0.89 [-0.94, -0.84] |
| big_cluster, loose | -11.42 [-11.48, -11.37] | -0.43 [-0.44, -0.42] | +3.47 [+3.42, +3.51] |
| three_clusters, tight | +0.66 [+0.61, +0.70] | -0.37 [-0.41, -0.32] | +0.06 [+0.02, +0.10] |
| three_clusters, normal | -3.18 [-3.25, -3.11] | -0.49 [-0.51, -0.46] | +2.66 [+2.61, +2.72] |
| three_clusters, loose | -3.17 [-3.21, -3.12] | -0.34 [-0.35, -0.32] | +0.41 [+0.34, +0.47] |
| mixed, tight | +0.96 [+0.90, +1.01] | -0.43 [-0.47, -0.40] | +0.04 [+0.00, +0.07] |
| mixed, normal | -2.13 [-2.26, -1.99] | -0.61 [-0.63, -0.59] | +1.30 [+1.20, +1.41] |
| mixed, loose | -3.63 [-3.68, -3.57] | -0.32 [-0.34, -0.31] | +0.89 [+0.81, +0.98] |
| meetup, normal | +2.95 [+2.91, +2.99] | -0.64 [-0.66, -0.63] | +0.28 [+0.25, +0.31] |

### p90 order to door (min)

| cell | stay - nearest | zhu - stay | jusup - stay |
|---|---|---|---|
| scattered, tight | -0.05 [-0.11, -0.00] | -0.32 [-0.38, -0.27] | +0.19 [+0.14, +0.24] |
| scattered, normal | +0.09 [+0.08, +0.09] | -0.09 [-0.09, -0.08] | -0.03 [-0.04, -0.03] |
| scattered, loose | +0.05 [+0.04, +0.05] | -0.05 [-0.06, -0.05] | -0.05 [-0.05, -0.04] |
| burst, tight | -0.08 [-0.14, -0.01] | -0.21 [-0.29, -0.14] | +0.25 [+0.17, +0.33] |
| burst, normal | +0.10 [+0.09, +0.10] | -0.11 [-0.12, -0.11] | -0.03 [-0.03, -0.02] |
| burst, loose | +0.06 [+0.05, +0.06] | -0.06 [-0.07, -0.06] | -0.05 [-0.05, -0.04] |
| big_cluster, tight | -0.01 [-0.12, +0.10] | -0.12 [-0.20, -0.04] | -1.64 [-1.75, -1.53] |
| big_cluster, normal | -0.06 [-0.09, -0.02] | -0.14 [-0.16, -0.12] | -2.20 [-2.28, -2.12] |
| big_cluster, loose | -0.02 [-0.04, -0.00] | -0.09 [-0.11, -0.08] | -3.04 [-3.08, -3.01] |
| three_clusters, tight | -0.26 [-0.37, -0.15] | -0.33 [-0.45, -0.22] | -2.84 [-2.97, -2.72] |
| three_clusters, normal | -0.25 [-0.29, -0.21] | -0.36 [-0.40, -0.33] | -3.11 [-3.16, -3.06] |
| three_clusters, loose | -0.11 [-0.13, -0.08] | -0.37 [-0.38, -0.35] | -2.17 [-2.21, -2.13] |
| mixed, tight | +0.03 [-0.06, +0.12] | -0.06 [-0.14, +0.03] | -2.21 [-2.35, -2.07] |
| mixed, normal | -0.03 [-0.05, -0.01] | -0.10 [-0.11, -0.08] | -1.50 [-1.53, -1.47] |
| mixed, loose | -0.02 [-0.03, -0.00] | -0.11 [-0.12, -0.10] | -0.65 [-0.68, -0.61] |
| meetup, normal | +0.09 [+0.08, +0.09] | -0.09 [-0.09, -0.08] | -0.03 [-0.04, -0.03] |

### km without an order per order

| cell | stay - nearest | zhu - stay | jusup - stay |
|---|---|---|---|
| scattered, tight | -2.13 [-2.15, -2.11] | +0.49 [+0.47, +0.50] | +0.78 [+0.76, +0.80] |
| scattered, normal | -2.50 [-2.50, -2.49] | +0.66 [+0.65, +0.66] | +1.08 [+1.07, +1.10] |
| scattered, loose | -2.83 [-2.83, -2.82] | +0.70 [+0.70, +0.71] | +1.63 [+1.60, +1.65] |
| burst, tight | -2.29 [-2.30, -2.28] | +0.39 [+0.38, +0.40] | +0.73 [+0.71, +0.75] |
| burst, normal | -2.44 [-2.45, -2.44] | +0.63 [+0.62, +0.63] | +1.07 [+1.05, +1.09] |
| burst, loose | -2.79 [-2.79, -2.79] | +0.69 [+0.68, +0.69] | +1.57 [+1.55, +1.60] |
| big_cluster, tight | -1.90 [-1.91, -1.89] | +0.21 [+0.20, +0.22] | +1.03 [+1.00, +1.05] |
| big_cluster, normal | -3.08 [-3.09, -3.07] | +0.45 [+0.45, +0.46] | +1.49 [+1.47, +1.52] |
| big_cluster, loose | -3.36 [-3.37, -3.35] | +0.50 [+0.50, +0.51] | +2.42 [+2.40, +2.44] |
| three_clusters, tight | -2.06 [-2.08, -2.05] | +0.22 [+0.21, +0.23] | +0.82 [+0.80, +0.84] |
| three_clusters, normal | -2.73 [-2.74, -2.72] | +0.41 [+0.40, +0.41] | +1.36 [+1.34, +1.39] |
| three_clusters, loose | -2.58 [-2.59, -2.58] | +0.45 [+0.45, +0.46] | +2.80 [+2.76, +2.85] |
| mixed, tight | -2.09 [-2.10, -2.07] | +0.28 [+0.27, +0.29] | +0.92 [+0.90, +0.94] |
| mixed, normal | -2.67 [-2.68, -2.66] | +0.51 [+0.50, +0.51] | +1.57 [+1.55, +1.58] |
| mixed, loose | -2.54 [-2.54, -2.53] | +0.54 [+0.53, +0.54] | +3.08 [+3.05, +3.11] |
| meetup, normal | -2.45 [-2.46, -2.45] | +0.65 [+0.65, +0.66] | +1.08 [+1.07, +1.10] |

# Part 3, Ashkrof et al.

## Part 3. One coherent behavior specification, Ashkrof et al. (exploratory, no test)

Recalibrated values beside the fitted behavior (95% bootstrap intervals over the Meituan moments):

| parameter | fitted | fitted_ci_lo | fitted_ci_hi | ashkrof | ashkrof_ci_lo | ashkrof_ci_hi | ashkrof_note |
|---|---|---|---|---|---|---|---|
| p_return | 0.750 | 0.675 | 0.825 | 0.750 | 0.650 | 0.850 | recalibrated |
| asc_stay | -3.000 | -3.500 | -2.000 | -3.000 | -4.000 | -2.000 | recalibrated |
| epoch_s | 42.000 | 29.400 | 42.000 | 42.000 | 42.000 | 42.000 | fixed at the fitted value |
| cruise_radius_m | 2000.000 | 2000.000 | 2800.000 | 2000.000 | 2000.000 | 2000.000 | fixed at the fitted value |
| part_time_stay | nan | nan | nan | 0.000 | nan | nan | set to 0 (Scenario 1 Primary otherwise) |
| objective | 2316.829 | nan | nan | 2591.285 | nan | nan |  |

Moments (Meituan peak hours, the fitted behavior and the Ashkrof setting):

| moment | in_fit | meituan_peak | meituan_all_day | simulated_fitted | simulated_ashkrof |
|---|---|---|---|---|---|
| exc_1000_15-30 | False | 0.431 | 0.443 | 0.494 | 0.493 |
| exc_1000_5-15 | False | 0.335 | 0.345 | 0.129 | 0.131 |
| exc_1000_<5 | False | 0.087 | 0.088 | 0.010 | 0.010 |
| exc_1000_>=30 | False | 0.391 | 0.448 | 0.594 | 0.589 |
| exc_1000_all | False | 0.285 | 0.323 | 0.200 | 0.200 |
| exc_2000_15-30 | True | 0.514 | 0.521 | 0.606 | 0.607 |
| exc_2000_5-15 | True | 0.420 | 0.427 | 0.269 | 0.279 |
| exc_2000_<5 | True | 0.098 | 0.105 | 0.049 | 0.048 |
| exc_2000_>=30 | True | 0.490 | 0.539 | 0.695 | 0.698 |
| exc_2000_all | False | 0.369 | 0.406 | 0.308 | 0.310 |
| exc_3000_15-30 | False | 0.501 | 0.522 | 0.587 | 0.590 |
| exc_3000_5-15 | False | 0.399 | 0.414 | 0.242 | 0.246 |
| exc_3000_<5 | False | 0.086 | 0.088 | 0.051 | 0.054 |
| exc_3000_>=30 | False | 0.528 | 0.559 | 0.687 | 0.688 |
| exc_3000_all | False | 0.386 | 0.424 | 0.312 | 0.315 |
| move_mean | nan | nan | nan | nan | 1166.896 |
| move_q10 | True | 43.393 | 73.282 | 0.000 | 0.000 |
| move_q25 | True | 312.686 | 427.585 | 263.037 | 275.651 |
| move_q50 | True | 910.804 | 1070.989 | 678.874 | 685.302 |
| move_q75 | True | 1751.876 | 1961.133 | 1515.168 | 1527.966 |
| move_q90 | True | 2748.672 | 2959.550 | 2864.637 | 2870.969 |
| ret_1000_15-30 | False | 0.532 | 0.551 | 0.595 | 0.596 |
| ret_1000_5-15 | False | 0.433 | 0.448 | 0.212 | 0.216 |
| ret_1000_<5 | False | 0.130 | 0.131 | 0.035 | 0.035 |
| ret_1000_>=30 | False | 0.484 | 0.555 | 0.687 | 0.683 |
| ret_1000_all | False | 0.366 | 0.413 | 0.263 | 0.264 |
| ret_2000_15-30 | True | 0.690 | 0.705 | 0.788 | 0.788 |
| ret_2000_5-15 | True | 0.600 | 0.611 | 0.402 | 0.414 |
| ret_2000_<5 | True | 0.162 | 0.171 | 0.085 | 0.085 |
| ret_2000_>=30 | True | 0.653 | 0.719 | 0.850 | 0.855 |
| ret_2000_all | False | 0.516 | 0.564 | 0.416 | 0.419 |
| ret_3000_15-30 | False | 0.711 | 0.736 | 0.798 | 0.798 |
| ret_3000_5-15 | False | 0.606 | 0.627 | 0.384 | 0.389 |
| ret_3000_<5 | False | 0.158 | 0.160 | 0.093 | 0.097 |
| ret_3000_>=30 | False | 0.728 | 0.768 | 0.876 | 0.877 |
| ret_3000_all | False | 0.563 | 0.610 | 0.438 | 0.440 |
| stay_15-30 | True | 0.035 | 0.040 | 0.038 | 0.034 |
| stay_5-15 | True | 0.093 | 0.082 | 0.069 | 0.065 |
| stay_<5 | True | 0.628 | 0.612 | 0.563 | 0.558 |
| stay_>=30 | True | 0.030 | 0.031 | 0.041 | 0.033 |

### Contrasts and classes

All ten models ran, seeds 1001 to 1030; the eight tested models are read against nearest courier, beside the fitted behavior's full-run rows at the same seeds, read the same way. Smallest effects per behavior: 10% of nearest courier's mean under that behavior (the fitted pilot for the fitted rows; seeds 1001 to 1030 of this part for `ashkrof`, which had no pilot). Holm within the E1-shaped and E2-shaped sets of each behavior, as a reading device. The DQN is a descriptive row (mean differences, no interval). Contrasts: `c3_ashkrof_contrasts.csv`; classes: `c3_ashkrof_classes.csv`; DQN: `c3_ashkrof_dqn.csv`.

W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model minus nearest courier, in minutes; lower is better.

| input | holm_set | contrasts | established |
|---|---|---|---|
| ashkrof | E1-shaped | 96 | 85 |
| ashkrof | E2-shaped | 160 | 134 |
| fitted | E1-shaped | 96 | 85 |
| fitted | E2-shaped | 160 | 132 |

Classes by model (cells):

| model | class | ashkrof | fitted |
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

# Part 4, noisy demand

## Part 4. Noisy demand information (exploratory, no test)

Forecast-aware matching, Li et al., Zhu et al. and Jusup et al. read the expected demand times a lognormal factor per zone and episode (mean 1, CV 0.2); W1 keeps the true demand. Seeds 1001 to 1030; nearest courier and the true-input rows come from the full runs at the same seeds. Holm runs within the E1-shaped and E2-shaped sets of each input, as a reading device. The noisy and true intervals of one contrast share their bootstrap resamples (common random numbers), so their difference is not blurred by resampling. Episodes equal to the true-input episode in every metric: forecast 0 of 480, li 480 of 480, zhu 0 of 480, jusup 6 of 480; a model with all its episodes equal reads no expected demand at run time. Contrasts: `c4_noise_contrasts.csv`; classes: `c4_noise_classes.csv`; identity: `c4_noise_identity.csv`.

W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model minus nearest courier, in minutes; lower is better.

| input | holm_set | contrasts | established |
|---|---|---|---|
| noisy | E1-shaped | 48 | 39 |
| noisy | E2-shaped | 80 | 69 |
| true | E1-shaped | 48 | 39 |
| true | E2-shaped | 80 | 70 |

Classes by model (cells):

| model | class | noisy | true |
|---|---|---|---|
| forecast | does not undo | 10 | 10 |
| forecast | prevents at no delivery cost | 4 | 4 |
| forecast | does not prevent | 2 | 2 |
| jusup | does not prevent | 6 | 6 |
| jusup | does not undo | 6 | 6 |
| jusup | undoes at no delivery cost | 4 | 4 |
| li | does not undo | 10 | 10 |
| li | prevents at no delivery cost | 4 | 4 |
| li | does not prevent | 2 | 2 |
| zhu | does not undo | 10 | 10 |
| zhu | does not prevent | 6 | 6 |

Classes that change: 0 of 64.

None.

# Part 5, tables from the existing runs

## Package C, part 5: tables from the existing runs (descriptive)


Seeds 1001 to 1150 (n = 150), fitted behavior unless stated, arm C at 100% obedience. Differences are model minus nearest courier, paired by seed, with 95% percentile bootstrap intervals; no test.

## W1 by window after the cluster appears

| cell | window (min) | model | difference [95% CI] |
|---|---|---|---|
| big_cluster, tight | 0-60 | foodmatch | +0.50 [+0.49, +0.52] |
| big_cluster, tight | 0-60 | forecast | +0.01 [+0.01, +0.01] |
| big_cluster, tight | 0-60 | backpressure | -0.06 [-0.06, -0.06] |
| big_cluster, tight | 0-60 | xu | +3.34 [+3.31, +3.38] |
| big_cluster, tight | 0-60 | li | -0.07 [-0.07, -0.06] |
| big_cluster, tight | 0-60 | jahanshahi | +0.00 [-0.00, +0.00] |
| big_cluster, tight | 0-60 | auad | +0.30 [+0.22, +0.37] |
| big_cluster, tight | 0-60 | zhu | -0.16 [-0.17, -0.15] |
| big_cluster, tight | 0-60 | jusup | +0.44 [+0.39, +0.48] |
| big_cluster, tight | 60-120 | foodmatch | -0.16 [-0.20, -0.13] |
| big_cluster, tight | 60-120 | forecast | +0.01 [-0.00, +0.02] |
| big_cluster, tight | 60-120 | backpressure | -0.00 [-0.02, +0.01] |
| big_cluster, tight | 60-120 | xu | +1.26 [+1.22, +1.30] |
| big_cluster, tight | 60-120 | li | +0.19 [+0.17, +0.22] |
| big_cluster, tight | 60-120 | jahanshahi | +0.01 [-0.00, +0.02] |
| big_cluster, tight | 60-120 | auad | -0.01 [-0.03, +0.02] |
| big_cluster, tight | 60-120 | zhu | -0.01 [-0.03, +0.01] |
| big_cluster, tight | 60-120 | jusup | -0.14 [-0.16, -0.12] |
| big_cluster, tight | 180-240 | foodmatch | +4.14 [+4.07, +4.21] |
| big_cluster, tight | 180-240 | forecast | -0.04 [-0.07, -0.00] |
| big_cluster, tight | 180-240 | backpressure | -0.23 [-0.27, -0.19] |
| big_cluster, tight | 180-240 | xu | +1.75 [+1.68, +1.82] |
| big_cluster, tight | 180-240 | li | +4.17 [+4.10, +4.26] |
| big_cluster, tight | 180-240 | jahanshahi | -0.03 [-0.07, +0.01] |
| big_cluster, tight | 180-240 | auad | +1.34 [+1.21, +1.46] |
| big_cluster, tight | 180-240 | zhu | -0.00 [-0.07, +0.06] |
| big_cluster, tight | 180-240 | jusup | +0.37 [+0.31, +0.43] |
| big_cluster, normal | 0-60 | foodmatch | +0.17 [+0.16, +0.18] |
| big_cluster, normal | 0-60 | forecast | +0.01 [+0.01, +0.02] |
| big_cluster, normal | 0-60 | backpressure | -0.10 [-0.10, -0.10] |
| big_cluster, normal | 0-60 | xu | +0.90 [+0.88, +0.93] |
| big_cluster, normal | 0-60 | li | -0.12 [-0.13, -0.12] |
| big_cluster, normal | 0-60 | jahanshahi | -0.00 [-0.00, -0.00] |
| big_cluster, normal | 0-60 | auad | +0.11 [+0.08, +0.13] |
| big_cluster, normal | 0-60 | zhu | -0.22 [-0.23, -0.21] |
| big_cluster, normal | 0-60 | jusup | -0.65 [-0.69, -0.61] |
| big_cluster, normal | 60-120 | foodmatch | +0.80 [+0.73, +0.88] |
| big_cluster, normal | 60-120 | forecast | -0.25 [-0.26, -0.23] |
| big_cluster, normal | 60-120 | backpressure | -0.38 [-0.40, -0.36] |
| big_cluster, normal | 60-120 | xu | +3.36 [+3.28, +3.45] |
| big_cluster, normal | 60-120 | li | -0.28 [-0.32, -0.24] |
| big_cluster, normal | 60-120 | jahanshahi | -0.00 [-0.02, +0.01] |
| big_cluster, normal | 60-120 | auad | -0.01 [-0.06, +0.05] |
| big_cluster, normal | 60-120 | zhu | +0.30 [+0.27, +0.33] |
| big_cluster, normal | 60-120 | jusup | +4.76 [+4.62, +4.89] |
| big_cluster, normal | 180-240 | foodmatch | -0.10 [-0.13, -0.06] |
| big_cluster, normal | 180-240 | forecast | +0.40 [+0.37, +0.42] |
| big_cluster, normal | 180-240 | backpressure | -0.96 [-0.99, -0.93] |
| big_cluster, normal | 180-240 | xu | -4.55 [-4.61, -4.50] |
| big_cluster, normal | 180-240 | li | -1.24 [-1.27, -1.20] |
| big_cluster, normal | 180-240 | jahanshahi | -0.06 [-0.08, -0.03] |
| big_cluster, normal | 180-240 | auad | -0.04 [-0.07, -0.01] |
| big_cluster, normal | 180-240 | zhu | -5.19 [-5.28, -5.10] |
| big_cluster, normal | 180-240 | jusup | -5.44 [-5.53, -5.34] |
| big_cluster, loose | 0-60 | foodmatch | +0.10 [+0.10, +0.11] |
| big_cluster, loose | 0-60 | forecast | +0.02 [+0.02, +0.02] |
| big_cluster, loose | 0-60 | backpressure | -0.06 [-0.06, -0.05] |
| big_cluster, loose | 0-60 | xu | +0.25 [+0.24, +0.25] |
| big_cluster, loose | 0-60 | li | -0.08 [-0.09, -0.08] |
| big_cluster, loose | 0-60 | jahanshahi | -0.00 [-0.00, -0.00] |
| big_cluster, loose | 0-60 | auad | +0.04 [+0.04, +0.05] |
| big_cluster, loose | 0-60 | zhu | -0.13 [-0.14, -0.12] |
| big_cluster, loose | 0-60 | jusup | -1.96 [-1.99, -1.93] |
| big_cluster, loose | 60-120 | foodmatch | -0.79 [-0.83, -0.75] |
| big_cluster, loose | 60-120 | forecast | +0.27 [+0.26, +0.28] |
| big_cluster, loose | 60-120 | backpressure | -0.41 [-0.42, -0.39] |
| big_cluster, loose | 60-120 | xu | +3.66 [+3.61, +3.72] |
| big_cluster, loose | 60-120 | li | -0.57 [-0.59, -0.55] |
| big_cluster, loose | 60-120 | jahanshahi | -0.06 [-0.07, -0.05] |
| big_cluster, loose | 60-120 | auad | +0.56 [+0.48, +0.65] |
| big_cluster, loose | 60-120 | zhu | -0.72 [-0.74, -0.70] |
| big_cluster, loose | 60-120 | jusup | +2.41 [+2.32, +2.50] |
| big_cluster, loose | 180-240 | foodmatch | -0.63 [-0.66, -0.61] |
| big_cluster, loose | 180-240 | forecast | +0.36 [+0.34, +0.38] |
| big_cluster, loose | 180-240 | backpressure | -0.91 [-0.93, -0.89] |
| big_cluster, loose | 180-240 | xu | -3.87 [-3.92, -3.83] |
| big_cluster, loose | 180-240 | li | -1.31 [-1.34, -1.29] |
| big_cluster, loose | 180-240 | jahanshahi | -0.06 [-0.08, -0.05] |
| big_cluster, loose | 180-240 | auad | +0.00 [-0.02, +0.03] |
| big_cluster, loose | 180-240 | zhu | -11.86 [-11.90, -11.81] |
| big_cluster, loose | 180-240 | jusup | -7.96 [-8.02, -7.89] |
| three_clusters, tight | 0-60 | foodmatch | -1.20 [-1.23, -1.18] |
| three_clusters, tight | 0-60 | forecast | -0.04 [-0.05, -0.04] |
| three_clusters, tight | 0-60 | backpressure | -0.06 [-0.06, -0.05] |
| three_clusters, tight | 0-60 | xu | -0.07 [-0.14, +0.01] |
| three_clusters, tight | 0-60 | li | -0.03 [-0.04, -0.02] |
| three_clusters, tight | 0-60 | jahanshahi | -0.00 [-0.00, +0.00] |
| three_clusters, tight | 0-60 | auad | -0.08 [-0.11, -0.05] |
| three_clusters, tight | 0-60 | zhu | -0.12 [-0.13, -0.10] |
| three_clusters, tight | 0-60 | jusup | -0.80 [-0.86, -0.74] |
| three_clusters, tight | 60-120 | foodmatch | -0.24 [-0.27, -0.22] |
| three_clusters, tight | 60-120 | forecast | -0.00 [-0.01, +0.01] |
| three_clusters, tight | 60-120 | backpressure | +0.00 [-0.01, +0.02] |
| three_clusters, tight | 60-120 | xu | +3.67 [+3.58, +3.75] |
| three_clusters, tight | 60-120 | li | +0.33 [+0.30, +0.35] |
| three_clusters, tight | 60-120 | jahanshahi | -0.00 [-0.01, +0.01] |
| three_clusters, tight | 60-120 | auad | +0.01 [-0.01, +0.04] |
| three_clusters, tight | 60-120 | zhu | +0.01 [-0.01, +0.03] |
| three_clusters, tight | 60-120 | jusup | +0.54 [+0.48, +0.61] |
| three_clusters, tight | 180-240 | foodmatch | +3.30 [+3.22, +3.37] |
| three_clusters, tight | 180-240 | forecast | -0.21 [-0.24, -0.17] |
| three_clusters, tight | 180-240 | backpressure | -0.14 [-0.17, -0.11] |
| three_clusters, tight | 180-240 | xu | +0.54 [+0.47, +0.61] |
| three_clusters, tight | 180-240 | li | +1.04 [+0.97, +1.11] |
| three_clusters, tight | 180-240 | jahanshahi | +0.02 [-0.02, +0.05] |
| three_clusters, tight | 180-240 | auad | +0.72 [+0.62, +0.84] |
| three_clusters, tight | 180-240 | zhu | +0.29 [+0.25, +0.34] |
| three_clusters, tight | 180-240 | jusup | +0.72 [+0.67, +0.76] |
| three_clusters, normal | 0-60 | foodmatch | -1.03 [-1.05, -1.01] |
| three_clusters, normal | 0-60 | forecast | -0.02 [-0.03, -0.02] |
| three_clusters, normal | 0-60 | backpressure | -0.10 [-0.10, -0.09] |
| three_clusters, normal | 0-60 | xu | -1.45 [-1.48, -1.42] |
| three_clusters, normal | 0-60 | li | -0.22 [-0.23, -0.21] |
| three_clusters, normal | 0-60 | jahanshahi | -0.01 [-0.01, -0.01] |
| three_clusters, normal | 0-60 | auad | -0.18 [-0.19, -0.17] |
| three_clusters, normal | 0-60 | zhu | -0.15 [-0.17, -0.14] |
| three_clusters, normal | 0-60 | jusup | -2.65 [-2.69, -2.62] |
| three_clusters, normal | 60-120 | foodmatch | -1.98 [-2.07, -1.89] |
| three_clusters, normal | 60-120 | forecast | -0.18 [-0.20, -0.15] |
| three_clusters, normal | 60-120 | backpressure | +0.01 [-0.03, +0.04] |
| three_clusters, normal | 60-120 | xu | +0.21 [+0.02, +0.42] |
| three_clusters, normal | 60-120 | li | +0.62 [+0.54, +0.70] |
| three_clusters, normal | 60-120 | jahanshahi | +0.02 [+0.00, +0.05] |
| three_clusters, normal | 60-120 | auad | -0.09 [-0.13, -0.04] |
| three_clusters, normal | 60-120 | zhu | +0.35 [+0.30, +0.40] |
| three_clusters, normal | 60-120 | jusup | +3.12 [+2.92, +3.32] |
| three_clusters, normal | 180-240 | foodmatch | +1.89 [+1.83, +1.95] |
| three_clusters, normal | 180-240 | forecast | -0.11 [-0.15, -0.08] |
| three_clusters, normal | 180-240 | backpressure | -0.31 [-0.35, -0.26] |
| three_clusters, normal | 180-240 | xu | +0.18 [+0.11, +0.26] |
| three_clusters, normal | 180-240 | li | -0.19 [-0.25, -0.14] |
| three_clusters, normal | 180-240 | jahanshahi | -0.03 [-0.06, -0.00] |
| three_clusters, normal | 180-240 | auad | +0.60 [+0.54, +0.66] |
| three_clusters, normal | 180-240 | zhu | -3.67 [-3.74, -3.60] |
| three_clusters, normal | 180-240 | jusup | -0.52 [-0.59, -0.44] |
| three_clusters, loose | 0-60 | foodmatch | -0.81 [-0.83, -0.80] |
| three_clusters, loose | 0-60 | forecast | -0.02 [-0.02, -0.01] |
| three_clusters, loose | 0-60 | backpressure | -0.10 [-0.11, -0.09] |
| three_clusters, loose | 0-60 | xu | -1.11 [-1.13, -1.08] |
| three_clusters, loose | 0-60 | li | -0.22 [-0.23, -0.21] |
| three_clusters, loose | 0-60 | jahanshahi | -0.01 [-0.01, -0.01] |
| three_clusters, loose | 0-60 | auad | -0.16 [-0.17, -0.15] |
| three_clusters, loose | 0-60 | zhu | -0.06 [-0.07, -0.05] |
| three_clusters, loose | 0-60 | jusup | -2.98 [-3.02, -2.95] |
| three_clusters, loose | 60-120 | foodmatch | -1.82 [-1.86, -1.79] |
| three_clusters, loose | 60-120 | forecast | -0.03 [-0.05, -0.02] |
| three_clusters, loose | 60-120 | backpressure | -0.22 [-0.24, -0.21] |
| three_clusters, loose | 60-120 | xu | -2.26 [-2.32, -2.20] |
| three_clusters, loose | 60-120 | li | -0.77 [-0.80, -0.73] |
| three_clusters, loose | 60-120 | jahanshahi | -0.06 [-0.07, -0.05] |
| three_clusters, loose | 60-120 | auad | -0.20 [-0.22, -0.17] |
| three_clusters, loose | 60-120 | zhu | -0.78 [-0.81, -0.76] |
| three_clusters, loose | 60-120 | jusup | -2.98 [-3.04, -2.91] |
| three_clusters, loose | 180-240 | foodmatch | -0.06 [-0.09, -0.04] |
| three_clusters, loose | 180-240 | forecast | -0.04 [-0.06, -0.02] |
| three_clusters, loose | 180-240 | backpressure | -0.36 [-0.38, -0.34] |
| three_clusters, loose | 180-240 | xu | -1.63 [-1.67, -1.60] |
| three_clusters, loose | 180-240 | li | -0.54 [-0.56, -0.51] |
| three_clusters, loose | 180-240 | jahanshahi | -0.04 [-0.06, -0.03] |
| three_clusters, loose | 180-240 | auad | +0.13 [+0.11, +0.16] |
| three_clusters, loose | 180-240 | zhu | -3.50 [-3.55, -3.46] |
| three_clusters, loose | 180-240 | jusup | -2.76 [-2.81, -2.71] |
| mixed, tight | 0-60 | foodmatch | -0.08 [-0.08, -0.07] |
| mixed, tight | 0-60 | forecast | +0.08 [+0.08, +0.09] |
| mixed, tight | 0-60 | backpressure | -0.08 [-0.09, -0.07] |
| mixed, tight | 0-60 | xu | -2.08 [-2.12, -2.05] |
| mixed, tight | 0-60 | li | -0.40 [-0.41, -0.39] |
| mixed, tight | 0-60 | jahanshahi | -0.02 [-0.02, -0.02] |
| mixed, tight | 0-60 | auad | +0.05 [+0.04, +0.06] |
| mixed, tight | 0-60 | zhu | -0.05 [-0.06, -0.03] |
| mixed, tight | 0-60 | jusup | -1.64 [-1.70, -1.59] |
| mixed, tight | 60-120 | foodmatch | -0.37 [-0.40, -0.34] |
| mixed, tight | 60-120 | forecast | -0.02 [-0.04, -0.01] |
| mixed, tight | 60-120 | backpressure | -0.02 [-0.03, -0.00] |
| mixed, tight | 60-120 | xu | +0.21 [+0.16, +0.26] |
| mixed, tight | 60-120 | li | +0.10 [+0.08, +0.12] |
| mixed, tight | 60-120 | jahanshahi | -0.01 [-0.02, +0.01] |
| mixed, tight | 60-120 | auad | +0.00 [-0.02, +0.02] |
| mixed, tight | 60-120 | zhu | -0.01 [-0.03, +0.00] |
| mixed, tight | 60-120 | jusup | +0.91 [+0.86, +0.95] |
| mixed, tight | 180-240 | foodmatch | +1.99 [+1.93, +2.05] |
| mixed, tight | 180-240 | forecast | -0.09 [-0.12, -0.06] |
| mixed, tight | 180-240 | backpressure | -0.23 [-0.26, -0.20] |
| mixed, tight | 180-240 | xu | +0.92 [+0.86, +0.97] |
| mixed, tight | 180-240 | li | +0.73 [+0.67, +0.79] |
| mixed, tight | 180-240 | jahanshahi | -0.04 [-0.07, -0.00] |
| mixed, tight | 180-240 | auad | +0.11 [+0.05, +0.17] |
| mixed, tight | 180-240 | zhu | +0.52 [+0.47, +0.58] |
| mixed, tight | 180-240 | jusup | +1.00 [+0.94, +1.06] |
| mixed, normal | 0-60 | foodmatch | +0.08 [+0.08, +0.09] |
| mixed, normal | 0-60 | forecast | +0.18 [+0.18, +0.19] |
| mixed, normal | 0-60 | backpressure | -0.10 [-0.10, -0.09] |
| mixed, normal | 0-60 | xu | -2.38 [-2.41, -2.36] |
| mixed, normal | 0-60 | li | -0.55 [-0.56, -0.54] |
| mixed, normal | 0-60 | jahanshahi | -0.03 [-0.03, -0.03] |
| mixed, normal | 0-60 | auad | +0.08 [+0.08, +0.08] |
| mixed, normal | 0-60 | zhu | -0.01 [-0.02, +0.00] |
| mixed, normal | 0-60 | jusup | -2.82 [-2.86, -2.78] |
| mixed, normal | 60-120 | foodmatch | -0.23 [-0.27, -0.20] |
| mixed, normal | 60-120 | forecast | -0.09 [-0.11, -0.08] |
| mixed, normal | 60-120 | backpressure | -0.17 [-0.20, -0.14] |
| mixed, normal | 60-120 | xu | +0.33 [+0.24, +0.42] |
| mixed, normal | 60-120 | li | -0.25 [-0.29, -0.21] |
| mixed, normal | 60-120 | jahanshahi | -0.01 [-0.02, +0.01] |
| mixed, normal | 60-120 | auad | -0.13 [-0.16, -0.10] |
| mixed, normal | 60-120 | zhu | -0.16 [-0.19, -0.14] |
| mixed, normal | 60-120 | jusup | +1.93 [+1.80, +2.07] |
| mixed, normal | 180-240 | foodmatch | +0.69 [+0.66, +0.73] |
| mixed, normal | 180-240 | forecast | +0.69 [+0.65, +0.72] |
| mixed, normal | 180-240 | backpressure | -0.69 [-0.72, -0.66] |
| mixed, normal | 180-240 | xu | +0.68 [+0.64, +0.73] |
| mixed, normal | 180-240 | li | -1.02 [-1.06, -0.98] |
| mixed, normal | 180-240 | jahanshahi | -0.05 [-0.08, -0.02] |
| mixed, normal | 180-240 | auad | -0.11 [-0.15, -0.07] |
| mixed, normal | 180-240 | zhu | -2.74 [-2.87, -2.61] |
| mixed, normal | 180-240 | jusup | -0.82 [-0.90, -0.75] |
| mixed, loose | 0-60 | foodmatch | +0.06 [+0.05, +0.06] |
| mixed, loose | 0-60 | forecast | +0.26 [+0.26, +0.27] |
| mixed, loose | 0-60 | backpressure | -0.12 [-0.12, -0.11] |
| mixed, loose | 0-60 | xu | -1.77 [-1.79, -1.75] |
| mixed, loose | 0-60 | li | -0.50 [-0.51, -0.49] |
| mixed, loose | 0-60 | jahanshahi | -0.03 [-0.03, -0.03] |
| mixed, loose | 0-60 | auad | +0.07 [+0.06, +0.07] |
| mixed, loose | 0-60 | zhu | +0.02 [+0.01, +0.03] |
| mixed, loose | 0-60 | jusup | -2.81 [-2.84, -2.78] |
| mixed, loose | 60-120 | foodmatch | +0.14 [+0.13, +0.16] |
| mixed, loose | 60-120 | forecast | +0.36 [+0.35, +0.38] |
| mixed, loose | 60-120 | backpressure | -0.24 [-0.25, -0.22] |
| mixed, loose | 60-120 | xu | -2.40 [-2.46, -2.35] |
| mixed, loose | 60-120 | li | -1.82 [-1.85, -1.79] |
| mixed, loose | 60-120 | jahanshahi | -0.13 [-0.14, -0.12] |
| mixed, loose | 60-120 | auad | +0.25 [+0.23, +0.26] |
| mixed, loose | 60-120 | zhu | -0.39 [-0.40, -0.37] |
| mixed, loose | 60-120 | jusup | -3.69 [-3.77, -3.60] |
| mixed, loose | 180-240 | foodmatch | +0.13 [+0.10, +0.15] |
| mixed, loose | 180-240 | forecast | +0.57 [+0.55, +0.59] |
| mixed, loose | 180-240 | backpressure | -0.38 [-0.40, -0.36] |
| mixed, loose | 180-240 | xu | -0.31 [-0.35, -0.27] |
| mixed, loose | 180-240 | li | -1.16 [-1.19, -1.13] |
| mixed, loose | 180-240 | jahanshahi | -0.04 [-0.06, -0.03] |
| mixed, loose | 180-240 | auad | -0.06 [-0.08, -0.04] |
| mixed, loose | 180-240 | zhu | -3.95 [-4.00, -3.90] |
| mixed, loose | 180-240 | jusup | -2.74 [-2.80, -2.68] |
| meetup, normal | 0-60 | foodmatch | +0.05 [+0.02, +0.07] |
| meetup, normal | 0-60 | forecast | -0.43 [-0.47, -0.40] |
| meetup, normal | 0-60 | backpressure | -0.14 [-0.17, -0.11] |
| meetup, normal | 0-60 | xu | -2.99 [-3.16, -2.82] |
| meetup, normal | 0-60 | li | -0.49 [-0.53, -0.46] |
| meetup, normal | 0-60 | jahanshahi | -0.04 [-0.06, -0.02] |
| meetup, normal | 0-60 | auad | +0.00 [-0.02, +0.03] |
| meetup, normal | 0-60 | zhu | +1.39 [+1.36, +1.43] |
| meetup, normal | 0-60 | jusup | +2.36 [+2.31, +2.40] |
| meetup, normal | 60-120 | foodmatch | +0.08 [+0.06, +0.11] |
| meetup, normal | 60-120 | forecast | -0.34 [-0.37, -0.31] |
| meetup, normal | 60-120 | backpressure | -0.26 [-0.29, -0.23] |
| meetup, normal | 60-120 | xu | -3.38 [-3.44, -3.32] |
| meetup, normal | 60-120 | li | -0.68 [-0.71, -0.65] |
| meetup, normal | 60-120 | jahanshahi | -0.07 [-0.09, -0.04] |
| meetup, normal | 60-120 | auad | +0.03 [+0.01, +0.06] |
| meetup, normal | 60-120 | zhu | +2.31 [+2.27, +2.35] |
| meetup, normal | 60-120 | jusup | +3.23 [+3.18, +3.28] |

## Q1 W1 without 20:30 to 21:00

| cell | model | full evening | without 20:30-21:00 |
|---|---|---|---|
| scattered, tight | foodmatch | +0.06 [+0.05, +0.07] | +0.02 [+0.01, +0.04] |
| scattered, tight | forecast | -0.41 [-0.43, -0.40] | -0.39 [-0.41, -0.38] |
| scattered, tight | backpressure | -0.20 [-0.21, -0.18] | -0.22 [-0.23, -0.20] |
| scattered, tight | xu | -0.68 [-0.72, -0.64] | -0.69 [-0.73, -0.65] |
| scattered, tight | li | -0.31 [-0.33, -0.29] | -0.31 [-0.33, -0.29] |
| scattered, tight | jahanshahi | -0.03 [-0.04, -0.02] | -0.03 [-0.04, -0.02] |
| scattered, tight | auad | -0.07 [-0.09, -0.06] | -0.10 [-0.11, -0.08] |
| scattered, tight | zhu | +0.70 [+0.67, +0.72] | +0.39 [+0.37, +0.42] |
| scattered, tight | jusup | +1.16 [+1.11, +1.21] | +0.84 [+0.80, +0.89] |
| scattered, normal | foodmatch | +0.09 [+0.08, +0.10] | +0.07 [+0.06, +0.08] |
| scattered, normal | forecast | -0.69 [-0.71, -0.67] | -0.69 [-0.70, -0.67] |
| scattered, normal | backpressure | -0.29 [-0.31, -0.28] | -0.28 [-0.30, -0.27] |
| scattered, normal | xu | +0.22 [+0.18, +0.26] | +0.29 [+0.25, +0.34] |
| scattered, normal | li | -0.68 [-0.70, -0.66] | -0.66 [-0.68, -0.64] |
| scattered, normal | jahanshahi | -0.07 [-0.08, -0.06] | -0.06 [-0.07, -0.05] |
| scattered, normal | auad | +0.09 [+0.08, +0.10] | +0.07 [+0.06, +0.08] |
| scattered, normal | zhu | +1.16 [+1.13, +1.18] | +0.85 [+0.83, +0.87] |
| scattered, normal | jusup | +2.01 [+1.98, +2.04] | +1.68 [+1.65, +1.71] |
| scattered, loose | foodmatch | +0.09 [+0.08, +0.10] | +0.08 [+0.07, +0.09] |
| scattered, loose | forecast | -0.57 [-0.58, -0.55] | -0.57 [-0.58, -0.55] |
| scattered, loose | backpressure | -0.46 [-0.47, -0.44] | -0.44 [-0.45, -0.43] |
| scattered, loose | xu | +0.67 [+0.64, +0.71] | +0.76 [+0.72, +0.79] |
| scattered, loose | li | -0.79 [-0.81, -0.78] | -0.76 [-0.77, -0.74] |
| scattered, loose | jahanshahi | -0.09 [-0.09, -0.08] | -0.08 [-0.09, -0.07] |
| scattered, loose | auad | +0.10 [+0.10, +0.11] | +0.09 [+0.09, +0.10] |
| scattered, loose | zhu | +0.95 [+0.93, +0.96] | +0.67 [+0.65, +0.69] |
| scattered, loose | jusup | +1.55 [+1.53, +1.58] | +1.27 [+1.24, +1.30] |
| burst, tight | foodmatch | -0.14 [-0.15, -0.12] | -0.13 [-0.15, -0.11] |
| burst, tight | forecast | -0.23 [-0.24, -0.21] | -0.19 [-0.20, -0.18] |
| burst, tight | backpressure | -0.15 [-0.17, -0.14] | -0.18 [-0.19, -0.17] |
| burst, tight | xu | -0.72 [-0.75, -0.70] | -0.69 [-0.71, -0.66] |
| burst, tight | li | -0.39 [-0.41, -0.37] | -0.35 [-0.38, -0.33] |
| burst, tight | jahanshahi | -0.01 [-0.02, +0.00] | -0.01 [-0.02, -0.00] |
| burst, tight | auad | -0.12 [-0.13, -0.11] | -0.10 [-0.11, -0.09] |
| burst, tight | zhu | +0.20 [+0.18, +0.22] | -0.04 [-0.05, -0.02] |
| burst, tight | jusup | +0.47 [+0.45, +0.49] | +0.21 [+0.20, +0.23] |
| burst, normal | foodmatch | +0.06 [+0.05, +0.07] | +0.04 [+0.03, +0.05] |
| burst, normal | forecast | -0.57 [-0.58, -0.56] | -0.56 [-0.58, -0.55] |
| burst, normal | backpressure | -0.27 [-0.29, -0.26] | -0.26 [-0.28, -0.25] |
| burst, normal | xu | -0.22 [-0.26, -0.18] | -0.20 [-0.24, -0.16] |
| burst, normal | li | -0.63 [-0.65, -0.61] | -0.61 [-0.62, -0.59] |
| burst, normal | jahanshahi | -0.07 [-0.08, -0.06] | -0.06 [-0.07, -0.05] |
| burst, normal | auad | +0.07 [+0.06, +0.09] | +0.05 [+0.04, +0.07] |
| burst, normal | zhu | +1.23 [+1.21, +1.26] | +0.93 [+0.90, +0.95] |
| burst, normal | jusup | +2.05 [+2.02, +2.08] | +1.75 [+1.72, +1.78] |
| burst, loose | foodmatch | +0.08 [+0.07, +0.09] | +0.07 [+0.06, +0.08] |
| burst, loose | forecast | -0.54 [-0.55, -0.53] | -0.53 [-0.55, -0.52] |
| burst, loose | backpressure | -0.42 [-0.43, -0.41] | -0.40 [-0.42, -0.39] |
| burst, loose | xu | +0.44 [+0.41, +0.47] | +0.50 [+0.46, +0.53] |
| burst, loose | li | -0.76 [-0.78, -0.75] | -0.72 [-0.74, -0.71] |
| burst, loose | jahanshahi | -0.07 [-0.08, -0.06] | -0.06 [-0.07, -0.06] |
| burst, loose | auad | +0.09 [+0.08, +0.10] | +0.08 [+0.07, +0.09] |
| burst, loose | zhu | +1.09 [+1.07, +1.11] | +0.81 [+0.80, +0.83] |
| burst, loose | jusup | +1.73 [+1.70, +1.76] | +1.45 [+1.43, +1.48] |

## Per training policy: range of the five policy means of each E1 and E2 contrast

Every policy mean with its interval: `c5_per_policy.csv`.

| family | model | scenario | level | metric | min | max |
|---|---|---|---|---|---|---|
| E1 | auad | burst | loose | p90_c2d_min | 0.347 | 0.370 |
| E1 | auad | burst | loose | w1_rule_min | 0.080 | 0.118 |
| E1 | auad | burst | normal | p90_c2d_min | 0.424 | 0.449 |
| E1 | auad | burst | normal | w1_rule_min | 0.055 | 0.100 |
| E1 | auad | burst | tight | p90_c2d_min | -1.651 | 1.025 |
| E1 | auad | burst | tight | w1_rule_min | -0.161 | -0.100 |
| E1 | auad | scattered | loose | p90_c2d_min | 0.332 | 0.350 |
| E1 | auad | scattered | loose | w1_rule_min | 0.094 | 0.112 |
| E1 | auad | scattered | normal | p90_c2d_min | 0.401 | 0.437 |
| E1 | auad | scattered | normal | w1_rule_min | 0.074 | 0.113 |
| E1 | auad | scattered | tight | p90_c2d_min | 0.506 | 0.835 |
| E1 | auad | scattered | tight | w1_rule_min | -0.084 | -0.051 |
| E1 | jusup | burst | loose | p90_c2d_min | 0.002 | 0.020 |
| E1 | jusup | burst | loose | w1_rule_min | 1.585 | 1.834 |
| E1 | jusup | burst | normal | p90_c2d_min | 0.042 | 0.095 |
| E1 | jusup | burst | normal | w1_rule_min | 1.962 | 2.169 |
| E1 | jusup | burst | tight | p90_c2d_min | 0.058 | 0.329 |
| E1 | jusup | burst | tight | w1_rule_min | 0.448 | 0.496 |
| E1 | jusup | scattered | loose | p90_c2d_min | -0.010 | 0.008 |
| E1 | jusup | scattered | loose | w1_rule_min | 1.367 | 1.665 |
| E1 | jusup | scattered | normal | p90_c2d_min | 0.031 | 0.062 |
| E1 | jusup | scattered | normal | w1_rule_min | 1.891 | 2.171 |
| E1 | jusup | scattered | tight | p90_c2d_min | 0.039 | 0.246 |
| E1 | jusup | scattered | tight | w1_rule_min | 1.106 | 1.218 |
| E1 | li | burst | loose | p90_c2d_min | 0.499 | 0.533 |
| E1 | li | burst | loose | w1_rule_min | -0.801 | -0.712 |
| E1 | li | burst | normal | p90_c2d_min | 0.379 | 0.412 |
| E1 | li | burst | normal | w1_rule_min | -0.692 | -0.575 |
| E1 | li | burst | tight | p90_c2d_min | -5.118 | -4.508 |
| E1 | li | burst | tight | w1_rule_min | -0.436 | -0.365 |
| E1 | li | scattered | loose | p90_c2d_min | 0.515 | 0.552 |
| E1 | li | scattered | loose | w1_rule_min | -0.860 | -0.746 |
| E1 | li | scattered | normal | p90_c2d_min | 0.452 | 0.479 |
| E1 | li | scattered | normal | w1_rule_min | -0.750 | -0.624 |
| E1 | li | scattered | tight | p90_c2d_min | -0.316 | -0.029 |
| E1 | li | scattered | tight | w1_rule_min | -0.336 | -0.274 |
| E1 | xu | burst | loose | p90_c2d_min | 3.339 | 3.411 |
| E1 | xu | burst | loose | w1_rule_min | 0.395 | 0.481 |
| E1 | xu | burst | normal | p90_c2d_min | 3.245 | 3.312 |
| E1 | xu | burst | normal | w1_rule_min | -0.280 | -0.138 |
| E1 | xu | burst | tight | p90_c2d_min | -4.929 | -4.347 |
| E1 | xu | burst | tight | w1_rule_min | -0.751 | -0.685 |
| E1 | xu | scattered | loose | p90_c2d_min | 3.186 | 3.242 |
| E1 | xu | scattered | loose | w1_rule_min | 0.622 | 0.745 |
| E1 | xu | scattered | normal | p90_c2d_min | 3.130 | 3.212 |
| E1 | xu | scattered | normal | w1_rule_min | 0.140 | 0.271 |
| E1 | xu | scattered | tight | p90_c2d_min | 1.710 | 2.171 |
| E1 | xu | scattered | tight | w1_rule_min | -0.741 | -0.640 |
| E2 | auad | big_cluster | loose | p90_c2d_min | 0.566 | 1.302 |
| E2 | auad | big_cluster | loose | w1_rule_60min_after_min | 0.024 | 0.091 |
| E2 | auad | big_cluster | normal | p90_c2d_min | 0.771 | 1.131 |
| E2 | auad | big_cluster | normal | w1_rule_60min_after_min | 0.015 | 0.393 |
| E2 | auad | big_cluster | tight | p90_c2d_min | -6.229 | 1.363 |
| E2 | auad | big_cluster | tight | w1_rule_60min_after_min | 0.002 | 1.237 |
| E2 | auad | meetup | normal | p90_c2d_min | 0.417 | 0.456 |
| E2 | auad | meetup | normal | w1_rule_60min_after_min | -0.022 | 0.055 |
| E2 | auad | mixed | loose | p90_c2d_min | 0.527 | 0.608 |
| E2 | auad | mixed | loose | w1_rule_60min_after_min | 0.064 | 0.071 |
| E2 | auad | mixed | normal | p90_c2d_min | 0.636 | 0.823 |
| E2 | auad | mixed | normal | w1_rule_60min_after_min | 0.075 | 0.086 |
| E2 | auad | mixed | tight | p90_c2d_min | -4.128 | 1.488 |
| E2 | auad | mixed | tight | w1_rule_60min_after_min | 0.037 | 0.060 |
| E2 | auad | three_clusters | loose | p90_c2d_min | 0.360 | 0.401 |
| E2 | auad | three_clusters | loose | w1_rule_60min_after_min | -0.176 | -0.149 |
| E2 | auad | three_clusters | normal | p90_c2d_min | -0.108 | 0.274 |
| E2 | auad | three_clusters | normal | w1_rule_60min_after_min | -0.193 | -0.171 |
| E2 | auad | three_clusters | tight | p90_c2d_min | -6.303 | 1.075 |
| E2 | auad | three_clusters | tight | w1_rule_60min_after_min | -0.206 | 0.240 |
| E2 | jusup | big_cluster | loose | p90_c2d_min | -3.154 | -2.854 |
| E2 | jusup | big_cluster | loose | w1_rule_60min_after_min | -2.065 | -1.816 |
| E2 | jusup | big_cluster | normal | p90_c2d_min | -2.458 | -2.076 |
| E2 | jusup | big_cluster | normal | w1_rule_60min_after_min | -0.810 | -0.450 |
| E2 | jusup | big_cluster | tight | p90_c2d_min | -1.826 | -1.461 |
| E2 | jusup | big_cluster | tight | w1_rule_60min_after_min | 0.344 | 0.546 |
| E2 | jusup | meetup | normal | p90_c2d_min | 0.033 | 0.065 |
| E2 | jusup | meetup | normal | w1_rule_60min_after_min | 2.272 | 2.455 |
| E2 | jusup | mixed | loose | p90_c2d_min | -0.708 | -0.612 |
| E2 | jusup | mixed | loose | w1_rule_60min_after_min | -2.944 | -2.609 |
| E2 | jusup | mixed | normal | p90_c2d_min | -1.585 | -1.471 |
| E2 | jusup | mixed | normal | w1_rule_60min_after_min | -3.002 | -2.683 |
| E2 | jusup | mixed | tight | p90_c2d_min | -2.485 | -1.739 |
| E2 | jusup | mixed | tight | w1_rule_60min_after_min | -1.849 | -1.502 |
| E2 | jusup | three_clusters | loose | p90_c2d_min | -2.366 | -2.152 |
| E2 | jusup | three_clusters | loose | w1_rule_60min_after_min | -3.261 | -2.853 |
| E2 | jusup | three_clusters | normal | p90_c2d_min | -3.445 | -3.249 |
| E2 | jusup | three_clusters | normal | w1_rule_60min_after_min | -2.908 | -2.479 |
| E2 | jusup | three_clusters | tight | p90_c2d_min | -3.435 | -2.834 |
| E2 | jusup | three_clusters | tight | w1_rule_60min_after_min | -0.974 | -0.561 |
| E2 | li | big_cluster | loose | p90_c2d_min | -0.024 | 0.014 |
| E2 | li | big_cluster | loose | w1_rule_60min_after_min | -0.091 | -0.076 |
| E2 | li | big_cluster | normal | p90_c2d_min | -0.480 | -0.225 |
| E2 | li | big_cluster | normal | w1_rule_60min_after_min | -0.124 | -0.116 |
| E2 | li | big_cluster | tight | p90_c2d_min | -10.254 | -9.179 |
| E2 | li | big_cluster | tight | w1_rule_60min_after_min | -0.075 | -0.059 |
| E2 | li | meetup | normal | p90_c2d_min | 0.448 | 0.479 |
| E2 | li | meetup | normal | w1_rule_60min_after_min | -0.549 | -0.409 |
| E2 | li | mixed | loose | p90_c2d_min | -0.078 | -0.048 |
| E2 | li | mixed | loose | w1_rule_60min_after_min | -0.526 | -0.463 |
| E2 | li | mixed | normal | p90_c2d_min | -0.568 | -0.435 |
| E2 | li | mixed | normal | w1_rule_60min_after_min | -0.566 | -0.527 |
| E2 | li | mixed | tight | p90_c2d_min | -9.080 | -8.788 |
| E2 | li | mixed | tight | w1_rule_60min_after_min | -0.423 | -0.387 |
| E2 | li | three_clusters | loose | p90_c2d_min | -0.403 | -0.294 |
| E2 | li | three_clusters | loose | w1_rule_60min_after_min | -0.226 | -0.210 |
| E2 | li | three_clusters | normal | p90_c2d_min | -0.914 | -0.650 |
| E2 | li | three_clusters | normal | w1_rule_60min_after_min | -0.224 | -0.208 |
| E2 | li | three_clusters | tight | p90_c2d_min | -10.323 | -9.793 |
| E2 | li | three_clusters | tight | w1_rule_60min_after_min | -0.063 | 0.016 |
| E2 | xu | big_cluster | loose | p90_c2d_min | 12.024 | 14.199 |
| E2 | xu | big_cluster | loose | w1_rule_60min_after_min | 0.216 | 0.266 |
| E2 | xu | big_cluster | normal | p90_c2d_min | 12.018 | 14.758 |
| E2 | xu | big_cluster | normal | w1_rule_60min_after_min | 0.884 | 0.922 |
| E2 | xu | big_cluster | tight | p90_c2d_min | 1.812 | 3.972 |
| E2 | xu | big_cluster | tight | w1_rule_60min_after_min | 3.303 | 3.395 |
| E2 | xu | meetup | normal | p90_c2d_min | 3.790 | 3.977 |
| E2 | xu | meetup | normal | w1_rule_60min_after_min | -3.950 | -1.119 |
| E2 | xu | mixed | loose | p90_c2d_min | 2.337 | 2.495 |
| E2 | xu | mixed | loose | w1_rule_60min_after_min | -1.925 | -1.676 |
| E2 | xu | mixed | normal | p90_c2d_min | 0.641 | 0.765 |
| E2 | xu | mixed | normal | w1_rule_60min_after_min | -2.563 | -2.266 |
| E2 | xu | mixed | tight | p90_c2d_min | -10.973 | -10.738 |
| E2 | xu | mixed | tight | w1_rule_60min_after_min | -2.290 | -1.971 |
| E2 | xu | three_clusters | loose | p90_c2d_min | 3.477 | 3.782 |
| E2 | xu | three_clusters | loose | w1_rule_60min_after_min | -1.173 | -0.915 |
| E2 | xu | three_clusters | normal | p90_c2d_min | 1.298 | 1.802 |
| E2 | xu | three_clusters | normal | w1_rule_60min_after_min | -1.561 | -1.215 |
| E2 | xu | three_clusters | tight | p90_c2d_min | -10.248 | -9.559 |
| E2 | xu | three_clusters | tight | w1_rule_60min_after_min | -0.343 | 0.193 |

## W1 over 20:00 to 20:59 by return probability (clustered starts)

| behavior | cell | model | difference [95% CI] |
|---|---|---|---|
| p0 | big_cluster, tight | zhu | -0.04 [-0.08, -0.00] |
| p0 | big_cluster, tight | jusup | +0.33 [+0.29, +0.37] |
| p0 | big_cluster, tight | xu | +1.85 [+1.75, +1.96] |
| p0 | big_cluster, normal | zhu | -0.38 [-0.41, -0.35] |
| p0 | big_cluster, normal | jusup | -0.62 [-0.68, -0.57] |
| p0 | big_cluster, normal | xu | +0.24 [+0.15, +0.33] |
| p0 | big_cluster, loose | zhu | -0.29 [-0.31, -0.27] |
| p0 | big_cluster, loose | jusup | +3.61 [+3.56, +3.67] |
| p0 | big_cluster, loose | xu | +1.95 [+1.91, +1.99] |
| p0 | three_clusters, tight | zhu | -0.08 [-0.12, -0.04] |
| p0 | three_clusters, tight | jusup | +0.34 [+0.30, +0.38] |
| p0 | three_clusters, tight | xu | -0.86 [-0.92, -0.79] |
| p0 | three_clusters, normal | zhu | -0.05 [-0.08, -0.02] |
| p0 | three_clusters, normal | jusup | +3.10 [+3.04, +3.16] |
| p0 | three_clusters, normal | xu | +1.15 [+1.07, +1.23] |
| p0 | three_clusters, loose | zhu | -0.42 [-0.45, -0.40] |
| p0 | three_clusters, loose | jusup | +0.32 [+0.25, +0.39] |
| p0 | three_clusters, loose | xu | -0.43 [-0.49, -0.37] |
| p0 | mixed, tight | zhu | -0.05 [-0.09, -0.01] |
| p0 | mixed, tight | jusup | +0.42 [+0.39, +0.46] |
| p0 | mixed, tight | xu | -0.54 [-0.62, -0.47] |
| p0 | mixed, normal | zhu | -0.14 [-0.16, -0.11] |
| p0 | mixed, normal | jusup | +1.78 [+1.66, +1.89] |
| p0 | mixed, normal | xu | +0.41 [+0.28, +0.55] |
| p0 | mixed, loose | zhu | -0.40 [-0.43, -0.38] |
| p0 | mixed, loose | jusup | +0.81 [+0.73, +0.90] |
| p0 | mixed, loose | xu | +1.01 [+0.93, +1.09] |
| fitted | big_cluster, tight | zhu | -0.00 [-0.07, +0.06] |
| fitted | big_cluster, tight | jusup | +0.37 [+0.31, +0.43] |
| fitted | big_cluster, tight | xu | +1.75 [+1.68, +1.82] |
| fitted | big_cluster, normal | zhu | -5.19 [-5.28, -5.10] |
| fitted | big_cluster, normal | jusup | -5.44 [-5.53, -5.34] |
| fitted | big_cluster, normal | xu | -4.55 [-4.61, -4.50] |
| fitted | big_cluster, loose | zhu | -11.86 [-11.90, -11.81] |
| fitted | big_cluster, loose | jusup | -7.96 [-8.02, -7.89] |
| fitted | big_cluster, loose | xu | -3.87 [-3.92, -3.83] |
| fitted | three_clusters, tight | zhu | +0.29 [+0.25, +0.34] |
| fitted | three_clusters, tight | jusup | +0.72 [+0.67, +0.76] |
| fitted | three_clusters, tight | xu | +0.54 [+0.47, +0.61] |
| fitted | three_clusters, normal | zhu | -3.67 [-3.74, -3.60] |
| fitted | three_clusters, normal | jusup | -0.52 [-0.59, -0.44] |
| fitted | three_clusters, normal | xu | +0.18 [+0.11, +0.26] |
| fitted | three_clusters, loose | zhu | -3.50 [-3.55, -3.46] |
| fitted | three_clusters, loose | jusup | -2.76 [-2.81, -2.71] |
| fitted | three_clusters, loose | xu | -1.63 [-1.67, -1.60] |
| fitted | mixed, tight | zhu | +0.52 [+0.47, +0.58] |
| fitted | mixed, tight | jusup | +1.00 [+0.94, +1.06] |
| fitted | mixed, tight | xu | +0.92 [+0.86, +0.97] |
| fitted | mixed, normal | zhu | -2.74 [-2.87, -2.61] |
| fitted | mixed, normal | jusup | -0.82 [-0.90, -0.75] |
| fitted | mixed, normal | xu | +0.68 [+0.64, +0.73] |
| fitted | mixed, loose | zhu | -3.95 [-4.00, -3.90] |
| fitted | mixed, loose | jusup | -2.74 [-2.80, -2.68] |
| fitted | mixed, loose | xu | -0.31 [-0.35, -0.27] |
| p1 | big_cluster, tight | zhu | -0.39 [-0.47, -0.32] |
| p1 | big_cluster, tight | jusup | -0.02 [-0.09, +0.04] |
| p1 | big_cluster, tight | xu | +3.22 [+3.17, +3.28] |
| p1 | big_cluster, normal | zhu | -6.63 [-6.71, -6.55] |
| p1 | big_cluster, normal | jusup | -6.88 [-6.96, -6.79] |
| p1 | big_cluster, normal | xu | -2.52 [-2.56, -2.49] |
| p1 | big_cluster, loose | zhu | -12.90 [-12.94, -12.85] |
| p1 | big_cluster, loose | jusup | -9.00 [-9.06, -8.93] |
| p1 | big_cluster, loose | xu | -2.01 [-2.03, -1.98] |
| p1 | three_clusters, tight | zhu | +0.12 [+0.08, +0.17] |
| p1 | three_clusters, tight | jusup | +0.55 [+0.50, +0.59] |
| p1 | three_clusters, tight | xu | +2.17 [+2.09, +2.24] |
| p1 | three_clusters, normal | zhu | -4.80 [-4.86, -4.74] |
| p1 | three_clusters, normal | jusup | -1.65 [-1.71, -1.58] |
| p1 | three_clusters, normal | xu | +0.66 [+0.59, +0.72] |
| p1 | three_clusters, loose | zhu | -3.92 [-3.97, -3.88] |
| p1 | three_clusters, loose | jusup | -3.18 [-3.23, -3.13] |
| p1 | three_clusters, loose | xu | -1.13 [-1.16, -1.10] |
| p1 | mixed, tight | zhu | +0.14 [+0.09, +0.20] |
| p1 | mixed, tight | jusup | +0.62 [+0.56, +0.68] |
| p1 | mixed, tight | xu | +2.31 [+2.25, +2.37] |
| p1 | mixed, normal | zhu | -4.47 [-4.60, -4.35] |
| p1 | mixed, normal | jusup | -2.56 [-2.63, -2.49] |
| p1 | mixed, normal | xu | +0.24 [+0.20, +0.28] |
| p1 | mixed, loose | zhu | -4.81 [-4.88, -4.75] |
| p1 | mixed, loose | jusup | -3.60 [-3.66, -3.54] |
| p1 | mixed, loose | xu | -0.37 [-0.40, -0.33] |

Nearest courier's own means: `c5_evening_by_return_nearest.csv`.

# C6, homes where customers live (exploratory, declared after E6 was seen)

## C6. Homes where customers live (exploratory, no test; declared after the E6 results were seen)

Setting `resid`: as `indep`, except that each courier's home cell is drawn in proportion to the expected drop-offs over 17:00 to 21:00 (the customer side of the demand model, which follows resident population), from its own stream keyed by (seed, 42, courier). The 9 clustered cells, ten models, arm C at 100%, seeds 1001 to 1030. Beside E6 (`indep`) and the fitted setting at the same seeds, each read with the E6 tables and Holm within its own 144 contrasts as a reading device. Differences are model minus nearest courier, in minutes; lower is better.

| setting | contrasts | established |
|---|---|---|
| resid | 144 | 135 |
| indep | 144 | 139 |
| fitted | 144 | 123 |

Classes (cells of 72):

| class | resid | indep | fitted |
|---|---|---|---|
| does not undo | 72 | 72 | 65 |
| undoes at no delivery cost | 0 | 0 | 6 |
| undoes at a delivery cost | 0 | 0 | 1 |

Cell-model pairs that undo under any of the three settings:

| cell | model | W1 60 min resid | class resid | W1 60 min indep | class indep | W1 60 min fitted | class fitted |
|---|---|---|---|---|---|---|---|
| mixed, tight | xu | -0.98 | does not undo | -1.23 | does not undo | -2.08 | undoes at no delivery cost |
| mixed, normal | xu | -0.94 | does not undo | -1.08 | does not undo | -2.40 | undoes at no delivery cost |
| mixed, loose | xu | -0.84 | does not undo | -0.91 | does not undo | -1.79 | undoes at a delivery cost |
| three_clusters, normal | jusup | +1.61 | does not undo | +1.72 | does not undo | -2.65 | undoes at no delivery cost |
| three_clusters, loose | jusup | +1.18 | does not undo | +1.36 | does not undo | -2.98 | undoes at no delivery cost |
| mixed, normal | jusup | +2.94 | does not undo | +2.58 | does not undo | -2.76 | undoes at no delivery cost |
| mixed, loose | jusup | +2.26 | does not undo | +1.93 | does not undo | -2.80 | undoes at no delivery cost |

### Nearest courier's own W1 over the first 60 min (min, mean over the seeds)

| scenario | level | resid | indep | fitted |
|---|---|---|---|---|
| big_cluster | tight | 16.89 | 17.06 | 18.51 |
| big_cluster | normal | 17.78 | 18.28 | 21.41 |
| big_cluster | loose | 17.09 | 17.55 | 22.27 |
| three_clusters | tight | 16.41 | 16.34 | 19.50 |
| three_clusters | normal | 16.20 | 16.08 | 20.46 |
| three_clusters | loose | 15.23 | 15.05 | 19.40 |
| mixed | tight | 11.19 | 11.60 | 16.12 |
| mixed | normal | 10.76 | 11.12 | 16.46 |
| mixed | loose | 10.33 | 10.66 | 15.38 |

### Time to undo and the second-hour check (pairs that undo under any setting, and nearest courier)

The time to undo is measured against the same model's scattered start under the fitted setting, for all three settings (as in E6); the second-hour check applies to the cells classed as undoing.

| setting | scenario | level | model | class | time_to_undo_median | censored_count | nearest_time_to_undo_median | second_hour_check |
|---|---|---|---|---|---|---|---|---|
| fitted | big_cluster | loose | nearest | nearest courier | 240.000 | 30 | 240.000 |  |
| indep | big_cluster | loose | nearest | nearest courier | 136.000 | 0 | 136.000 |  |
| resid | big_cluster | loose | nearest | nearest courier | 112.000 | 0 | 112.000 |  |
| fitted | big_cluster | normal | nearest | nearest courier | 74.000 | 0 | 74.000 |  |
| indep | big_cluster | normal | nearest | nearest courier | 93.000 | 0 | 93.000 |  |
| resid | big_cluster | normal | nearest | nearest courier | 90.000 | 0 | 90.000 |  |
| fitted | big_cluster | tight | nearest | nearest courier | 54.000 | 0 | 54.000 |  |
| indep | big_cluster | tight | nearest | nearest courier | 55.500 | 0 | 55.500 |  |
| resid | big_cluster | tight | nearest | nearest courier | 56.000 | 0 | 56.000 |  |
| fitted | mixed | loose | nearest | nearest courier | 240.000 | 30 | 240.000 |  |
| indep | mixed | loose | nearest | nearest courier | 74.000 | 0 | 74.000 |  |
| resid | mixed | loose | nearest | nearest courier | 68.000 | 0 | 68.000 |  |
| fitted | mixed | normal | nearest | nearest courier | 113.000 | 0 | 113.000 |  |
| indep | mixed | normal | nearest | nearest courier | 67.500 | 0 | 67.500 |  |
| resid | mixed | normal | nearest | nearest courier | 63.000 | 0 | 63.000 |  |
| fitted | mixed | tight | nearest | nearest courier | 64.000 | 0 | 64.000 |  |
| indep | mixed | tight | nearest | nearest courier | 61.500 | 0 | 61.500 |  |
| resid | mixed | tight | nearest | nearest courier | 57.500 | 0 | 57.500 |  |
| fitted | three_clusters | loose | nearest | nearest courier | 240.000 | 30 | 240.000 |  |
| indep | three_clusters | loose | nearest | nearest courier | 171.500 | 5 | 171.500 |  |
| resid | three_clusters | loose | nearest | nearest courier | 240.000 | 30 | 240.000 |  |
| fitted | three_clusters | normal | nearest | nearest courier | 240.000 | 17 | 240.000 |  |
| indep | three_clusters | normal | nearest | nearest courier | 137.000 | 0 | 137.000 |  |
| resid | three_clusters | normal | nearest | nearest courier | 146.500 | 10 | 146.500 |  |
| fitted | three_clusters | tight | nearest | nearest courier | 60.000 | 0 | 60.000 |  |
| indep | three_clusters | tight | nearest | nearest courier | 64.000 | 0 | 64.000 |  |
| resid | three_clusters | tight | nearest | nearest courier | 64.000 | 0 | 64.000 |  |
| fitted | mixed | loose | jusup | undoes at no delivery cost | 240.000 | 23 | 240.000 | holds after the first hour |
| indep | mixed | loose | jusup | does not undo | 240.000 | 23 | 74.000 |  |
| resid | mixed | loose | jusup | does not undo | 240.000 | 23 | 68.000 |  |
| fitted | mixed | normal | jusup | undoes at no delivery cost | 126.000 | 0 | 113.000 | undoes in the first hour, not after |
| indep | mixed | normal | jusup | does not undo | 126.000 | 0 | 67.500 |  |
| resid | mixed | normal | jusup | does not undo | 126.000 | 0 | 63.000 |  |
| fitted | three_clusters | loose | jusup | undoes at no delivery cost | 240.000 | 30 | 240.000 | holds after the first hour |
| indep | three_clusters | loose | jusup | does not undo | 240.000 | 30 | 171.500 |  |
| resid | three_clusters | loose | jusup | does not undo | 240.000 | 30 | 240.000 |  |
| fitted | three_clusters | normal | jusup | undoes at no delivery cost | 240.000 | 29 | 240.000 | undoes in the first hour, not after |
| indep | three_clusters | normal | jusup | does not undo | 240.000 | 29 | 137.000 |  |
| resid | three_clusters | normal | jusup | does not undo | 240.000 | 29 | 146.500 |  |
| fitted | mixed | loose | xu | undoes at a delivery cost | 240.000 | 30 | 240.000 | holds after the first hour |
| indep | mixed | loose | xu | does not undo | 60.000 | 0 | 74.000 |  |
| resid | mixed | loose | xu | does not undo | 55.500 | 0 | 68.000 |  |
| fitted | mixed | normal | xu | undoes at no delivery cost | 240.000 | 30 | 113.000 | undoes in the first hour, not after |
| indep | mixed | normal | xu | does not undo | 56.000 | 0 | 67.500 |  |
| resid | mixed | normal | xu | does not undo | 53.000 | 0 | 63.000 |  |
| fitted | mixed | tight | xu | undoes at no delivery cost | 86.000 | 0 | 64.000 | undoes in the first hour, not after |
| indep | mixed | tight | xu | does not undo | 53.500 | 0 | 61.500 |  |
| resid | mixed | tight | xu | does not undo | 52.000 | 0 | 57.500 |  |

### W1 over 20:00 to 20:59, model minus nearest courier, mean of the nine cells

| model | resid | indep | fitted |
|---|---|---|---|
| auad | -0.020 | 0.070 | 0.290 |
| backpressure | -0.160 | -0.230 | -0.480 |
| foodmatch | 0.000 | -0.010 | 1.240 |
| forecast | -0.570 | 0.080 | 0.150 |
| jahanshahi | -0.050 | -0.080 | -0.060 |
| jusup | 3.570 | 4.190 | -2.050 |
| li | -0.530 | -0.700 | 0.070 |
| xu | -0.550 | 0.120 | -0.710 |
| zhu | 2.240 | 2.860 | -3.370 |

The DQN row is descriptive.

Every number per cell: `c6_resid_contrasts.csv`, `c6_resid_classes.csv`, `c6_resid_undo.csv`, `c6_resid_evening.csv`, `c6_resid_nearest.csv`.

# C7, the fitted behavior's bands on a wider grid

## C7. The fitted behavior's bands on a wider grid (Paper A, Table 1)


Bands are 95% bootstrap intervals over the Meituan moments (the earlier fit's procedure: moments, seeds, objective, bootstrap picks over every grid point run). The wide grid adds two steps beyond the lowest and the highest value the earlier fit explored for every fitted parameter, then grows on any side a band end still touches (4 rounds; at most 8).

| parameter | earlier band | wide-grid band | wide grid explored | end still touches the grid | point: earlier, wide |
|---|---|---|---|---|---|
| return probability | [0.675, 0.825] | [0.675, 0.825] | [0.45, 0.975] | no | 0.75, 0.75 |
| decision delay (s) | [29.4, 42] | [29.4, 42] | [15, 117.6] | no | 42, 42 |
| cruise radius (m) | [2000, 2800] | [1979, 2800] | [714.286, 7056] | no | 2000, 2800 |
| stay constant (beta0) | [-3.5, -2] | [-6, -2.5] | [-6.5, -1] | no | -3, -3.5 |

Band ends that still touch the wide grid: none.
Band ends one value from the edge of the explored values: stay constant (beta0) (low).
Values added in the rounds were tried only across the other parameters' values inside their bands, so a band end there may be too narrow: stay constant (beta0): lowest value at 18 points against a median of 512 per value.
Objective values are not comparable across fits: the moment weights depend on the grid's coarse points.
Point estimate: moved for cruise radius (m), stay constant (beta0). As instructed, nothing in the frozen behavior changes: every run keeps the frozen values.
0 of 156 grid points shared with the earlier fit reproduce its moments exactly.

# The Ashkrof variant's bands on a wider grid

## The Ashkrof variant's bands on a wider grid


Bands are 95% bootstrap intervals over the Meituan moments (the earlier fit's procedure: moments, seeds, objective, bootstrap picks over every grid point run). The wide grid adds two steps beyond the lowest and the highest value the earlier fit explored for every fitted parameter, then grows on any side a band end still touches (4 rounds; at most 8).

| parameter | earlier band | wide-grid band | wide grid explored | end still touches the grid | point: earlier, wide |
|---|---|---|---|---|---|
| return probability | [0.65, 0.85] | [0.675, 0.85] | [0.4, 1] | no | 0.75, 0.75 |
| decision delay (s) | [42, 42] | [42, 42] | [42, 42] | fixed | 42, 42 |
| cruise radius (m) | [2000, 2000] | [2000, 2000] | [2000, 2000] | fixed | 2000, 2000 |
| stay constant (beta0) | [-4, -2] | [-6.5, -2.7375] | [-7, -1] | no | -3, -4.5 |

Band ends that still touch the wide grid: none.
Band ends one value from the edge of the explored values: stay constant (beta0) (low).
Objective values are not comparable across fits: the moment weights depend on the grid's coarse points.
Point estimate: moved for stay constant (beta0). Part 3 ran again at the wide-grid values (setting `ashkrofw`, files `c3w_ashkrof_*`); the first runs stay beside them.
25 of 25 grid points shared with the earlier fit reproduce its moments exactly.

# Part 3 again, at the wide-grid recalibration

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

# Files

One CSV per table, in this folder:

- `c1_e6_classes.csv`
- `c1_e6_contrasts.csv`
- `c1_e6_dqn.csv`
- `c1_e6_evening.csv`
- `c1_e6_undo.csv`
- `c2_stay.csv`
- `c3_ashkrof_bands.csv`
- `c3_ashkrof_classes.csv`
- `c3_ashkrof_contrasts.csv`
- `c3_ashkrof_dqn.csv`
- `c3_ashkrof_fit.csv`
- `c3_ashkrof_moments.csv`
- `c3_ashkrof_nearest_means.csv`
- `c3w_ashkrof_classes.csv`
- `c3w_ashkrof_contrasts.csv`
- `c3w_ashkrof_dqn.csv`
- `c3w_ashkrof_fit.csv`
- `c3w_ashkrof_moments.csv`
- `c3w_ashkrof_nearest_means.csv`
- `c4_noise_classes.csv`
- `c4_noise_contrasts.csv`
- `c4_noise_identity.csv`
- `c5_evening_by_return.csv`
- `c5_evening_by_return_nearest.csv`
- `c5_evening_truncated.csv`
- `c5_per_policy.csv`
- `c5_w1_windows.csv`
- `c6_resid_classes.csv`
- `c6_resid_contrasts.csv`
- `c6_resid_evening.csv`
- `c6_resid_nearest.csv`
- `c6_resid_undo.csv`
- `c7_bands.csv`

This research was supported by data provided by Meituan.
