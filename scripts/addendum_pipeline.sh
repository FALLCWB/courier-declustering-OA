#!/usr/bin/env bash
# G8 addendum pipeline (instructions of 2026-11-05; G8 verdict, ruling 7): once phase <k> of the full runs is complete,
# snapshot the complete lines of the running file, run the analysis on the families given (E1 and E2 again, which give
# identical numbers, so the joint reading and checks stay whole), with the sweep values of the plan run, and write the
# Q4 addendum numbers. A frozen rerun that differs from S8 writes STOP.
# Usage: bash scripts/addendum_pipeline.sh <full_dir> <pilot_dir> <n> <out_dir> <families> <phase>
set -euo pipefail
cd "$(dirname "$0")/.."
F=$1; P=$2; N=$3; O=$4; FAM=$5; K=$6
FIRST=avaliacao/20261102-2130-part1-untrained
PY=".venv/bin/python"
PLAN=$(cat "$F/plan.txt")
SWEEP="p0,p0.25,p0.5,p1"; [[ "$PLAN" == *":short" ]] && SWEEP="p0,p1"
mkdir -p "$O/snapshot"
$PY scripts/phase_status.py . "$F" "$PLAN" --wait-phase "$K" > "$O/phase_status.json" || { echo "phase $K not complete"; exit 1; }
$PY - "$F/episodes.jsonl" "$O/snapshot/episodes.jsonl" > "$O/snapshot.json" <<'PYEOF'
import hashlib, json, sys
raw = open(sys.argv[1], "rb").read()
cut = raw.rfind(b"\n") + 1
open(sys.argv[2], "wb").write(raw[:cut])
print(json.dumps({"source": sys.argv[1], "bytes": cut, "rows": raw[:cut].count(b"\n"),
                  "sha256": hashlib.sha256(raw[:cut]).hexdigest()}))
PYEOF
S="$O/snapshot"
nice -n 10 $PY sim/analysis_extension.py "$O/analysis" "$S" "$P" "$FIRST/results" "$FIRST" --n "$N" --families "$FAM" --sweep "$SWEEP" > "$O/analysis.log" 2>&1
if grep -q "FROZEN RERUNS DIFFER" "$O/analysis.log"; then echo "frozen reruns differ from S8" > "$O/STOP"; fi
nice -n 10 $PY scripts/paper_numbers_q4.py "$O/analysis" "$S" "$O/paper" --n "$N" --first "$FIRST/results"
rm -rf "$S"
if [ -e "$O/STOP" ]; then echo "addendum done $(date -Iseconds), WITH STOP: read STOP first" > "$O/DONE"
else echo "addendum done $(date -Iseconds), no stop" > "$O/DONE"; fi
