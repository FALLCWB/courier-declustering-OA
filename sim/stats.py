"""Statistics fixed in preregistration.md, sections 5 and 6: paired contrasts, bootstrap intervals, Holm, the joint
reading of the co-primaries (G3 verdict C1) and the sample-size rule.
"""
import math
import zlib

import numpy as np
from scipy import stats

N_BOOT = 10_000
BOOT_SEED = 20261103
P90_SESOI_MIN = 1.0
W1_SESOI_SHARE = 0.10


def contrast_rng(cell, model, metric, seed=BOOT_SEED):
    """Bootstrap generator of one contrast: seed 20261103 with the contrast's own key, so an interval never depends on
    which contrasts ran before it."""
    return np.random.default_rng([seed, zlib.crc32(repr((tuple(cell), model, metric)).encode())])


def paired_contrast(model, base, rng=None, n_boot=N_BOOT):
    """Mean of model - base over paired seeds, its 95% percentile bootstrap interval over seeds, and the two-sided
    paired t-test p-value. Raises on fewer than two seeds or a non-finite difference."""
    d = np.asarray(model, float) - np.asarray(base, float)
    n = len(d)
    if n < 2 or not np.isfinite(d).all():
        raise ValueError(f"paired contrast needs at least two finite paired differences, got {n} ({np.isfinite(d).sum()} finite)")
    rng = rng if rng is not None else np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, n, (n_boot, n))
    boot = d[idx].mean(axis=1)
    sd = d.std(ddof=1)
    if sd == 0:
        p = 1.0 if d.mean() == 0 else 0.0                 # a constant difference: none, or certain
    else:
        p = float(stats.ttest_1samp(d, 0.0).pvalue)
    return {"n": n, "mean": float(d.mean()), "lo": float(np.percentile(boot, 2.5)), "hi": float(np.percentile(boot, 97.5)),
            "sd": float(sd), "p": p}


def holm(pvalues):
    """Holm step-down adjusted p-values (monotone, capped at 1), in the input order."""
    p = np.asarray(pvalues, float)
    if not np.isfinite(p).all():
        raise ValueError("Holm needs finite p-values")
    m = len(p)
    order = np.argsort(p, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(running, 1.0)
    return adj


def classify(w1, p90, w1_sesoi, alpha=0.05, p90_sesoi=P90_SESOI_MIN):
    """Joint reading of the co-primaries for one model in one F1 cell (G3 verdict C1). w1 and p90 are contrast dicts
    with the Holm-adjusted p-value in "p_holm"; differences are model - nearest, lower is better."""
    declusters = w1["p_holm"] < alpha and w1["mean"] < 0 and -w1["mean"] >= w1_sesoi
    if not declusters:
        return "does not decluster"
    if p90["hi"] < p90_sesoi:
        return "declusters at no delivery cost"
    if p90["p_holm"] < alpha and p90["mean"] >= p90_sesoi:
        return "declusters at a delivery cost"
    return "declusters, cost unresolved"


def required_n(sd_d, delta, m_family, power=0.80, alpha=0.05):
    """n_c = ceil(((z_(1 - alpha*/2) + z_power) sd_d / delta)^2) with alpha* = alpha / m_family (preregistration 6)."""
    if not np.isfinite(sd_d):
        raise ValueError("required_n needs a finite standard deviation")
    if sd_d == 0:
        return 0
    z = stats.norm.ppf(1 - alpha / m_family / 2) + stats.norm.ppf(power)
    return int(math.ceil((z * sd_d / delta) ** 2))


def sample_size(ns, floor=30, step=10):
    """The largest n_c, at least `floor`, rounded up to a multiple of `step`."""
    n = max([floor, *ns])
    return int(math.ceil(n / step) * step)


def time_to_undo(series, scattered, start_min=0, tolerance=0.10):
    """Extension Q2: minutes from the cluster's appearance (start_min) until the model's per-minute W1 first comes
    within 10% of its own W1 at the same clock time from the scattered start (series <= 1.1 x scattered); censored at
    21:00, so the result is at most the minutes left in the 4 hours."""
    x = np.asarray(series, float)[start_min:]
    s = np.asarray(scattered, float)[start_min:]
    hit = np.flatnonzero(x <= (1.0 + tolerance) * s)
    return float(hit[0]) if len(hit) else float(len(x))
