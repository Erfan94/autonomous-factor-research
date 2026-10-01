"""
`--return-start skip1`: the diagnostic skip-a-day forward return.

The base of month t+1's return moves from the signal-date close to the close
of the name's first trade in month t+1; the end, the staleness test and the
delisting convention are unchanged, and the default path is untouched.
"""
import argparse

import numpy as np
import pandas as pd
import pytest

from harness import run_test as RT
from harness.analytics import parse_result_blocks
from harness.data_layer import (build_first_trade_monthly, build_universe, compute_month_frame,
                                forward_returns)
from tests.fixtures import synthetic_snapshot as S
from tests.test_data_layer import _alive_in
from tests.test_run_end_to_end import C_V0, _ns, _patch_candidates, _run  # noqa: F401  (autouse patch)

SIG, END = pd.Timestamp("1999-06-30"), pd.Timestamp("1999-07-30")


def _closes(snap, tkr):
    sep = snap.table("SEP")
    return sep[sep["ticker"] == tkr].set_index("date")["closeadj"].sort_index()


# ---- the skip1 return itself ------------------------------------------------------

def test_skip1_return_is_first_day_close_to_month_end_close(snap, pidx, cfg, synthetic):
    u = build_universe(pidx, SIG, cfg)
    fr = forward_returns(pidx, u, SIG, END, cfg, return_start="skip1")
    tkr = _alive_in(u, synthetic)
    p = str(synthetic["perma"][tkr])
    s = _closes(snap, tkr)
    july = s[(s.index > SIG) & (s.index <= END)]
    assert july.index[0] == pd.Timestamp("1999-07-01")          # the first trading day of July
    expect = s.loc["1999-07-30"] / july.iloc[0] - 1
    assert fr.loc[p, "monthly_ret"] == pytest.approx(expect)
    assert fr.loc[p, "ret_kind"] == "full"
    assert fr.loc[p, "ret_base"] == "first_day"
    # and it is not the default's signal-close return
    default = forward_returns(pidx, u, SIG, END, cfg)
    assert default.loc[p, "monthly_ret"] == pytest.approx(s.loc["1999-07-30"] / s.loc["1999-06-30"] - 1)
    assert fr.loc[p, "monthly_ret"] != pytest.approx(default.loc[p, "monthly_ret"])


def test_first_trade_frame_is_the_first_sep_row_of_each_month(snap):
    ft = build_first_trade_monthly(snap, log=lambda *a, **k: None)
    tkr = "T000"
    pid = str(snap.ticker_map("SEP")[tkr])
    row = ft[(ft["ID"] == pid) & (pd.to_datetime(ft["me"]) == pd.Timestamp("1999-07-30"))].iloc[0]
    s = _closes(snap, tkr)
    assert pd.Timestamp(row["first_date"]) == pd.Timestamp("1999-07-01")
    assert row["first_closeadj"] == pytest.approx(s.loc["1999-07-01"])


def test_a_name_delisting_on_the_first_trading_day_earns_only_the_delisting_return(snap, pidx, cfg, synthetic):
    """An EXTRA_DELIST name whose last trade IS the first trading day of month
    t+1: under skip1 its first trade is its last, the end is stale, the
    partial is 0.0 and the configured performance return is all it earns."""
    perf = float(cfg["returns"]["delisting"]["performance_return"])
    hits = 0
    for tkr, last in S.EXTRA_DELIST.items():
        if last.dayofweek >= 5:
            continue
        sig = (last - pd.offsets.BMonthEnd(1)).normalize()
        end = (last + pd.offsets.BMonthEnd(0)).normalize()
        u = build_universe(pidx, sig, cfg)
        p = str(synthetic["perma"][tkr])
        if p not in u.index:
            continue
        fr = forward_returns(pidx, u, sig, end, cfg, return_start="skip1")
        dflt = forward_returns(pidx, u, sig, end, cfg)
        assert fr.loc[p, "ret_kind"] == dflt.loc[p, "ret_kind"] == "partial_delisted_performance"
        assert fr.loc[p, "ret_base"] == "first_day"
        assert fr.loc[p, "monthly_ret"] == pytest.approx(perf)
        s = _closes(snap, tkr)
        assert dflt.loc[p, "monthly_ret"] == pytest.approx((s.loc[last] / s.loc[sig]) * (1 + perf) - 1)
        hits += 1
    assert hits >= 1, "no first-trading-day delisting survived the universe screens"


def test_a_name_with_no_trade_in_the_month_falls_back_to_the_default(snap, pidx, cfg, synthetic):
    """T081 stops on 1999-07-30 (its delist date is a Sunday): no trade in
    August, so the skip1 base is the signal close and the return and kind are
    the default's exactly."""
    tkr = "T081"
    sig, end = pd.Timestamp("1999-07-30"), pd.Timestamp("1999-08-31")
    u = build_universe(pidx, sig, cfg)
    p = str(synthetic["perma"][tkr])
    if p not in u.index:
        pytest.skip("T081 did not pass the July screens")
    fr = forward_returns(pidx, u, sig, end, cfg, return_start="skip1")
    dflt = forward_returns(pidx, u, sig, end, cfg)
    assert fr.loc[p, "ret_base"] == "signal_close"
    assert fr.loc[p, "ret_kind"] == dflt.loc[p, "ret_kind"]
    assert fr.loc[p, "monthly_ret"] == dflt.loc[p, "monthly_ret"]


def test_ret_kind_never_depends_on_the_return_start(pidx, cfg):
    for sig, end in [(SIG, END), (pd.Timestamp("1999-08-31"), pd.Timestamp("1999-09-30")),
                     (pd.Timestamp("2000-02-29"), pd.Timestamp("2000-03-31"))]:
        u = build_universe(pidx, sig, cfg)
        a = forward_returns(pidx, u, sig, end, cfg)
        b = forward_returns(pidx, u, sig, end, cfg, return_start="skip1")
        pd.testing.assert_series_equal(a["ret_kind"], b["ret_kind"])


def test_an_unknown_return_start_is_refused(pidx, cfg):
    u = build_universe(pidx, SIG, cfg)
    with pytest.raises(ValueError):
        forward_returns(pidx, u, SIG, END, cfg, return_start="skip2")


# ---- the default path is untouched -------------------------------------------------

def test_default_forward_returns_are_the_signal_close_ratio_with_no_new_column(snap, pidx, cfg, synthetic):
    u = build_universe(pidx, SIG, cfg)
    a = forward_returns(pidx, u, SIG, END, cfg)
    b = forward_returns(pidx, u, SIG, END, cfg, return_start="close")
    assert list(a.columns) == ["monthly_ret", "ret_kind"]
    pd.testing.assert_frame_equal(a, b)
    full = a["ret_kind"] == "full"
    p_end = pidx.month_rows(END).set_index("ID")["closeadj"].reindex(u.index)
    expect = (p_end / u["closeadj"] - 1)[full]
    np.testing.assert_allclose(a.loc[full, "monthly_ret"].values, expect.values)


def test_default_month_frame_is_unchanged_and_skip1_differs_only_in_the_return(snap, pidx, cfg):
    reb, sig, rs, re_ = (pd.Timestamp("1999-07-01"), SIG, pd.Timestamp("1999-07-01"), END)
    a = compute_month_frame(snap, pidx, {}, [], reb, sig, rs, re_, cfg)
    b = compute_month_frame(snap, pidx, {}, [], reb, sig, rs, re_, cfg, return_start="close")
    pd.testing.assert_frame_equal(a, b)
    assert "monthly_ret_close" not in a.columns and "RET_BASE" not in a.columns
    k = compute_month_frame(snap, pidx, {}, [], reb, sig, rs, re_, cfg, return_start="skip1")
    assert sorted(k.columns) == sorted(list(a.columns) + ["monthly_ret_close", "RET_BASE"])
    np.testing.assert_array_equal(k["monthly_ret_close"].values, a["monthly_ret"].values)
    same = [c for c in a.columns if c != "monthly_ret"]
    pd.testing.assert_frame_equal(k[same], a[same])
    assert (k["monthly_ret"] != a["monthly_ret"]).any()


# ---- the runner -----------------------------------------------------------------

@pytest.mark.parametrize("kw", [dict(factors="ValueLike,Noise", stage=1),
                                dict(factor="ValueLike", stage=2),
                                dict(baseline=True, stage=3),
                                dict(baseline=True, stage=2, include_holdout=True)])
def test_skip1_is_refused_outside_the_in_window_baseline(kw, synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit):
        _run(_ns(return_start="skip1", **kw), synthetic, cfg, runtime, snap)


def test_the_flag_absent_and_close_give_the_same_block(synthetic, cfg, runtime, snap):
    absent, _ = _run(_ns(baseline=True, stage=2), synthetic, cfg, runtime, snap)
    close, _ = _run(_ns(baseline=True, stage=2, return_start="close"), synthetic, cfg, runtime, snap)
    assert absent[0] == close[0]
    assert "return_start" not in absent[0]


def test_skip1_baseline_is_stamped_and_pairs_with_the_default(synthetic, cfg, runtime, snap):
    import json
    dflt, _ = _run(_ns(baseline=True, stage=2), synthetic, cfg, runtime, snap)
    sk, text = _run(_ns(baseline=True, stage=2, return_start="skip1"), synthetic, cfg, runtime, snap)
    d, b = parse_result_blocks(dflt[0])[0], parse_result_blocks(sk[0])[0]
    assert b["return_start"] == "skip1" and "RETURN START  skip1" in text
    # the close-base composite IC inside the skip1 run IS the default run's IC
    assert b["paired_close_ic_mean"] == pytest.approx(d["ic_mean"], abs=1e-6)
    assert b["ic_mean"] != pytest.approx(d["ic_mean"], abs=1e-9)
    for k in ("n_months", "coverage_pct", "delisting_adjusted_pct", "avg_names_per_decile"):
        assert b[k] == d[k], k
    shares = sum(b[f"skip1_base_{k}_pct"] for k in ("first_day", "first_trade_late", "signal_close"))
    assert shares == pytest.approx(100.0)
    for leg in C_V0.active_factors():
        assert f"legic_{leg.col}_skip1" in b and f"legic_{leg.col}_close" in b
    f = sorted((synthetic["root"] / "results").glob("*_BASELINE_SKIP1_stage2_*.txt"))[-1]
    meta = json.loads(f.with_suffix(".meta.json").read_text())
    assert meta["return_start"] == "skip1"
