"""Append episode rows from stdin to a run's episodes.jsonl that another process is also appending to (the FE-SIM-1
runner), skipping any row whose key is already in the file, so a resend after a dropped connection never duplicates.
Each line goes out in one write on an O_APPEND descriptor, so it never interleaves with the runner's own lines.
Usage: python scripts/append_rows.py <episodes.jsonl> < rows.jsonl
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim.run_extension import key  # noqa: E402


def main():
    path = Path(sys.argv[1])
    raw = path.read_bytes() if path.exists() else b""
    done = {key(json.loads(x)) for x in raw[:raw.rfind(b"\n") + 1].decode().splitlines() if x.strip()}
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    added = skipped = 0
    try:
        for line in sys.stdin.buffer:
            if not line.endswith(b"\n") or not line.strip():
                continue
            k = key(json.loads(line))
            if k in done:
                skipped += 1
                continue
            os.write(fd, line)
            done.add(k)
            added += 1
    finally:
        os.close(fd)
    print(f"appended {added}, skipped {skipped}")


if __name__ == "__main__":
    main()
