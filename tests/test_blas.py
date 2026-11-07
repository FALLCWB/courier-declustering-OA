"""BLAS threads of evaluation runs: the S8 episodes reproduce bit for bit only at OpenBLAS's 30 threads (DECISIONS.md)."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif((os.cpu_count() or 0) < 30, reason="OpenBLAS caps its threads at the processors it sees, so this "
                    "check needs 30 of them; on a smaller machine scripts/fake_nprocs.c restores the 30 threads")
def test_pin_sets_thirty_blas_threads_before_numpy_loads():
    code = ("import sys; sys.path.insert(0, %r)\n"
            "from sim.blas import pin, threads\n"
            "pin()\n"
            "import numpy\n"
            "print(threads())") % str(ROOT)
    env = {"PATH": "/usr/bin:/bin", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "30"


def test_pin_refuses_once_numpy_is_loaded():
    import numpy  # noqa: F401
    from sim.blas import pin
    with pytest.raises(RuntimeError):
        pin()
