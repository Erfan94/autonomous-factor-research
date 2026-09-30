"""
Beta — CAPM beta: the slope of a stock's monthly return on the equal-weighted
market's monthly return over a trailing 60-month window; a high-beta stock
bears more market risk and is predicted to earn a higher return.

OSAP: Beta, Fama and MacBeth 1973, Journal of Political Economy (Table 3A,
t(gamma_1)). Predicted sign: + (high beta earns higher returns).
Spec: osap_source/cache/b4e911e6/Beta/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  r_k  = SEP.closeadj at business month-end k / closeadj at k-1, minus 1, for
         the 60 months ending at the signal month (ctx.monthly_closeadj(60),
         61 month-ends -> 60 returns; a missing close nulls both adjacent
         months, nothing is chained across a gap).
  m_k  = ctx.monthly_market(60, col="ew"): the equal-weighted market's
         monthly return compounded from DAILY-marketcap name-days, same
         month spans as r_k (harness-built, causal bad-print guards).
  Beta = cov(r, m) / var(m), OLS slope with intercept, over the months where
         both r and m are finite, required n >= 20 pairs. The window includes
         the signal month (the return through t is known at t). Variance of
         m guarded > 0.
  The market series is blank for 1998-12 (series stub) and for any month with
  fewer than 15 market days, so the first scorable signal is 2000-08.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Beta is a continuous OLS
  slope; the only degenerate value is exactly 0.0 for a name whose returns
  are all exactly zero over its paired window (a stale, never-trading price).
  What share of the universe does nothing? ~0% (the price/dollar-volume
  screens remove nearly all stale names); not measured here, preflight decides.
  Tie handling: null. A name with zero return variance over its paired
  window is set NaN (its slope is an artefact of a flat price, not a
  measured sensitivity) and blend_ranks renormalises. Otherwise ties are
  negligible.

DEVIATIONS FROM OSAP:
  - rf: the snapshot holds no risk-free rate, so the regression is r on m
    (raw returns), not (r - rf) on (m - rf). Over a monthly 60-month window
    rf drifts from ~5%/yr to ~0 across 1999-2021, so this differs more than
    for a daily window; it is a stated approximation, not measured here.
  - ewretd: the harness equal-weighted market (common stock on
    NYSE/NASDAQ/NYSEMKT per current TICKERS, no size/price screen, no
    delisting returns, returns across a trading gap and >+100% / <-80% daily
    prints excluded) replaces CRSP ewretd (all NYSE/AMEX/NASDAQ, with DLRET).
  - ret: SEP closeadj month-end ratio (total return, splits and dividends,
    no delisting return) replaces CRSP ret with dlret.
  - window: 60 calendar months with n >= 20 valid pairs, where OSAP uses the
    last 60 rows of the stock's own history (a listing gap reaches further
    back in OSAP).
  - var(r) == 0 names are set NaN (OSAP would emit 0.0).
  - history gate: history_months=20 (20 monthly returns), not 60, to match
    OSAP's 20-observation minimum; the estimate rests on 20-59 months until
    2003-12.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 60
_MIN_OBS = 20


def _compute(ctx):
    px = ctx.monthly_closeadj(_WINDOW).astype(float)          # IDs x (<=61) month-ends
    mkt = ctx.monthly_market(_WINDOW, col="ew").astype(float)  # 60 month-ends, RAW EW

    cols = list(px.columns)
    if len(cols) < 2:
        return pd.Series(np.nan, index=px.index)
    prev = px.iloc[:, :-1].to_numpy()
    cur = px.iloc[:, 1:].to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(prev > 0, cur / prev - 1.0, np.nan)      # NaN on either close missing
    m = mkt.reindex(pd.DatetimeIndex(cols[1:])).to_numpy()    # label-aligned month spans

    ok = np.isfinite(r) & np.isfinite(m)[None, :]
    n = ok.sum(axis=1).astype(float)
    r0 = np.where(ok, r, 0.0)
    m0 = np.where(ok, m[None, :], 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        rbar = r0.sum(axis=1) / n
        mbar = m0.sum(axis=1) / n
        dr = np.where(ok, r - rbar[:, None], 0.0)
        dm = np.where(ok, m[None, :] - mbar[:, None], 0.0)
        var_m = (dm * dm).sum(axis=1)
        var_r = (dr * dr).sum(axis=1)
        cov = (dr * dm).sum(axis=1)
        beta = cov / var_m
    valid = (n >= _MIN_OBS) & (var_m > 0) & (var_r > 0)
    beta = np.where(valid, beta, np.nan)
    return pd.Series(beta, index=px.index)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Beta",
    col="f_beta",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high beta predicts high returns
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="Beta",
    source="Fama and MacBeth 1973 (Journal of Political Economy)",
    lookback_months=60,             # 60-month window (61 month-end closes)
    history_months=20,              # OSAP minimum: 20 monthly returns
    notes="OLS slope of monthly raw return on harness EW market return, 60m window, >= 20 pairs; no rf",
    field_mappings=(
        ("crsp.ret", "SEP.closeadj (month-end ratio via monthly_closeadj)",
         "total return from adjacent business month-ends; no delisting return; no-trade zeros kept"),
        ("crsp.ewretd", "MonthContext.monthly_market(col='ew') from DAILY.marketcap name-days",
         "harness EW market of common stock on the universe's exchanges, no dlret, gap returns and bad prints excluded; blank 1998-12, so first scorable signal 2000-08"),
        ("ff.rf", "omitted (not in the snapshot)",
         "raw r on raw m instead of excess returns; larger effect on monthly windows than daily"),
        ("window", "60 calendar months, n >= 20 finite pairs",
         "OSAP uses the last 60 rows of the stock's history; zero-variance-return names set NaN"),
    ),
)
