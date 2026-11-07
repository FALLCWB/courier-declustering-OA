#!/usr/bin/env bash
# G8 pipeline (instructions of 2026-11-05, sections 3 and 4), on FE-SIM-1 once phase 1 of the full runs is complete
# (E1, E2 and the R4 fresh block). It snapshots the complete lines of the run's episodes.jsonl (the run keeps appending)
# so that every step reads the same rows, then: the E1 and E2 analysis with the R3 equivalence reading and the R4 fresh
# block, the Part 1 equivalence reading (post hoc), the Zhu tie sensitivity, the Jusup adaptation-10 counts, the W1 over
# time CSV, the paper numbers and the Python figure previews. A frozen rerun that differs from S8 writes STOP (a stop
# condition under Filipe's no-pause rule); the outputs are still written for the record.
# Usage: bash scripts/g8_pipeline.sh <full_dir> <pilot_dir> <n> <out_dir>
set -euo pipefail
cd "$(dirname "$0")/.."
F=$1; P=$2; N=$3; O=$4
FIRST=avaliacao/20261102-2130-part1-untrained
PY=".venv/bin/python"
mkdir -p "$O/snapshot"
$PY scripts/phase_status.py . "$F" "$(cat "$F/plan.txt")" --wait-phase 1 > "$O/phase_status.json" || { echo "phase 1 not complete"; exit 1; }
$PY - "$F/episodes.jsonl" "$O/snapshot/episodes.jsonl" > "$O/snapshot.json" <<'PYEOF'
import json, sys
raw = open(sys.argv[1], "rb").read()
cut = raw.rfind(b"\n") + 1
open(sys.argv[2], "wb").write(raw[:cut])
import hashlib
print(json.dumps({"source": sys.argv[1], "bytes": cut, "rows": raw[:cut].count(b"\n"),
                  "sha256": hashlib.sha256(raw[:cut]).hexdigest()}))
PYEOF
S="$O/snapshot"
nice -n 10 $PY sim/analysis_extension.py "$O/analysis" "$S" "$P" "$FIRST/results" "$FIRST" --n "$N" --families E1,E2 > "$O/analysis.log" 2>&1
if grep -q "FROZEN RERUNS DIFFER" "$O/analysis.log"; then echo "frozen reruns differ from S8" > "$O/STOP"; fi
nice -n 10 $PY scripts/equivalence_part1.py "$FIRST/results" "$O/analysis" > /dev/null
nice -n 10 $PY scripts/zhu_ties_report.py . avaliacao/20261104-1416-zhu-random-ties "$S" "$O/zhu_ties" > "$O/zhu_ties.log" 2>&1
nice -n 10 $PY scripts/jusup_events_report.py "$S" "$O/jusup" --n "$N"
nice -n 10 $PY scripts/x9_w1_over_time.py "$S" "$O/w1" --n "$N" > "$O/w1.log" 2>&1
nice -n 10 $PY scripts/paper_numbers.py "$O/analysis" "$S" "$O/zhu_ties" "$O/paper" --n "$N" --first "$FIRST/results"
nice -n 10 $PY scripts/preview_figures.py "$O/analysis" "$O/w1" "$O/paper/figures"
rm -rf "$S"
if [ -e "$O/STOP" ]; then echo "G8 pipeline done $(date -Iseconds), WITH STOP: read STOP first" > "$O/DONE"
else echo "G8 pipeline done $(date -Iseconds), no stop" > "$O/DONE"; fi
