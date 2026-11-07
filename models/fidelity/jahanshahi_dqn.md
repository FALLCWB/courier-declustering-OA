# Fidelity note: deep Q-network assignment for meal delivery (Jahanshahi et al. 2022), assignment action only

Paper: Jahanshahi, Bozanta, Cevik, Kavuk, Tosun, Sonuc, Kosucu, Basar, "A deep reinforcement learning approach for the meal delivery problem", Knowledge-Based Systems 243, 108489 (DOI 10.1016/j.knosys.2022.108489). Read: arXiv 2104.12000v2. Reading note: `literature/model-specs/jahanshahi-2022.md`. Code: `models/jahanshahi_dqn.py`; training `sim/train_dqn.py`; network `sim/nn.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Eq. 1, p.11-12 | expected delivery time delta = d_o + max{pi_o, tau_c + d(c, o)} | `deltas` (tau_c = 0: one order per courier) |
| Eq. 3, p.13 | reward 45 - delta for an assignment | `JahanshahiDQN.assign` (reward divided by 45 inside the network) |
| Sec 4.1, Table 4 | double DQN, rank-based prioritized replay, hard target update chosen among eight variants | `Learner`, `Replay` |
| Table 2, Table 6 | layers 64-128-128-64, gamma 0.9, batch 128, memory 20,000, update every 100 steps; PER alpha 0.6, beta from 0.4 | constants of `models/jahanshahi_dqn.py` |
| p.22 | a single-courier policy shared by all couriers | one network scores each candidate courier |

## Adaptations, each with its reason

1. Assignment action only: reject, move-to-restaurant and return-to-depot are off (the plan's design; orders are never refused, idle movement is the fitted behavior).
2. Candidates: the 30 idle couriers nearest by time; the paper scored 3 to 7 couriers.
3. Orders of a 30 s window are decided one at a time in creation order (the paper decides as each order arrives).
4. Not in the paper, chosen here: Adam with learning rate 1e-3, epsilon-greedy from 1.0 to 0.05 over the first 100 peaks, one update every 4 decisions (for the 12 h budget), mean-squared TD loss weighted by importance weights.
5. Training: 200 simulated peaks per training seed, 5 seeds (the paper: 500 or 1,000 days).
6. With delta as the only input, any Q that falls with delta picks exactly the nearest courier (test below); the learned model can only differ from nearest courier where its Q is not monotone.

## Known-answer tests (`tests/test_models.py`, `tests/test_nn.py`)

- `test_jahanshahi_delta_and_reward_match_the_paper_example` (delta 11, reward 34; Fig. 1a).
- `test_jahanshahi_with_a_q_decreasing_in_delta_picks_the_nearest_courier`.
- `test_double_dqn_learns_to_prefer_the_lower_delta`.
- `test_gradients_match_finite_differences`, `test_adam_fits_a_decreasing_line`.
