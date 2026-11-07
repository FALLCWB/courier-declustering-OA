# Package C status (courier declustering, response to the external review)

This research was supported by data provided by Meituan.

Updated 2026-11-07 15:45. Package C is complete: parts 1 to 5, C6, C7 and part 3 again at the wide-grid values. G10 filed (`G10-request.pdf` here); the open-access refresh follows.

## Waiting on Filipe

Nothing blocks anything; G10 is not a stop.

1. **G10 is filed:** `G10-request.pdf` in this folder. It asks five questions on how Paper A states Q2, arm C's evening edge, Table 1, the noise result and C6; each has my proposal.
2. **Everything is ready to read** in `paper-numbers-C.pdf` (summary on page 1) and one CSV per table.
3. **C7, for Table 1:** the frozen values lie inside the wide-grid bands (the decision delay, 42 s, on its band's upper end), but the best point moves (cruise radius 2,000 to 2,800 m, beta0 -3.0 to -3.5), and the beta0 band widens to at least [-6.0, -2.5]. The Table 1 fit predates the per-gap behavior draws (S8 review fixes), the probable cause; G4 and G5 kept it without a refit, so C7 is also that refit at the current code. Nothing in the frozen behavior changes (your rule).

## C7 in one screen (Table 1 bands on a wide grid, 4,231 points)

| Parameter | Table 1 band | Wide-grid band | Point: Table 1, wide |
|---|---|---|---|
| Return probability | [0.675, 0.825] | [0.675, 0.825] | 0.75, 0.75 |
| Decision delay (s) | [29.4, 42] | [29.4, 42] | 42, 42 |
| Cruise radius (m) | [2,000, 2,800] | [1,979, 2,800] | 2,000, 2,800 |
| Stay constant (beta0) | [-3.5, -2.0] | at least [-6.0, -2.5] | -3.0, -3.5 |

No band end touches the wide grid (explored: 0.45 to 0.975; 15 to 117.6 s; 714 to 7,056 m; -6.5 to -1.0). The beta0 lower end is one value from the edge, and its tail values were tried at 18 points each, so it may be lower still.

Code review of the extra parts (five agents): no wrong number, class or band; fixes and corrections in the decision log.

## E6 in one screen (confirmatory, n = 150, Holm within E6)

| Item | Result |
|---|---|
| Contrasts | 144; 141 established; the 3 not established are equivalent within delta (R3) |
| Classes | no model undoes the cluster in any of the 9 cells (72 of 72 "does not undo") |
| Against the classes Paper A quotes | 8 change, all from "undoes" to "does not undo": Xu on the mixed start (3 cells), Jusup on three clusters at normal and loose supply and on the mixed start (5 cells) |
| Xu | still lowers W1 over the first 60 min in all 9 cells (-0.42 to -1.41 min, established), below the smallest effect (1.53 to 2.23 min) |
| Jusup | raises W1 over the first 60 min wherever it undid under the fitted behavior (+1.40 to +2.97 min) |
| Nearest courier itself | W1 over the first 60 min is 1.3 to 5.3 min lower than with homes in the cluster: drift home now disperses the fleet |
| Evening (20:00 to 20:59, secondary) | arm C's evening edge reverses: Zhu +0.4 to +7.6 min, Jusup +0.8 to +8.3 min; Li -0.1 to -1.3 |
| p90 | Xu, Li and FoodMatch lower p90 by 5.9 to 9.6 min on the big cluster and three clusters at tight supply |

## `stay` in one screen (exploratory, n = 150, no test)

`stay`: nearest-courier assignment, and every obedient idle courier stays where it is (arm C with no command). Differences paired by seed, in minutes; lower is better.

| Question | Result on the 10 Q2 cells |
|---|---|
| Does holding couriers still undo the cluster in the first hour? (`stay` - nearest) | No: W1 over 60 min -0.20 to +0.08 on the 9 clustered starts; +1.92 on the meet-up |
| Does it explain arm C's evening edge? (`stay` - nearest, 20:00 to 20:59) | Largely, where the fleet drifts back: -11.42 (big cluster, loose), -4.54, -3.63, -3.18, -3.17, -2.13; it raises evening W1 elsewhere (+0.33 to +2.95) |
| What does Zhu's repositioning add? (Zhu - `stay`) | Little: W1 over 60 min -0.53 to +0.04; evening -0.32 to -0.65 |
| What does Jusup's repositioning add? (Jusup - `stay`) | It undoes beyond holding: W1 over 60 min -0.65 to -3.07 on three clusters and the mixed start, -1.85 on the big cluster at loose supply; p90 -0.65 to -3.11 |
| Km without an order per order | `stay` saves 1.9 to 3.4 km; Zhu adds 0.2 to 0.7 and Jusup 0.8 to 3.1 on top |

## Noisy demand in one screen (exploratory, seeds 1001 to 1030, no test)

| Item | Result |
|---|---|
| Classes (4 models x 16 cells) | 0 of 64 change between noisy and true input |
| W1 contrast, noisy minus true | within -0.02 to +0.09 min |
| p90 contrast, noisy minus true | within -0.12 to +0.19 min |
| Li et al. | all 480 episodes equal the true-input ones: it reads the expected demand only in its training reward |

## Ashkrof setting in one screen (exploratory, seeds 1001 to 1030, no test)

| Item | Result |
|---|---|
| Recalibration (part-time coefficient 0) | return probability 0.75 [0.65, 0.85], beta0 -3.0 [-4.0, -2.0]: the fitted values; the beta0 interval reached both grid ends |
| Same recalibration on a wide grid | return probability 0.75 [0.675, 0.85], beta0 **-4.5**, band at least [-6.5, -2.74] |
| Part 3 again at beta0 -4.5 | 0 of 128 classes change (against the fitted behavior and the first runs); contrasts move by at most 0.2 min |
| Classes (8 models x 16 cells) | 0 of 128 change against the fitted behavior at the same seeds |
| Contrasts, Ashkrof minus fitted | W1 -0.03 to +0.02, W1 over 60 min -0.10 to +0.01, p90 -0.29 to +0.24 min |
| Nearest courier's own W1 | within 0.05 min of the fitted behavior in every cell |

## C6 in one screen (exploratory, declared after E6 was seen, seeds 1001 to 1030, no test)

Homes drawn where the customers are (expected drop-offs, 17:00 to 21:00), beside E6 (`indep`) and the fitted setting at the same seeds.

| Item | `resid` | `indep` (E6) | fitted |
|---|---|---|---|
| Cell-model pairs that undo (of 72) | 0 | 0 | 7 (Xu 3, Jusup 4) |
| Nearest courier's W1 over the first 60 min | 10.3 to 17.8 | 10.7 to 18.3 | 15.4 to 22.3 |
| Zhu, evening W1 (mean of 9 cells) | +2.24 | +2.86 | -3.37 |
| Jusup, evening W1 (mean of 9 cells) | +3.57 | +4.19 | -2.05 |

E6's result comes from homes lying outside the cluster, not from homes lying at the demand: `resid` and `indep` agree within 0.5 min for nearest courier and give the same classes.

## Milestones

| Part | What | State |
|---|---|---|
| 5 | Tables from the existing runs (windows, evening without 20:30, per policy, evening by return) | done 2026-11-07 00:30 |
| 0 | Addendum C committed before any new row | done, ed05df2 |
| 1 | E6, confirmatory: `indep` homes, 9 clustered cells x 10 models x 150 seeds (13,500 episodes) | done 2026-11-07 06:30 (348 min); analysed |
| 2 | `stay` without commands, 16 cells x 150 seeds (2,400) | done 2026-11-07 07:00 (33 min); analysed |
| 4 | Noisy demand input (CV 0.2 per zone), 4 models x 16 cells x 30 seeds (1,920) | done 2026-11-07 08:15 (75 min); analysed |
| 3 | Ashkrof setting: recalibration of beta0 and the return probability, then 10 models x 16 cells x 30 seeds (4,800) | done 2026-11-07 10:30 (fit 3 min, runs 131 min); analysed |
| C6 | Homes where customers live (`resid`), exploratory, 9 clustered cells x 10 models x 30 seeds (2,700) | done 2026-11-07 11:45 (S8 regression 100 of 100 equal; runs 74 min); analysed |
| C7 | Table 1 bands on a wider grid (4,231 points with the band rounds) | done 2026-11-07 13:18 (86 min) |
| Ashkrof wide | The Ashkrof interval on a wider grid (97 points) | done 2026-11-07 12:00: beta0 moved to -4.5 |
| Part 3 again | 4,800 episodes at the wide-grid Ashkrof values (`ashkrofw`) | done 2026-11-07 15:30 (131 min); analysed |
| G10 | `reviews/G10-request.md`, filed when all parts are in (not a stop) | filed 2026-11-07 |
| OA | Refresh of the private FALLCWB/courier-declustering-OA | after G10 |

All runs on FE-SIM-1 under the CPU rule (at most 24 busy CPUs), no PC share, no GPU.

## Files

- `paper-numbers-C.md` and `.pdf`: summary first, then each part; parts not yet run say "pending".
- One CSV per table: `c1_e6_*`, `c2_stay`, `c3_ashkrof_*`, `c4_noise_*` and `c5_*`; `c6_resid_*`, `c7_bands`, `c3_ashkrof_bands`, `c3w_ashkrof_*`.
- Code review of package C (five agents): no wrong number or class; fixes recorded in the study's decision log.
- `preregistration-addendum-C.pdf`: what each part was declared to test, before its episodes.

This research was supported by data provided by Meituan.
