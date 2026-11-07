# G8 results: E1, E2, the R4 fresh block and the meet-up variants

This research was supported by data provided by Meituan.

Produced on FE-SIM-1 by `scripts/g8_pipeline.sh` when phase 1 of the full runs (`avaliacao/20261104-1911-full-extension`, plan `full:150:short`) was complete. The first run finished at 14:05, the second at 16:49 after the code review's fixes, and the third at 18:22 after the G8 verdict's D1 and A1 to A3. The confirmatory files (contrasts, classes, the fresh-block files, class counts, costs, profile, time to undo) are byte-identical across the three runs. The episode rows stay on FE-SIM-1, and every file here is an aggregate over seeds.

| Folder | What |
|---|---|
| `analysis/` | `sim/analysis_extension.py --families E1,E2`: contrasts with Holm and the R3 reading, classes, time to undo, costs, descriptive meet-ups, profile, the R4 fresh-block files, checks (frozen reruns against S8: 1,800 compared, 0 differ), and the Part 1 equivalence reading (post hoc) |
| `paper/` | `scripts/paper_numbers.py`: `paper-numbers-G8.md` with one CSV per table; `figures/` holds the Python previews, marked preview |
| `jusup/` | G8 item 1, couriers reached per policy step by adaptation 10 |
| `zhu_ties/` | G8 item 2, Zhu with random partition ties (post-freeze, outside every family) |
| `paper/a1_second_hour_split.csv`, `a2_km_split.csv`, `a3_evening_2000_2059.csv`, `q3_summary.csv` | G8 verdict: A1 second-hour split, A2 km split, A3 W1 over 20:00 to 20:59 (exploratory), D1 Q3 summary per model |
| `w1/` | W1 per minute for the W1-over-time figure (MATLAB renders it on CT 315) |
| `snapshot.json` | rows, bytes and sha256 of the episode snapshot the outputs were computed on |
