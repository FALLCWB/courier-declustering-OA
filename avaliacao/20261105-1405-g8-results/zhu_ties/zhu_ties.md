# Zhu et al. with random partition ties (post-freeze sensitivity, descriptive)

Outside every family; changes no confirmatory number (Filipe, 2026-11-04). Normal supply, fitted behavior, 100% obedience, seeds 1001 to 1030. The frozen rule sends a cell tied between closest couriers to the lower courier index, so couriers in one cell leave one per 30-s step; the sensitivity draws the winner of each tied cell at random from the episode's own stream.

| Variant | Start | W1 | W1, first 60 min | Time to undo, median (censored) | p90 | Unassigned >30 min | Own no cell per step |
|---|---|---|---|---|---|---|---|
| Zhu, random ties (sensitivity) | big_cluster | 11.50 | 21.20 | 76 (0%) | 42.86 | 0.0% | 449 |
| Zhu, random ties (sensitivity) | meetup | 6.97 | 9.84 | 120 (100%) | 35.83 | 0.0% | 341 |
| Zhu, lower-index ties (frozen) | big_cluster | 11.52 | 21.20 | 74 (0%) | 43.48 | 0.0% | 573 |
| Zhu, lower-index ties (frozen) | meetup | 6.99 | 9.87 | 120 (100%) | 35.83 | 0.0% | 508 |
| Nearest courier | big_cluster | 12.35 | 21.41 | 74 (0%) | 43.61 | 0.0% | none |
| Nearest courier | meetup | 6.13 | 8.47 | 120 (100%) | 35.83 | 0.0% | none |

Random minus frozen, paired by seed (95% bootstrap interval):

| Start | Metric | Difference | 95% CI |
|---|---|---|---|
| big_cluster | W1 | -0.021 | -0.057 to +0.015 |
| big_cluster | W1, first 60 min | +0.000 | -0.011 to +0.012 |
| big_cluster | time to undo | +2.233 | +1.367 to +3.233 |
| big_cluster | p90 | -0.624 | -0.714 to -0.545 |
| big_cluster | unassigned >30 min | +0.000 | +0.000 to +0.000 |
| big_cluster | couriers owning no cell per step | -124.144 | -126.499 to -122.039 |
| big_cluster | commands per step | +81.357 | +79.190 to +83.619 |
| meetup | W1 | -0.014 | -0.030 to +0.002 |
| meetup | W1, first 60 min | -0.030 | -0.068 to +0.009 |
| meetup | time to undo | +0.000 | +0.000 to +0.000 |
| meetup | p90 | -0.005 | -0.013 to +0.002 |
| meetup | unassigned >30 min | +0.000 | +0.000 to +0.000 |
| meetup | couriers owning no cell per step | -167.259 | -169.895 to -164.801 |
| meetup | commands per step | +103.982 | +102.291 to +105.739 |

This research was supported by data provided by Meituan.
