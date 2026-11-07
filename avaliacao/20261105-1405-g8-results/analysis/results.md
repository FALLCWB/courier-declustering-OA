# Extension results (X8), analysis

This research was supported by data provided by Meituan.

Seeds 1001 to 1150 (n = 150); 36,023 episodes read (7,800 of them in the R4 fresh block, seeds 5001 on); frozen reruns against S8: 1800 compared, 0 differ.

## Established contrasts per family (Holm within each)

| Family | Contrasts | Established | Established decrease of at least the smallest effect | Established increase | Not established: equivalent within delta (R3) | Not established: inconclusive (R3) |
|---|---|---|---|---|---|---|
| E1 | 60 | 56 | 8 | 38 | 4 | 0 |
| E2 | 133 | 125 | 24 | 45 | 8 | 0 |
| E2-fresh (R4) | 160 | 146 | 28 | 59 | 14 | 0 |
| E2-fresh, frozen three only (R4) | 60 | 54 | 4 | 29 | 6 | 0 |

## Frozen three on Q2: frozen seeds and the fresh seed block (R4)

The fresh-seed contrasts are the ones Paper A quotes for these models on Q2. Holm over the 160 contrasts of E2 with the frozen three's rows taken from the fresh block (`contrasts_e2_fresh.csv`); classes in `classes_e2_fresh.csv`, time to undo in `undo_e2_fresh.csv`.

| cell | model | metric | seeds 1001-1150 | fresh seed block 5001-5150 |
|---|---|---|---|---|
| big_cluster, tight | foodmatch | w1_rule_60min_after_min | +0.50 [+0.49, +0.52], p_Holm 2.12e-107 | +0.50 [+0.49, +0.52], p_Holm 1.3e-111 |
| big_cluster, normal | foodmatch | w1_rule_60min_after_min | +0.17 [+0.16, +0.18], p_Holm 6.53e-93 | +0.16 [+0.16, +0.17], p_Holm 1.79e-87 |
| big_cluster, loose | foodmatch | w1_rule_60min_after_min | +0.10 [+0.10, +0.11], p_Holm 2.68e-87 | +0.10 [+0.10, +0.11], p_Holm 2.41e-89 |
| three_clusters, tight | foodmatch | w1_rule_60min_after_min | -1.20 [-1.23, -1.18], p_Holm 1.11e-141 | -1.21 [-1.23, -1.19], p_Holm 1.93e-140 |
| three_clusters, normal | foodmatch | w1_rule_60min_after_min | -1.03 [-1.05, -1.01], p_Holm 7.11e-147 | -1.04 [-1.06, -1.02], p_Holm 6.15e-144 |
| three_clusters, loose | foodmatch | w1_rule_60min_after_min | -0.81 [-0.83, -0.80], p_Holm 6.06e-140 | -0.80 [-0.82, -0.78], p_Holm 9.83e-136 |
| mixed, tight | foodmatch | w1_rule_60min_after_min | -0.08 [-0.08, -0.07], p_Holm 5.16e-31 | -0.08 [-0.09, -0.07], p_Holm 1.36e-36 |
| mixed, normal | foodmatch | w1_rule_60min_after_min | +0.08 [+0.08, +0.09], p_Holm 3.85e-54 | +0.08 [+0.08, +0.09], p_Holm 2.61e-50 |
| mixed, loose | foodmatch | w1_rule_60min_after_min | +0.06 [+0.05, +0.06], p_Holm 4.4e-59 | +0.06 [+0.05, +0.06], p_Holm 8.58e-59 |
| meetup, normal | foodmatch | w1_rule_60min_after_min | +0.05 [+0.02, +0.07], p_Holm 0.00464 | +0.04 [+0.01, +0.06], p_Holm 0.0889 |
| big_cluster, tight | foodmatch | p90_c2d_min | F1 (first round) | -10.90 [-11.03, -10.77], p_Holm 4.67e-168 |
| big_cluster, normal | foodmatch | p90_c2d_min | F1 (first round) | +1.01 [+0.92, +1.10], p_Holm 1.9e-48 |
| big_cluster, loose | foodmatch | p90_c2d_min | F1 (first round) | +1.82 [+1.79, +1.85], p_Holm 1.38e-141 |
| three_clusters, tight | foodmatch | p90_c2d_min | F1 (first round) | -12.52 [-12.65, -12.38], p_Holm 2.05e-174 |
| three_clusters, normal | foodmatch | p90_c2d_min | F1 (first round) | -1.68 [-1.73, -1.62], p_Holm 9.49e-103 |
| three_clusters, loose | foodmatch | p90_c2d_min | F1 (first round) | -0.05 [-0.08, -0.02], p_Holm 0.0346 |
| mixed, tight | foodmatch | p90_c2d_min | F1 (first round) | -10.80 [-10.94, -10.65], p_Holm 9.65e-162 |
| mixed, normal | foodmatch | p90_c2d_min | F1 (first round) | -0.79 [-0.82, -0.76], p_Holm 1.78e-94 |
| mixed, loose | foodmatch | p90_c2d_min | F1 (first round) | -0.20 [-0.23, -0.17], p_Holm 9.41e-28 |
| meetup, normal | foodmatch | p90_c2d_min | +0.05 [+0.05, +0.06], p_Holm 8.07e-44 | +0.06 [+0.05, +0.06], p_Holm 7.01e-47 |
| big_cluster, tight | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.01], p_Holm 2.18e-24 | +0.01 [+0.01, +0.01], p_Holm 4.64e-22 |
| big_cluster, normal | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.02], p_Holm 6.63e-48 | +0.01 [+0.01, +0.02], p_Holm 1.06e-50 |
| big_cluster, loose | forecast | w1_rule_60min_after_min | +0.02 [+0.02, +0.02], p_Holm 1.25e-65 | +0.02 [+0.02, +0.02], p_Holm 6.01e-74 |
| three_clusters, tight | forecast | w1_rule_60min_after_min | -0.04 [-0.05, -0.04], p_Holm 1.29e-34 | -0.04 [-0.05, -0.04], p_Holm 2.1e-30 |
| three_clusters, normal | forecast | w1_rule_60min_after_min | -0.02 [-0.03, -0.02], p_Holm 9.77e-21 | -0.02 [-0.03, -0.02], p_Holm 2.81e-16 |
| three_clusters, loose | forecast | w1_rule_60min_after_min | -0.02 [-0.02, -0.01], p_Holm 2.24e-14 | -0.02 [-0.02, -0.01], p_Holm 4.99e-13 |
| mixed, tight | forecast | w1_rule_60min_after_min | +0.08 [+0.08, +0.09], p_Holm 6.67e-65 | +0.08 [+0.08, +0.08], p_Holm 2.46e-67 |
| mixed, normal | forecast | w1_rule_60min_after_min | +0.18 [+0.18, +0.19], p_Holm 7.35e-108 | +0.19 [+0.18, +0.19], p_Holm 6.52e-115 |
| mixed, loose | forecast | w1_rule_60min_after_min | +0.26 [+0.26, +0.27], p_Holm 5.14e-130 | +0.26 [+0.26, +0.27], p_Holm 1.36e-132 |
| meetup, normal | forecast | w1_rule_60min_after_min | -0.43 [-0.47, -0.40], p_Holm 1.45e-49 | -0.45 [-0.48, -0.42], p_Holm 6.25e-60 |
| big_cluster, tight | forecast | p90_c2d_min | F1 (first round) | +0.04 [-0.04, +0.12], p_Holm 1 |
| big_cluster, normal | forecast | p90_c2d_min | F1 (first round) | +0.30 [+0.28, +0.32], p_Holm 4.9e-68 |
| big_cluster, loose | forecast | p90_c2d_min | F1 (first round) | +0.25 [+0.24, +0.26], p_Holm 9.58e-78 |
| three_clusters, tight | forecast | p90_c2d_min | F1 (first round) | -0.01 [-0.10, +0.08], p_Holm 1 |
| three_clusters, normal | forecast | p90_c2d_min | F1 (first round) | +0.27 [+0.25, +0.29], p_Holm 2.9e-47 |
| three_clusters, loose | forecast | p90_c2d_min | F1 (first round) | +0.29 [+0.27, +0.30], p_Holm 1.75e-75 |
| mixed, tight | forecast | p90_c2d_min | F1 (first round) | +0.45 [+0.36, +0.55], p_Holm 8.67e-15 |
| mixed, normal | forecast | p90_c2d_min | F1 (first round) | +0.62 [+0.60, +0.64], p_Holm 2.38e-104 |
| mixed, loose | forecast | p90_c2d_min | F1 (first round) | +0.71 [+0.69, +0.73], p_Holm 5.73e-119 |
| meetup, normal | forecast | p90_c2d_min | +0.58 [+0.57, +0.59], p_Holm 6.58e-129 | +0.58 [+0.57, +0.59], p_Holm 1.95e-131 |
| big_cluster, tight | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.06], p_Holm 5.82e-74 | -0.06 [-0.06, -0.05], p_Holm 4.55e-65 |
| big_cluster, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.10], p_Holm 4.73e-89 | -0.10 [-0.10, -0.10], p_Holm 8.78e-94 |
| big_cluster, loose | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05], p_Holm 1.39e-76 | -0.06 [-0.06, -0.05], p_Holm 7.58e-84 |
| three_clusters, tight | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05], p_Holm 6.92e-32 | -0.05 [-0.06, -0.05], p_Holm 4.89e-36 |
| three_clusters, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.09], p_Holm 4.19e-60 | -0.09 [-0.10, -0.08], p_Holm 6.69e-62 |
| three_clusters, loose | backpressure | w1_rule_60min_after_min | -0.10 [-0.11, -0.09], p_Holm 5.23e-66 | -0.09 [-0.10, -0.09], p_Holm 6.6e-71 |
| mixed, tight | backpressure | w1_rule_60min_after_min | -0.08 [-0.09, -0.07], p_Holm 1.48e-37 | -0.08 [-0.09, -0.08], p_Holm 5.33e-39 |
| mixed, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.09], p_Holm 1.1e-58 | -0.10 [-0.10, -0.09], p_Holm 8.4e-65 |
| mixed, loose | backpressure | w1_rule_60min_after_min | -0.12 [-0.12, -0.11], p_Holm 4.7e-74 | -0.11 [-0.11, -0.10], p_Holm 1.24e-75 |
| meetup, normal | backpressure | w1_rule_60min_after_min | -0.14 [-0.17, -0.11], p_Holm 1.97e-14 | -0.13 [-0.17, -0.10], p_Holm 4.95e-12 |
| big_cluster, tight | backpressure | p90_c2d_min | F1 (first round) | -0.06 [-0.15, +0.03], p_Holm 1 |
| big_cluster, normal | backpressure | p90_c2d_min | F1 (first round) | +0.30 [+0.27, +0.33], p_Holm 2.57e-44 |
| big_cluster, loose | backpressure | p90_c2d_min | F1 (first round) | +0.02 [+0.01, +0.03], p_Holm 0.03 |
| three_clusters, tight | backpressure | p90_c2d_min | F1 (first round) | -0.03 [-0.14, +0.08], p_Holm 1 |
| three_clusters, normal | backpressure | p90_c2d_min | F1 (first round) | +0.06 [+0.03, +0.08], p_Holm 0.000754 |
| three_clusters, loose | backpressure | p90_c2d_min | F1 (first round) | +0.16 [+0.15, +0.18], p_Holm 2.58e-39 |
| mixed, tight | backpressure | p90_c2d_min | F1 (first round) | -0.00 [-0.09, +0.08], p_Holm 1 |
| mixed, normal | backpressure | p90_c2d_min | F1 (first round) | +0.03 [+0.01, +0.05], p_Holm 0.0409 |
| mixed, loose | backpressure | p90_c2d_min | F1 (first round) | +0.08 [+0.06, +0.09], p_Holm 1.09e-17 |
| meetup, normal | backpressure | p90_c2d_min | +0.26 [+0.25, +0.27], p_Holm 1.9e-97 | +0.26 [+0.25, +0.27], p_Holm 1.53e-100 |

## Joint reading, class counts

| question | model | does not prevent | does not undo | prevents at a delivery cost | prevents at no delivery cost | undoes at a delivery cost | undoes at no delivery cost |
|---|---|---|---|---|---|---|---|
| Q1 | auad | 6 | 0 | 0 | 0 | 0 | 0 |
| Q1 | jusup | 6 | 0 | 0 | 0 | 0 | 0 |
| Q1 | li | 2 | 0 | 0 | 4 | 0 | 0 |
| Q1 | xu | 4 | 0 | 1 | 1 | 0 | 0 |
| Q1 | zhu | 6 | 0 | 0 | 0 | 0 | 0 |
| Q2 | auad | 0 | 10 | 0 | 0 | 0 | 0 |
| Q2 | backpressure | 0 | 10 | 0 | 0 | 0 | 0 |
| Q2 | foodmatch | 0 | 10 | 0 | 0 | 0 | 0 |
| Q2 | forecast | 0 | 10 | 0 | 0 | 0 | 0 |
| Q2 | jusup | 0 | 5 | 0 | 0 | 0 | 5 |
| Q2 | li | 0 | 10 | 0 | 0 | 0 | 0 |
| Q2 | xu | 0 | 6 | 0 | 0 | 2 | 2 |
| Q2 | zhu | 0 | 10 | 0 | 0 | 0 | 0 |

## Profile

| model | descriptive_only | q1_classes | q1_source | q2_classes | time_to_undo_median_of_cells | nearest_time_to_undo_median_of_cells | cells_undo_first_hour_only | p90_diff_mean | extra_km_per_order_diff_mean | idle_km_per_order_diff_mean | unassigned_over_30min_share_diff_mean | undelivered_diff_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| foodmatch | False | {"does not prevent": 6} | F1 | {"does not undo": 10} | 118.000 | 117.000 | 0 | -2.602 | -0.556 | -0.076 | 0.004 | 0.058 |
| forecast | False | {"does not prevent": 2, "prevents at no delivery cost": 4} | F1 | {"does not undo": 10} | 121.000 | 117.000 | 0 | 0.431 | 0.083 | -0.079 | 0.000 | 0.000 |
| backpressure | False | {"does not prevent": 4, "prevents at no delivery cost": 2} | F1 | {"does not undo": 10} | 117.000 | 117.000 | 0 | 0.139 | 0.298 | 0.121 | 0.000 | 0.000 |
| xu | False | {"does not prevent": 4, "prevents at a delivery cost": 1, "prevents at no delivery cost": 1} | E1 | {"does not undo": 6, "undoes at a delivery cost": 2, "undoes at no delivery cost": 2} | 168.750 | 117.000 | 2 | 1.984 | -0.011 | -0.394 | 0.038 | 0.000 |
| li | False | {"does not prevent": 2, "prevents at no delivery cost": 4} | E1 | {"does not undo": 10} | 120.250 | 117.000 | 0 | -2.090 | 0.524 | 0.273 | 0.001 | 0.000 |
| jahanshahi | True | {} | none | {} | 117.000 | 117.000 | 0 | 0.000 | 0.059 | 0.028 | 0.000 | 0.000 |
| auad | False | {"does not prevent": 6} | E1 | {"does not undo": 10} | 116.750 | 117.000 | 0 | 0.203 | -0.207 | -0.070 | 0.004 | 0.021 |
| zhu | False | {"does not prevent": 6} | E1 | {"does not undo": 10} | 113.000 | 117.000 | 0 | -0.195 | -2.042 | -1.882 | 0.000 | 0.000 |
| jusup | False | {"does not prevent": 6} | E1 | {"does not undo": 5, "undoes at no delivery cost": 5} | 123.500 | 117.000 | 3 | -1.225 | -1.063 | -0.803 | 0.000 | 0.000 |

Arm C models enter at 100% obedience, an upper bound, never real courier behavior. The DQN row is descriptive.
