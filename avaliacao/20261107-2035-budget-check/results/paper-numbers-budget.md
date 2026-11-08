# Paper numbers, training-budget check (exploratory)

This research was supported by data provided by Meituan.

Pre-registration addendum `preregistration-addendum-budget.md`, committed at c217ca4 before any retraining; exploratory, outside every family. Policy 1 of each learned model retrained with three times the budget (600 peaks; Jusup et al. patience 300, at most 3,000 epochs), evaluated at the 30 seeds of policy 1 against the current policy 1 on the same seeds.

## Classes, retrained against current policy 1

Seeds 1001, 1006, 1011, ..., 1146 (n = 30), the 16 primary cells, fitted behavior, arm C at 100%. Smallest effects from the pilot; Holm within the E1-shaped and E2-shaped sets of each policy, as a reading device. Contrasts: `b2_contrasts.csv`; classes: `b2_classes.csv`; the DQN's differences: `b2_dqn.csv`.

W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model minus nearest courier, in minutes; lower is better.

| input | holm_set | contrasts | established |
|---|---|---|---|
| current | E1-shaped | 48 | 44 |
| current | E2-shaped | 80 | 75 |
| retrained | E1-shaped | 48 | 46 |
| retrained | E2-shaped | 80 | 76 |

Classes by model (cells):

| model | class | retrained | current |
|---|---|---|---|
| auad | does not undo | 10 | 10 |
| auad | does not prevent | 6 | 6 |
| jusup | does not prevent | 6 | 6 |
| jusup | does not undo | 5 | 5 |
| jusup | undoes at no delivery cost | 5 | 5 |
| li | does not undo | 10 | 10 |
| li | prevents at no delivery cost | 4 | 4 |
| li | does not prevent | 2 | 2 |
| xu | does not undo | 6 | 6 |
| xu | does not prevent | 4 | 4 |
| xu | undoes at no delivery cost | 2 | 2 |
| xu | undoes at a delivery cost | 2 | 2 |
| xu | prevents at a delivery cost | 1 | 1 |
| xu | prevents at no delivery cost | 1 | 1 |

Classes that change: 0 of 64.

None.

## Training: the checkpoint kept and the reproduction at peak 200

| model | kept | status | budget (peaks; Jusup: most epochs) | reproduces_frozen_policy_1_at_200 | epochs_run | best_epoch | frozen_epochs_reproduced |
|---|---|---|---|---|---|---|---|
| xu | final table (the frozen code saves the table of all peaks) | done | 600 | True |  |  |  |
| li | final actor (the frozen code saves the actor after the last peak) | done | 600 | True |  |  |  |
| dqn | final network (the frozen code saves the network after the last peak) | done | 600 | True |  |  |  |
| auad | theta_best, the theta with the lowest cost on its gate peak (Algorithm 1 lines 13-14) | done | 600 | True |  |  |  |
| jusup | the best validation objective (early stopping keeps the best state) | done | 3000 |  | 2098 | 1798 | 386 of 386 |

Curves (each model's own objective, and W1 and p90 on the validation seeds, per checkpoint): `b1_curves.csv`.

**xu** (every 100 peaks)

| checkpoint | p90_valid | table_change_frobenius | table_change_max_abs | w1_valid |
|---|---|---|---|---|
| 0 | 39.240 |  |  | 7.885 |
| 100 | 47.255 | 16.096 | 2.002 | 8.583 |
| 200 | 46.999 | 9.632 | 1.894 | 8.604 |
| 300 | 46.962 | 7.426 | 1.802 | 8.617 |
| 400 | 47.253 | 5.669 | 1.055 | 8.651 |
| 500 | 47.285 | 5.312 | 1.509 | 8.638 |
| 600 | 47.327 | 4.319 | 1.167 | 8.631 |

**li** (every 100 peaks)

| checkpoint | actor_loss | critic_loss | episode_reward | p90_valid | w1_valid |
|---|---|---|---|---|---|
| 0 |  |  |  | 39.728 | 7.761 |
| 100 | -0.515 | 0.536 | 3344.443 | 39.726 | 7.813 |
| 200 | -0.158 | 0.383 | 3306.154 | 39.731 | 7.784 |
| 300 | -0.007 | 0.382 | 3638.202 | 39.786 | 7.779 |
| 400 | -0.007 | 0.284 | 3518.180 | 39.734 | 7.797 |
| 500 | -0.061 | 0.474 | 3927.887 | 39.748 | 7.748 |
| 600 | -0.027 | 0.442 | 4107.742 | 39.727 | 7.825 |

**dqn** (every 100 peaks)

| checkpoint | episode_reward | loss | p90_valid | w1_valid |
|---|---|---|---|---|
| 0 |  |  | 71.485 | 6.876 |
| 100 | 4488.586 | 0.200 | 39.627 | 8.341 |
| 200 | 4784.283 | 0.187 | 39.590 | 8.384 |
| 300 | 4876.488 | 0.192 | 39.655 | 8.390 |
| 400 | 4994.952 | 0.137 | 39.609 | 8.386 |
| 500 | 4821.322 | 0.201 | 39.607 | 8.445 |
| 600 | 4772.414 | 0.220 | 39.568 | 8.392 |

**auad** (every 100 peaks)

| checkpoint | best_cost | gate_capped_share | gate_cost | p90_valid | train_cost | w1_valid |
|---|---|---|---|---|---|---|
| 0 |  |  |  | 200.264 |  | 12.105 |
| 100 | 98912.981 | 0.560 | 99134.196 | 40.205 | 175934.520 | 8.447 |
| 200 | 98733.044 | 0.760 | 98845.235 | 40.140 | 145051.666 | 8.455 |
| 300 | 98733.044 | 1.000 |  | 40.140 | 127881.496 | 8.455 |
| 400 | 98733.044 | 1.000 |  | 40.140 | 92089.162 | 8.455 |
| 500 | 98733.044 | 1.000 |  | 40.140 | 137911.620 | 8.455 |
| 600 | 97775.503 | 1.000 |  | 40.220 | 186104.544 | 8.409 |

**jusup** (every 200 epochs)

| checkpoint | p90_valid | valid_objective | w1_valid |
|---|---|---|---|
| 0 | 39.213 | 15.936 | 8.901 |
| 200 | 38.700 | 17.917 | 9.298 |
| 400 | 38.598 | 18.297 | 9.536 |
| 600 | 38.556 | 18.526 | 9.497 |
| 800 | 38.603 | 18.674 | 9.661 |
| 1000 | 38.489 | 18.864 | 9.648 |
| 1200 | 38.704 | 18.955 | 9.861 |
| 1400 | 38.727 | 19.041 | 9.757 |
| 1600 | 38.394 | 19.095 | 9.645 |
| 1800 | 38.965 | 19.510 | 9.756 |
| 2000 | 38.865 | 19.561 | 9.629 |

## Per-policy check of the G8 classes (existing rows)

For each prevent or undo class: each training policy's mean contrast (30 seeds each) against -delta, the pilot's smallest effect of the cell.

| model | question | scenario | level | class | delta | policy_1_mean | policy_2_mean | policy_3_mean | policy_4_mean | policy_5_mean | policies_beyond_minus_delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| li | Q1 | burst | loose | prevents at no delivery cost | 0.417 | -0.801 | -0.712 | -0.767 | -0.739 | -0.800 | 5 |
| li | Q1 | burst | normal | prevents at no delivery cost | 0.488 | -0.661 | -0.575 | -0.623 | -0.612 | -0.692 | 5 |
| xu | Q1 | burst | tight | prevents at no delivery cost | 0.484 | -0.716 | -0.744 | -0.751 | -0.723 | -0.685 | 5 |
| li | Q1 | scattered | loose | prevents at no delivery cost | 0.394 | -0.860 | -0.746 | -0.785 | -0.767 | -0.816 | 5 |
| li | Q1 | scattered | normal | prevents at no delivery cost | 0.453 | -0.750 | -0.624 | -0.663 | -0.649 | -0.727 | 5 |
| xu | Q1 | scattered | tight | prevents at a delivery cost | 0.482 | -0.684 | -0.679 | -0.741 | -0.640 | -0.655 | 5 |
| xu | Q2 | meetup | normal | undoes at a delivery cost | 0.849 | -3.297 | -3.749 | -3.950 | -2.850 | -1.119 | 5 |
| jusup | Q2 | mixed | loose | undoes at no delivery cost | 1.528 | -2.944 | -2.757 | -2.800 | -2.609 | -2.941 | 5 |
| xu | Q2 | mixed | loose | undoes at a delivery cost | 1.528 | -1.786 | -1.726 | -1.746 | -1.676 | -1.925 | 5 |
| jusup | Q2 | mixed | normal | undoes at no delivery cost | 1.638 | -3.002 | -2.731 | -2.770 | -2.683 | -2.905 | 5 |
| xu | Q2 | mixed | normal | undoes at no delivery cost | 1.638 | -2.443 | -2.321 | -2.318 | -2.266 | -2.563 | 5 |
| jusup | Q2 | mixed | tight | undoes at no delivery cost | 1.612 | -1.849 | -1.626 | -1.502 | -1.630 | -1.605 | 3 |
| xu | Q2 | mixed | tight | undoes at no delivery cost | 1.612 | -2.153 | -1.971 | -2.012 | -1.996 | -2.290 | 5 |
| jusup | Q2 | three_clusters | loose | undoes at no delivery cost | 1.940 | -2.853 | -2.875 | -3.261 | -2.955 | -2.978 | 5 |
| jusup | Q2 | three_clusters | normal | undoes at no delivery cost | 2.049 | -2.598 | -2.479 | -2.908 | -2.659 | -2.627 | 5 |

## Auad et al.: the configuration search and the validation cost

| alpha | mem | n_step | diverged | theta_best_is_theta0 | valid_cost | gate_best_cost | peaks | chosen |
|---|---|---|---|---|---|---|---|---|
| 1e-07 | 3000 | 1000 | False | False | 88916.600 | 98733.000 | 200 | True |
| 1e-07 | 3000 | 2 | False | False | 173649.500 | 92519.600 | 200 | False |
| 1e-06 | 3000 | 2 | True | True | inf | inf | 1 | False |
| 1e-06 | 3000 | 1000 | True | True | inf | inf | 2 | False |
| 1e-05 | 3000 | 2 | True | True | inf | inf | 1 | False |
| 1e-05 | 3000 | 1000 | True | True | inf | inf | 2 | False |

Validation cost per checkpoint at the selected configuration (mean over the five training seeds and the validation cases): change from 25 to 200 peaks -96.4.

| checkpoint | mean_cost | seed_1 | seed_2 | seed_3 | seed_4 | seed_5 |
|---|---|---|---|---|---|---|
| 25 | 96050.800 | 89398.570 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 50 | 96039.310 | 89341.130 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 75 | 96039.310 | 89341.130 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 100 | 96060.500 | 89447.050 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 125 | 96060.500 | 89447.050 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 150 | 95954.410 | 88916.590 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 175 | 95954.410 | 88916.590 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |
| 200 | 95954.410 | 88916.590 | 122906.240 | 89185.530 | 90072.280 | 88691.380 |

This research was supported by data provided by Meituan.
