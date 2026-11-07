# Fidelity note: assignment with holding (Auad, Lagos and Lagos 2026), bundling and rejection off

Paper: Auad, Lagos, Lagos, "Data-driven optimization for meal delivery: a reinforcement learning approach for order-courier assignment and routing at Meituan", Transportation Science, trsc.2025.0129 (2026). Read: Optimization Online manuscript, October 2025. Reading note: `literature/model-specs/auad-2026.md`. Code: `models/auad_holding.py`; training `sim/train_auad.py`.

Written before the configuration was trained (reviewer pre-note of 2026-11-03, `reviews/G6-reviewer-note-2026-11-03.md`). The first training (`avaliacao/20261103-1023-training-auad`) used scaled features and no theta_best gate; its policy held orders up to the 2 h limit and is kept only as evidence.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Eq. 1, p.12 | Q(s, x) = c0(s, x) + theta . phi(s, x) | `AuadHolding.assign` |
| Eq. 2, p.12 | immediate cost of an offer: K_dist extra km + K_late extra lateness | `c0` in `assign` (empty route) |
| p.13-14 | 14 raw features: active orders per courier, open orders not offered per courier and their count, deadline buckets of 1,200 s, on-duty couriers receiving no offer, mean restaurant-to-customer distance of offered orders | `features` (no scaling) |
| Rewards, p.10 | r_lateness, r_dist, r_lost with K_dist, K_late, K_lost = 1, 4, 16 (Table 6) | `episode_cost` (total cost); costs booked per epoch in `assign` |
| p.9, Table 6 | an order unassigned 2 h past its deadline is lost (lambda_lost) | `LAMBDA_LOST_S`: booked as lost (K_lost) and offered |
| Algorithm 1, p.15 | n-step SARSA, ring buffer m, batch b = 20, linear update; actions minimize Q under theta_best; every n_update = 200 epochs theta_best <- theta if a Monte Carlo episode costs less | `Learner`, `Learner.consider`, `sim/train_auad.py` |
| p.29 | grid alpha in {1e-7, 1e-6, 1e-5}, m in {3000, 5000, 9000}, n in {2, 1000, 3000}; gamma 0.999, epoch 30 s | `GRID`, `GAMMA` |
| Sec 4.4.2 | the simple policy offers each order, in a random order, to the cheapest courier | same order of decisions |

## Configuration, fixed before training

1. Features as printed, unscaled.
2. alpha and n from the paper's grid, m = 3000 (the paper's best n-step SARSA setting, (n, m, alpha) = (3000, 3000, 1e-6), p.30). Each of the 6 combinations of alpha in {1e-7, 1e-6, 1e-5} and n in {2, 3000} (n = 1000 and n = 3000 both give the Monte Carlo return to the episode's end, since an episode has 840 epochs; the code runs it as n = 1000) trains training seed 1 for 200 peaks; its theta_best then runs on the validation seeds 95001 to 95003 (big cluster and scattered, normal supply; training range, never an evaluation seed). The lowest mean total cost wins; a combination whose theta stops being finite is out. The chosen combination then trains seeds 1 to 5.
3. Maximum hold time: lambda_lost = 2 h past the deadline (Table 6). The paper loses such an order; here no order is refused, so the order is offered to the cheapest courier at that moment and its cost includes K_lost = 16.
4. theta_best gate: once per training peak (about every 840 epochs instead of every 200) the learned theta runs greedily on one fixed gate peak per training seed (start and supply drawn from the seed, episode seed 97000 + k) and replaces theta_best when its total cost is lower; theta_best starts at theta_0 = 0. The policy acts with theta_best during training, and theta_best is the trained model. theta_0 holds every order to the lost limit, so it loses to any policy that offers and its own gate run is skipped (its cost is taken as infinite). A gate or selection run stops as soon as a lower bound of its cost (lateness already incurred by delivered and open orders, kilometres already ridden) passes the smaller of theta_best's cost and 3 times nearest courier's cost on the same peak; such a theta could not win, and an order-holding run would otherwise take about 25 min.

## Adaptations, each with its reason

1. Bundling and courier rejection are off (the study's scope): no route insertion, no hyper-heuristic, no rejection model.
2. The offer test compares Q(offer) with Q(hold); the paper's "offer only if Q <= 0" and this test both hold everything at theta = 0.
3. Exploration: epsilon-greedy on hold or offer, from 1.0 to 0.02 over 100 peaks (the paper explores through the hyper-heuristic, which is off).
4. Costs are booked when the offer is made (planned c0, from the travel times without the trip noise), not as lateness at delivery and distance per epoch; the total is the same, earlier by the trip time.
5. K_late is applied per minute late; the paper states no unit.
6. Episodes are 4-hour peaks plus a 3-hour drain, not 24-hour days; training: 200 peaks per training seed, 5 seeds (the paper: 10^5 epochs at 1:10 scale).
7. Training and gate peaks run in the runner's light mode (one concentration snapshot instead of one per minute); the simulation is unchanged (`test_fewer_snapshots_leave_the_simulation_unchanged`).

## Known-answer tests (`tests/test_models.py`)

- `test_auad_holds_when_the_only_courier_is_far_and_offers_when_a_near_one_appears` (hold at c0 31 > 5, offer at c0 1 < 5, theta = 0 holds, held until 2 h past the deadline, then offered).
- `test_auad_features_are_the_papers_raw_counts`.
- `test_auad_acts_with_theta_best_and_the_gate_replaces_it_only_when_cheaper`.
- `test_auad_episode_cost_is_lateness_distance_and_lost_orders`.
- `test_auad_learner_target_is_the_discounted_cost_beyond_the_immediate_one`.
- `test_auad_vectorized_decisions_equal_the_order_by_order_loop`.
- `test_auad_capped_run_stops_once_the_cost_lower_bound_passes_the_cap`.

## Result of the training, by training seed (G6 verdict, ruling 1)

The configuration was accepted at G6 as stated above, including the cap at 3 times nearest courier's cost on gate and selection runs, which only stops runs that cannot win the gate. One gate peak per training seed follows Algorithm 1 (one Monte Carlo episode per check); seed 2's costlier theta_best stays, since retraining after seeing the validation costs would be a choice made on results. Spread across the five trained policies at 200 peaks, validation seeds 95001 to 95003, normal supply (`avaliacao/20261103-2154-training-auad/curve.csv`; nearest courier's cost on the same seeds: big cluster 134,102, scattered 40,072):

| Training seed | Big cluster cost | W1 / p90 (min) | Unassigned over 30 min | Scattered cost | W1 / p90 (min) |
|---|---|---|---|---|---|
| 1 | 137,561 | 12.34 / 44.1 | 0.00% | 40,272 | 4.57 / 36.2 |
| 2 | 205,473 | 12.48 / 44.7 | 1.20% | 40,340 | 4.61 / 36.2 |
| 3 | 138,031 | 12.33 / 44.2 | 0.05% | 40,340 | 4.61 / 36.2 |
| 4 | 139,805 | 12.32 / 44.4 | 0.04% | 40,340 | 4.61 / 36.2 |
| 5 | 137,043 | 12.33 / 44.1 | 0.00% | 40,340 | 4.61 / 36.2 |

On the big cluster the mean cost is 13% above nearest courier's (2 to 4% without seed 2); on the scattered start the two are nearly tied. This is the model's behavior in this setting: the paper finds most n-step SARSA settings worse than its simple policy (Table 3) and calls the method highly sensitive to its hyperparameters (p.30).
