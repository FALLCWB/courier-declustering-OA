"""Statistics of preregistration.md with known answers."""
import numpy as np
import pytest

from sim.stats import classify, holm, paired_contrast, required_n, sample_size


def test_holm_matches_a_hand_computed_example():
    # p = (0.01, 0.04, 0.03, 0.005), m = 4: sorted 0.005 x4 = 0.02, 0.01 x3 = 0.03, 0.03 x2 = 0.06, 0.04 x1 = 0.04 -> 0.06
    assert np.allclose(holm([0.01, 0.04, 0.03, 0.005]), [0.03, 0.06, 0.06, 0.02])
    assert np.allclose(holm([0.5, 0.9]), [1.0, 1.0])


def test_paired_contrast_mean_interval_and_t_test():
    rng = np.random.default_rng(0)
    base = rng.normal(10, 2, 200)
    model = base - 1.0 + rng.normal(0, 0.5, 200)       # paired: the base noise cancels
    c = paired_contrast(model, base)
    assert c["mean"] == pytest.approx(-1.0, abs=0.1) and c["lo"] < c["mean"] < c["hi"] and c["hi"] < 0
    assert c["p"] < 1e-50 and c["sd"] == pytest.approx(0.5, abs=0.06)
    same = paired_contrast(base, base)
    assert same["mean"] == 0.0 and same["p"] == 1.0


def contrast(mean, lo, hi, p_holm):
    return {"mean": mean, "lo": lo, "hi": hi, "p_holm": p_holm}


def test_joint_reading_puts_each_case_in_its_class():
    w1_good = contrast(-1.0, -1.2, -0.8, 0.001)          # W1 lower by 1 min, smallest effect 0.5 min
    assert classify(w1_good, contrast(0.2, -0.3, 0.7, 0.4), 0.5) == "declusters at no delivery cost"
    assert classify(w1_good, contrast(1.5, 1.1, 1.9, 0.001), 0.5) == "declusters at a delivery cost"
    assert classify(w1_good, contrast(0.6, 0.1, 1.1, 0.01), 0.5) == "declusters, cost unresolved"
    assert classify(contrast(-0.3, -0.4, -0.2, 0.001), contrast(0.0, -0.1, 0.1, 1.0), 0.5) == "does not decluster"
    assert classify(contrast(-1.0, -2.0, 0.1, 0.2), contrast(0.0, -0.1, 0.1, 1.0), 0.5) == "does not decluster"


def test_sample_size_rule():
    # z(1 - 0.05/90/2) = 3.4523, z(0.8) = 0.8416: ((4.2939 x 2) / 1)^2 = 73.75 -> 74
    assert required_n(2.0, 1.0, 90) == 74
    assert sample_size([74, 12]) == 80 and sample_size([3]) == 30


def test_statistics_fail_loudly_instead_of_inventing_numbers():
    with pytest.raises(ValueError):
        holm([0.01, float("nan"), 0.02])
    with pytest.raises(ValueError):
        paired_contrast([1.0], [0.5])                     # one seed: no variance, no test
    with pytest.raises(ValueError):
        required_n(float("nan"), 1.0, 90)
    c = paired_contrast(np.full(10, 2.0), np.full(10, 1.0))
    assert c["mean"] == 1.0 and c["p"] == 0.0             # a constant non-zero difference is certain


def test_bootstrap_interval_does_not_depend_on_what_ran_before():
    from sim.stats import contrast_rng
    a = np.arange(30.0)
    b = a + np.linspace(-1, 1, 30)
    one = paired_contrast(a, b, contrast_rng(("F1", "big_cluster", "tight"), "foodmatch", "W1"))
    paired_contrast(b, a, contrast_rng(("F1", "scattered", "loose"), "forecast", "p90"))
    two = paired_contrast(a, b, contrast_rng(("F1", "big_cluster", "tight"), "foodmatch", "W1"))
    assert (one["lo"], one["hi"]) == (two["lo"], two["hi"])


def test_joint_reading_boundaries():
    w1_at_sesoi = contrast(-0.5, -0.6, -0.4, 0.01)        # exactly the smallest effect counts
    assert classify(w1_at_sesoi, contrast(0.0, -0.5, 0.999, 0.9), 0.5) == "declusters at no delivery cost"
    assert classify(w1_at_sesoi, contrast(0.5, 0.0, 1.0, 0.9), 0.5) == "declusters, cost unresolved"   # hi = 1.0
    assert classify(w1_at_sesoi, contrast(1.0, 1.0, 1.5, 0.01), 0.5) == "declusters at a delivery cost"


def test_resume_reads_finished_jobs_and_drops_a_cut_last_line(tmp_path):
    import json
    from sim.run_cells import read_done
    f = tmp_path / "episodes.jsonl"
    rows = [{"family": "F1", "scenario": "burst", "level": "tight", "behavior": "fitted", "layout": "s0", "scale": 1.0,
             "time_mult": 1.0, "seed": s, "model": "nearest"} for s in (1001, 1002)]
    f.write_text("\n".join(json.dumps(r) for r in rows) + '\n{"family": "F1", "scen')
    done = read_done(f)
    assert len(done) == 2 and f.read_text().endswith("\n") and f.read_text().count("\n") == 2


def test_time_to_undo_is_the_first_minute_within_10_percent_of_the_scattered_series():
    from sim.stats import time_to_undo
    scattered = np.full(240, 5.0)
    clustered = np.r_[np.linspace(15.0, 5.0, 101), np.full(139, 5.0)]   # reaches 5.5 at minute 95
    assert time_to_undo(clustered, scattered) == 95.0
    assert time_to_undo(np.full(240, 9.0), scattered) == 240.0           # never: censored at 21:00
    meet = np.r_[np.full(120, 5.0), np.full(60, 8.0), np.full(60, 5.2)]  # meet-up at 19:00 (minute 120)
    assert time_to_undo(meet, scattered, start_min=120) == 60.0
