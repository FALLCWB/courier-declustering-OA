## The Ashkrof variant's bands on a wider grid

This research was supported by data provided by Meituan.

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

This research was supported by data provided by Meituan.
