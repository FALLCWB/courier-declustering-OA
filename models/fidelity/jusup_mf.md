# Fidelity note: constrained mean-field rebalancing (Jusup et al. 2026), reimplemented

Paper: Jusup, Zhang, Hu, Pasztor, Krause, Corman, "Scalable ride-sourcing vehicle rebalancing with service accessibility guarantee: a constrained mean-field reinforcement learning approach", Transportation Research Part C 188, 105705 (DOI 10.1016/j.trc.2026.105705). Read: arXiv 2503.24183v3 and the BSD-3 repository `mjusup1501/mf-vehicle-rebalancing` (commit 16a98a2), including, on 2026-11-04, `safe_mf/utils/reward.py`, `safe_mf/models/gradient_descent.py`, `safe_mf/utils/entropy.py` and the MFC training config `configs/training/trc_0wg-d-od_18s_18k-v_14k-r_0u_mfc_1ot_50pct_run1.yaml` (section below). Reading note: `literature/model-specs/jusup-2026.md`. Code: `models/jusup_mf.py`; training `sim/train_jusup.py` (torch 2.6.0, CPU).

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Sec 3.1, Eq. 7 | a representative vehicle's action: repositioning share p and a move; available mass (1 - p) mu, the repositioning part is not available in its step | `Policy`, `rollout` (`avail`) |
| Eqs. 10, 11, 14 | the fleet splits into repositioning, matched and cruising parts; next mass = cruising + matched at customer zones + repositioned at destinations | `rollout` |
| Eq. 16-17 | R = matched share of the fleet minus the Jensen-Shannon gap between available vehicles and demand; r = (R + 1) / 2, summed over the steps | `rollout`, `js` |
| Eqs. 18-19, 25 | entropy of available vehicles at least C = p h_max; p = 0.5, the authors' `max_entropy_ratio` | `entropy`, `P_ENTROPY` = 0.5 |
| Eq. 23a | log-barrier lambda log(h(mu^A_{t+1}) - C), lambda = 1, on the available mass after each step, added to r | `rollout`, `barrier_term` |
| Sec 4.1 | matching within a radius (optimal transport) | `MATCH_M` kernel |
| Table 3 | policy layers 512-256-256-64, LeakyReLU, AdamW 5e-4 (weight decay 5e-4 from the authors' config), up to 1,000 epochs, early stopping, gradient clipping at norm 1 | `Policy`, `sim/train_jusup.py` |
| Sec 5.1 | 20-minute steps | `STEP_S` |

## Adaptations, each with its reason

1. Reimplemented from the paper: the code assumes a square grid, Euclidean moves and a min-cost-flow matcher.
2. The move u is a distribution over zones within 3 km (the zone graph replaces the continuous square).
3. Matching in the mean-field model spreads each zone's supply evenly over the zones within 1.5 km (a smooth stand-in for the OT matcher); matched couriers end at customer zones by the order kernel within the step.
4. The obedient share q enters the policy and scales the controllable mass (the paper assumes full compliance).
5. The barrier extends linearly below a gap of 0.05, so a clustered start (infeasible for the bound, which the paper excludes) still gives a gradient toward more entropy.
6. Model-based training only (MFC style with this analytic matcher; no learned matching classifier); about 1,000 mean-field epochs per training seed instead of simulator peaks.
7. An obedient courier without a command stays where it is. That is the paper's world: vehicles fully comply, and the cruising part (neither repositioned nor matched) stays in its zone (Eqs. 11 and 14, `rollout`). The policy was trained on these dynamics; letting such couriers drift by the fitted behavior would run it in dynamics it never saw (G6 verdict, ruling 5). On the scattered start this keeps most free couriers at drop-off cells and raises W1, which is reported as the model's behavior here.
8. Not used: batch normalization and the decaying truncated Gaussian exploration of Table 3. Back-propagation through the deterministic mean-field model needs no exploration for its gradient, and the authors' noise perturbs the continuous move u, which the categorical move over zones does not have; batch normalization was left out to keep the policy a plain function of its inputs in the simulator. Early stopping: patience 100 epochs on the validation objective (the authors check every 100 epochs on the training reward, patience 1, minimum relative improvement 5%).
9. In the simulator, the policy is queried every 20 min; each obedient idle courier in a zone leaves with probability p for a destination zone drawn from the policy, at its representative cell; orders go to the nearest courier.
10. The idle mass mu fed to the policy counts each idle courier at its current cell (`sim.pos`), while the zone whose leave probability applies to a courier is that of the cell it can start from (`v.cell`, the next cell for a courier in mid-hop). The two differ only for couriers relocating across a zone border at the 20-min step. Found by the X8 code review after the freeze; kept, since a change would alter a frozen model, and stated here and at G8.

## Known-answer tests (`tests/test_jusup.py`, run on FE-SIM-1)

- `test_entropy_and_js_known_values` (uniform entropy log 9; JS 0; barrier log 0.5).
- `test_rollout_conserves_mass_and_zero_obedience_moves_nobody`.
- `test_repositioning_mass_is_not_available_in_its_step` (Eq. 7 with p = 0.5: only zone 0's own demand is matched; r = (R + 1) / 2).
- `test_objective_is_the_eq_17_reward_plus_the_barrier_on_the_next_available_mass` (Eqs. 16, 17, 23a on a clustered start: the start's own mass is not constrained, the barrier reads the mass after the step).

## Agreement with the authors' code (G6 verdict, ruling 6; read 2026-11-04)

| Item | Authors' code | This implementation |
|---|---|---|
| Main reward | `mu_matched.sum() - js_penalty * js_divergence(mu_available, demand)`, `js_penalty = 1`, repositioning and cruising penalties 0; then `(main_reward + 1) / 2` | same since 2026-11-04 (before: matched share of demand, and no map to [0, 1]) |
| Available mass in the reward | `mu_matched + mu_cruising` at step t, normalized (`reward_type: current_mu`) | `avail = mu - q p mu` at step t, normalized in `js` |
| JS and entropy | `entropy.py`: KL with 1e-10, entropy `-sum(w * log(mu + 1e-10) * mu)` | same formulas, unit weights (no non-operational cells in the zone graph) |
| Constraint | `constraint_function(mu_available_next, weight_matrix)`: entropy of the next step's available mass minus C, C from `max_entropy_ratio: 0.5` | `entropy(avail)` of the next step minus C = 0.5 h_max, since 2026-11-04 (before: the step's own mass, which also constrained the start) |
| Barrier | `barrier_lambda * log(constraint)`, NaN and minus infinity set to -10 (flat when infeasible); positive values divided by `max_barrier` | lambda log(gap) for gap above 0.05, extended linearly below (adaptation 5); no division of positive values |
| Combination | `(main_reward + barrier) / 2` per step | r + barrier per step: the same optimum (a factor 1/2 on both terms) |
| Optimizer and loss | AdamW, lr 5e-4, weight decay 5e-4; loss `-torch.stack(rewards).sum()` over the horizon (18 steps); `clip_grad_norm_(..., max_norm=1.0)` | AdamW, lr 5e-4, weight decay 5e-4 since 2026-11-04 (before: torch's default 0.01); loss -(sum r + sum barrier) over 12 steps of 20 min (17:00 to 21:00); clipping at 1.0 |
| Exploration and early stopping | `exploration_decay: 0.02`, `control_std: 0.0175`; early stopping every 100 epochs, patience 1, minimum improvement 5% on the training reward | adaptation 8 |
| Differentiability | rewards collected over the horizon without `detach`, one backward pass | the same |

Not traced: how `max_barrier` is set (absent from the config) and the body of `env.step`.

The objective fix of 2026-11-04 (first three rows) changed the trained policies: the five Jusup policies were retrained on episode seeds 98000 + 1000 k + epoch, clear of the validation seeds (`avaliacao/20261104-0040-training-jusup`); the trainings of 2026-11-03 stay as evidence.
