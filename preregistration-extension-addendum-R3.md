# Pre-registration addendum R3: equivalence reading of contrasts that are not established

This research was supported by data provided by Meituan.

| | |
|---|---|
| Added | 2026-11-05, after the freeze of `preregistration-extension.md` at commit 8e082e3 |
| Decided by | Filipe Lemos, on the paper-review verdict of 2026-11-04 (risk R3) |
| State of the data when added | No E1 or E2 contrast had been computed or seen. The full runs' rows existed only in `episodes.jsonl` on FE-SIM-1, and no analysis had read them. The only numbers seen were the pilot's (seeds 1 to 30), which section 6 keeps for variances, smallest effects and runtime, and the pilot profile labelled pilot. |
| Frozen text | `preregistration-extension.md` is unchanged. This file adds a secondary reading and changes nothing in the frozen text. |

## Rule

For every confirmatory contrast of E1 to E5 that is not established (Holm-adjusted p of 0.05 or more within its family), the analysis reports whether its 95% paired bootstrap interval lies strictly inside (-delta, +delta). Delta is that metric's pre-registered smallest effect: 10% of nearest courier's mean W1 in the cell, from the pilot, for W1 and W1 over 60 min, and 1.0 min for p90 order to door (section 6).

Each such contrast gets one of two labels:

- "equivalent within delta": the whole interval lies inside (-delta, +delta);
- "inconclusive": the interval touches or crosses -delta or +delta.

An established contrast gets no equivalence reading. A quantity without a pre-registered smallest effect gets no equivalence reading, and the report says so. These quantities are the time to undo, the share of orders unassigned for more than 30 min, and the Q3 cost metrics other than p90.

## Standing

The reading is secondary. It changes no confirmatory class, no joint-reading class and no Holm result. The bootstrap interval is the one already pre-registered for each contrast (10,000 resamples, generator seed 20261103 keyed by the contrast).

## Part 1

The same reading is applied to the first round's contrasts (families F1 to F4). It is labelled "post hoc" everywhere, because those results were seen before this addendum.

## Implementation

- `sim/analysis_extension.py`, function `equivalence`: column `equivalence` in `contrasts.csv`, with counts per family in `results.md`.
- `scripts/equivalence_part1.py`: `equivalence_part1_post_hoc.csv` and `.md`, from the first round's `contrasts.csv`.
- Tests `tests/test_equivalence.py`, watched failing at 4b3ce3f before the code of 2f48c2b existed (DECISIONS.md, 2026-11-05).
