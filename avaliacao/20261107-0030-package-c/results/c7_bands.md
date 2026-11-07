## C7. The fitted behavior's bands on a wider grid (Paper A, Table 1)

This research was supported by data provided by Meituan.

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

This research was supported by data provided by Meituan.
