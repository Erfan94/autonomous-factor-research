import numpy as np
import pandas as pd

from harness.preflight import masspoint_stats


def test_masspoint_counts_distinct_values_at_any_scale():
    x = pd.Series(np.linspace(1.0, 2.0, 500) * 1e-10)
    st = masspoint_stats(x)
    assert st["n_distinct"] == 500, "a ~1e-10 factor must not collapse into false ties (HD-PF-ROUND)"
    assert st["mode_pct"] == 100.0 / 500


def test_masspoint_still_detects_a_true_tie():
    x = pd.Series(np.r_[np.zeros(30), np.linspace(1.0, 2.0, 70)] * 1e-10)
    st = masspoint_stats(x)
    assert st["mode"] == 0.0
    assert st["mode_pct"] == 30.0
    assert st["n_distinct"] == 71
