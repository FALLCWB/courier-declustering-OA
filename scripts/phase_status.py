"""Progress of a run of sim/run_extension.py by phase (1 = E1 and E2, 2 = meet-ups, 3 = E5, 4 = E3 and E4).

Usage: python scripts/phase_status.py <project_root> <run_dir> <plan> [--wait-phase <k>]
Prints done/planned per phase; with --wait-phase, exits 0 if phase k is complete and 1 otherwise.
"""
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from sim.run_extension import jobs, key, phase  # noqa: E402

run, plan = Path(sys.argv[2]), sys.argv[3]
man = json.loads((ROOT / "scenarios/manifest.json").read_text())
planned = jobs(plan, man)
path = run / "episodes.jsonl"
raw = path.read_bytes() if path.exists() else b""
raw = raw[:raw.rfind(b"\n") + 1]                         # a line still being written is not counted
done = {key(json.loads(line)) for line in raw.decode().splitlines() if line.strip()}
status = {}
for j in planned:
    p = phase(j)
    d, t = status.get(p, (0, 0))
    status[p] = (d + (key(j) in done), t + 1)
print(json.dumps({str(p): {"done": d, "planned": t} for p, (d, t) in sorted(status.items())}))
if "--wait-phase" in sys.argv:
    k = int(sys.argv[sys.argv.index("--wait-phase") + 1])
    d, t = status[k]
    sys.exit(0 if d == t else 1)
