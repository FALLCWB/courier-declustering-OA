# Paper A numbers at G8 (E1, E2 and the R4 fresh seed block)

This research was supported by data provided by Meituan.

Seeds 1001 to 1150 (n = 150); the frozen four's Q2 cells also on the fresh seed block 5001 to 5150 (R4). Differences are model minus nearest courier, lower is better; 95% percentile bootstrap intervals; Holm within each family. Arm C (Zhu, Jusup) at 100% obedience, an upper bound. The DQN row is descriptive. Q4 (E3, E4, E5) is added to this file when phases 3 and 4 finish.

## Q1, prevent (E1)

| cell | model | metric | difference [95% CI] | % of nearest | n | p (Holm) | class | equivalence |
|---|---|---|---|---|---|---|---|---|
| scattered, tight | xu | w1_rule_min | -0.68 [-0.72, -0.64] | -13.9% | 150 | 3.85e-74 | prevents at a delivery cost | not read: established |
| scattered, normal | xu | w1_rule_min | +0.22 [+0.18, +0.26] | +4.7% | 150 | 9.41e-18 | does not prevent | not read: established |
| scattered, loose | xu | w1_rule_min | +0.67 [+0.64, +0.71] | +16.8% | 150 | 5.64e-79 | does not prevent | not read: established |
| burst, tight | xu | w1_rule_min | -0.72 [-0.75, -0.70] | -14.9% | 150 | 7.86e-101 | prevents at no delivery cost | not read: established |
| burst, normal | xu | w1_rule_min | -0.22 [-0.26, -0.18] | -4.5% | 150 | 1.7e-21 | does not prevent | not read: established |
| burst, loose | xu | w1_rule_min | +0.44 [+0.41, +0.47] | +10.4% | 150 | 1.4e-57 | does not prevent | not read: established |
| scattered, tight | xu | p90_c2d_min | +1.95 [+1.76, +2.13] | +5.2% | 150 | 2.98e-43 | prevents at a delivery cost | not read: established |
| scattered, normal | xu | p90_c2d_min | +3.17 [+3.15, +3.19] | +8.8% | 150 | 5.11e-197 | does not prevent | not read: established |
| scattered, loose | xu | p90_c2d_min | +3.22 [+3.20, +3.25] | +9.0% | 150 | 2.92e-197 | does not prevent | not read: established |
| burst, tight | xu | p90_c2d_min | -4.58 [-4.77, -4.38] | -10.4% | 150 | 5.56e-88 | prevents at no delivery cost | not read: established |
| burst, normal | xu | p90_c2d_min | +3.27 [+3.24, +3.30] | +9.1% | 150 | 3.42e-188 | does not prevent | not read: established |
| burst, loose | xu | p90_c2d_min | +3.37 [+3.35, +3.40] | +9.4% | 150 | 1.02e-191 | does not prevent | not read: established |
| scattered, tight | li | w1_rule_min | -0.31 [-0.33, -0.29] | -6.4% | 150 | 6.6e-68 | does not prevent | not read: established |
| scattered, normal | li | w1_rule_min | -0.68 [-0.70, -0.66] | -14.8% | 150 | 9.22e-117 | prevents at no delivery cost | not read: established |
| scattered, loose | li | w1_rule_min | -0.79 [-0.81, -0.78] | -19.9% | 150 | 6.26e-136 | prevents at no delivery cost | not read: established |
| burst, tight | li | w1_rule_min | -0.39 [-0.41, -0.37] | -8.0% | 150 | 2.94e-77 | does not prevent | not read: established |
| burst, normal | li | w1_rule_min | -0.63 [-0.65, -0.62] | -12.9% | 150 | 1.19e-113 | prevents at no delivery cost | not read: established |
| burst, loose | li | w1_rule_min | -0.76 [-0.78, -0.75] | -18.1% | 150 | 5.57e-137 | prevents at no delivery cost | not read: established |
| scattered, tight | li | p90_c2d_min | -0.11 [-0.23, -0.00] | -0.3% | 150 | 0.24 | does not prevent | equivalent within delta |
| scattered, normal | li | p90_c2d_min | +0.47 [+0.46, +0.48] | +1.3% | 150 | 1.53e-119 | prevents at no delivery cost | not read: established |
| scattered, loose | li | p90_c2d_min | +0.53 [+0.52, +0.55] | +1.5% | 150 | 9.84e-132 | prevents at no delivery cost | not read: established |
| burst, tight | li | p90_c2d_min | -4.84 [-5.03, -4.65] | -11.0% | 150 | 2.65e-94 | does not prevent | not read: established |
| burst, normal | li | p90_c2d_min | +0.39 [+0.38, +0.40] | +1.1% | 150 | 4.47e-108 | prevents at no delivery cost | not read: established |
| burst, loose | li | p90_c2d_min | +0.51 [+0.50, +0.52] | +1.4% | 150 | 4.31e-130 | prevents at no delivery cost | not read: established |
| scattered, tight | auad | w1_rule_min | -0.07 [-0.08, -0.06] | -1.5% | 150 | 8.97e-18 | does not prevent | not read: established |
| scattered, normal | auad | w1_rule_min | +0.09 [+0.08, +0.10] | +1.9% | 150 | 3.97e-27 | does not prevent | not read: established |
| scattered, loose | auad | w1_rule_min | +0.10 [+0.10, +0.11] | +2.6% | 150 | 1.25e-52 | does not prevent | not read: established |
| burst, tight | auad | w1_rule_min | -0.12 [-0.13, -0.11] | -2.5% | 150 | 1.99e-41 | does not prevent | not read: established |
| burst, normal | auad | w1_rule_min | +0.07 [+0.06, +0.09] | +1.5% | 150 | 5.17e-20 | does not prevent | not read: established |
| burst, loose | auad | w1_rule_min | +0.09 [+0.08, +0.10] | +2.2% | 150 | 4.66e-39 | does not prevent | not read: established |
| scattered, tight | auad | p90_c2d_min | +0.75 [+0.67, +0.83] | +2.0% | 150 | 6.33e-38 | does not prevent | not read: established |
| scattered, normal | auad | p90_c2d_min | +0.42 [+0.41, +0.43] | +1.2% | 150 | 1.35e-124 | does not prevent | not read: established |
| scattered, loose | auad | p90_c2d_min | +0.34 [+0.33, +0.35] | +0.9% | 150 | 2.21e-111 | does not prevent | not read: established |
| burst, tight | auad | p90_c2d_min | +0.14 [-0.04, +0.31] | +0.3% | 150 | 0.389 | does not prevent | equivalent within delta |
| burst, normal | auad | p90_c2d_min | +0.44 [+0.43, +0.45] | +1.2% | 150 | 2.29e-117 | does not prevent | not read: established |
| burst, loose | auad | p90_c2d_min | +0.36 [+0.35, +0.37] | +1.0% | 150 | 5.99e-108 | does not prevent | not read: established |
| scattered, tight | zhu | w1_rule_min | +0.70 [+0.67, +0.72] | +14.3% | 150 | 4.86e-101 | does not prevent | not read: established |
| scattered, normal | zhu | w1_rule_min | +1.16 [+1.13, +1.18] | +25.0% | 150 | 7.85e-136 | does not prevent | not read: established |
| scattered, loose | zhu | w1_rule_min | +0.95 [+0.93, +0.96] | +23.6% | 150 | 7.63e-142 | does not prevent | not read: established |
| burst, tight | zhu | w1_rule_min | +0.20 [+0.18, +0.22] | +4.1% | 150 | 1.06e-46 | does not prevent | not read: established |
| burst, normal | zhu | w1_rule_min | +1.23 [+1.21, +1.26] | +25.1% | 150 | 9.92e-134 | does not prevent | not read: established |
| burst, loose | zhu | w1_rule_min | +1.09 [+1.07, +1.11] | +25.9% | 150 | 7.48e-144 | does not prevent | not read: established |
| scattered, tight | zhu | p90_c2d_min | -0.37 [-0.45, -0.31] | -1.0% | 150 | 4.12e-18 | does not prevent | not read: established |
| scattered, normal | zhu | p90_c2d_min | -0.00 [-0.01, +0.00] | -0.0% | 150 | 0.662 | does not prevent | equivalent within delta |
| scattered, loose | zhu | p90_c2d_min | -0.01 [-0.01, -0.00] | -0.0% | 150 | 0.000304 | does not prevent | not read: established |
| burst, tight | zhu | p90_c2d_min | -0.29 [-0.36, -0.22] | -0.7% | 150 | 4.78e-12 | does not prevent | not read: established |
| burst, normal | zhu | p90_c2d_min | -0.01 [-0.02, -0.01] | -0.0% | 150 | 7.91e-06 | does not prevent | not read: established |
| burst, loose | zhu | p90_c2d_min | -0.01 [-0.01, -0.00] | -0.0% | 150 | 0.000481 | does not prevent | not read: established |
| scattered, tight | jusup | w1_rule_min | +1.16 [+1.11, +1.21] | +23.8% | 150 | 7.58e-92 | does not prevent | not read: established |
| scattered, normal | jusup | w1_rule_min | +2.01 [+1.98, +2.04] | +43.4% | 150 | 5.76e-154 | does not prevent | not read: established |
| scattered, loose | jusup | w1_rule_min | +1.55 [+1.53, +1.58] | +38.8% | 150 | 5.11e-140 | does not prevent | not read: established |
| burst, tight | jusup | w1_rule_min | +0.47 [+0.45, +0.49] | +9.7% | 150 | 2.9e-89 | does not prevent | not read: established |
| burst, normal | jusup | w1_rule_min | +2.05 [+2.02, +2.08] | +41.8% | 150 | 3.49e-154 | does not prevent | not read: established |
| burst, loose | jusup | w1_rule_min | +1.73 [+1.70, +1.76] | +41.0% | 150 | 2.71e-150 | does not prevent | not read: established |
| scattered, tight | jusup | p90_c2d_min | +0.14 [+0.08, +0.20] | +0.4% | 150 | 0.000108 | does not prevent | not read: established |
| scattered, normal | jusup | p90_c2d_min | +0.05 [+0.05, +0.06] | +0.1% | 150 | 2.34e-35 | does not prevent | not read: established |
| scattered, loose | jusup | p90_c2d_min | +0.00 [-0.00, +0.00] | +0.0% | 150 | 0.662 | does not prevent | equivalent within delta |
| burst, tight | jusup | p90_c2d_min | +0.17 [+0.09, +0.25] | +0.4% | 150 | 0.000312 | does not prevent | not read: established |
| burst, normal | jusup | p90_c2d_min | +0.07 [+0.06, +0.08] | +0.2% | 150 | 1.19e-40 | does not prevent | not read: established |
| burst, loose | jusup | p90_c2d_min | +0.01 [+0.01, +0.01] | +0.0% | 150 | 3.57e-06 | does not prevent | not read: established |
| scattered, tight | jahanshahi | w1_rule_min | -0.03 [-0.04, -0.02] | -0.6% | 150 | descriptive | descriptive | not read: descriptive |
| scattered, normal | jahanshahi | w1_rule_min | -0.07 [-0.08, -0.06] | -1.5% | 150 | descriptive | descriptive | not read: descriptive |
| scattered, loose | jahanshahi | w1_rule_min | -0.09 [-0.09, -0.08] | -2.1% | 150 | descriptive | descriptive | not read: descriptive |
| burst, tight | jahanshahi | w1_rule_min | -0.01 [-0.02, +0.00] | -0.2% | 150 | descriptive | descriptive | not read: descriptive |
| burst, normal | jahanshahi | w1_rule_min | -0.07 [-0.08, -0.06] | -1.4% | 150 | descriptive | descriptive | not read: descriptive |
| burst, loose | jahanshahi | w1_rule_min | -0.07 [-0.08, -0.06] | -1.7% | 150 | descriptive | descriptive | not read: descriptive |
| scattered, tight | jahanshahi | p90_c2d_min | +0.06 [+0.04, +0.09] | +0.2% | 150 | descriptive | descriptive | not read: descriptive |
| scattered, normal | jahanshahi | p90_c2d_min | +0.04 [+0.03, +0.04] | +0.1% | 150 | descriptive | descriptive | not read: descriptive |
| scattered, loose | jahanshahi | p90_c2d_min | +0.02 [+0.02, +0.02] | +0.1% | 150 | descriptive | descriptive | not read: descriptive |
| burst, tight | jahanshahi | p90_c2d_min | +0.07 [+0.01, +0.13] | +0.2% | 150 | descriptive | descriptive | not read: descriptive |
| burst, normal | jahanshahi | p90_c2d_min | +0.03 [+0.03, +0.04] | +0.1% | 150 | descriptive | descriptive | not read: descriptive |
| burst, loose | jahanshahi | p90_c2d_min | +0.02 [+0.02, +0.03] | +0.1% | 150 | descriptive | descriptive | not read: descriptive |

## Q2, undo (E2, seeds as pre-registered)

| cell | model | metric | difference [95% CI] | % of nearest | n | p (Holm) | class | equivalence |
|---|---|---|---|---|---|---|---|---|
| big_cluster, tight | xu | w1_rule_60min_after_min | +3.34 [+3.31, +3.38] | +18.0% | 150 | 5.27e-175 | does not undo | not read: established |
| big_cluster, normal | xu | w1_rule_60min_after_min | +0.90 [+0.88, +0.93] | +4.2% | 150 | 5.52e-122 | does not undo | not read: established |
| big_cluster, loose | xu | w1_rule_60min_after_min | +0.25 [+0.24, +0.25] | +1.1% | 150 | 1.35e-97 | does not undo | not read: established |
| three_clusters, tight | xu | w1_rule_60min_after_min | -0.07 [-0.14, +0.01] | -0.3% | 150 | 0.424 | does not undo | equivalent within delta |
| three_clusters, normal | xu | w1_rule_60min_after_min | -1.45 [-1.48, -1.42] | -7.1% | 150 | 1.99e-132 | does not undo | not read: established |
| three_clusters, loose | xu | w1_rule_60min_after_min | -1.11 [-1.13, -1.08] | -5.7% | 150 | 7.27e-124 | does not undo | not read: established |
| mixed, tight | xu | w1_rule_60min_after_min | -2.08 [-2.12, -2.05] | -12.9% | 150 | 7.47e-142 | undoes at no delivery cost | not read: established |
| mixed, normal | xu | w1_rule_60min_after_min | -2.38 [-2.41, -2.36] | -14.5% | 150 | 2.5e-173 | undoes at no delivery cost | not read: established |
| mixed, loose | xu | w1_rule_60min_after_min | -1.77 [-1.79, -1.75] | -11.6% | 150 | 1.51e-169 | undoes at a delivery cost | not read: established |
| meetup, normal | xu | w1_rule_60min_after_min | -2.99 [-3.17, -2.82] | -35.3% | 150 | 2.21e-70 | undoes at a delivery cost | not read: established |
| big_cluster, tight | li | w1_rule_60min_after_min | -0.07 [-0.07, -0.06] | -0.4% | 150 | 5.84e-40 | does not undo | not read: established |
| big_cluster, normal | li | w1_rule_60min_after_min | -0.12 [-0.13, -0.11] | -0.6% | 150 | 2.63e-84 | does not undo | not read: established |
| big_cluster, loose | li | w1_rule_60min_after_min | -0.08 [-0.09, -0.08] | -0.4% | 150 | 1.81e-80 | does not undo | not read: established |
| three_clusters, tight | li | w1_rule_60min_after_min | -0.03 [-0.04, -0.02] | -0.2% | 150 | 0.00037 | does not undo | not read: established |
| three_clusters, normal | li | w1_rule_60min_after_min | -0.22 [-0.23, -0.21] | -1.1% | 150 | 1.06e-81 | does not undo | not read: established |
| three_clusters, loose | li | w1_rule_60min_after_min | -0.22 [-0.23, -0.21] | -1.1% | 150 | 1.42e-89 | does not undo | not read: established |
| mixed, tight | li | w1_rule_60min_after_min | -0.40 [-0.41, -0.39] | -2.5% | 150 | 2.89e-115 | does not undo | not read: established |
| mixed, normal | li | w1_rule_60min_after_min | -0.55 [-0.56, -0.54] | -3.4% | 150 | 1.22e-133 | does not undo | not read: established |
| mixed, loose | li | w1_rule_60min_after_min | -0.50 [-0.51, -0.49] | -3.3% | 150 | 3.36e-137 | does not undo | not read: established |
| meetup, normal | li | w1_rule_60min_after_min | -0.49 [-0.53, -0.46] | -5.8% | 150 | 3.1e-60 | does not undo | not read: established |
| big_cluster, tight | auad | w1_rule_60min_after_min | +0.30 [+0.22, +0.37] | +1.6% | 150 | 7.83e-11 | does not undo | not read: established |
| big_cluster, normal | auad | w1_rule_60min_after_min | +0.11 [+0.08, +0.13] | +0.5% | 150 | 3.24e-13 | does not undo | not read: established |
| big_cluster, loose | auad | w1_rule_60min_after_min | +0.04 [+0.04, +0.05] | +0.2% | 150 | 1.2e-34 | does not undo | not read: established |
| three_clusters, tight | auad | w1_rule_60min_after_min | -0.08 [-0.11, -0.05] | -0.4% | 150 | 2.64e-06 | does not undo | not read: established |
| three_clusters, normal | auad | w1_rule_60min_after_min | -0.18 [-0.19, -0.17] | -0.9% | 150 | 4.97e-76 | does not undo | not read: established |
| three_clusters, loose | auad | w1_rule_60min_after_min | -0.16 [-0.17, -0.15] | -0.8% | 150 | 4.78e-72 | does not undo | not read: established |
| mixed, tight | auad | w1_rule_60min_after_min | +0.05 [+0.04, +0.06] | +0.3% | 150 | 9.41e-29 | does not undo | not read: established |
| mixed, normal | auad | w1_rule_60min_after_min | +0.08 [+0.08, +0.08] | +0.5% | 150 | 3.43e-71 | does not undo | not read: established |
| mixed, loose | auad | w1_rule_60min_after_min | +0.07 [+0.06, +0.07] | +0.4% | 150 | 1.86e-69 | does not undo | not read: established |
| meetup, normal | auad | w1_rule_60min_after_min | +0.00 [-0.02, +0.03] | +0.1% | 150 | 1 | does not undo | equivalent within delta |
| big_cluster, tight | zhu | w1_rule_60min_after_min | -0.16 [-0.17, -0.15] | -0.9% | 150 | 9.37e-65 | does not undo | not read: established |
| big_cluster, normal | zhu | w1_rule_60min_after_min | -0.22 [-0.23, -0.21] | -1.0% | 150 | 2.63e-84 | does not undo | not read: established |
| big_cluster, loose | zhu | w1_rule_60min_after_min | -0.13 [-0.14, -0.12] | -0.6% | 150 | 3.5e-64 | does not undo | not read: established |
| three_clusters, tight | zhu | w1_rule_60min_after_min | -0.12 [-0.13, -0.10] | -0.6% | 150 | 1.53e-32 | does not undo | not read: established |
| three_clusters, normal | zhu | w1_rule_60min_after_min | -0.15 [-0.17, -0.14] | -0.7% | 150 | 8.27e-42 | does not undo | not read: established |
| three_clusters, loose | zhu | w1_rule_60min_after_min | -0.06 [-0.07, -0.05] | -0.3% | 150 | 5.55e-14 | does not undo | not read: established |
| mixed, tight | zhu | w1_rule_60min_after_min | -0.05 [-0.06, -0.03] | -0.3% | 150 | 3.48e-10 | does not undo | not read: established |
| mixed, normal | zhu | w1_rule_60min_after_min | -0.01 [-0.02, +0.00] | -0.1% | 150 | 0.398 | does not undo | equivalent within delta |
| mixed, loose | zhu | w1_rule_60min_after_min | +0.02 [+0.01, +0.03] | +0.2% | 150 | 0.000211 | does not undo | not read: established |
| meetup, normal | zhu | w1_rule_60min_after_min | +1.39 [+1.36, +1.43] | +16.4% | 150 | 3e-119 | does not undo | not read: established |
| big_cluster, tight | jusup | w1_rule_60min_after_min | +0.44 [+0.39, +0.48] | +2.4% | 150 | 5.84e-40 | does not undo | not read: established |
| big_cluster, normal | jusup | w1_rule_60min_after_min | -0.65 [-0.69, -0.61] | -3.0% | 150 | 2.84e-61 | does not undo | not read: established |
| big_cluster, loose | jusup | w1_rule_60min_after_min | -1.96 [-1.99, -1.93] | -8.8% | 150 | 3.06e-145 | does not undo | not read: established |
| three_clusters, tight | jusup | w1_rule_60min_after_min | -0.80 [-0.86, -0.74] | -4.1% | 150 | 2.07e-56 | does not undo | not read: established |
| three_clusters, normal | jusup | w1_rule_60min_after_min | -2.65 [-2.69, -2.62] | -13.0% | 150 | 3.88e-160 | undoes at no delivery cost | not read: established |
| three_clusters, loose | jusup | w1_rule_60min_after_min | -2.98 [-3.02, -2.95] | -15.4% | 150 | 2.63e-171 | undoes at no delivery cost | not read: established |
| mixed, tight | jusup | w1_rule_60min_after_min | -1.64 [-1.70, -1.59] | -10.2% | 150 | 5.95e-102 | undoes at no delivery cost | not read: established |
| mixed, normal | jusup | w1_rule_60min_after_min | -2.82 [-2.86, -2.78] | -17.2% | 150 | 2.44e-160 | undoes at no delivery cost | not read: established |
| mixed, loose | jusup | w1_rule_60min_after_min | -2.81 [-2.84, -2.78] | -18.4% | 150 | 3.36e-173 | undoes at no delivery cost | not read: established |
| meetup, normal | jusup | w1_rule_60min_after_min | +2.36 [+2.31, +2.40] | +27.8% | 150 | 1.03e-140 | does not undo | not read: established |
| big_cluster, tight | foodmatch | w1_rule_60min_after_min | +0.50 [+0.49, +0.52] | +2.7% | 150 | 2.12e-107 | does not undo | not read: established |
| big_cluster, normal | foodmatch | w1_rule_60min_after_min | +0.17 [+0.16, +0.18] | +0.8% | 150 | 6.53e-93 | does not undo | not read: established |
| big_cluster, loose | foodmatch | w1_rule_60min_after_min | +0.10 [+0.10, +0.11] | +0.5% | 150 | 2.68e-87 | does not undo | not read: established |
| three_clusters, tight | foodmatch | w1_rule_60min_after_min | -1.20 [-1.23, -1.18] | -6.2% | 150 | 1.11e-141 | does not undo | not read: established |
| three_clusters, normal | foodmatch | w1_rule_60min_after_min | -1.03 [-1.05, -1.01] | -5.0% | 150 | 7.11e-147 | does not undo | not read: established |
| three_clusters, loose | foodmatch | w1_rule_60min_after_min | -0.81 [-0.83, -0.80] | -4.2% | 150 | 6.06e-140 | does not undo | not read: established |
| mixed, tight | foodmatch | w1_rule_60min_after_min | -0.08 [-0.08, -0.07] | -0.5% | 150 | 5.16e-31 | does not undo | not read: established |
| mixed, normal | foodmatch | w1_rule_60min_after_min | +0.08 [+0.08, +0.09] | +0.5% | 150 | 3.85e-54 | does not undo | not read: established |
| mixed, loose | foodmatch | w1_rule_60min_after_min | +0.06 [+0.05, +0.06] | +0.4% | 150 | 4.4e-59 | does not undo | not read: established |
| meetup, normal | foodmatch | w1_rule_60min_after_min | +0.05 [+0.02, +0.07] | +0.6% | 150 | 0.00464 | does not undo | not read: established |
| big_cluster, tight | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.01] | +0.0% | 150 | 2.18e-24 | does not undo | not read: established |
| big_cluster, normal | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.02] | +0.1% | 150 | 6.63e-48 | does not undo | not read: established |
| big_cluster, loose | forecast | w1_rule_60min_after_min | +0.02 [+0.02, +0.02] | +0.1% | 150 | 1.25e-65 | does not undo | not read: established |
| three_clusters, tight | forecast | w1_rule_60min_after_min | -0.04 [-0.05, -0.04] | -0.2% | 150 | 1.29e-34 | does not undo | not read: established |
| three_clusters, normal | forecast | w1_rule_60min_after_min | -0.02 [-0.03, -0.02] | -0.1% | 150 | 9.77e-21 | does not undo | not read: established |
| three_clusters, loose | forecast | w1_rule_60min_after_min | -0.02 [-0.02, -0.01] | -0.1% | 150 | 2.24e-14 | does not undo | not read: established |
| mixed, tight | forecast | w1_rule_60min_after_min | +0.08 [+0.08, +0.09] | +0.5% | 150 | 6.67e-65 | does not undo | not read: established |
| mixed, normal | forecast | w1_rule_60min_after_min | +0.18 [+0.18, +0.19] | +1.1% | 150 | 7.35e-108 | does not undo | not read: established |
| mixed, loose | forecast | w1_rule_60min_after_min | +0.26 [+0.26, +0.27] | +1.7% | 150 | 5.14e-130 | does not undo | not read: established |
| meetup, normal | forecast | w1_rule_60min_after_min | -0.43 [-0.47, -0.40] | -5.1% | 150 | 1.45e-49 | does not undo | not read: established |
| big_cluster, tight | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.06] | -0.3% | 150 | 5.82e-74 | does not undo | not read: established |
| big_cluster, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.10] | -0.5% | 150 | 4.73e-89 | does not undo | not read: established |
| big_cluster, loose | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05] | -0.3% | 150 | 1.39e-76 | does not undo | not read: established |
| three_clusters, tight | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05] | -0.3% | 150 | 6.92e-32 | does not undo | not read: established |
| three_clusters, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.09] | -0.5% | 150 | 4.19e-60 | does not undo | not read: established |
| three_clusters, loose | backpressure | w1_rule_60min_after_min | -0.10 [-0.11, -0.09] | -0.5% | 150 | 5.23e-66 | does not undo | not read: established |
| mixed, tight | backpressure | w1_rule_60min_after_min | -0.08 [-0.09, -0.07] | -0.5% | 150 | 1.48e-37 | does not undo | not read: established |
| mixed, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.09] | -0.6% | 150 | 1.1e-58 | does not undo | not read: established |
| mixed, loose | backpressure | w1_rule_60min_after_min | -0.12 [-0.12, -0.11] | -0.8% | 150 | 4.7e-74 | does not undo | not read: established |
| meetup, normal | backpressure | w1_rule_60min_after_min | -0.14 [-0.17, -0.11] | -1.6% | 150 | 1.97e-14 | does not undo | not read: established |
| big_cluster, tight | xu | p90_c2d_min | +3.12 [+2.89, +3.34] | +5.3% | 150 | 3.03e-58 | does not undo | not read: established |
| big_cluster, normal | xu | p90_c2d_min | +13.57 [+13.33, +13.81] | +31.0% | 150 | 5.37e-141 | does not undo | not read: established |
| big_cluster, loose | xu | p90_c2d_min | +13.16 [+12.94, +13.37] | +30.7% | 150 | 4.82e-148 | does not undo | not read: established |
| three_clusters, tight | xu | p90_c2d_min | -9.92 [-10.08, -9.76] | -17.5% | 150 | 1.75e-149 | does not undo | not read: established |
| three_clusters, normal | xu | p90_c2d_min | +1.66 [+1.58, +1.74] | +3.9% | 150 | 9.19e-79 | does not undo | not read: established |
| three_clusters, loose | xu | p90_c2d_min | +3.64 [+3.58, +3.70] | +9.2% | 150 | 8.98e-151 | does not undo | not read: established |
| mixed, tight | xu | p90_c2d_min | -10.90 [-11.07, -10.71] | -21.5% | 150 | 1.14e-146 | undoes at no delivery cost | not read: established |
| mixed, normal | xu | p90_c2d_min | +0.70 [+0.66, +0.74] | +1.8% | 150 | 6.96e-68 | undoes at no delivery cost | not read: established |
| mixed, loose | xu | p90_c2d_min | +2.43 [+2.38, +2.47] | +6.6% | 150 | 1.61e-135 | undoes at a delivery cost | not read: established |
| meetup, normal | xu | p90_c2d_min | +3.87 [+3.84, +3.90] | +10.8% | 150 | 1.24e-199 | undoes at a delivery cost | not read: established |
| big_cluster, tight | li | p90_c2d_min | -9.82 [-9.97, -9.67] | -16.7% | 150 | 1.03e-152 | does not undo | not read: established |
| big_cluster, normal | li | p90_c2d_min | -0.36 [-0.43, -0.29] | -0.8% | 150 | 3.64e-17 | does not undo | not read: established |
| big_cluster, loose | li | p90_c2d_min | -0.01 [-0.03, +0.02] | -0.0% | 150 | 1 | does not undo | equivalent within delta |
| three_clusters, tight | li | p90_c2d_min | -10.00 [-10.15, -9.86] | -17.7% | 150 | 3.95e-156 | does not undo | not read: established |
| three_clusters, normal | li | p90_c2d_min | -0.74 [-0.79, -0.70] | -1.8% | 150 | 7.2e-67 | does not undo | not read: established |
| three_clusters, loose | li | p90_c2d_min | -0.35 [-0.38, -0.33] | -0.9% | 150 | 1.14e-54 | does not undo | not read: established |
| mixed, tight | li | p90_c2d_min | -9.00 [-9.17, -8.83] | -17.7% | 150 | 2.42e-140 | does not undo | not read: established |
| mixed, normal | li | p90_c2d_min | -0.50 [-0.53, -0.47] | -1.3% | 150 | 4.2e-68 | does not undo | not read: established |
| mixed, loose | li | p90_c2d_min | -0.07 [-0.09, -0.04] | -0.2% | 150 | 6.97e-06 | does not undo | not read: established |
| meetup, normal | li | p90_c2d_min | +0.47 [+0.45, +0.48] | +1.3% | 150 | 7.63e-118 | does not undo | not read: established |
| big_cluster, tight | auad | p90_c2d_min | -1.22 [-1.67, -0.79] | -2.1% | 150 | 3.7e-06 | does not undo | not read: established |
| big_cluster, normal | auad | p90_c2d_min | +0.93 [+0.87, +0.99] | +2.1% | 150 | 5e-62 | does not undo | not read: established |
| big_cluster, loose | auad | p90_c2d_min | +0.79 [+0.74, +0.84] | +1.8% | 150 | 2.64e-63 | does not undo | not read: established |
| three_clusters, tight | auad | p90_c2d_min | -1.62 [-2.05, -1.22] | -2.9% | 150 | 8.05e-11 | does not undo | not read: established |
| three_clusters, normal | auad | p90_c2d_min | +0.15 [+0.11, +0.20] | +0.4% | 150 | 1.72e-09 | does not undo | not read: established |
| three_clusters, loose | auad | p90_c2d_min | +0.38 [+0.36, +0.41] | +1.0% | 150 | 3.37e-62 | does not undo | not read: established |
| mixed, tight | auad | p90_c2d_min | -0.33 [-0.67, +0.01] | -0.6% | 150 | 0.398 | does not undo | equivalent within delta |
| mixed, normal | auad | p90_c2d_min | +0.75 [+0.72, +0.78] | +1.9% | 150 | 8.28e-97 | does not undo | not read: established |
| mixed, loose | auad | p90_c2d_min | +0.55 [+0.53, +0.57] | +1.5% | 150 | 4.29e-98 | does not undo | not read: established |
| meetup, normal | auad | p90_c2d_min | +0.43 [+0.42, +0.44] | +1.2% | 150 | 4.1e-123 | does not undo | not read: established |
| big_cluster, tight | zhu | p90_c2d_min | -0.13 [-0.24, -0.03] | -0.2% | 150 | 0.136 | does not undo | equivalent within delta |
| big_cluster, normal | zhu | p90_c2d_min | -0.20 [-0.24, -0.17] | -0.5% | 150 | 1.97e-19 | does not undo | not read: established |
| big_cluster, loose | zhu | p90_c2d_min | -0.12 [-0.14, -0.10] | -0.3% | 150 | 5.78e-24 | does not undo | not read: established |
| three_clusters, tight | zhu | p90_c2d_min | -0.60 [-0.70, -0.50] | -1.1% | 150 | 1.97e-20 | does not undo | not read: established |
| three_clusters, normal | zhu | p90_c2d_min | -0.62 [-0.65, -0.58] | -1.5% | 150 | 3.24e-69 | does not undo | not read: established |
| three_clusters, loose | zhu | p90_c2d_min | -0.47 [-0.50, -0.45] | -1.2% | 150 | 1.36e-75 | does not undo | not read: established |
| mixed, tight | zhu | p90_c2d_min | -0.03 [-0.12, +0.07] | -0.1% | 150 | 1 | does not undo | equivalent within delta |
| mixed, normal | zhu | p90_c2d_min | -0.13 [-0.15, -0.11] | -0.3% | 150 | 5.6e-24 | does not undo | not read: established |
| mixed, loose | zhu | p90_c2d_min | -0.13 [-0.14, -0.12] | -0.4% | 150 | 1.77e-38 | does not undo | not read: established |
| meetup, normal | zhu | p90_c2d_min | +0.00 [-0.00, +0.01] | +0.0% | 150 | 1 | does not undo | equivalent within delta |
| big_cluster, tight | jusup | p90_c2d_min | -1.65 [-1.78, -1.52] | -2.8% | 150 | 3.32e-54 | does not undo | not read: established |
| big_cluster, normal | jusup | p90_c2d_min | -2.26 [-2.35, -2.17] | -5.2% | 150 | 2.34e-93 | does not undo | not read: established |
| big_cluster, loose | jusup | p90_c2d_min | -3.07 [-3.11, -3.03] | -7.1% | 150 | 3.18e-165 | does not undo | not read: established |
| three_clusters, tight | jusup | p90_c2d_min | -3.10 [-3.24, -2.98] | -5.5% | 150 | 6.94e-89 | does not undo | not read: established |
| three_clusters, normal | jusup | p90_c2d_min | -3.36 [-3.42, -3.31] | -7.9% | 150 | 1.92e-153 | undoes at no delivery cost | not read: established |
| three_clusters, loose | jusup | p90_c2d_min | -2.28 [-2.32, -2.23] | -5.8% | 150 | 4.33e-138 | undoes at no delivery cost | not read: established |
| mixed, tight | jusup | p90_c2d_min | -2.18 [-2.32, -2.04] | -4.3% | 150 | 8.55e-64 | undoes at no delivery cost | not read: established |
| mixed, normal | jusup | p90_c2d_min | -1.53 [-1.56, -1.50] | -4.0% | 150 | 1e-132 | undoes at no delivery cost | not read: established |
| mixed, loose | jusup | p90_c2d_min | -0.67 [-0.70, -0.63] | -1.8% | 150 | 2.23e-81 | undoes at no delivery cost | not read: established |
| meetup, normal | jusup | p90_c2d_min | +0.05 [+0.05, +0.06] | +0.1% | 150 | 2.85e-34 | does not undo | not read: established |
| meetup, normal | foodmatch | p90_c2d_min | +0.05 [+0.05, +0.06] | +0.2% | 150 | 8.07e-44 | does not undo | not read: established |
| meetup, normal | forecast | p90_c2d_min | +0.58 [+0.57, +0.59] | +1.6% | 150 | 6.58e-129 | does not undo | not read: established |
| meetup, normal | backpressure | p90_c2d_min | +0.26 [+0.25, +0.27] | +0.7% | 150 | 1.9e-97 | does not undo | not read: established |
| big_cluster, tight | jahanshahi | w1_rule_60min_after_min | +0.00 [-0.00, +0.00] | +0.0% | 150 | descriptive | descriptive | not read: descriptive |
| big_cluster, normal | jahanshahi | w1_rule_60min_after_min | -0.00 [-0.00, -0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| big_cluster, loose | jahanshahi | w1_rule_60min_after_min | -0.00 [-0.00, -0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, tight | jahanshahi | w1_rule_60min_after_min | -0.00 [-0.00, +0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, normal | jahanshahi | w1_rule_60min_after_min | -0.01 [-0.01, -0.01] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, loose | jahanshahi | w1_rule_60min_after_min | -0.01 [-0.01, -0.01] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, tight | jahanshahi | w1_rule_60min_after_min | -0.02 [-0.02, -0.02] | -0.1% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, normal | jahanshahi | w1_rule_60min_after_min | -0.03 [-0.03, -0.03] | -0.2% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, loose | jahanshahi | w1_rule_60min_after_min | -0.03 [-0.04, -0.03] | -0.2% | 150 | descriptive | descriptive | not read: descriptive |
| meetup, normal | jahanshahi | w1_rule_60min_after_min | -0.04 [-0.06, -0.02] | -0.5% | 150 | descriptive | descriptive | not read: descriptive |
| big_cluster, tight | jahanshahi | p90_c2d_min | +0.02 [-0.06, +0.11] | +0.0% | 150 | descriptive | descriptive | not read: descriptive |
| big_cluster, normal | jahanshahi | p90_c2d_min | -0.01 [-0.03, -0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| big_cluster, loose | jahanshahi | p90_c2d_min | -0.01 [-0.02, -0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, tight | jahanshahi | p90_c2d_min | -0.13 [-0.21, -0.04] | -0.2% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, normal | jahanshahi | p90_c2d_min | -0.02 [-0.04, +0.00] | -0.0% | 150 | descriptive | descriptive | not read: descriptive |
| three_clusters, loose | jahanshahi | p90_c2d_min | -0.04 [-0.05, -0.02] | -0.1% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, tight | jahanshahi | p90_c2d_min | -0.04 [-0.13, +0.04] | -0.1% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, normal | jahanshahi | p90_c2d_min | -0.03 [-0.04, -0.01] | -0.1% | 150 | descriptive | descriptive | not read: descriptive |
| mixed, loose | jahanshahi | p90_c2d_min | -0.02 [-0.03, -0.01] | -0.1% | 150 | descriptive | descriptive | not read: descriptive |
| meetup, normal | jahanshahi | p90_c2d_min | +0.04 [+0.03, +0.04] | +0.1% | 150 | descriptive | descriptive | not read: descriptive |

## Q2, frozen three on the fresh seed block (R4; the numbers Paper A quotes for these models on Q2)

Holm over the 160 contrasts of E2 with the frozen three's rows from the fresh block.

| cell | model | metric | difference [95% CI] | % of nearest | n | p (Holm) | class | equivalence |
|---|---|---|---|---|---|---|---|---|
| big_cluster, tight | foodmatch | w1_rule_60min_after_min | +0.50 [+0.49, +0.52] | +2.7% | 150 | 1.3e-111 | does not undo | not read: established |
| big_cluster, normal | foodmatch | w1_rule_60min_after_min | +0.16 [+0.16, +0.17] | +0.8% | 150 | 1.79e-87 | does not undo | not read: established |
| big_cluster, loose | foodmatch | w1_rule_60min_after_min | +0.10 [+0.10, +0.11] | +0.5% | 150 | 2.41e-89 | does not undo | not read: established |
| three_clusters, tight | foodmatch | w1_rule_60min_after_min | -1.21 [-1.23, -1.19] | -6.2% | 150 | 1.93e-140 | does not undo | not read: established |
| three_clusters, normal | foodmatch | w1_rule_60min_after_min | -1.04 [-1.06, -1.02] | -5.1% | 150 | 6.15e-144 | does not undo | not read: established |
| three_clusters, loose | foodmatch | w1_rule_60min_after_min | -0.80 [-0.82, -0.78] | -4.1% | 150 | 9.83e-136 | does not undo | not read: established |
| mixed, tight | foodmatch | w1_rule_60min_after_min | -0.08 [-0.09, -0.07] | -0.5% | 150 | 1.36e-36 | does not undo | not read: established |
| mixed, normal | foodmatch | w1_rule_60min_after_min | +0.08 [+0.08, +0.09] | +0.5% | 150 | 2.61e-50 | does not undo | not read: established |
| mixed, loose | foodmatch | w1_rule_60min_after_min | +0.06 [+0.05, +0.06] | +0.4% | 150 | 8.58e-59 | does not undo | not read: established |
| meetup, normal | foodmatch | w1_rule_60min_after_min | +0.04 [+0.01, +0.06] | +0.4% | 150 | 0.0889 | does not undo | equivalent within delta |
| big_cluster, tight | foodmatch | p90_c2d_min | -10.90 [-11.03, -10.77] | -18.6% | 150 | 4.67e-168 | does not undo | not read: established |
| big_cluster, normal | foodmatch | p90_c2d_min | +1.01 [+0.92, +1.10] | +2.3% | 150 | 1.9e-48 | does not undo | not read: established |
| big_cluster, loose | foodmatch | p90_c2d_min | +1.82 [+1.79, +1.85] | +4.2% | 150 | 1.38e-141 | does not undo | not read: established |
| three_clusters, tight | foodmatch | p90_c2d_min | -12.52 [-12.65, -12.38] | -22.2% | 150 | 2.05e-174 | does not undo | not read: established |
| three_clusters, normal | foodmatch | p90_c2d_min | -1.68 [-1.73, -1.62] | -4.0% | 150 | 9.49e-103 | does not undo | not read: established |
| three_clusters, loose | foodmatch | p90_c2d_min | -0.05 [-0.08, -0.02] | -0.1% | 150 | 0.0346 | does not undo | not read: established |
| mixed, tight | foodmatch | p90_c2d_min | -10.80 [-10.94, -10.65] | -21.3% | 150 | 9.65e-162 | does not undo | not read: established |
| mixed, normal | foodmatch | p90_c2d_min | -0.79 [-0.82, -0.76] | -2.0% | 150 | 1.78e-94 | does not undo | not read: established |
| mixed, loose | foodmatch | p90_c2d_min | -0.20 [-0.23, -0.17] | -0.5% | 150 | 9.41e-28 | does not undo | not read: established |
| meetup, normal | foodmatch | p90_c2d_min | +0.06 [+0.05, +0.06] | +0.2% | 150 | 7.01e-47 | does not undo | not read: established |
| big_cluster, tight | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.01] | +0.0% | 150 | 4.64e-22 | does not undo | not read: established |
| big_cluster, normal | forecast | w1_rule_60min_after_min | +0.01 [+0.01, +0.02] | +0.1% | 150 | 1.06e-50 | does not undo | not read: established |
| big_cluster, loose | forecast | w1_rule_60min_after_min | +0.02 [+0.02, +0.02] | +0.1% | 150 | 6.01e-74 | does not undo | not read: established |
| three_clusters, tight | forecast | w1_rule_60min_after_min | -0.04 [-0.05, -0.04] | -0.2% | 150 | 2.1e-30 | does not undo | not read: established |
| three_clusters, normal | forecast | w1_rule_60min_after_min | -0.02 [-0.03, -0.02] | -0.1% | 150 | 2.81e-16 | does not undo | not read: established |
| three_clusters, loose | forecast | w1_rule_60min_after_min | -0.02 [-0.02, -0.01] | -0.1% | 150 | 4.99e-13 | does not undo | not read: established |
| mixed, tight | forecast | w1_rule_60min_after_min | +0.08 [+0.08, +0.08] | +0.5% | 150 | 2.46e-67 | does not undo | not read: established |
| mixed, normal | forecast | w1_rule_60min_after_min | +0.19 [+0.18, +0.19] | +1.2% | 150 | 6.52e-115 | does not undo | not read: established |
| mixed, loose | forecast | w1_rule_60min_after_min | +0.26 [+0.26, +0.27] | +1.7% | 150 | 1.36e-132 | does not undo | not read: established |
| meetup, normal | forecast | w1_rule_60min_after_min | -0.45 [-0.48, -0.42] | -5.3% | 150 | 6.25e-60 | does not undo | not read: established |
| big_cluster, tight | forecast | p90_c2d_min | +0.04 [-0.04, +0.12] | +0.1% | 150 | 1 | does not undo | equivalent within delta |
| big_cluster, normal | forecast | p90_c2d_min | +0.30 [+0.28, +0.32] | +0.7% | 150 | 4.9e-68 | does not undo | not read: established |
| big_cluster, loose | forecast | p90_c2d_min | +0.25 [+0.24, +0.26] | +0.6% | 150 | 9.58e-78 | does not undo | not read: established |
| three_clusters, tight | forecast | p90_c2d_min | -0.01 [-0.10, +0.08] | -0.0% | 150 | 1 | does not undo | equivalent within delta |
| three_clusters, normal | forecast | p90_c2d_min | +0.27 [+0.25, +0.29] | +0.6% | 150 | 2.9e-47 | does not undo | not read: established |
| three_clusters, loose | forecast | p90_c2d_min | +0.29 [+0.27, +0.30] | +0.7% | 150 | 1.75e-75 | does not undo | not read: established |
| mixed, tight | forecast | p90_c2d_min | +0.45 [+0.36, +0.55] | +0.9% | 150 | 8.67e-15 | does not undo | not read: established |
| mixed, normal | forecast | p90_c2d_min | +0.62 [+0.60, +0.64] | +1.6% | 150 | 2.38e-104 | does not undo | not read: established |
| mixed, loose | forecast | p90_c2d_min | +0.71 [+0.69, +0.73] | +1.9% | 150 | 5.73e-119 | does not undo | not read: established |
| meetup, normal | forecast | p90_c2d_min | +0.58 [+0.57, +0.59] | +1.6% | 150 | 1.95e-131 | does not undo | not read: established |
| big_cluster, tight | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05] | -0.3% | 150 | 4.55e-65 | does not undo | not read: established |
| big_cluster, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.10] | -0.5% | 150 | 8.78e-94 | does not undo | not read: established |
| big_cluster, loose | backpressure | w1_rule_60min_after_min | -0.06 [-0.06, -0.05] | -0.3% | 150 | 7.58e-84 | does not undo | not read: established |
| three_clusters, tight | backpressure | w1_rule_60min_after_min | -0.05 [-0.06, -0.05] | -0.3% | 150 | 4.89e-36 | does not undo | not read: established |
| three_clusters, normal | backpressure | w1_rule_60min_after_min | -0.09 [-0.10, -0.08] | -0.4% | 150 | 6.69e-62 | does not undo | not read: established |
| three_clusters, loose | backpressure | w1_rule_60min_after_min | -0.09 [-0.10, -0.09] | -0.5% | 150 | 6.6e-71 | does not undo | not read: established |
| mixed, tight | backpressure | w1_rule_60min_after_min | -0.08 [-0.09, -0.08] | -0.5% | 150 | 5.33e-39 | does not undo | not read: established |
| mixed, normal | backpressure | w1_rule_60min_after_min | -0.10 [-0.10, -0.09] | -0.6% | 150 | 8.4e-65 | does not undo | not read: established |
| mixed, loose | backpressure | w1_rule_60min_after_min | -0.11 [-0.11, -0.10] | -0.7% | 150 | 1.24e-75 | does not undo | not read: established |
| meetup, normal | backpressure | w1_rule_60min_after_min | -0.13 [-0.17, -0.10] | -1.6% | 150 | 4.95e-12 | does not undo | not read: established |
| big_cluster, tight | backpressure | p90_c2d_min | -0.06 [-0.15, +0.03] | -0.1% | 150 | 1 | does not undo | equivalent within delta |
| big_cluster, normal | backpressure | p90_c2d_min | +0.30 [+0.27, +0.33] | +0.7% | 150 | 2.57e-44 | does not undo | not read: established |
| big_cluster, loose | backpressure | p90_c2d_min | +0.02 [+0.01, +0.03] | +0.0% | 150 | 0.03 | does not undo | not read: established |
| three_clusters, tight | backpressure | p90_c2d_min | -0.03 [-0.14, +0.08] | -0.1% | 150 | 1 | does not undo | equivalent within delta |
| three_clusters, normal | backpressure | p90_c2d_min | +0.06 [+0.03, +0.08] | +0.1% | 150 | 0.000754 | does not undo | not read: established |
| three_clusters, loose | backpressure | p90_c2d_min | +0.16 [+0.15, +0.18] | +0.4% | 150 | 2.58e-39 | does not undo | not read: established |
| mixed, tight | backpressure | p90_c2d_min | -0.00 [-0.09, +0.08] | -0.0% | 150 | 1 | does not undo | equivalent within delta |
| mixed, normal | backpressure | p90_c2d_min | +0.03 [+0.01, +0.05] | +0.1% | 150 | 0.0409 | does not undo | not read: established |
| mixed, loose | backpressure | p90_c2d_min | +0.08 [+0.06, +0.09] | +0.2% | 150 | 1.09e-17 | does not undo | not read: established |
| meetup, normal | backpressure | p90_c2d_min | +0.26 [+0.25, +0.27] | +0.7% | 150 | 1.53e-100 | does not undo | not read: established |

## Q2, time to undo, second-hour check and unassigned share

Time to undo has no pre-registered smallest effect, so it gets no equivalence reading (R3).

| seeds | scenario | level | model | class | time_to_undo_median | time_to_undo_q25 | time_to_undo_q75 | censored_count | second_hour_check | unassigned_over_30min_share_model | unassigned_over_30min_share_nearest |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1001-1150 | big_cluster | tight | nearest | nearest courier | 54.000 | 51.000 | 56.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | tight | xu | does not undo | 81.000 | 76.000 | 90.750 | 15 | not read (cell not classed as undoing) | 0.118 | 0.000 |
| 1001-1150 | big_cluster | tight | li | does not undo | 55.000 | 53.000 | 58.000 | 0 | not read (cell not classed as undoing) | 0.008 | 0.000 |
| 1001-1150 | big_cluster | tight | auad | does not undo | 55.000 | 52.000 | 58.000 | 0 | not read (cell not classed as undoing) | 0.033 | 0.000 |
| 1001-1150 | big_cluster | tight | zhu | does not undo | 54.000 | 52.000 | 57.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | tight | jusup | does not undo | 55.000 | 54.000 | 57.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | tight | foodmatch | does not undo | 60.000 | 58.000 | 63.000 | 0 | not read (cell not classed as undoing) | 0.030 | 0.000 |
| 1001-1150 | big_cluster | tight | forecast | does not undo | 57.000 | 53.000 | 59.750 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | tight | backpressure | does not undo | 55.000 | 52.000 | 57.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | tight | jahanshahi | descriptive | 54.000 | 51.000 | 56.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | nearest | nearest courier | 74.000 | 71.000 | 77.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | xu | does not undo | 97.500 | 96.000 | 100.000 | 0 | not read (cell not classed as undoing) | 0.097 | 0.000 |
| 1001-1150 | big_cluster | normal | li | does not undo | 78.000 | 75.000 | 82.750 | 1 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | auad | does not undo | 75.000 | 71.000 | 79.000 | 0 | not read (cell not classed as undoing) | 0.003 | 0.000 |
| 1001-1150 | big_cluster | normal | zhu | does not undo | 74.000 | 71.000 | 77.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | jusup | does not undo | 102.000 | 96.250 | 108.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | foodmatch | does not undo | 71.000 | 69.000 | 73.000 | 0 | not read (cell not classed as undoing) | 0.004 | 0.000 |
| 1001-1150 | big_cluster | normal | forecast | does not undo | 76.000 | 73.000 | 80.000 | 3 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | backpressure | does not undo | 74.500 | 72.000 | 79.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | normal | jahanshahi | descriptive | 74.000 | 71.000 | 77.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | xu | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.094 | 0.000 |
| 1001-1150 | big_cluster | loose | li | does not undo | 240.000 | 240.000 | 240.000 | 149 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | auad | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.003 | 0.000 |
| 1001-1150 | big_cluster | loose | zhu | does not undo | 117.000 | 112.250 | 122.750 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | jusup | does not undo | 240.000 | 213.500 | 240.000 | 85 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 120 | not read (cell not classed as undoing) | 0.009 | 0.000 |
| 1001-1150 | big_cluster | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | big_cluster | loose | jahanshahi | descriptive | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | nearest | nearest courier | 59.000 | 57.000 | 61.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | xu | does not undo | 93.000 | 90.000 | 98.000 | 0 | not read (cell not classed as undoing) | 0.058 | 0.000 |
| 1001-1150 | three_clusters | tight | li | does not undo | 60.000 | 58.000 | 62.000 | 0 | not read (cell not classed as undoing) | 0.009 | 0.000 |
| 1001-1150 | three_clusters | tight | auad | does not undo | 59.000 | 57.250 | 61.000 | 0 | not read (cell not classed as undoing) | 0.024 | 0.000 |
| 1001-1150 | three_clusters | tight | zhu | does not undo | 59.000 | 57.000 | 61.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | jusup | does not undo | 65.000 | 63.000 | 67.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | foodmatch | does not undo | 57.000 | 56.000 | 60.000 | 0 | not read (cell not classed as undoing) | 0.016 | 0.000 |
| 1001-1150 | three_clusters | tight | forecast | does not undo | 60.000 | 58.000 | 62.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | backpressure | does not undo | 59.000 | 57.000 | 61.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | tight | jahanshahi | descriptive | 59.000 | 57.000 | 61.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | nearest | nearest courier | 240.000 | 139.250 | 240.000 | 96 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | xu | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.039 | 0.000 |
| 1001-1150 | three_clusters | normal | li | does not undo | 240.000 | 240.000 | 240.000 | 146 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | auad | does not undo | 240.000 | 136.250 | 240.000 | 100 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | zhu | does not undo | 135.500 | 129.000 | 146.000 | 6 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | jusup | undoes at no delivery cost | 240.000 | 240.000 | 240.000 | 145 | undoes in the first hour, not after | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 134 | not read (cell not classed as undoing) | 0.001 | 0.000 |
| 1001-1150 | three_clusters | normal | forecast | does not undo | 240.000 | 240.000 | 240.000 | 126 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | backpressure | does not undo | 240.000 | 137.250 | 240.000 | 100 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | normal | jahanshahi | descriptive | 240.000 | 141.000 | 240.000 | 102 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | xu | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.034 | 0.000 |
| 1001-1150 | three_clusters | loose | li | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | auad | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | zhu | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | jusup | undoes at no delivery cost | 240.000 | 240.000 | 240.000 | 150 | holds after the first hour | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.003 | 0.000 |
| 1001-1150 | three_clusters | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | three_clusters | loose | jahanshahi | descriptive | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | nearest | nearest courier | 64.000 | 62.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | xu | undoes at no delivery cost | 85.000 | 81.000 | 90.000 | 0 | undoes in the first hour, not after | 0.018 | 0.000 |
| 1001-1150 | mixed | tight | li | does not undo | 66.000 | 64.000 | 68.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | auad | does not undo | 63.500 | 62.000 | 65.000 | 0 | not read (cell not classed as undoing) | 0.009 | 0.000 |
| 1001-1150 | mixed | tight | zhu | does not undo | 64.000 | 62.000 | 65.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | jusup | undoes at no delivery cost | 70.000 | 68.000 | 72.000 | 0 | undoes in the first hour, not after | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | foodmatch | does not undo | 64.000 | 62.000 | 65.000 | 0 | not read (cell not classed as undoing) | 0.004 | 0.000 |
| 1001-1150 | mixed | tight | forecast | does not undo | 64.000 | 62.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | backpressure | does not undo | 64.000 | 62.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | tight | jahanshahi | descriptive | 64.000 | 62.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | nearest | nearest courier | 114.000 | 110.250 | 120.750 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | xu | undoes at no delivery cost | 240.000 | 240.000 | 240.000 | 150 | undoes in the first hour, not after | 0.016 | 0.000 |
| 1001-1150 | mixed | normal | li | does not undo | 120.500 | 115.000 | 129.000 | 8 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | auad | does not undo | 113.500 | 109.000 | 119.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | zhu | does not undo | 109.000 | 105.000 | 112.750 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | jusup | undoes at no delivery cost | 127.000 | 121.000 | 133.000 | 0 | undoes in the first hour, not after | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | foodmatch | does not undo | 116.000 | 110.000 | 126.000 | 12 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | forecast | does not undo | 122.000 | 117.000 | 130.000 | 21 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | backpressure | does not undo | 114.000 | 109.000 | 119.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | normal | jahanshahi | descriptive | 114.000 | 110.000 | 121.000 | 1 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | xu | undoes at a delivery cost | 240.000 | 240.000 | 240.000 | 150 | holds after the first hour | 0.016 | 0.000 |
| 1001-1150 | mixed | loose | li | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | auad | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | zhu | does not undo | 221.000 | 205.250 | 240.000 | 45 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | jusup | undoes at no delivery cost | 240.000 | 233.000 | 240.000 | 108 | holds after the first hour | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | mixed | loose | jahanshahi | descriptive | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | nearest | nearest courier | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | xu | undoes at a delivery cost | 13.500 | 3.250 | 20.750 | 0 | holds after the first hour | 0.015 | 0.000 |
| 1001-1150 | meetup | normal | li | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | auad | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | zhu | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | jusup | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | foodmatch | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | forecast | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | backpressure | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 1001-1150 | meetup | normal | jahanshahi | descriptive | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | tight | nearest | nearest courier | 54.000 | 52.000 | 56.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | tight | foodmatch | does not undo | 60.000 | 58.000 | 63.000 | 0 | not read (cell not classed as undoing) | 0.030 | 0.000 |
| 5001-5150 | big_cluster | tight | forecast | does not undo | 56.500 | 54.000 | 59.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | tight | backpressure | does not undo | 55.000 | 53.000 | 58.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | normal | nearest | nearest courier | 75.000 | 71.000 | 78.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | normal | foodmatch | does not undo | 72.000 | 69.000 | 73.000 | 0 | not read (cell not classed as undoing) | 0.004 | 0.000 |
| 5001-5150 | big_cluster | normal | forecast | does not undo | 77.000 | 73.000 | 81.000 | 5 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | normal | backpressure | does not undo | 76.000 | 72.250 | 79.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 130 | not read (cell not classed as undoing) | 0.009 | 0.000 |
| 5001-5150 | big_cluster | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | big_cluster | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | tight | nearest | nearest courier | 59.000 | 57.000 | 60.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | tight | foodmatch | does not undo | 57.000 | 56.000 | 59.000 | 0 | not read (cell not classed as undoing) | 0.015 | 0.000 |
| 5001-5150 | three_clusters | tight | forecast | does not undo | 60.000 | 58.000 | 62.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | tight | backpressure | does not undo | 59.000 | 58.000 | 61.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | normal | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 114 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | normal | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 142 | not read (cell not classed as undoing) | 0.001 | 0.000 |
| 5001-5150 | three_clusters | normal | forecast | does not undo | 240.000 | 240.000 | 240.000 | 133 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | normal | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 114 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.003 | 0.000 |
| 5001-5150 | three_clusters | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | three_clusters | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | tight | nearest | nearest courier | 64.000 | 63.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | tight | foodmatch | does not undo | 64.000 | 63.000 | 65.000 | 0 | not read (cell not classed as undoing) | 0.003 | 0.000 |
| 5001-5150 | mixed | tight | forecast | does not undo | 65.000 | 63.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | tight | backpressure | does not undo | 64.000 | 63.000 | 66.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | normal | nearest | nearest courier | 115.000 | 109.250 | 120.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | normal | foodmatch | does not undo | 116.000 | 110.000 | 124.000 | 13 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | normal | forecast | does not undo | 122.500 | 116.000 | 130.000 | 23 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | normal | backpressure | does not undo | 114.000 | 109.000 | 119.000 | 0 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | loose | nearest | nearest courier | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | loose | foodmatch | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | loose | forecast | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | mixed | loose | backpressure | does not undo | 240.000 | 240.000 | 240.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | meetup | normal | nearest | nearest courier | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | meetup | normal | foodmatch | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | meetup | normal | forecast | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |
| 5001-5150 | meetup | normal | backpressure | does not undo | 120.000 | 120.000 | 120.000 | 150 | not read (cell not classed as undoing) | 0.000 | 0.000 |

## Q2, descriptive meet-ups (exploratory median meet-up and ride variant)

| part | scenario | level | model | episodes_equal_to_nearest | seeds | w1_minus_nearest | w1_60_minus_nearest | p90_minus_nearest | w1_60_mean | p90_mean | unassigned_over_30min_share | undelivered | time_to_undo_median | censored_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ride | meetup_ride | normal | auad | nan | 150 | nan | 0.074 | 0.419 | 5.275 | 36.247 | 0.000 | 5.000 | nan | nan |
| ride | meetup_ride | normal | backpressure | nan | 150 | nan | -0.127 | 0.245 | 5.074 | 36.073 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | foodmatch | nan | 150 | nan | 0.077 | 0.053 | 5.278 | 35.881 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | forecast | nan | 150 | nan | -1.016 | 0.585 | 4.184 | 36.413 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | jahanshahi | nan | 150 | nan | -0.073 | 0.038 | 5.128 | 35.866 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | jusup | nan | 150 | nan | 2.883 | 0.050 | 8.084 | 35.878 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | li | nan | 150 | nan | -0.722 | 0.471 | 4.479 | 36.299 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | nearest | nan | 150 | nan | 0.000 | 0.000 | 5.201 | 35.828 | 0.000 | 0.000 | nan | nan |
| ride | meetup_ride | normal | xu | nan | 150 | nan | -0.567 | 3.377 | 4.634 | 39.205 | 0.015 | 0.000 | nan | nan |
| ride | meetup_ride | normal | zhu | nan | 150 | nan | 1.766 | -0.001 | 6.967 | 35.828 | 0.000 | 0.000 | nan | nan |
| explore | meetup_median | normal | auad | nan | 30 | nan | 0.066 | 0.423 | 6.913 | 36.256 | 0.000 | 1.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | backpressure | nan | 30 | nan | -0.244 | 0.241 | 6.603 | 36.074 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | foodmatch | nan | 30 | nan | 0.117 | 0.046 | 6.964 | 35.879 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | forecast | nan | 30 | nan | -0.729 | 0.562 | 6.118 | 36.395 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | jahanshahi | nan | 30 | nan | -0.092 | 0.033 | 6.755 | 35.866 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | jusup | nan | 30 | nan | 1.993 | 0.043 | 8.840 | 35.876 | 0.000 | 0.000 | 18.000 | 0.000 |
| explore | meetup_median | normal | li | nan | 30 | nan | -0.827 | 0.448 | 6.020 | 36.281 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | nearest | nan | 30 | nan | 0.000 | 0.000 | 6.847 | 35.833 | 0.000 | 0.000 | 120.000 | 1.000 |
| explore | meetup_median | normal | xu | nan | 30 | nan | -1.090 | 3.248 | 5.757 | 39.081 | 0.016 | 0.000 | 31.500 | 0.000 |
| explore | meetup_median | normal | zhu | nan | 30 | nan | 1.236 | -0.002 | 8.083 | 35.831 | 0.000 | 0.000 | 71.000 | 0.100 |

## Q3, cost (descriptive, primary cells)

Per model and metric over the 16 primary cells (6 Q1, 10 Q2): the mean of the cell differences, their range, and the cells whose 95% interval lies above or below 0. Every cell: `q3_costs.csv`.

| model | p90 (min) | mean order to door (min) | late share | km without an order per order | idle km per order | largest share unassigned >30 min |
|---|---|---|---|---|---|---|
| foodmatch | -2.602 (-12.703 to +1.860; 7 up, 9 down) | -1.400 (-7.145 to +1.083; 7 up, 9 down) | -0.042 (-0.219 to +0.023; 7 up, 9 down) | -0.556 (-1.889 to +0.364; 2 up, 14 down) | -0.076 (-0.244 to +0.202; 4 up, 12 down) | 3.0% (big_cluster, tight) |
| forecast | +0.431 (+0.004 to +0.704; 14 up, 0 down) | +0.299 (+0.067 to +0.447; 16 up, 0 down) | +0.005 (+0.002 to +0.009; 16 up, 0 down) | +0.083 (+0.000 to +0.170; 14 up, 0 down) | -0.079 (-0.151 to -0.028; 0 up, 16 down) | 0.0% (none: 0 in every cell) |
| backpressure | +0.139 (-0.076 to +0.380; 13 up, 0 down) | +0.150 (+0.007 to +0.252; 14 up, 0 down) | +0.002 (-0.001 to +0.005; 12 up, 0 down) | +0.298 (+0.047 to +0.626; 16 up, 0 down) | +0.121 (+0.003 to +0.274; 15 up, 0 down) | 0.0% (none: 0 in every cell) |
| xu | +1.984 (-10.895 to +13.571; 13 up, 3 down) | +0.404 (-5.592 to +4.310; 12 up, 4 down) | -0.010 (-0.190 to +0.073; 11 up, 4 down) | -0.011 (-1.814 to +1.121; 10 up, 6 down) | -0.394 (-0.673 to +0.134; 1 up, 15 down) | 11.8% (big_cluster, tight) |
| li | -2.090 (-10.004 to +0.534; 5 up, 10 down) | -0.859 (-6.667 to +0.769; 11 up, 5 down) | -0.039 (-0.215 to +0.002; 5 up, 11 down) | +0.524 (-1.383 to +1.686; 12 up, 4 down) | +0.273 (-0.009 to +0.550; 15 up, 1 down) | 0.9% (three_clusters, tight) |
| jahanshahi | +0.000 (-0.127 to +0.068; 7 up, 6 down) | +0.007 (-0.052 to +0.039; 8 up, 4 down) | +0.000 (-0.002 to +0.001; 8 up, 4 down) | +0.059 (+0.001 to +0.111; 15 up, 0 down) | +0.028 (+0.001 to +0.061; 15 up, 0 down) | 0.0% (none: 0 in every cell) |
| auad | +0.203 (-1.621 to +0.928; 12 up, 2 down) | +0.335 (+0.043 to +0.756; 15 up, 0 down) | -0.002 (-0.052 to +0.010; 13 up, 2 down) | -0.207 (-0.594 to -0.036; 0 up, 16 down) | -0.070 (-0.202 to +0.126; 2 up, 14 down) | 3.3% (big_cluster, tight) |
| zhu | -0.195 (-0.616 to +0.000; 0 up, 13 down) | -0.151 (-0.382 to -0.035; 0 up, 16 down) | -0.003 (-0.011 to -0.000; 0 up, 15 down) | -2.042 (-2.855 to -1.643; 0 up, 16 down) | -1.882 (-2.606 to -1.426; 0 up, 16 down) | 0.0% (none: 0 in every cell) |
| jusup | -1.225 (-3.364 to +0.172; 6 up, 9 down) | -0.687 (-2.011 to +0.049; 5 up, 11 down) | -0.020 (-0.063 to +0.002; 5 up, 11 down) | -1.063 (-1.586 to +0.541; 2 up, 14 down) | -0.803 (-1.569 to +0.903; 2 up, 14 down) | 0.0% (none: 0 in every cell) |

Each cell: the mean over the 16 primary cells of the model-minus-nearest difference, its range over the cells, and the cells whose 95% interval lies above (up) or below (down) 0. Wherever Paper A quotes Xu et al., the unassigned share goes beside it (G8 verdict, ruling 6).

## A1, second-hour split on the undoing cells (descriptive)

W1 over the second hour after the cluster appears (minutes 60 to 119; 180 to 239 for the meet-up), mean and 95% interval over seeds: the model and nearest courier on the cell, and both from the scattered start at the same clock minutes, supply and seeds. Excess = model minus nearest courier, paired by seed; the last column is the part of the excess on the cell beyond the excess the model already carries from a spread start. Every interval: `a1_second_hour_split.csv`.

| cell | model | nearest | model_scattered | nearest_scattered | excess_cell | excess_scattered | excess_beyond_scattered |
|---|---|---|---|---|---|---|---|
| xu, meetup, normal | 3.60 [3.57, 3.64] | 6.98 [6.92, 7.04] | 4.14 [4.10, 4.18] | 4.19 [4.15, 4.24] | -3.38 [-3.44, -3.32] | -0.05 [-0.09, -0.01] | -3.33 [-3.39, -3.26] |
| jusup, mixed, loose | 13.05 [12.96, 13.15] | 16.74 [16.70, 16.77] | 5.46 [5.40, 5.51] | 4.49 [4.44, 4.54] | -3.69 [-3.77, -3.60] | 0.97 [0.94, 1.01] | -4.66 [-4.75, -4.56] |
| xu, mixed, loose | 14.33 [14.27, 14.39] | 16.74 [16.70, 16.77] | 5.38 [5.35, 5.42] | 4.49 [4.44, 4.54] | -2.40 [-2.46, -2.35] | 0.89 [0.84, 0.95] | -3.30 [-3.38, -3.22] |
| jusup, mixed, normal | 13.72 [13.62, 13.82] | 11.78 [11.68, 11.89] | 7.15 [7.08, 7.22] | 5.69 [5.62, 5.76] | 1.93 [1.80, 2.06] | 1.46 [1.42, 1.50] | 0.47 [0.33, 0.62] |
| xu, mixed, normal | 12.11 [12.04, 12.18] | 11.78 [11.68, 11.89] | 5.75 [5.70, 5.79] | 5.69 [5.62, 5.76] | 0.33 [0.24, 0.42] | 0.06 [-0.02, 0.14] | 0.27 [0.15, 0.39] |
| jusup, mixed, tight | 6.43 [6.36, 6.50] | 5.53 [5.49, 5.57] | 7.05 [6.93, 7.16] | 6.34 [6.25, 6.44] | 0.91 [0.86, 0.95] | 0.70 [0.66, 0.75] | 0.20 [0.15, 0.26] |
| xu, mixed, tight | 5.74 [5.68, 5.79] | 5.53 [5.49, 5.57] | 4.68 [4.62, 4.74] | 6.34 [6.25, 6.44] | 0.21 [0.16, 0.26] | -1.66 [-1.76, -1.57] | 1.88 [1.78, 1.97] |
| jusup, three_clusters, loose | 17.08 [17.02, 17.13] | 20.05 [20.00, 20.10] | 5.46 [5.40, 5.51] | 4.49 [4.44, 4.54] | -2.98 [-3.05, -2.91] | 0.97 [0.93, 1.01] | -3.95 [-4.02, -3.87] |
| jusup, three_clusters, normal | 18.73 [18.65, 18.82] | 15.62 [15.40, 15.83] | 7.15 [7.08, 7.22] | 5.69 [5.62, 5.76] | 3.12 [2.92, 3.31] | 1.46 [1.42, 1.50] | 1.66 [1.46, 1.86] |

## A2, km ridden without an order: the ride to the restaurant and idle riding (descriptive)

Per model, the mean over the 16 primary cells of the model-minus-nearest difference per delivered order. Arm C models at 100% obedience: their commands replace the couriers' own idle moves, the ride back to the preferred area included. Every cell, with 95% intervals: `a2_km_split.csv`.

| model | ride to restaurant, difference | idle riding, difference | ride to restaurant, nearest courier | idle riding, nearest courier |
|---|---|---|---|---|
| foodmatch | -0.480 | -0.076 | 2.112 | 2.545 |
| forecast | 0.162 | -0.079 | 2.112 | 2.545 |
| backpressure | 0.177 | 0.121 | 2.112 | 2.545 |
| xu | 0.383 | -0.394 | 2.112 | 2.545 |
| li | 0.251 | 0.273 | 2.112 | 2.545 |
| jahanshahi | 0.032 | 0.028 | 2.112 | 2.545 |
| auad | -0.137 | -0.070 | 2.112 | 2.545 |
| zhu | -0.160 | -1.882 | 2.112 | 2.545 |
| jusup | -0.259 | -0.803 | 2.112 | 2.545 |

## A3, W1 over 20:00 to 20:59 on the clustered starts (exploratory)

Exploratory: defined after the results were seen (G8 verdict, ruling 5), outside every family, no test. Mean W1 over minutes 180 to 239, model minus nearest courier paired by seed, with 95% intervals. The Q2 window covers only the first hour, and the time to undo stops at the first crossing.

| cell | model | model W1 | nearest W1 | difference [95% CI] |
|---|---|---|---|---|
| big_cluster, tight | foodmatch | 8.990 | 4.850 | +4.14 [+4.06, +4.21] |
| big_cluster, tight | forecast | 4.810 | 4.850 | -0.04 [-0.07, -0.00] |
| big_cluster, tight | backpressure | 4.620 | 4.850 | -0.23 [-0.27, -0.19] |
| big_cluster, tight | xu | 6.600 | 4.850 | +1.75 [+1.68, +1.82] |
| big_cluster, tight | li | 9.020 | 4.850 | +4.17 [+4.09, +4.25] |
| big_cluster, tight | jahanshahi | 4.820 | 4.850 | -0.03 [-0.07, +0.01] |
| big_cluster, tight | auad | 6.190 | 4.850 | +1.34 [+1.21, +1.46] |
| big_cluster, tight | zhu | 4.850 | 4.850 | -0.00 [-0.07, +0.06] |
| big_cluster, tight | jusup | 5.220 | 4.850 | +0.37 [+0.31, +0.43] |
| big_cluster, normal | foodmatch | 13.590 | 13.690 | -0.10 [-0.13, -0.06] |
| big_cluster, normal | forecast | 14.080 | 13.690 | +0.40 [+0.37, +0.42] |
| big_cluster, normal | backpressure | 12.730 | 13.690 | -0.96 [-0.99, -0.93] |
| big_cluster, normal | xu | 9.140 | 13.690 | -4.55 [-4.61, -4.50] |
| big_cluster, normal | li | 12.450 | 13.690 | -1.24 [-1.27, -1.20] |
| big_cluster, normal | jahanshahi | 13.630 | 13.690 | -0.06 [-0.08, -0.03] |
| big_cluster, normal | auad | 13.650 | 13.690 | -0.04 [-0.07, -0.01] |
| big_cluster, normal | zhu | 8.500 | 13.690 | -5.19 [-5.28, -5.10] |
| big_cluster, normal | jusup | 8.250 | 13.690 | -5.44 [-5.53, -5.34] |
| big_cluster, loose | foodmatch | 15.990 | 16.620 | -0.63 [-0.66, -0.61] |
| big_cluster, loose | forecast | 16.980 | 16.620 | +0.36 [+0.34, +0.38] |
| big_cluster, loose | backpressure | 15.720 | 16.620 | -0.91 [-0.93, -0.89] |
| big_cluster, loose | xu | 12.750 | 16.620 | -3.87 [-3.92, -3.83] |
| big_cluster, loose | li | 15.310 | 16.620 | -1.31 [-1.34, -1.29] |
| big_cluster, loose | jahanshahi | 16.560 | 16.620 | -0.06 [-0.08, -0.05] |
| big_cluster, loose | auad | 16.630 | 16.620 | +0.00 [-0.02, +0.03] |
| big_cluster, loose | zhu | 4.770 | 16.620 | -11.86 [-11.91, -11.81] |
| big_cluster, loose | jusup | 8.670 | 16.620 | -7.96 [-8.02, -7.89] |
| three_clusters, tight | foodmatch | 7.990 | 4.690 | +3.30 [+3.22, +3.37] |
| three_clusters, tight | forecast | 4.490 | 4.690 | -0.21 [-0.24, -0.17] |
| three_clusters, tight | backpressure | 4.550 | 4.690 | -0.14 [-0.17, -0.11] |
| three_clusters, tight | xu | 5.240 | 4.690 | +0.54 [+0.47, +0.61] |
| three_clusters, tight | li | 5.740 | 4.690 | +1.04 [+0.97, +1.11] |
| three_clusters, tight | jahanshahi | 4.710 | 4.690 | +0.02 [-0.02, +0.05] |
| three_clusters, tight | auad | 5.420 | 4.690 | +0.72 [+0.62, +0.84] |
| three_clusters, tight | zhu | 4.990 | 4.690 | +0.29 [+0.25, +0.34] |
| three_clusters, tight | jusup | 5.410 | 4.690 | +0.72 [+0.67, +0.76] |
| three_clusters, normal | foodmatch | 12.720 | 10.830 | +1.89 [+1.83, +1.95] |
| three_clusters, normal | forecast | 10.720 | 10.830 | -0.11 [-0.15, -0.08] |
| three_clusters, normal | backpressure | 10.520 | 10.830 | -0.31 [-0.35, -0.26] |
| three_clusters, normal | xu | 11.010 | 10.830 | +0.18 [+0.11, +0.26] |
| three_clusters, normal | li | 10.640 | 10.830 | -0.19 [-0.24, -0.14] |
| three_clusters, normal | jahanshahi | 10.800 | 10.830 | -0.03 [-0.06, -0.00] |
| three_clusters, normal | auad | 11.430 | 10.830 | +0.60 [+0.54, +0.66] |
| three_clusters, normal | zhu | 7.160 | 10.830 | -3.67 [-3.74, -3.60] |
| three_clusters, normal | jusup | 10.310 | 10.830 | -0.52 [-0.59, -0.44] |
| three_clusters, loose | foodmatch | 15.220 | 15.280 | -0.06 [-0.09, -0.04] |
| three_clusters, loose | forecast | 15.240 | 15.280 | -0.04 [-0.06, -0.02] |
| three_clusters, loose | backpressure | 14.920 | 15.280 | -0.36 [-0.38, -0.34] |
| three_clusters, loose | xu | 13.650 | 15.280 | -1.63 [-1.67, -1.60] |
| three_clusters, loose | li | 14.740 | 15.280 | -0.54 [-0.56, -0.51] |
| three_clusters, loose | jahanshahi | 15.240 | 15.280 | -0.04 [-0.06, -0.03] |
| three_clusters, loose | auad | 15.410 | 15.280 | +0.13 [+0.11, +0.16] |
| three_clusters, loose | zhu | 11.780 | 15.280 | -3.50 [-3.55, -3.46] |
| three_clusters, loose | jusup | 12.520 | 15.280 | -2.76 [-2.81, -2.71] |
| mixed, tight | foodmatch | 6.560 | 4.570 | +1.99 [+1.93, +2.05] |
| mixed, tight | forecast | 4.480 | 4.570 | -0.09 [-0.12, -0.06] |
| mixed, tight | backpressure | 4.340 | 4.570 | -0.23 [-0.26, -0.20] |
| mixed, tight | xu | 5.490 | 4.570 | +0.92 [+0.86, +0.97] |
| mixed, tight | li | 5.300 | 4.570 | +0.73 [+0.67, +0.79] |
| mixed, tight | jahanshahi | 4.540 | 4.570 | -0.04 [-0.07, -0.00] |
| mixed, tight | auad | 4.680 | 4.570 | +0.11 [+0.05, +0.17] |
| mixed, tight | zhu | 5.100 | 4.570 | +0.52 [+0.47, +0.58] |
| mixed, tight | jusup | 5.570 | 4.570 | +1.00 [+0.94, +1.06] |
| mixed, normal | foodmatch | 9.190 | 8.500 | +0.69 [+0.66, +0.73] |
| mixed, normal | forecast | 9.190 | 8.500 | +0.69 [+0.65, +0.72] |
| mixed, normal | backpressure | 7.810 | 8.500 | -0.69 [-0.72, -0.65] |
| mixed, normal | xu | 9.180 | 8.500 | +0.68 [+0.64, +0.73] |
| mixed, normal | li | 7.480 | 8.500 | -1.02 [-1.06, -0.98] |
| mixed, normal | jahanshahi | 8.450 | 8.500 | -0.05 [-0.08, -0.02] |
| mixed, normal | auad | 8.380 | 8.500 | -0.11 [-0.15, -0.07] |
| mixed, normal | zhu | 5.760 | 8.500 | -2.74 [-2.87, -2.60] |
| mixed, normal | jusup | 7.670 | 8.500 | -0.82 [-0.90, -0.75] |
| mixed, loose | foodmatch | 11.860 | 11.730 | +0.13 [+0.10, +0.15] |
| mixed, loose | forecast | 12.300 | 11.730 | +0.57 [+0.55, +0.59] |
| mixed, loose | backpressure | 11.350 | 11.730 | -0.38 [-0.41, -0.36] |
| mixed, loose | xu | 11.430 | 11.730 | -0.31 [-0.35, -0.26] |
| mixed, loose | li | 10.570 | 11.730 | -1.16 [-1.19, -1.13] |
| mixed, loose | jahanshahi | 11.690 | 11.730 | -0.04 [-0.06, -0.03] |
| mixed, loose | auad | 11.670 | 11.730 | -0.06 [-0.08, -0.04] |
| mixed, loose | zhu | 7.780 | 11.730 | -3.95 [-4.00, -3.90] |
| mixed, loose | jusup | 9.000 | 11.730 | -2.74 [-2.80, -2.68] |

## Secondary: does W1 agree with total variation, uncovered share and idle-weighted W1?

Sign agreement over the established W1 cells. On Q2 the W1 metric is the 60-min window and the secondary metrics are evening means.

| family | secondary | agrees | disagrees |
|---|---|---|---|
| E1 | tv | 20 | 10 |
| E1 | uncovered | 26 | 4 |
| E1 | w1_idle_weighted_min | 29 | 1 |
| E2 | tv | 58 | 19 |
| E2 | uncovered | 66 | 11 |
| E2 | w1_idle_weighted_min | 60 | 17 |

## Profile: cells per class

Q3 is the cost reading of the joint reading on p90, applied to every primary cell: no delivery cost when the interval's upper end is below +1 min, a delivery cost when an established difference is at least +1 min, unresolved otherwise.

**Q1**

| model | does not prevent | prevents at a delivery cost | prevents at no delivery cost |
|---|---|---|---|
| auad | 6 | 0 | 0 |
| backpressure | 4 | 0 | 2 |
| foodmatch | 6 | 0 | 0 |
| forecast | 2 | 0 | 4 |
| jusup | 6 | 0 | 0 |
| li | 2 | 0 | 4 |
| xu | 4 | 1 | 1 |
| zhu | 6 | 0 | 0 |

**Q2**

| model | does not undo | undoes at a delivery cost | undoes at no delivery cost |
|---|---|---|---|
| auad | 10 | 0 | 0 |
| backpressure | 10 | 0 | 0 |
| foodmatch | 10 | 0 | 0 |
| forecast | 10 | 0 | 0 |
| jusup | 5 | 0 | 5 |
| li | 10 | 0 | 0 |
| xu | 6 | 2 | 2 |
| zhu | 10 | 0 | 0 |

**Q3**

| model | delivery cost | no delivery cost |
|---|---|---|
| auad | 0 | 16 |
| backpressure | 0 | 16 |
| foodmatch | 2 | 14 |
| forecast | 0 | 16 |
| jusup | 0 | 16 |
| li | 0 | 16 |
| xu | 12 | 4 |
| zhu | 0 | 16 |

**Q2 fresh block (R4)**

| model | does not undo |
|---|---|
| backpressure | 10 |
| foodmatch | 10 |
| forecast | 10 |

**Q3 fresh block (R4)**

| model | delivery cost | no delivery cost |
|---|---|---|
| backpressure | 0 | 10 |
| foodmatch | 2 | 8 |
| forecast | 0 | 10 |

## R3 equivalence reading, counts per family

| family | equivalent within delta | not read: established |
|---|---|---|
| E1 | 4 | 56 |
| E2 | 8 | 125 |
| E2-fresh, frozen three only (R4) | 6 | 54 |

## Zhu with random partition ties (post-freeze sensitivity, outside every family)

| variant | start | W1 | W1, first 60 min | time to undo | p90 | unassigned >30 min | couriers owning no cell per step | commands per step | time to undo, median | censored share |
|---|---|---|---|---|---|---|---|---|---|---|
| Zhu, random ties (sensitivity) | big_cluster | 11.503 | 21.200 | 76.000 | 42.861 | 0.000 | 449.161 | 648.237 | 76.000 | 0.000 |
| Zhu, random ties (sensitivity) | meetup | 6.972 | 9.842 | 120.000 | 35.826 | 0.000 | 340.583 | 873.714 | 120.000 | 1.000 |
| Zhu, lower-index ties (frozen) | big_cluster | 11.524 | 21.200 | 73.767 | 43.485 | 0.000 | 573.305 | 566.880 | 74.000 | 0.000 |
| Zhu, lower-index ties (frozen) | meetup | 6.986 | 9.872 | 120.000 | 35.831 | 0.000 | 507.842 | 769.732 | 120.000 | 1.000 |
| Nearest courier | big_cluster | 12.346 | 21.412 | 74.300 | 43.606 | 0.000 | nan | nan | 74.000 | 0.000 |
| Nearest courier | meetup | 6.126 | 8.474 | 120.000 | 35.833 | 0.000 | nan | nan | 120.000 | 1.000 |

## Training budgets

| model | training_seeds | episodes_per_seed | wall_hours | wall_hours_scope | other_runs | convergence | demand_information | folder |
|---|---|---|---|---|---|---|---|---|
| xu | 1 2 3 4 5 | 200 | 1.540 | final run only | the final run is the curve re-run with the planner of Eqs. 6-8 (92 min, a pause for the core limit inside); an earlier run failed at its end and lost its 1,000 collection episodes (time not recorded) | fixed budget of 200 peaks per seed (X3 ruling); validation curve every 25 peaks, flat from 25 on; value table mean absolute change between checkpoints 0.077 to 0.018 (G6) | none at decision time: a value table by H3 resolution-8 zone and 5-min slot, learned offline from 200 peaks under nearest courier | avaliacao/20261103-1021-training-xu |
| li | 1 2 3 4 5 | 200 | 4.810 | final run only | none recorded | fixed budget of 200 interacting peaks per seed (X3 ruling); validation curve every 25 peaks | expected pickups over the next 30 min by zone from the demand model (code: `models/li_meanfield.py`, `expected_pickups(t, t + 1800)`), for the destination potential of Eq. 3, with the open orders and couriers | avaliacao/20261103-1449-training-li |
| jahanshahi | 1 2 3 4 5 | 200 | 6.700 | final run only | a first configuration was stopped at about 11 min per peak (time not recorded; X3) | fixed budget of 200 interacting peaks per seed (X3 ruling), epsilon 1.0 to 0.05 over the first 100; validation curve every 25 peaks | none: the only input is each pair's expected delivery time delta (Eq. 1) | avaliacao/20261103-1449-training-dqn |
| auad | 1 2 3 4 5 | 200 | 0.710 | final run only | first training with scaled features, discarded (5.26 h); configuration grid on training seed 1 (1.04 h) | 200 peaks per seed with the theta_best gate after each (Algorithm 1); configuration alpha 1e-7, n = 1000, memory 3000 from the paper's grid on training seed 1 (G6) | none: 14 raw state counts (active and open orders per courier, deadline buckets, couriers with no offer, mean restaurant-to-customer distance) | avaliacao/20261103-2154-training-auad |
| jusup | 1 2 3 4 5 | at most 1000 epochs | 0.310 | final run only | two earlier trainings superseded by objective fixes (0.32 h and 0.68 h) | early stopping on the validation objective, at most 1,000 epochs (stops at 361 to 727, X5) | expected orders per zone and 20-min step from the demand model, and the idle courier mass per zone | avaliacao/20261104-0040-training-jusup |
| forecast | not learned | not learned | not learned | not learned | not learned | not learned | the rates of Ozkan and Ward's Remark 3 from the demand model: expected pickups per minute by restaurant zone and expected drop-offs per minute by customer zone, per 15-min bin | none (not learned) |

Wall hours are the final run's only; `other_runs` lists the runs behind it. Learning curves (means over the validation seeds): `learning_curves.csv`; Jusup et al.'s validation objective per epoch: `learning_curves_jusup_epochs.csv`.

This research was supported by data provided by Meituan.
