"""BLAS threads of every evaluation run.

The S8 episodes (and the regression reference built from them) ran with OpenBLAS's default on FE-SIM-1, 30 threads (one
per vCPU). Results depend on the exact count (DECISIONS.md, 2026-11-04). Measured on the S8 regression episodes:
  1 thread: 89 of the 100 episodes differ; W1 metrics differ in the last digit for every model, and forecast-aware
            matching takes other decisions in 20 of its 25 episodes (delivery and distance metrics differ too);
  2 and 8 threads: 5 episodes replayed, chosen among those that differ at 1 thread, and all 5 differ: the 3
            forecast-aware episodes take other decisions, the 2 mirror backpressure ones differ in W1 only;
            a rate over all 25 forecast-aware episodes was not measured at these counts;
  30 threads and the default: the same 5 episodes, and the full regression, match bit for bit.
Evaluation scripts call pin() before numpy is imported; every runner row records threads().
Training runs keep one thread per process (their own seeds, never compared with S8).

CPU rule (G7 verdict, ruling 5): 30 BLAS threads per worker are kept, so the reused frozen cells and their extension
keep the same numbers, but the worker cap is not a CPU cap. During a run the busy CPUs are logged every minute, and the
worker count is set so that they stay at or below 24 of FE-SIM-1's 30 vCPUs: cut workers, never threads (the worker
count changes no value). The count used is recorded in DECISIONS.md.
"""
import os
import sys

EVAL_THREADS = 30
VARS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")


def pin(n=EVAL_THREADS):
    """Set the BLAS thread count for this process and its workers; must run before numpy loads."""
    if "numpy" in sys.modules:
        raise RuntimeError("pin the BLAS threads before numpy is imported")
    for v in VARS:
        os.environ[v] = str(n)


def threads():
    """OpenBLAS threads in use now (0 when OpenBLAS is not loaded)."""
    from threadpoolctl import threadpool_info
    return max((i["num_threads"] for i in threadpool_info() if i.get("internal_api") == "openblas"), default=0)
