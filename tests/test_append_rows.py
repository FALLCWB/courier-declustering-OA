"""scripts/append_rows.py: rows of the PC's share appended to the FE-SIM-1 run file without duplicates."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def row(seed, model="nearest"):
    return {"set": "new", "scenario": "burst", "level": "tight", "behavior": "p0", "model": model, "obedience": None,
            "seed": seed, "w1_rule_min": 1.5}


def test_append_skips_keys_already_in_the_file_and_keeps_whole_lines(tmp_path):
    f = tmp_path / "episodes.jsonl"
    f.write_text(json.dumps(row(1001)) + "\n" + json.dumps(row(1002)) + "\n")
    new = "".join(json.dumps(r) + "\n" for r in (row(1002), row(1003), row(1003, "xu")))
    res = subprocess.run([sys.executable, str(ROOT / "scripts/append_rows.py"), str(f)], input=new, text=True,
                         capture_output=True, check=True)
    lines = f.read_text().splitlines()
    assert len(lines) == 4 and [json.loads(x)["seed"] for x in lines] == [1001, 1002, 1003, 1003]
    assert "appended 2, skipped 1" in res.stdout
