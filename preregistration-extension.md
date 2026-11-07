# Pre-registration: extension to ten models, prevent and undo

Plan: `plans/2026-11-02-extension.md`, step X6, objective X4. Written 2026-11-04, before any run of a new model on an evaluation seed (the learned models' validation seeds 95001 to 95003, the check seeds 96001 to 96030 and the end-to-end seed 501 lie outside the evaluation seeds). Frozen by the commit that applies the G7 verdict's edits E1 to E4, whose hash is recorded in `DECISIONS.md` and at the top of `reviews/G8-request.md`. The frozen first round (`preregistration.md`, 126631b) stands unchanged; its results are carried into the profile and its contrasts are not tested again. Every later change goes to Filipe as a choice (rerun, narrower claim, limitation) and into the plan's "Changes to the plan". This research was supported by data provided by Meituan.

## 1. Questions and unit

For ten published dispatch models in three arms (which courier gets each order, when to assign, moving idle couriers), four questions are answered against nearest-courier dispatch:

- **Q1, prevent:** starting spread out, does the model keep idle couriers from clustering?
- **Q2, undo:** given a cluster nobody chose, does the model spread the couriers, and how fast?
- **Q3, cost:** what does it pay in delivery time and in kilometres ridden without an order?
- **Q4, conditions:** do the answers hold across drift-back, supply and, in arm C, obedience?

Each model's result is read against its own claim in `literature/claims.md`. The goal is a profile per model, not a ranking.

- **Unit, common random numbers and pairing:** as in `preregistration.md` section 1. One episode is one simulated evening, 17:00 to 21:00 plus up to 3 h of drain, with its own seed; within a cell (start or scenario x supply level x behavior setting x model x obedience level), every model sees the same orders, start cells, preferred areas, full-time flags, behavior streams and obedience draws. Comparisons are paired by seed within a cell.

## 2. Inputs (fixed at the freeze commit)

- Everything listed in `preregistration.md` section 2, unchanged.
- Simulator additions of X2, off by default and covered by the bit-for-bit regression on the S8 episodes: holding (arm B), relocation commands with per-courier obedience (arm C), the meet-up, the Q2 metrics.
- Models and trained policies: `models/`, fidelity notes in `models/fidelity/`, trained files in `models/trained/` (five per learned model, training seeds 1 to 5).
- Meet-up: `scenarios/manifest.json`, key `meetup`, and the exploratory point, key `meetup_median` (section 3).
- Floating point: every evaluation run pins 30 OpenBLAS threads before numpy loads (`sim/blas.py`), the setting of S8; values depend on the exact count, and every row records it (`blas_threads`).

## 3. Design

| # | Model | Arm | In the tests |
|---|---|---|---|
| 1 | Nearest courier | baseline | reference of every contrast |
| 2 | FoodMatch, bundling off (Joshi et al. 2021) | A | frozen; new contrasts only on Q2 metrics and the meet-up |
| 3 | Forecast-aware matching (Ozkan and Ward 2020) | A | as row 2 |
| 4 | Mirror backpressure (Kanoria and Qian 2024) | A | as row 2 |
| 5 | Learning and planning, value table with Kuhn-Munkres (Xu et al. 2018) | A | yes |
| 6 | Mean-field actor-critic (Li et al. 2019) | A | yes |
| 7 | Deep Q-network, assignment action only (Jahanshahi et al. 2022) | A | no: descriptive row, "equal to nearest courier by construction in this setting" (G6 verdict, ruling 3) |
| 8 | Assignment with holding (Auad, Lagos and Lagos 2026) | B | yes |
| 9 | Coverage control (Zhu et al. 2024) | C | yes, at 100% obedience in the primary families |
| 10 | Constrained mean-field RL (Jusup et al. 2026) | C | as row 9 |

Factors:

| Factor | Levels |
|---|---|
| Start or scenario (6) | the five frozen starts (big cluster, three clusters, scattered, mixed, burst) and the meet-up |
| Supply level (3) | tight, normal, loose, as frozen; the meet-up runs at normal supply only (plan decision 4) |
| Behavior setting (5) | fitted (return probability 0.75) and the return sweep 0, 0.25, 0.5, 1 |
| Obedience (arm C) | 25, 50, 75 and 100% with the fitted behavior; 100% under the return sweep; 0% on the pilot seeds only, as the identity check (section 8) |

**Meet-up.** The scattered start at normal supply; at 19:00, 20% of the idle couriers, drawn from the seed, are at one cell and stay online there (jump variant, primary). The cell is fixed by rule: among cells at least 3 km (straight line) from the three cluster hubs and with resident population above zero, the cell with the fewest expected pickups within 2 km over 19:00 to 20:00; ties go to the tied cell closest to the city centre. The rule gives cell 89a804cb377ffff, 10.6 km from the centre, with no expected pickup within 2 km (the median populated cell has 72). Couriers keep their own preferred areas, so drift-back pulls them home. The share check on seeds 96001 to 96030 kept 20% (nearest courier's W1 at 19:15 rose by 3.47 min, 95% CI 3.30 to 3.65, 61% of its value without the meet-up, against the 10% threshold; `avaliacao/20261104-0109-meetup-share-check/`). The meet-up happens before the dispatch and the snapshot of 19:00, as a start precedes those of 17:00. Riding to the point (`meetup_ride`) is a sensitivity run: all ten models, normal supply, fitted behavior, descriptive only (W1 over 60 min and p90; no time to undo, since the cluster forms only after 19:00).

**Exploratory meet-up at a median-demand point** (G7 verdict, ruling 6 and E2(c); pre-registered, outside every family, no test). The fringe point has no pickup within 2 km, so orders never thin that cluster. This run adds a middle case. Point: among the meet-up's eligible cells, the cell whose expected pickups within 2 km over 19:00 to 20:00 is closest to the median over those cells; ties go to the cell closest to the city centre. The rule gives cell 89a804db203ffff (`scenarios/manifest.json`, key `meetup_median`): 61.1 expected pickups within 2 km, the median over the 3,477 eligible cells; 10.9 km from the centre and 5.7 km from the nearest hub. Runs: all ten models (arm C at 100% obedience), jump variant, 20% of the idle couriers at 19:00, normal supply, fitted behavior, seeds 1001 to 1030. Reported per model: W1 over 60 min, time to undo (against the same model and seed from the scattered start), and p90 order to door beside the share of orders unassigned for more than 30 min.

**Cells to run.** Cells already run in S8 (four frozen models x five starts x three supply levels x five behavior settings) are reused with their seeds. New cells: the four learned or holding models (rows 5 to 8) in all 16 start-supply combinations under the five behavior settings (320 cells); the four frozen models on the meet-up under the five settings (20); the two arm C models in the 16 combinations at four obedience levels under the fitted behavior and at 100% under the four sweep values (256); the ride variant (10); the exploratory meet-up (10, seeds 1001 to 1030 only). The pilot also runs arm C at 0% (32 cells).

## 4. Metrics (per episode)

- **W1** (Q1 primary) and **p90 order to door** (co-primary of every question): as frozen in `preregistration.md` section 4. W1 counts an idle courier at the cell it is in, so a relocating courier counts where it is along its route; a meet-up courier counts at the point from 19:00.
- **W1 over the 60 min after the cluster appears** (Q2 primary): the mean of the soon-free W1 snapshots from 17:00 to 17:59 for the clustered starts and from 19:00 to 19:59 for the meet-up. Reason, fixed before any comparison: it is continuous, every episode contributes, it is defined the same way for the starts and the meet-up, and it covers the hour in which most of the gap arises (G5 P2: 61% of nearest courier's evening-mean gap on the big cluster accrues before 18:30 under the fitted behavior, 83% at return probability 0).
- **Time to undo** (Q2 secondary, descriptive): minutes from the cluster's appearance until the model's per-minute W1 first comes within 10% of the W1, at the same clock time, of the same model at the same obedience level, supply level, behavior setting and seed from the scattered start, censored at 21:00 (`sim.stats.time_to_undo`); reported as the median over seeds with the share of censored episodes. It stops at the first crossing, so it does not see a cluster that re-forms later (under the fitted behavior, nearest courier's big-cluster gap reopens after 19:30 as couriers return home; G5 P2).
- **Q3, cost:** p90 order to door (co-primary) and, descriptive, kilometres without an order per order, idle km per order, the share of orders unassigned for more than 30 min and the number of orders undelivered at the drain's end, reported beside every p90 (G4 verdict V4, G6 verdict ruling 2).
- **Other secondary metrics:** those of `preregistration.md` section 4, descriptive, and for arm C the share of free obedient couriers moved per 20 min.

## 5. Families and tests

Each contrast is a model against nearest courier in one cell, on one metric: the mean over seeds of the paired difference, model minus nearest; lower is better for every metric. Intervals: 95% percentile bootstrap over seeds, 10,000 resamples, generator seed 20261103. p-values: two-sided paired t-test. Multiplicity: Holm step-down at alpha 0.05 within each family, never across families. "Established": Holm-adjusted p below 0.05. A contrast already in F1 to F4 is not tested again.

Q1 cells: scattered and burst starts x 3 supply levels (6). Q2 cells: big cluster, three clusters and mixed starts x 3 supply levels, and the meet-up (10). Tested models: Xu, Li, Auad, Zhu and Jusup (the five new) and, on Q2 metrics and the meet-up only, FoodMatch, forecast-aware matching and mirror backpressure (the frozen three).

| Family | Contrasts | Number |
|---|---|---|
| E1, Q1 primary | 5 new models x {W1, p90} x 6 Q1 cells, fitted behavior | 60 |
| E2, Q2 primary | 8 models x W1 over 60 min x 10 Q2 cells (80); 5 new models x p90 x 10 Q2 cells (50); 3 frozen models x p90 x the meet-up (3); fitted behavior | 133 |
| E3, Q4 sweep for Q1 | E1's contrasts at return probability 0, 0.25, 0.5 and 1 | 240 |
| E4, Q4 sweep for Q2 | E2's contrasts at the four sweep values | 532 |
| E5, Q4 obedience | Zhu and Jusup at 25, 50 and 75% x the primary metrics of E1 and E2 in their cells (2 x 6 + 2 x 10 per level), fitted behavior | 192 |

Arm C enters E1 to E4 at 100% obedience, labelled an upper bound, never real courier behavior. Supply levels are part of the cells of every family.

**Joint reading** (as `preregistration.md` section 5, per primary cell and model, exactly one class):

| Class | W1 (Q1) or W1 over 60 min (Q2) | p90 order to door |
|---|---|---|
| prevents (Q1) or undoes (Q2) at no delivery cost | established lower, estimate at least the smallest effect | upper end of the 95% interval below +1.0 min |
| prevents or undoes at a delivery cost | as above | established higher, estimate at least +1.0 min |
| prevents or undoes, cost unresolved | as above | every other case |
| does not prevent or undo | any other result; an established increase is reported as such | any |

**Profile** (objective X6): one row per model with its claim from `literature/claims.md`, the count of Q1 cells per class (F1 for the frozen three, E1 for the new five), the count of Q2 cells per class (E2), the median time to undo against nearest courier's, and the cost columns. The DQN row is descriptive.

For every Q2 cell classed as undoing (any of the first three classes), the profile also reports two numbers beside nearest courier's in the same cell: the mean over seeds of W1 over the next 60 min (the soon-free W1 snapshots from 18:00 to 18:59 for the clustered starts and from 20:00 to 20:59 for the meet-up, read from the per-minute series) and the median time to undo. If the model's second-hour mean is higher than nearest courier's by at least the smallest effect (10% of nearest courier's mean of that metric in that cell), or its median time to undo is longer than nearest courier's, the row reads "undoes in the first hour, not after". This is descriptive, with no test (G7 verdict, ruling 3 and E2(b)).

## 6. Smallest effects, pilot and sample size

- **Smallest effects of interest:** W1 and W1 over 60 min: 10% of nearest courier's mean of the same metric in the same cell, from the pilot; p90 order to door: 1.0 min.
- **Pilot (X7):** every new cell with seeds 1 to 30 (the frozen cells have their S7 pilot); used only for sigma_d of each paired difference and for runtime; never reused in the main analysis.
- **Sample size:** n_c = ceil(((z_(1 - alpha*/2) + z_0.80) x sigma_d / delta)^2), with alpha* = 0.05 divided by the size of the contrast's family (Holm's first threshold: 0.05/60 in E1, 0.05/133 in E2) and 80% power; n = the largest n_c over the E1 and E2 contrasts, at least 30, rounded up to a multiple of 10; the same n for every new cell of every family. Full runs use seeds 1001 to 1000 + n; if n exceeds 30, the reused frozen cells (nearest courier included) are extended with seeds 1031 to 1000 + n by the same code.
- **Runtime limit:** if the estimate for the full runs on 24 cores of FE-SIM-1 exceeds 24 h, Filipe chooses between fewer sweep values and fewer obedience levels (plan step X7); E1 and E2 always run in full.

## 7. Trained policies, obedience and seeds

- **Trained policies:** evaluation seed s runs the policy of training seed ((s - 1) mod 5) + 1 (G6 verdict, "For X5 and X6"), so training variance is part of each learned model's spread; the means per policy are reported as descriptive results.
- **Obedience:** each courier is drawn once per episode as obedient or not, from the seed (nested: a courier obedient at 25% is obedient at 50%). A non-obedient courier keeps the fitted behavior; an obedient courier without a command stays where it is (G6 verdict, ruling 5).
- **Seeds:** evaluation seeds 1 to 30 (pilot) and 1001 on (full runs); none of them was used in training, validation (95001 to 95003), the gate runs (97001 to 97005), the checks (96001 to 96030) or the end-to-end check (501). Training seed 5's episodes overlap the validation seeds (G6 verdict); no evaluation seed is affected.

## 8. Exclusions and checks

- No episode is excluded. Undelivered orders and empty W1 snapshots are handled as in `preregistration.md` section 7.
- **Identity checks before the full runs:** each arm C model at 0% obedience equals nearest courier on every metric of every pilot episode; Jahanshahi et al. is reported beside nearest courier. A failed identity check stops the runs as a defect.
- **Regression:** the S8 regression passes on the code that makes the full runs.
- **Review:** before the full runs, five review agents read the scripts that produce numbers (plan step X8); they can change code only to fix a defect, and every number that changes is rerun and reported.

## 9. What the analysis does not do

- No bundling, prices, bonuses, push messages, human participants or courier rejection beyond obedience.
- No new robustness layouts or D1 runs for the new models (F3 and F4 stay first-round only).
- No contrast of Jahanshahi et al. against nearest courier, no test across families, no post hoc subgroup, no ranking of models.
- No data from any Brazilian platform.
