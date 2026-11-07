"""Extension plan X0: the four frozen models replay the S8 episodes bit for bit.

Reference: `tests/regression/s8_reference.json`, written by `scripts/make_regression_reference.py` from the S8 full runs
(`avaliacao/20261102-2130-part1-untrained/episodes.jsonl` on FE-SIM-1): five seeds (1001 to 1005) per start, normal
supply, fitted behavior, the four models, 100 episodes. The test needs the built city (FE-SIM-1 only) and runs when
RUN_REGRESSION=1. The comparison runs in a plain Python process (`scripts/regression_check.py`): inside pytest's own
process the W1 metrics differed by up to 2 units in the last place while a plain process reproduces every value.
REGRESSION_WORKERS sets the number of worker processes (default up to 20).
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(os.environ.get("RUN_REGRESSION") != "1" or not (ROOT / "sim/city/curitiba").exists(),
                    reason="needs the built city and RUN_REGRESSION=1 (FE-SIM-1)")
def test_frozen_models_replay_s8_episodes_bit_for_bit():
    cmd = [sys.executable, str(ROOT / "scripts/regression_check.py")]
    if os.environ.get("REGRESSION_WORKERS"):
        cmd.append(os.environ["REGRESSION_WORKERS"])
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, res.stdout[-2000:] + res.stderr[-2000:]
