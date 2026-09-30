"""
Stage 3 construction variants on a synthetic audit frame. What is asserted is
the contract: every variant is point-in-time, the reference equals the
search construction, tier-neutral uses within-tier cuts, ICIR weights are
estimated on prior months only, the buffer lowers turnover, vol targeting
lands near its target.
"""
import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from harness import portfolio as P
from harness.analytics import assign_composite_decile

CFG = {"rebalance": {"n_deciles": 10},
       "statistics": {"newey_west_lags": 3},
       "construction": {"variants": ["equal_rank_decile", "tier_neutral", "icir_weighted", "buffered", "vol_targeted"],
                        "icir_lookback_months": 12, "icir_min_months": 6, "buffer_pct": 20,
                        "vol_target_pct": 10, "vol_lookback_months": 12, "max_leverage": 3.0}}
METAS = [{"name": "A", "col": "f_a", "ascending": True, "winsorize": True, "weight": 1.0},
         {"name": "B", "col": "f_b", "ascending": True, "winsorize": True, "weight": 1.0}]


def _audit(n_dates=48, n_names=300, seed=0, persist=0.8):
    """Two legs; A carries return, B is noise; scores persist month to month so
    turnover is meaningful."""
    rng = np.random.default_rng(seed)
    a = rng.normal(size=n_names); b = rng.normal(size=n_names)
    tiers = np.array(["MEGA", "MID", "SMALL"])[np.arange(n_names) % 3]
    frames = []
    for d in pd.date_range("2005-01-31", periods=n_dates, freq="ME"):
        a = persist * a + np.sqrt(1 - persist ** 2) * rng.normal(size=n_names)
        b = persist * b + np.sqrt(1 - persist ** 2) * rng.normal(size=n_names)
        ret = 0.03 * a + rng.normal(0, 0.06, n_names)
        df = pd.DataFrame({"ID": [f"S{i}" for i in range(n_names)], "DATE": d, "f_a": a, "f_b": b,
                           "monthly_ret": ret, "liq_tier": tiers, "region": "US"})
        frames.append(assign_composite_decile(df, METAS, {"A": 0.5, "B": 0.5}))
    return pd.concat(frames, ignore_index=True)


def test_reference_variant_reproduces_the_search_construction():
    audit = _audit()
    s, tl, ts, _ = P.equal_rank_decile(audit, METAS, CFG)
    manual = audit.dropna(subset=["DECILE"]).groupby(["DATE", "DECILE"])["monthly_ret"].mean().unstack()
    expected = manual[10] - manual[1]
    assert np.allclose(s.values, expected.values) and len(s) == 48
    assert 0 < tl < 100 and 0 < ts < 100


def test_tier_neutral_uses_within_tier_deciles():
    audit = _audit()
    s, tl, ts, _ = P.tier_neutral(audit, METAS, CFG)
    ref, _, _, _ = P.equal_rank_decile(audit, METAS, CFG)
    assert len(s) == 48 and not np.allclose(s.values, ref.values)
    assert s.mean() > 0


def test_icir_weights_learn_the_informative_leg_using_only_prior_months():
    audit = _audit(n_dates=60)
    s, tl, ts, desc = P.icir_weighted(audit, METAS, CFG)
    w = dict(kv.split("=") for kv in desc.split(";"))
    assert float(w["A"]) > float(w["B"]), desc
    # the first months (before the window is long enough) use equal weights,
    # so the series is identical to the reference there
    ref, _, _, _ = P.equal_rank_decile(audit, METAS, CFG)
    first = CFG["construction"]["icir_min_months"]
    assert np.allclose(s.iloc[:first].values, ref.iloc[:first].values)


def test_buffer_lowers_turnover_without_killing_the_return():
    audit = _audit()
    ref, tl0, ts0, _ = P.equal_rank_decile(audit, METAS, CFG)
    s, tl, ts, _ = P.buffered(audit, METAS, CFG)
    assert tl < tl0 and ts < ts0
    assert s.mean() > 0.3 * ref.mean()


def test_vol_targeting_uses_trailing_vol_only_and_caps_leverage():
    audit = _audit()
    ref = P.equal_rank_decile(audit, METAS, CFG)
    s, _, _, desc = P.vol_targeted(audit, METAS, CFG, ref)
    lev = (s / ref[0]).dropna()
    assert lev.iloc[0] == pytest.approx(1.0)              # no history -> unlevered
    assert lev.max() <= CFG["construction"]["max_leverage"] + 1e-9
    assert "target 10%" in desc


def test_run_construction_reports_every_variant_gross_with_turnover():
    audit = _audit()
    buf = io.StringIO()
    with redirect_stdout(buf):
        out = P.run_construction(audit, METAS, CFG)
    assert [v for v, _ in out] == CFG["construction"]["variants"]
    for v, st in out:
        assert st["n_months"] > 12 and "ls_tstat_nw" in st and "worst_12m_pct" in st
        assert "turnover_long_pct" in st and not any(k.startswith("ls_net") for k in st)
    assert "Stage 3" in buf.getvalue()


def test_ls_summary_is_consistent_with_the_report_formulas():
    idx = pd.date_range("2000-01-31", periods=36, freq="ME")
    ls = pd.Series(0.01, index=idx)
    st = P.ls_summary(ls, 20.0, 20.0)
    assert st["ls_ann_return_pct"] == pytest.approx(12.0) and st["ls_hit_rate_pct"] == 100.0
    assert st["ls_maxdd_pct"] == pytest.approx(0.0)
