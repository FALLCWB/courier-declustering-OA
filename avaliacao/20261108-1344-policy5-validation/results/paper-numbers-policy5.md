# Policy 5 on validation seeds disjoint from its training

This research was supported by data provided by Meituan.

Exploratory, outside every family. Question, seeds and reading rule declared in `DECISIONS.md` at commit **5a15a35**, before any episode (Filipe, 2026-11-08: "Package B").

## Summary

| Question | Answer |
|---|---|
| Does any choice for training seed 5 use 95001 to 95003? | No. Xu, Li and the DQN keep their final state, Auad's theta_best is chosen on gate seed 97005, and the shared Auad configuration was chosen with policy 1 |
| Reading rule | Policy 5 reads as **unaffected** by the overlap: Xu et al. W1 gap -0.067 (policies 1 to 4: -0.222 to -0.096), p90 gap -1.153 (-0.864 to -0.711); Li et al. W1 gap 0.006 (policies 1 to 4: -0.037 to 0.010), p90 gap -0.258 (-0.242 to -0.191); Deep Q-network W1 gap 0.053 (policies 1 to 4: -0.017 to 0.016), p90 gap -0.359 (-0.392 to -0.308); Auad et al. W1 gap -0.024 (policies 1 to 4: -0.012 to 0.039), p90 gap -0.549 (-0.530 to -0.327) |
| Policy 5's curve on 95501 to 95503 | Largest move of W1 from its peak-25 value: Xu et al. 0.120 min (peak 50); Li et al. 0.024 min (peak 100); Deep Q-network 0.084 min (peak 175); Auad et al. 0.000 min (peak 50) |
| Where 35.9 min comes from | The calibration run of 2026-11-02 (normal supply, seeds 201 to 210): mean of per-episode p90 35.896, p90 of pooled orders 35.896; the 35.8 of Results is the mean of per-episode p90 on seeds 1001 to 1150 (35.828) |

Policy 5 reads as **unaffected** by the overlap under the declared rule: for every model, its gap lies within the range of policies 1 to 4, widened by 0.10 min for W1 and 0.5 min for p90.

Before the widening, policy 5's gap lies outside the range of policies 1 to 4 in 6 of 8 checks; a fifth value drawn like the other four falls outside their range with probability 2/5, about 3.2 of 8. Of these, 4 lie below the range (policy 5 relatively lower on 95001 to 95003, its training seeds) and 2 above it; the distances are Xu et al. W1 0.030 (above), Xu et al. p90 0.289 (below), Li et al. p90 0.016 (below), Deep Q-network W1 0.037 (above), Auad et al. W1 0.012 (below), Auad et al. p90 0.019 (below) min.

## 1. What the code keeps, and which seeds its choices used

| Model | Kept state and seeds |
|---|---|
| Xu et al. | Keeps the final value table, fitted once on the nearest-courier transitions of all 200 peaks; training seed 5's peaks ran on episode seeds 95000 to 95199, and no choice reads any validation seed (the curve is recorded, never used). |
| Li et al. | Keeps the actor after peak 200 (final); training seed 5 trains on 95000 to 95199 with a temperature schedule fixed by the peak count, and no choice reads any validation seed. |
| Deep Q-network | Keeps the network after peak 200 (final); training seed 5 trains on 95000 to 95199 with an epsilon schedule fixed by the peak count, and no choice reads any validation seed. |
| Auad et al. | Keeps theta_best, the theta with the lowest cost on the gate peak, which for training seed 5 is seed 97005 (big-cluster start, normal supply); training seed 5 trains on 95000 to 95199; the configuration (alpha 1e-7, m 3,000, n 1,000) was chosen once from training seed 1 (seeds 91000 to 91199) by its cost on 95001 to 95003 and holds for all five policies, so no policy-5 state ran in any choice on those seeds. |
| Jusup et al. | Keeps the epoch with the best validation objective on 95001 to 95003 (mean-field rollouts from those seeds' start positions); training seed 5 trains on seeds 103000 to 103726 (98000 + 1000 k + epoch, 727 epochs), disjoint from the validation seeds, so it is not affected and does not run here. |

No choice for training seed 5 used 95001 to 95003, so the check ran.

## 2. What ran

- 288 episodes on FE-SIM-1 (`sim/policy5_validation.py`, 20 workers, one BLAS thread per process): the curve code's validation cases (big-cluster and scattered starts, normal supply, fitted behavior) on seeds 95501 to 95503, which no training, gate or choice of these four models ever ran.
- Policy 5 at every checkpoint (25 to 200 peaks): the recorded checkpoint files of Li, the DQN and Auad; Xu's tables refit from the recorded transitions (the refit at 200 peaks equals the kept table bit for bit). Policies 1 to 4 at the kept state. Each episode is the call the training code's own evaluation makes (a test checks it).
- The rows for 95001 to 95003 are the existing curve rows. At one BLAS thread the current code reproduces them: the budget check's peak-200 rows of policy 1 equal them bit for bit.

## 3.1 Kept state, mean over the six cases (minutes; Auad's cost in its own units)

| Model | Policy | W1, 95001-95003 | W1, 95501-95503 | p90, 95001-95003 | p90, 95501-95503 | Auad cost, 95001-95003 | Auad cost, 95501-95503 |
|---|---|---|---|---|---|---|---|
| Xu et al. | 1 | 8.604 | 8.701 | 47.00 | 47.86 |  |  |
| Xu et al. | 2 | 8.665 | 8.769 | 47.89 | 48.64 |  |  |
| Xu et al. | 3 | 8.507 | 8.729 | 47.54 | 48.25 |  |  |
| Xu et al. | 4 | 8.635 | 8.757 | 47.57 | 48.36 |  |  |
| Xu et al. | 5 | 8.669 | 8.736 | 46.39 | 47.54 |  |  |
| Li et al. | 1 | 7.784 | 7.790 | 39.73 | 39.97 |  |  |
| Li et al. | 2 | 7.810 | 7.846 | 39.68 | 39.87 |  |  |
| Li et al. | 3 | 7.813 | 7.803 | 39.71 | 39.92 |  |  |
| Li et al. | 4 | 7.828 | 7.829 | 39.69 | 39.91 |  |  |
| Li et al. | 5 | 7.809 | 7.803 | 39.66 | 39.92 |  |  |
| Deep Q-network | 1 | 8.384 | 8.400 | 39.59 | 39.96 |  |  |
| Deep Q-network | 2 | 8.403 | 8.387 | 39.63 | 39.94 |  |  |
| Deep Q-network | 3 | 8.388 | 8.388 | 39.59 | 39.98 |  |  |
| Deep Q-network | 4 | 8.430 | 8.432 | 39.59 | 39.95 |  |  |
| Deep Q-network | 5 | 8.406 | 8.353 | 39.62 | 39.98 |  |  |
| Auad et al. | 1 | 8.455 | 8.415 | 40.14 | 40.66 | 88,916.6 | 96,413.0 |
| Auad et al. | 2 | 8.544 | 8.509 | 40.46 | 40.79 | 122,906.2 | 129,858.7 |
| Auad et al. | 3 | 8.468 | 8.479 | 40.18 | 40.71 | 89,185.5 | 97,014.2 |
| Auad et al. | 4 | 8.467 | 8.442 | 40.27 | 40.67 | 90,072.3 | 97,358.1 |
| Auad et al. | 5 | 8.470 | 8.494 | 40.14 | 40.69 | 88,691.4 | 95,908.3 |

## 3.2 Gap, 95001-95003 minus 95501-95503, at the kept state

| Model | Metric | Policy 5 | Policies 1 to 4 | Beyond that range | Widened range | Within |
|---|---|---|---|---|---|---|
| Xu et al. | W1 | -0.067 | -0.222 to -0.096 | 0.030 (above) | -0.322 to 0.004 | yes |
| Xu et al. | p90 | -1.153 | -0.864 to -0.711 | 0.289 (below) | -1.364 to -0.211 | yes |
| Li et al. | W1 | 0.006 | -0.037 to 0.010 | 0 | -0.137 to 0.110 | yes |
| Li et al. | p90 | -0.258 | -0.242 to -0.191 | 0.016 (below) | -0.742 to 0.309 | yes |
| Deep Q-network | W1 | 0.053 | -0.017 to 0.016 | 0.037 (above) | -0.117 to 0.116 | yes |
| Deep Q-network | p90 | -0.359 | -0.392 to -0.308 | 0 | -0.892 to 0.192 | yes |
| Auad et al. | W1 | -0.024 | -0.012 to 0.039 | 0.012 (below) | -0.112 to 0.139 | yes |
| Auad et al. | p90 | -0.549 | -0.530 to -0.327 | 0.019 (below) | -1.030 to 0.173 | yes |
| Auad et al. | Auad cost | -7,216.9 | -7,828.7 to -6,952.5 | 0 |  | no rule (descriptive) |

## 3.3 Policy 5's curve (mean over the six cases)

| Model | Peak | W1, 95501-95503 | W1, 95001-95003 | Gap | p90, 95501-95503 | p90, 95001-95003 | Auad cost, 95501-95503 |
|---|---|---|---|---|---|---|---|
| Xu et al. | 25 | 8.786 | 8.752 | -0.034 | 46.65 | 46.21 |  |
| Xu et al. | 50 | 8.666 | 8.649 | -0.016 | 46.83 | 46.10 |  |
| Xu et al. | 75 | 8.747 | 8.613 | -0.134 | 47.13 | 46.24 |  |
| Xu et al. | 100 | 8.806 | 8.671 | -0.135 | 47.25 | 46.32 |  |
| Xu et al. | 125 | 8.698 | 8.654 | -0.044 | 47.81 | 46.69 |  |
| Xu et al. | 150 | 8.706 | 8.667 | -0.038 | 47.31 | 46.39 |  |
| Xu et al. | 175 | 8.734 | 8.708 | -0.026 | 47.67 | 46.51 |  |
| Xu et al. | 200 | 8.736 | 8.669 | -0.067 | 47.54 | 46.39 |  |
| Li et al. | 25 | 7.805 | 7.822 | 0.017 | 40.01 | 39.90 |  |
| Li et al. | 50 | 7.822 | 7.848 | 0.025 | 39.98 | 39.77 |  |
| Li et al. | 75 | 7.802 | 7.777 | -0.025 | 39.90 | 39.70 |  |
| Li et al. | 100 | 7.829 | 7.835 | 0.006 | 39.91 | 39.74 |  |
| Li et al. | 125 | 7.811 | 7.781 | -0.030 | 39.93 | 39.73 |  |
| Li et al. | 150 | 7.810 | 7.844 | 0.034 | 39.90 | 39.68 |  |
| Li et al. | 175 | 7.814 | 7.778 | -0.036 | 39.92 | 39.75 |  |
| Li et al. | 200 | 7.803 | 7.809 | 0.006 | 39.92 | 39.66 |  |
| Deep Q-network | 25 | 8.314 | 8.293 | -0.020 | 39.96 | 39.70 |  |
| Deep Q-network | 50 | 8.330 | 8.353 | 0.023 | 39.95 | 39.61 |  |
| Deep Q-network | 75 | 8.377 | 8.322 | -0.054 | 40.04 | 39.67 |  |
| Deep Q-network | 100 | 8.355 | 8.359 | 0.004 | 39.96 | 39.65 |  |
| Deep Q-network | 125 | 8.347 | 8.337 | -0.010 | 40.01 | 39.63 |  |
| Deep Q-network | 150 | 8.388 | 8.357 | -0.031 | 39.98 | 39.63 |  |
| Deep Q-network | 175 | 8.398 | 8.383 | -0.014 | 39.97 | 39.61 |  |
| Deep Q-network | 200 | 8.353 | 8.406 | 0.053 | 39.98 | 39.62 |  |
| Auad et al. | 25 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 50 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 75 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 100 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 125 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 150 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 175 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |
| Auad et al. | 200 | 8.494 | 8.470 | -0.024 | 40.69 | 40.14 | 95,908.3 |

Checkpoints 25 to 200 give identical rows for Auad et al.: they hold the same state on both seed sets.

Largest move of W1 from the peak-25 value, peaks 50 to 200:

| Model | 95501-95503 | At peak | 95001-95003 | At peak |
|---|---|---|---|---|
| Xu et al. | 0.120 | 50 | 0.139 | 75 |
| Li et al. | 0.024 | 100 | 0.045 | 75 |
| Deep Q-network | 0.084 | 175 | 0.112 | 200 |
| Auad et al. | 0.000 | 50 | 0.000 | 50 |

## 4. The 35.9 min of the threats paragraph

| Source | p90 order to door (min) | Runs | Seeds |
|---|---|---|---|
| calibration, mean of per-episode p90 | 35.90 | calibration `avaliacao/20261102-1026-calibration` (code 572610b): normal supply, 10 episodes, nearest idle courier, calibration's scattered start, every courier full-time and staying where it is while idle | 201 to 210 |
| calibration, p90 of pooled orders | 35.90 | calibration `avaliacao/20261102-1026-calibration` (code 572610b): normal supply, 10 episodes, nearest idle courier, calibration's scattered start, every courier full-time and staying where it is while idle | 201 to 210 |
| study runs, mean of per-episode p90 | 35.83 | frozen code, nearest courier, scattered start, normal supply, fitted behavior, 150 episodes | 1001 to 1150 |
| Meituan orders delivered alone, p90 of pooled orders | 41.08 | Meituan single-order waves, 17:00 to 20:59 |  |

The 35.9 min is the calibration run's p90 at normal supply, the number the calibration report prints beside Meituan's 41.1. Both statistics give it there: the mean of the ten per-episode p90 values and the p90 of the pooled orders round to 35.9. Meituan's 41.1 is the p90 of pooled orders, so the like-for-like figure is the pooled one. The 35.8 of Results is another sample: the study's frozen code (fitted idle behavior, part-time couriers, the scenario start), seeds 1001 to 1150, mean of per-episode p90.

## Files

`p5_kept.csv`, `p5_gap.csv`, `p5_curve.csv`, `p5_curve_move.csv`, `p5_p90_sources.csv`; run rows in `rows.jsonl` beside `run.json`.

This research was supported by data provided by Meituan.
