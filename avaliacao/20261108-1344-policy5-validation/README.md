# Policy 5 on validation seeds disjoint from its training

This research was supported by data provided by Meituan.

Exploratory check, outside every family, declared in `DECISIONS.md` at 5a15a35 before any episode (Filipe, 2026-11-08: "Package B"). Training seed 5 trains on episode seeds 95000 to 95199, which contain the validation seeds 95001 to 95003; this run puts the curve code's validation cases on 95501 to 95503, which no training, gate or choice of Xu et al., Li et al., the deep Q-network or Auad et al. ever ran.

- Run: `sim/policy5_validation.py . <this folder> 20` on FE-SIM-1, 2026-11-08 13:44 to 13:54 (FE-SIM-1 clock; the folder's label is the PC's), one BLAS thread per process, 20 workers, at most 20 of 30 vCPU busy (`cpu_vmstat.log`, not in git). 288 episodes in `rows.jsonl` (sha256 beside it), each with `blas_threads` 1.
- Report: `scripts/policy5_report.py`, outputs in `results/` (`paper-numbers-policy5.md` and five CSVs). The rows for 95001 to 95003 come from the frozen training folders' `curve.csv`; the 35.9 min sources from `avaliacao/20261102-1026-calibration` and the full runs' episodes (FE-SIM-1).

Result: under the declared rule policy 5 reads as unaffected by the overlap (every gap within the range of policies 1 to 4, widened by 0.10 min for W1 and 0.5 min for p90).
