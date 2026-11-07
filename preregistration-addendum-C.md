# Pre-registration addendum C: preferred areas independent of the start (E6), and three exploratory analyses

This research was supported by data provided by Meituan.

| | |
|---|---|
| Added | 2026-11-07, after the freeze of `preregistration-extension.md` (8e082e3) and after the extension's results (G8 and its addenda) were seen |
| Decided by | Filipe Lemos, package C of the response to the external review of Paper A (2026-11-07) |
| State of the data when added | No episode of E6 or of the exploratory parts 2 to 4 existed. This file was committed before the first episode of any of them. Part 5 (tables from the existing runs) needs no new episode. |
| Frozen text | `preregistration.md`, `preregistration-extension.md` and `preregistration-extension-addendum-R3.md` are unchanged. |

Throughout: seeds as stated per part; fitted behavior unless stated; arm C (Zhu et al., Jusup et al.) at 100% obedience; the DQN (Jahanshahi et al.) as a descriptive row; differences are model minus nearest courier, paired by seed, lower is better; intervals are 95% percentile bootstraps over seeds (10,000 resamples, generator seed 20261103 keyed by the contrast); metrics as in `preregistration-extension.md` section 4.

## 1. E6: clustered starts with preferred areas independent of the start (confirmatory)

**Behavior setting `indep`.** The same as the fitted behavior, except the preferred area. Each courier's preferred area is the set of cells within 2 km of a home cell drawn independently of its start cell. The home cell comes from the scattered start's distribution, proportional to the pickups expected in the first 30 min, and is drawn from the courier's own random stream, keyed by (seed, 41, courier). The start cells, the orders and every other draw stay as in E2, so the contrasts pair with E2 by seed.

**Cells and runs.**
- Cells: the big cluster, three clusters and the mixed start, each at tight, normal and loose supply (9 cells).
- Models: all ten. Seeds: 1001 to 1150, n = 150 (the extension's n). That is 13,500 episodes.

**Contrasts.**
- E6 holds W1 over the first 60 min for the 8 tested models in the 9 cells (72 contrasts) and p90 order to door for the same 8 models in the 9 cells (72), so 144 in all.
- The 8 tested models are Xu et al., Li et al., Auad et al., Zhu et al., Jusup et al., FoodMatch, forecast-aware matching and mirror backpressure.
- Each contrast takes a two-sided paired t-test, with Holm at 0.05 within E6.

**Smallest effects (as in E2):**
- W1 over 60 min: 10% of nearest courier's pilot mean of that metric in the same cell (fitted behavior, seeds 1 to 30, `pilot_nearest_means.csv`).
- p90 order to door: 1.0 min.

**Readings (as in E2):**
- The joint class per cell and model (undoes at no delivery cost, at a delivery cost, cost unresolved, or does not undo), with p90 from E6 itself.
- The R3 equivalence reading.
- The time to undo, against the same model, obedience, supply level and seed from the scattered start. The reference uses the fitted behavior's existing scattered rows: under `indep` the homes are drawn from the scattered start's distribution, so the scattered start is the same reference.
- The second-hour check.

**Pre-registered secondary (descriptive).** W1 over 20:00 to 20:59, model minus nearest courier, with paired intervals, in the 9 cells. It measures whether the evening re-forming, and arm C's evening edge, survive when the preferred areas do not lie inside the starting cluster.

## 2. Exploratory: stay without commands (suppression against repositioning)

**Policy `stay`.**
- Nearest-courier assignment; every obedient idle courier stays where it is unless dispatched.
- It is an arm C policy with an empty command set, run at 100% obedience, and it reuses the obedience machinery: obedient couriers make no idle decision of their own.
- A test checks that at 0% obedience `stay` equals nearest courier in every metric.

**Cells.**
- The 16 primary cells: the scattered and burst starts and the three clustered starts, each at three supply levels, and the meet-up.
- Fitted behavior, seeds 1001 to 1150 (2,400 episodes).

**Report** (exploratory, no test):
- `stay` minus nearest courier, Zhu et al. minus `stay`, and Jusup et al. minus `stay`, paired by seed.
- Metrics: W1, W1 over the first 60 min, W1 over 20:00 to 20:59, p90 order to door, and km without an order per order.
- The second and third contrasts are the active-repositioning part of arm C.

## 3. Exploratory: one coherent behavior specification (Ashkrof et al.)

**Setting `ashkrof`.**
- The part-time coefficient of the stay utility is set to 0, so every remaining coefficient comes from Ashkrof et al.'s Scenario 1 Primary.
- The stay constant (beta0) and the return probability are recalibrated with the same Meituan moments and the same simulated method of moments as the fitted behavior (`sim/behavior_fit.py`, single-decision structure).
- The calibration grid covers these two only. The decision interval (42 s) and the cruise radius (2,000 m) stay at their fitted values.
- The new values, their bootstrap intervals and the moments are reported as in the paper's Table 1.
- Episodes start only after the recalibration.

**Cells.** The 16 primary cells, all ten models, seeds 1001 to 1030 (4,800 episodes).

**Report** (exploratory, no test):
- Each model's W1 contrast (W1 over 60 min on the Q2 cells) and p90 contrast against nearest courier.
- The joint class, read by the same rule. As a reading device, not a confirmatory test, Holm runs within the E1-shaped and E2-shaped contrast sets of this part.
- These sit beside the main results at the same 30 seeds, read the same way, and every class that changes is listed.

## 4. Exploratory: noisy demand information

**Setting.**
- Forecast-aware matching, Li et al., Zhu et al. and Jusup et al. receive the expected demand multiplied by a lognormal factor with mean 1 and coefficient of variation 0.2, so sigma = sqrt(ln 1.04).
- The factor is drawn per zone (H3 resolution 8) and per episode, is fixed for the episode, and comes from its own stream keyed by (seed, 31, zone).
- It multiplies the expected pickups and the expected drop-offs of every cell in the zone, wherever these four policies read them.
- W1 keeps the true expected demand.
- Trained policies are not retrained: they read the noisy input at run time.

**Cells.**
- The 16 primary cells, seeds 1001 to 1030: 4 models x 16 cells x 30 seeds = 1,920 episodes.
- Nearest courier's rows at these seeds come from the full runs.

**Report** (exploratory, no test): the four models' contrasts with noisy input beside those with true input at the same seeds, with the joint class read as in part 3.

## 5. Tables from the existing runs (descriptive, no new episode)

- W1 over 0 to 60, 60 to 120 and 180 to 240 min after the cluster appears, per model, on the clustered starts and on the meet-up (0 to 60 and 60 to 120 only).
- Q1 W1 and the E1 W1 contrasts without 20:30 to 21:00.
- Per-policy means (5 policies x 30 seeds) of every E1 and E2 contrast of Xu et al., Li et al., Auad et al. and Jusup et al.
- W1 over 20:00 to 20:59 at return probability 0, fitted and 1, for nearest courier, Zhu et al., Jusup et al. and Xu et al. on the clustered starts.

## Order

Part 5 first, then E6, then parts 2, 4 and 3; part 3 starts after its recalibration. All runs on the project's simulation server, under the CPU rule.
