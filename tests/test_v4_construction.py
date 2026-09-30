"""
This project's construction changes (docs/DECISIONS.md D3-D5): ranks formed
within sector with a thin-group fallback, the ex-ante market hedge on the
long-short, the date-free regime diagnostics, the holdout cuts, and the beta
diagnostic on every block. None of them is a bar; each must be exactly what
the config says it is.
"""
import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from harness.analytics import (assign_composite_decile, compute_ic, fullwindow_beta, hedge_long_short,
                               hedge_params, market_state, print_summary, rank_group_col, rank_one_factor,
                               regime_diagnostics, regime_params, trailing_beta, universe_market_return)
from harness.provenance import load_config

CFG = load_config()


def test_config_declares_the_three_changes_and_the_windows():
    cfg = load_config()
    assert rank_group_col(cfg) == "sector"
    assert hedge_params(cfg) == {"beta_window_months": 36, "beta_min_months": 12}
    assert regime_params(cfg) == {"ex_regime_top_years": 3, "market_state_lookback_months": 12}
    assert cfg["dates"] == {"eval_start": "1999-01-01", "eval_end": "2021-12-31",
                            "out_of_sample_start": "2022-01-01", "out_of_sample_end": "2026-09-30"}


def test_a_missing_config_section_means_off():
    assert rank_group_col({}) is None and hedge_params({}) is None
    assert hedge_params({"market_hedge": {"enabled": False}}) is None
    assert regime_params({}) == {"ex_regime_top_years": 3, "market_state_lookback_months": 12}


# ---- within-sector ranks -----------------------------------------------------

def test_rank_within_group_is_relative_to_sector_peers():
    df = pd.DataFrame({"x": list(range(1, 21)) + list(range(101, 121)), "sector": ["A"] * 20 + ["B"] * 20})
    r = rank_one_factor(df, "x", winsorize=False, group_col="sector")
    assert r.iloc[19] == pytest.approx(1.0) and r.iloc[0] == pytest.approx(0.05)   # top / bottom of A
    assert rank_one_factor(df, "x", winsorize=False).iloc[19] == pytest.approx(0.5)  # the same name, cross-section


def test_a_thin_group_falls_back_to_the_cross_section_rank():
    df = pd.DataFrame({"x": list(range(1, 31)) + [1000.0, 2000.0], "sector": ["A"] * 30 + ["B"] * 2})
    r = rank_one_factor(df, "x", winsorize=False, group_col="sector", min_group_obs=10)
    g = rank_one_factor(df, "x", winsorize=False)
    assert r.iloc[30] == pytest.approx(g.iloc[30]) and r.iloc[31] == pytest.approx(g.iloc[31]) == pytest.approx(1.0)
    assert r.iloc[29] == pytest.approx(1.0)


def test_a_missing_sector_is_its_own_group_and_nan_values_stay_nan():
    df = pd.DataFrame({"x": [1.0, 2.0, np.nan] + list(range(10, 30)), "sector": [None, None, "A"] + ["A"] * 20})
    r = rank_one_factor(df, "x", winsorize=False, group_col="sector", min_group_obs=2)
    assert np.isnan(r.iloc[2]) and r.iloc[1] == pytest.approx(1.0) and r.iloc[0] == pytest.approx(0.5)


def test_assign_composite_decile_ranks_within_the_group_column():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"f_a": rng.normal(size=300), "sector": [["A", "B", "C"][i % 3] for i in range(300)]})
    df.loc[df["sector"] == "A", "f_a"] += 10.0                 # one sector dominates the cross-section
    meta = [{"name": "A", "col": "f_a", "ascending": True, "winsorize": False, "weight": 1.0}]
    plain = assign_composite_decile(df, meta)
    grouped = assign_composite_decile(df, meta, group_col="sector")
    assert (plain.loc[plain["DECILE"] == 10, "sector"] == "A").all()
    assert set(grouped.loc[grouped["DECILE"] == 10, "sector"]) == {"A", "B", "C"}


# ---- the hedge ---------------------------------------------------------------

def test_universe_market_return_is_cap_weighted():
    df = pd.DataFrame({"DATE": ["2020-01-31"] * 3, "monthly_ret": [0.10, -0.10, 0.0], "mkt_cap_usd": [3.0, 1.0, 0.0]})
    assert universe_market_return(df).iloc[0] == pytest.approx((0.3 - 0.1) / 4.0)


def _series(n=120, beta=1.5, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2000-01-31", periods=n, freq="ME")
    mkt = pd.Series(rng.normal(0.01, 0.04, n), index=idx)
    return beta * mkt + pd.Series(rng.normal(0.0, 0.01, n), index=idx), mkt


def test_trailing_beta_uses_only_the_months_before_t():
    ls, mkt = _series()
    b = trailing_beta(ls, mkt, window=36, min_months=12)
    assert (b.iloc[:12] == 0.0).all(), "no hedge before the minimum history"
    t = 60
    win = slice(t - 36, t)                                        # months t-36 .. t-1
    manual = np.cov(ls.iloc[win], mkt.iloc[win])[0, 1] / np.var(mkt.iloc[win], ddof=1)
    assert b.iloc[t] == pytest.approx(manual)
    ls2 = ls.copy(); ls2.iloc[t] += 1.0                           # month t's own return must not move beta_t
    assert trailing_beta(ls2, mkt, 36, 12).iloc[t] == pytest.approx(b.iloc[t])
    assert trailing_beta(ls2, mkt, 36, 12).iloc[t + 1] != pytest.approx(b.iloc[t + 1])


def test_the_hedged_series_has_near_zero_ex_post_beta_when_the_true_beta_is_stable():
    ls, mkt = _series(n=240, beta=1.5)
    h, b = hedge_long_short(ls, mkt, 36, 12)
    assert abs(fullwindow_beta(ls, mkt) - 1.5) < 0.1
    assert abs(fullwindow_beta(h.iloc[36:], mkt)) < 0.15
    assert b.index.equals(ls.index)


def test_a_flat_market_leaves_the_series_unhedged():
    ls, mkt = _series(beta=0.0)
    h, b = hedge_long_short(ls, mkt * 0.0, 36, 12)
    assert np.allclose(h.values, ls.values) and (b == 0).all()


# ---- date-free diagnostics -----------------------------------------------------

def test_market_state_is_ex_ante():
    idx = pd.date_range("2000-01-31", periods=30, freq="ME")
    st = market_state(pd.Series([-0.05] * 15 + [0.05] * 15, index=idx), 12)
    assert st.iloc[:12].isna().all() and st.iloc[12] == "bear"
    assert st.iloc[15] == "bear"                                  # month 15's own +5% is not in its window
    assert st.iloc[-1] == "bull"


def test_regime_diagnostics_are_date_free_and_drop_the_best_years():
    rng = np.random.default_rng(3)
    idx = pd.date_range("1999-01-31", periods=240, freq="ME")
    ls = pd.Series(rng.normal(0.005, 0.03, 240), index=idx)
    ls[ls.index.year.isin([2003, 2010, 2015])] += 0.05             # three carried years
    d = regime_diagnostics(ls, None, top_years=3)
    assert d["ls_top_years"] == "2003,2010,2015"
    rest = ls[~ls.index.year.isin([2003, 2010, 2015])]
    assert d["ls_sharpe_ex_top_years"] == pytest.approx(rest.mean() * 12 / (rest.std() * np.sqrt(12)))
    assert d["ls_top_years_share_pct"] > 50
    shifted = ls.copy(); shifted.index = idx + pd.DateOffset(years=7)
    d2 = regime_diagnostics(shifted, None, top_years=3)
    assert d2["ls_sharpe_ex_top_years"] == pytest.approx(d["ls_sharpe_ex_top_years"])
    assert d2["ls_top_years"] == "2010,2017,2022"
    assert d["ls_sharpe_bear"] != d["ls_sharpe_bear"]              # no market -> NaN, never a guess


# ---- the report --------------------------------------------------------------

def _audit(n_dates=60, n_names=90, seed=0):
    rng = np.random.default_rng(seed)
    rows, sectors = [], ["Tech", "Health", "Energy"]
    for d in pd.date_range("2000-01-31", periods=n_dates, freq="ME"):
        mkt, score = rng.normal(0.01, 0.05), rng.random(n_names)
        ret = 0.3 * (score - 0.5) * 0.2 + mkt + rng.normal(0, 0.05, n_names)
        for j in range(n_names):
            rows.append({"ID": f"S{j}", "DATE": d, "COMPOSITE_SCORE": score[j], "monthly_ret": ret[j],
                         "region": "US", "liq_tier": ["MEGA", "MID", "SMALL"][j % 3], "sector": sectors[j % 3],
                         "mkt_cap_usd": 1e9 * (1 + j)})
    df = pd.DataFrame(rows)
    df["DECILE"] = df.groupby("DATE")["COMPOSITE_SCORE"].transform(
        lambda x: pd.qcut(x, 10, labels=False, duplicates="drop") + 1)
    return df


def _tables(audit):
    g = audit.dropna(subset=["DECILE", "monthly_ret"]).groupby(["DATE", "DECILE"])["monthly_ret"]
    ret = g.mean().unstack("DECILE").sort_index(); ret.columns = [f"D{int(c)}" for c in ret.columns]
    cnt = g.count().unstack("DECILE").sort_index(); cnt.columns = [f"N_D{int(c)}" for c in cnt.columns]
    ret["LS"] = ret["D10"] - ret["D1"]
    return ret, cnt


def test_report_prints_the_hedge_regime_and_cut_sections_and_records_them():
    audit = _audit(); ret, cnt = _tables(audit)
    buf = io.StringIO()
    with redirect_stdout(buf):
        st = print_summary("t", ret, cnt, compute_ic(audit), audit,
                           hedge={"beta_window_months": 24, "beta_min_months": 12},
                           regime={"ex_regime_top_years": 2, "market_state_lookback_months": 6},
                           oos_start="2004-01-01")
    out = buf.getvalue()
    for marker in ("--- Market hedge", "Hedge           : ON", "Raw LS", "--- Regime diagnostics", "Sharpe ex top-2",
                   "Sharpe by market state", "--- Cuts at 2004-01-01", "in-window", "holdout"):
        assert marker in out, marker
    for k in ("ls_raw_sharpe", "ls_beta_mean", "ls_beta_fullwindow", "ls_hedged_months", "ls_sharpe_ex_top_years",
              "ls_top_years", "ls_sharpe_bear", "ls_sharpe_bull", "cut_inwindow_ls_sharpe", "cut_holdout_ls_sharpe",
              "cut_holdout_n_months", "cut_holdout_ic_tstat_nw", "cut_holdout_ls_beta_mean"):
        assert k in st, k
    assert st["hedge_on"] == "True" and st["ls_hedged_months"] == 60 - 12
    assert st["cut_inwindow_n_months"] + st["cut_holdout_n_months"] == 60 and st["cut_holdout_n_months"] == 12
    assert st["ls_sharpe"] != pytest.approx(st["ls_raw_sharpe"]), "the headline is the hedged series"
    assert "ls_raw_series" in st and "ls_beta_series" in st


def test_report_without_a_hedge_is_the_raw_series():
    audit = _audit(); ret, cnt = _tables(audit)
    with redirect_stdout(io.StringIO()):
        st = print_summary("t", ret, cnt, compute_ic(audit), audit)
    assert st["hedge_on"] == "False" and st["ls_sharpe"] == pytest.approx(st["ls_raw_sharpe"])
    assert st["ls_beta_mean"] == 0.0 and "cut_holdout_n_months" not in st


# =============================================================================
# D11 — the Stage 1 spread bar reads the RAW D10−D1; the Stage 2 guard reads
# the hedged blend. The hedge reaches the bars in exactly one place.
# =============================================================================

def _s1_values(raw, hedged):
    return {"ic_mean": 0.02, "ic_tstat_nw": 3.0, "ic_half_min": 0.005, "coverage_pct": 70.0,
            "avg_names_per_decile": 120.0, "ls_ann_return_pct": hedged, "ls_raw_ann_return_pct": raw}


def test_the_config_declares_the_raw_spread_bar_and_the_bar_row_is_named_after_it():
    from harness.analytics import stage1_checks
    thr = CFG["acceptance_thresholds"]["stage1_standalone"]
    assert thr["ls_spread_series"] == "raw"
    names = [c[0] for c in stage1_checks(_s1_values(1.0, 1.0), thr)]
    assert "ls_raw_ann_return_pct" in names and "ls_ann_return_pct" not in names


def test_stage1_judges_the_raw_spread_not_the_hedged_one():
    from harness.analytics import check_stage1
    thr = CFG["acceptance_thresholds"]["stage1_standalone"]
    assert not check_stage1(_s1_values(raw=-0.5, hedged=+3.0), thr)[0], "negative raw spread fails"
    assert check_stage1(_s1_values(raw=+0.5, hedged=-3.0), thr)[0], "the hedged headline is not a bar"


def test_an_absent_switch_defaults_to_raw_and_hedged_must_be_asked_for():
    from harness.analytics import stage1_checks
    thr = {k: v for k, v in CFG["acceptance_thresholds"]["stage1_standalone"].items() if k != "ls_spread_series"}
    assert [c[0] for c in stage1_checks(_s1_values(1.0, 1.0), thr)][3] == "ls_raw_ann_return_pct"
    thr["ls_spread_series"] = "hedged"
    assert [c[0] for c in stage1_checks(_s1_values(1.0, 1.0), thr)][3] == "ls_ann_return_pct"


def test_the_switch_has_no_effect_on_stage2():
    from harness.analytics import stage2_checks
    s2 = dict(CFG["acceptance_thresholds"]["stage2_marginal"])
    vals = {"resid_ic_tstat_nw": 2.5, "paired_delta_ls_tstat": -0.5}
    base = stage2_checks(vals, s2)
    s2["ls_spread_series"] = "hedged"
    assert stage2_checks(vals, s2) == base
    assert [c[0] for c in base] == ["resid_ic_tstat_nw", "paired_delta_ls_tstat"]


def test_a_stage1_block_must_carry_the_raw_spread():
    from harness.analytics import REQUIRED_STAGE1_KEYS
    assert "ls_raw_ann_return_pct" in REQUIRED_STAGE1_KEYS and "ls_ann_return_pct" in REQUIRED_STAGE1_KEYS
