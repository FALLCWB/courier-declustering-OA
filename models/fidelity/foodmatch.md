# Fidelity note: FoodMatch with order batching off

Paper: Joshi, Singh, Ranu, Bagchi, Karia, Kala, "Batching and Matching for Food Delivery in Dynamic Road Networks", ICDE 2021 (DOI 10.1109/ICDE51399.2021.00207); extended as FoodMatch, ACM TSAS 8(1), 2022 (DOI 10.1145/3494530). Read: arXiv 2008.12905v1, with the authors' code (github.com/idea-iitd/FoodMatch) for ambiguities; the TSAS text was not accessible, so equation numbers are those of arXiv v1. Reading notes: `literature/model-specs/foodmatch-2021.md`. Code: `models/foodmatch.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Def. 4, MAXO | at most MAXO orders per vehicle; batching off means MAXO = 1, so only empty couriers take orders | the engine offers only idle couriers (`View.couriers`) |
| Eq. 2, Def. 5-7 | XDT = EDT - SDT with EDT = max{time + firstMile, o_p} + lastMile; with an empty vehicle XDT = max(0, t + firstMile - ready) | `foodmatch.py:40-42` |
| Sec IV-A, w(o, v) | min(mCost, Omega); Omega for pairs that break Def. 4 | `foodmatch.py:42` |
| Sec V-B | Omega = 7,200 s; first mile over 45 min costs Omega | `foodmatch.py:7-8`, `:43` |
| Alg. 2 l.8 and l.19, Lemma 1, Sec V-B | each vehicle keeps finite edges to its k nearest orders, k = 200 x |O| / |V| (code: max(1, int(...))) | `foodmatch.py:44-47` |
| Sec IV-A, ref. [19] | Kuhn-Munkres on the rectangular FoodGraph, sum x = min(|O|, |V|) | `foodmatch.py:13-23`, `:52` (`scipy.optimize.linear_sum_assignment`) |
| Sec V-F, code | pairs matched at Omega are not assigned | `foodmatch.py:53` |
| Sec IV-E | unassigned orders carry over to the next window | the engine keeps them pending |
| Alg. 2, code | first mile measured from the vehicle's position at dispatch, loc(v, t) | `foodmatch.py:41`: a courier between cells starts from the cell it is entering, after the rest of its hop (`View.delay`) |

## Adaptations, each with its reason

1. Window: the paper accumulates for Delta = 1 min (city A) or 3 min (cities B, C); every model here dispatches on the same 30 s clock (plan decision 5), so the comparison isolates the matching rule.
2. No rejection after 30 min unassigned and no Omega for rejected orders: orders in this study are never refused (the lever is assignment only). An order that waits more than 30 min unassigned is counted in the results as the paper's rejection would be.
3. Reshuffling (Sec IV-D2) is off: once assigned, an order stays with its courier. The paper reports reshuffling only together with batching.
4. Angular distance (Eq. 8) is not used: it orders the search only for vehicles with a route plan and is zero for idle couriers (authors' code).
5. Static road times (free flow times the calibrated speed factor, with per-order travel noise the policy never sees) instead of hourly time-dependent shortest paths.
6. Ties (G3 verdict C4): every courier that arrives before the food is ready has weight 0, and the paper does not break ties. The assignment minimizes total XDT first and total first mile second (`lexicographic_assignment`, `foodmatch.py:13-23`): XDT counts in whole hundredths of a second and the capped first mile enters as a fraction below one hundredth in total, so any XDT difference of 0.01 s or more is never traded for first mile, every assignment chosen is optimal for the paper's objective, and the rule follows the nearest-first search of Alg. 2. The S5 variant shuffled the courier columns with a seeded stream instead (`ties="shuffle"`); on seed 501 (big cluster, normal supply) it gave 6.95 km without an order per order and p90 45.15 min, against 5.94 km and 44.88 min with the frozen rule and 5.88 km and 43.78 min for nearest-courier (`avaliacao/20261102-1209-e2e/README.md`).
7. The k cap counts the k nearest orders by first-mile time per courier; Alg. 2 adds all orders at a node before checking the degree, so at a node with several orders the paper may keep slightly more edges.

## Known-answer tests (`tests/test_models.py`)

- `test_foodmatch_minimizes_extra_delivery_time_where_nearest_is_greedy`: two orders, two couriers; nearest-courier (oldest order first) and FoodMatch give different, hand-computed assignments.
- `test_foodmatch_leaves_an_order_pending_when_the_first_mile_passes_45_min`: 3,000 s first mile is not assigned, 2,400 s is.
- `test_foodmatch_breaks_ties_by_first_mile_but_never_trades_extra_delivery_time_for_it`: 1 s of XDT outweighs 4,000 s of first mile; equal XDT goes to the shorter first mile.
- `test_foodmatch_takes_the_closer_of_two_couriers_that_both_beat_the_food`.
