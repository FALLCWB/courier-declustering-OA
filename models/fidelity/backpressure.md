# Fidelity note: mirror backpressure, assignment only

Paper: Kanoria and Qian, "Blind Dynamic Resource Allocation in Closed Networks via Mirror Backpressure", Management Science 70(8):5445-5462, 2024 (DOI 10.1287/mnsc.2023.4934). Read: arXiv 1903.02764v4; the version of record was not accessible, so equation numbers are those of arXiv v4. Reading notes: `literature/model-specs/kanoria-qian-2024.md`. Code: `models/backpressure.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Sec 2; footnotes 10-11 | nodes; demand type tau = (j, k); P = neighboring locations of j; D(j, k) = {k} | nodes = H3 resolution-8 zones; P(j) = j and the zones sharing a boundary with it (`backpressure.py:36-43`, `:70-71`) |
| Eq (8) | f(qbar) = -sqrt(m) qbar^(-1/2) | `backpressure.py:12-14` |
| Eq (9) | qbar_i = (q_i + sqrt(K)) / (K + m sqrt(K)) | `backpressure.py:17-21`, K = idle couriers available now (`:63`) |
| Eq (10) | argmax over j in P(tau) of w + f(qbar_j) - f(qbar_k) | `backpressure.py:24-33`; with D = {k} the destination term is the same for all candidates and is left out |
| Sec 2, p.10 | payoff normalized to max abs w = 1; pickup cost folded into w (JEA model) | w_ij = -pickup time / longest pickup time in P(j) (`backpressure.py:72-73`) |
| App F.1, footnote 20 | pickup time max{travel, 2 min} | `backpressure.py:9`, `:72` |
| Algorithm 1, eq (3) | after each decision the queue of the serving node drops by one | `backpressure.py:81` (the courier rejoins at the customer zone when it finishes, through the engine) |
| Sec 2 | one demand per period | orders of a 30 s window are processed one at a time in creation order (`backpressure.py:67`) |

## Adaptations, each with its reason

1. Assignment only: Algorithm 1 drops a demand when the best score is negative or the chosen node is empty (entry control). In this study the only lever is which courier gets each order (Filipe, 2026-11-01), so no order is refused: the argmax is restricted to pickup-compatible zones with an idle courier, and when none has one, the closest courier serves. Each episode reports the share of orders served this way (G3 verdict C3).
2. Eq (8) is kept, as the authors' own simulations use it: "We use the congestion function given in (8)" (Sec 6.1.1, p.30). Eq (53) is defined in App H.4 (p.57) and used only for the F.2 simulations (footnote 23, p.53), an entry-control experiment in which every demand has a single pickup node (P(i, j) = {i}), so it never chooses among couriers. In the paper's simulations the payoff is the trip time from j to k, the same for every pickup node, so Algorithm 1 alone takes the car from the fullest pickup-compatible node; pickup time enters only through the supply-aware term -vD (adaptation 4). Here too the policy takes the order from the neighboring zone with the most idle couriers, and the folded pickup cost only breaks near ties (G3 verdict, ruling 1 and C5).
3. Normalization by the live number of idle couriers; the paper's simulations normalize by an estimate of free cars, 0.05K (Sec 6.1.1).
4. The supply-aware variant of Sec 6.1.1 (shadow price v on travel time) is not used: the initial value, units and time base of its update are not stated.
5. Inside the chosen zone, the courier that reaches the restaurant first serves (units are identical in the paper).
6. No guarantee applies: Theorem 1 holds for K at least K1, a polynomial in m and 1/lambda_min; the proof of Proposition 3 (p.20) takes K1 at least m^2, so K1 is at least about 449,000 couriers for m = 670, a lower bound on what the theorem needs.

## Known-answer tests (`tests/test_models.py`)

- `test_backpressure_scores_match_the_paper_example`: m = 4, K = 16, q = (9, 1, 0, 6): qbar = (13, 5, 4, 10)/32, f values to 1e-5, the longer queue serves, payoff beats supply at w = (-1, 1) and not at (-0.9, 1), an empty zone is never chosen.
- `test_backpressure_takes_the_courier_from_the_fuller_neighbor_zone`: nearest-courier takes the courier at the restaurant; backpressure takes one from the neighbor zone with five idle couriers; with no courier in the neighborhood, the closest serves.
