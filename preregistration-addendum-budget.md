# Pre-registration addendum: training-budget check of the learned models

This research was supported by data provided by Meituan.

| | |
|---|---|
| Added | 2026-11-07, after G10 passed and after every result of the extension and of package C was seen |
| Decided by | Filipe Lemos, "Rerun + narrow claims" (2026-11-07), answering risk R1 of the fresh-session review of Paper A (whether the learned reimplementations were trained enough) |
| State of the data when added | No retrained policy and no episode of this check existed. This file is committed before any retraining starts. |
| Status | Exploratory. It lies outside every family; it has no confirmatory test. The frozen files and addenda are unchanged. |

## Question

Does a longer training budget change any class of the learned models?

## Retraining (policy 1 only)

- **Xu et al., Li et al., the deep Q-network (Jahanshahi et al.) and Auad et al.:** training seed 1 retrains with 600 peaks, three times the frozen budget of 200.
- **Jusup et al.:** training seed 1 retrains with early-stopping patience 300 (frozen: 100) and at most 3,000 epochs (frozen: 1,000).
- **Everything else as in the frozen training:** settings, training seeds, the peaks' starts and episode seeds, validation seeds, step sizes, Auad et al.'s selected configuration (step size 1e-7, memory 3,000, n = 1,000).
- **Schedules keep their frozen values in peaks:** Li et al.'s temperature anneals over the first 200 peaks and then stays at 0.01; the deep Q-network's replay-weight exponent reaches 1 at the frozen update count and stays; the epsilon schedules (first 100 peaks) are unchanged. So the first 200 peaks repeat the frozen training, and peaks 201 to 600 are added training. The policy at peak 200 is compared with the frozen policy 1 as a reproduction check.
- **Checkpoint kept:** the one the frozen code keeps: Xu et al., Li et al. and the deep Q-network the final one; Auad et al. theta_best, the lowest cost on its gate peak; Jusup et al. the best validation objective.
- **Curves from peak 0 (epoch 0):** each model's own training objective beside W1 and p90 on the validation seeds 95001 to 95003 (big cluster and scattered start, normal supply), every 25 peaks (every 100 epochs for Jusup et al.):
  - Xu et al.: the change of the value table between checkpoints;
  - Li et al.: actor and critic losses and the episode reward;
  - deep Q-network: TD loss and the episode reward;
  - Auad et al.: the gate-run cost per peak;
  - Jusup et al.: the validation objective per epoch.
- The retrained policies are stored apart from the frozen ones (`models/trained_budget/`); every frozen policy file stays unchanged.

## Evaluation

- **Seeds:** the evaluation seeds that map to policy 1, s = 1001, 1006, ..., 1146 (30 seeds).
- **Cells:** the 16 primary cells (scattered and burst starts, the three clustered starts, each at three supply levels, and the meet-up), fitted behavior, arm C at 100% obedience.
- **Runs:** the retrained policy 1 of each of the five models, 5 x 16 x 30 = 2,400 episodes. Nearest courier's rows and the current policy 1's rows at these seeds come from the full runs.

## Reading rule

- For each model, the W1 contrast (W1 on the Q1 cells, W1 over the first 60 min on the Q2 cells) and the p90 contrast against nearest courier, paired by seed, with 95% percentile bootstrap intervals, for the retrained and the current policy 1 on the same seeds.
- The joint class by the frozen rule, with the pilot's smallest effects, and Holm at 0.05 as a reading device within each E1-shaped (6 Q1 cells) and E2-shaped (10 Q2 cells) set of the four tested learned models (Xu et al., Li et al., Auad et al., Jusup et al.), separately for the retrained and the current policy.
- A class counts as changed when the retrained policy 1's joint class differs from the current policy 1's on the same seeds. Every changed class is listed. The deep Q-network is a descriptive row.

## Also reported, from existing rows (no new episodes)

1. Per-policy class check: for each learned model and each prevent or undo class of G8, whether each of the five training policies' means (30 seeds each) lies beyond -delta, with the pilot's delta of the cell.
2. Auad et al.: the six costs of the configuration search, and the change in validation cost over the 200 peaks at the selected step size.

This research was supported by data provided by Meituan.
