"""Write tests/regression/s8_reference.json from the S8 full runs (extension plan X0).

Usage: python scripts/make_regression_reference.py <project_root> <s8_run_dir>
Takes seeds 1001 to 1005 of every start, normal supply, fitted behavior, the four frozen models (100 episodes), with the
metrics `tests/test_regression.py` compares. Values are written with full float precision (JSON round trip).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from tests.test_regression import METRICS  # noqa: E402


def main():
    # the json module reads floats exactly; pandas' default JSON parser rounds the last digit
    with (Path(sys.argv[2]) / "episodes.jsonl").open() as f:
        ep = pd.DataFrame([json.loads(line) for line in f if line.strip()])
    sel = ep[(ep.family == "F1") & (ep.level == "normal") & (ep.behavior == "fitted") & ep.seed.between(1001, 1005)]
    cases = [{"scenario": r["scenario"], "level": r["level"], "behavior": r["behavior"], "seed": int(r["seed"]),
              "model": r["model"], "expected": {k: (int(r[k]) if k in ("delivered", "undelivered", "orders") else float(r[k]))
                                                 for k in METRICS}}
             for _, r in sel.sort_values(["scenario", "model", "seed"]).iterrows()]
    out = ROOT / "tests/regression/s8_reference.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(cases, indent=1))
    print(len(cases), "cases written to", out)


if __name__ == "__main__":
    main()
