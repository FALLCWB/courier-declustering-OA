# Fidelity note: learning and planning (Xu et al. 2018)

Paper: Xu, Li, Guan, Zhang, Li, Nan, Liu, Bian, Ye, "Large-scale order dispatch in on-demand ride-hailing platforms: a learning and planning approach", KDD 2018, 905-913 (DOI 10.1145/3219819.3219824). Read: the KDD full text (kept local, `literature/papers/`). Reading note: `literature/model-specs/xu-2018.md`. Code: `models/xu_value.py`; training `sim/train_xu.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Sec 3, p.907 | state = (location, time); reward = order price spread over the trip, pickup included; idle = stay one slot with zero reward | `fit_value`, `transitions_from` |
| Eq. 1, p.907 | discounted spread reward R (gamma^T - 1) / (T (gamma - 1)) | `discounted_reward` |
| Algorithm 1, p.908 | one backward pass over time; V(s) = sample mean of the targets from s | `fit_value` |
| Eq. 8, p.909 | edge weight A = gamma^dt V(s') - V(s) + R_gamma | `td_weight`, `XuValue.assign` |
| Eqs. 6-7, p.909 | Kuhn-Munkres with at most one courier per order and order per courier: pairs that do not add value stay unmatched | `XuValue.assign` keeps pairs with a positive weight |
| p.912 | gamma 0.9 in production; data of the previous month | gamma 0.95 per 5-minute slot (about 0.9 per 10 min); 200 simulated peaks per training seed |

## Adaptations, each with its reason

1. Reward 1 per delivered order: food delivery has no fare in this study.
2. State = H3 resolution-8 zone and 5-minute slot, 17:00 to 21:00 with a terminal slot of value 0: the paper gives no production grid or slot length; 670 zones keep the table filled (resolution-9 cells would be sparse).
3. Idle gaps enter as one zero-reward jump from the drop-off zone to the zone of the next acceptance, not the paper's one-slot stay, so the table sees the couriers' drift back to their areas.
4. Unvisited (zone, slot) states take the mean of their slot (the paper leaves them at 0).
5. dt is the expected time from now to the door (approach, wait for food, ride), fractional in slots; the paper uses integer slots.
6. Rounds every 30 s (the paper: 1 to 2 s).
7. Orders are never refused: an order unassigned for 30 min goes to the closest courier left.
8. Training data come from simulated peaks under nearest courier with the fitted behavior, the analogue of the paper's historical trajectories; one learning pass (the paper's V0), no repeated learning and planning.

## Known-answer tests (`tests/test_models.py`)

- `test_xu_value_dynamic_programming_matches_the_hand_computed_table` (10, then 9.5 with a two-slot trip).
- `test_xu_planning_weight_is_the_td_error_and_kuhn_munkres_takes_the_larger` (0.5 against 1.7).
- `test_xu_planner_prefers_the_courier_whose_destination_value_is_higher`.
