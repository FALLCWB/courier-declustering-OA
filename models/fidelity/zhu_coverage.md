# Fidelity note: coverage control of idle couriers (Zhu et al. 2024), graph version

Paper: Zhu, Sirmatel, Ferrari-Trecate, Geroliminis, "A coverage control-based idle vehicle rebalancing approach for autonomous mobility-on-demand systems", IEEE TCST 32(5), 1839-1853 (DOI 10.1109/tcst.2024.3375765). Read: arXiv 2311.11716v1. Reading note: `literature/model-specs/zhu-2024.md`. Code: `models/zhu_coverage.py`.

## Paper to code

| Paper | What it says | Code |
|---|---|---|
| Eq. 18 | graph Voronoi partition among idle vehicles by shortest-path distance | `owner` in `relocate` (road metres) |
| Eq. 19 | radius-limited part, r_G = sqrt(2) r, r = 1,000 m | `R_G_M`, `reach` |
| Eq. 12 | static origin density (probability mass over nodes) | `phi` = expected pickups of the whole evening |
| Eq. 22 | the node of the part minimizing sum of d^2 phi | `cost`, `argmin` |
| Algorithm 1 | each idle vehicle heads to its part's centroid, recomputed every control step | `relocate` every 30 s |
| Algorithm 2 | orders go to the nearest idle vehicle | inherits `NearestIdle` |

## Adaptations, each with its reason

1. Arm C: only obedient couriers follow (share 0 to 100%, drawn once per courier); the partition uses every idle courier, obedient or not, since all of them cover demand.
2. Control step 30 s (the paper: 10 s); H3 resolution-9 cells as nodes, road distance from the city build.
3. No pick-up tolerance or request cancellation (orders wait here).
4. No hold-position layer (CVR-alpha, CVR-PI), which was tuned for the paper's scenario only.
5. Empty-part rule (G7 verdict, ruling 7 and E1, fixed before any comparison). The paper limits each part to r_G only to bound computation (p.8); its base law has no radius (Eq. 6). When a courier's radius-limited part holds no pickup (phi = 0 in every cell; 2,331 of the 4,311 cells have phi = 0 exactly), the courier takes the centroid of its whole graph Voronoi part (Eq. 18 without Eq. 19). A part with no pickup at all gets no command, and the courier stays. Without this rule, a courier at the meet-up point or after a drop-off on the city's fringe got no command for the rest of the evening. The model counts, per episode, its control steps, the commands it sends, those sent by this rule, the couriers whose whole part holds no pickup, and the couriers that own no cell (row fields `events_steps`, `events_commands`, `events_whole_part_commands`, `events_no_demand_in_part`, `events_owns_no_cell`). On the X5 seed (501, full obedience, `avaliacao/20261104-1029-zhu-empty-part-rule/`) the rule sends 77 to 84 commands per episode out of 344,000 to 473,000, and Zhu's X5 metrics move little (big cluster W1 11.70 to 11.67; meet-up W1 over 60 min 10.02 to 10.12; scattered W1 5.67 to 5.65).
6. Partition ties go to the lower courier index (`np.argmin`). Couriers in the same cell are at distance 0 from the same cells, so the lowest-index one owns them all and the others own no cell: they get no command, and leave one per control step as the cells free up. Distinct cells can also be at road distance 0 (1,457 pairs; 679 cells share a road node with another cell in the city build), and act as one cell for the partition. The paper does not state a tie rule for Eq. 18. Below full obedience, the partition still counts non-obedient idle couriers (adaptation 1), so an obedient courier that shares a cell with a lower-index non-obedient one owns no cell and stays until that courier is dispatched (found by the X8 code review; part of this tie rule, not changed). On the X5 seed this rule weighs far more than adaptation 5: per control step, about 580 obedient idle couriers own no cell on the big cluster (about 530 on the meet-up and 490 on the scattered start), against about 570, 760 and 780 commands.
7. Centroid ties go to the lower cell index (`np.argmin` over the part's cells). The paper breaks ties at random.

## Known-answer tests (`tests/test_models.py`)

- `test_zhu_sends_two_couriers_on_a_line_to_the_centres_of_their_halves` (cells 2 and 6).
- `test_zhu_courier_with_no_demand_in_its_radius_takes_its_whole_part_centroid`: on a 9-cell line with pickups only at cells 2 and 4 and r_G = 500 m, the courier at cell 0 reaches no pickup and goes to cell 3, the centroid of its whole part (cells 0 to 4); the courier at cell 8 owns cells 5 to 8, which hold no pickup, and gets no command. Watched failing first (no command before the fix).
- `test_zhu_at_zero_obedience_is_nearest_courier` (and obedient couriers are moved).
