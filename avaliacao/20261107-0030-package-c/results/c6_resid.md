This research was supported by data provided by Meituan.

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

This research was supported by data provided by Meituan.
