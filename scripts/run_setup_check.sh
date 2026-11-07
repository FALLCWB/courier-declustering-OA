#!/usr/bin/env bash
# S0 reproduction check on the server: rebuild the city, rerun the data profiles, tests and the sanity run.
# Usage: bash scripts/run_setup_check.sh <out_dir>
set -euo pipefail
OUT=$1
mkdir -p "$OUT" data/derived
export PATH=$HOME/.local/bin:$PATH
run() { echo "== $*" ; /usr/bin/time -f "%e s, %M KB" nice -n 10 "$@"; }
{
  run uv run python sim/city/build.py .
  cp sim/city/curitiba/build_report.txt "$OUT/build_report.txt"
  run uv run python scripts/profile_meituan.py data/raw/meituan data/derived
  cp data/derived/profile.txt "$OUT/meituan_profile.txt"
  run uv run python scripts/profile_grubhub.py data/raw/grubhub/mdrplib-master/public_instances > "$OUT/grubhub_profile.txt"
  run uv run python scripts/meituan_idle_behavior.py . "$OUT/meituan-idle-moments"
  run uv run pytest -q
  run uv run python scripts/sanity_run.py . "$OUT/sanity"
} 2>&1 | tee "$OUT/run.log"
echo DONE >> "$OUT/run.log"
