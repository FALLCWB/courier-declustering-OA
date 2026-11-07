# Jusup et al., adaptation 10: couriers reached per policy step

This research was supported by data provided by Meituan.

Seeds 1001 to 1150. A courier is reached when the zone where it is counted in the idle mass (its current cell) differs from the zone whose leave probability applies to it (the cell it can start from). A policy step runs at the first 30-s epoch with at least one obedient idle courier, 20 min or more after the previous step, so tight supply, with stretches of no idle courier, takes fewer steps. Per cell: policy steps taken, obedient idle couriers per step taken, those reached, their share, and the largest count in one step over all episodes.

| Start | Supply | Behavior | Obedience | Episodes | Policy steps taken per episode | Idle obedient per step | Reached per step | Share | Max in one step |
|---|---|---|---|---|---|---|---|---|---|
| big_cluster | loose | fitted | 1.00 | 150 | 15.4 | 2103.2 | 6.00 | 0.29% | 52 |
| big_cluster | normal | fitted | 1.00 | 150 | 15.4 | 1368.4 | 3.95 | 0.29% | 43 |
| big_cluster | tight | fitted | 1.00 | 150 | 10.3 | 1185.0 | 3.41 | 0.29% | 36 |
| burst | loose | fitted | 1.00 | 150 | 15.4 | 2171.5 | 5.07 | 0.23% | 18 |
| burst | normal | fitted | 1.00 | 150 | 15.5 | 1463.4 | 3.53 | 0.24% | 15 |
| burst | tight | fitted | 1.00 | 150 | 12.6 | 1041.4 | 2.22 | 0.21% | 12 |
| meetup | normal | fitted | 1.00 | 150 | 15.4 | 1478.1 | 3.49 | 0.24% | 15 |
| mixed | loose | fitted | 1.00 | 150 | 15.4 | 2174.5 | 6.43 | 0.30% | 37 |
| mixed | normal | fitted | 1.00 | 150 | 15.4 | 1448.9 | 4.00 | 0.28% | 25 |
| mixed | tight | fitted | 1.00 | 150 | 11.8 | 1078.1 | 2.68 | 0.25% | 19 |
| scattered | loose | fitted | 1.00 | 150 | 15.4 | 2184.0 | 5.15 | 0.24% | 18 |
| scattered | normal | fitted | 1.00 | 150 | 15.4 | 1478.3 | 3.64 | 0.25% | 16 |
| scattered | tight | fitted | 1.00 | 150 | 15.2 | 937.5 | 2.17 | 0.23% | 16 |
| three_clusters | loose | fitted | 1.00 | 150 | 15.4 | 2149.5 | 13.59 | 0.63% | 74 |
| three_clusters | normal | fitted | 1.00 | 150 | 15.4 | 1409.8 | 8.41 | 0.60% | 53 |
| three_clusters | tight | fitted | 1.00 | 150 | 11.3 | 1091.0 | 4.48 | 0.41% | 39 |
