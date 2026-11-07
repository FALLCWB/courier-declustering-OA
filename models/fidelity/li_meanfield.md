# Fidelity note: mean-field multi-agent order dispatch (Li et al. 2019), COD

Paper: Li, Qin, Jiao, Yang, Wang, Wang, Wu, Ye, "Efficient ridesharing order dispatching with mean field multi-agent reinforcement learning", WWW 2019, 983-994 (DOI 10.1145/3308558.3313433). Read: arXiv 1901.11454v1 (nine authors on that byline). Reading note: `literature/model-specs/li-2019.md`. Code: `models/li_meanfield.py`; training `sim/train_li.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| p.3 | each driver acts on its order pool within radius r; reward = income + alpha1 destination potential + alpha2 pick-up distance | `LiMeanField.assign` |
| Eq. 3 | destination potential = demand minus supply at the destination, only when orders exceed drivers at the origin | `dp` in `assign` |
| p.5 | mean-field response = drivers in the neighborhood (radius 2r) over available orders | `a_bar` in `assign` |
| Eq. 6 | Boltzmann softmax over the pool's actor scores | `assign` |
| Eqs. 9-10 | critic target r + gamma sum over the next pool of pi Q (mean-field value) | `Learner.update` |
| p.5 | conflicts: a driver whose order was taken re-chooses from the updated pool | couriers act in random order on what is left |
| p.7 | critic 512-256-128-64, actor 256-128-64, Adam 1e-4 and 1e-3, gamma 0.95, batch 2,048 every 3,000 samples, memory 500,000, temperature 1.0 to 0.01 | constants of `models/li_meanfield.py` |

## Adaptations, each with its reason

1. Pool radius 10 min of riding (the paper does not give r) and at most the 20 nearest orders per pool.
2. Observation = courier position and time; action embedding = destination position, pick-up and trip minutes.
3. The actor is updated by a likelihood-ratio step on the critic's advantage, not by the deterministic policy gradient through a discrete action embedding (Eq. 11), which the discrete pool does not support directly.
4. Decisions every 30 s (the paper's grid simulator steps 10 min); gamma 0.95 per decision.
5. Orders are never refused: an order outside every pool goes to the closest courier left.
6. Training: 200 simulated peaks per training seed, 5 seeds (the paper: 20 episodes of its grid simulator).

## Known-answer tests (`tests/test_models.py`)

- `test_li_softmax_matches_eq_6_and_one_courier_wins_a_contested_order` (0.0900, 0.2447, 0.6652).
- `test_li_serves_an_order_outside_every_pool_by_the_closest_courier`.
- `test_li_learner_stores_a_transition_when_the_courier_acts_again`, `test_li_critic_and_actor_update_on_a_full_batch`.
