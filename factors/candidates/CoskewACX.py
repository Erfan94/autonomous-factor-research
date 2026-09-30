"""
CoskewACX — coskewness of a stock's daily return with the market over the past
twelve calendar months, E[r~ m~^2] / (SD[r~] * SD[m~]^2); a stock that adds
negative skewness to the market (low coskewness) is a risk the market pays for,
so HIGH coskewness is predicted to earn LOWER returns.

OSAP: CoskewACX, Ang, Chen and Xing 2006, Review of Financial Studies
(Table 8B). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/CoskewACX/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window: the market trading days d with BME(t-12) < d <= t, where t is the
  signal date (12 calendar months, the signal month included) and BME is the
  business month-end.
  r_d = ln(closeadj_d / closeadj_{d-1}) from ctx.daily("SEP", ["closeadj"]),
        d-1 being the market day before d: prices are reindexed onto the
        market_daily calendar before the lag, so a stray SEP weekend/holiday
        row of any one name never breaks the lag for the others (a name with
        no row on either day has no return for d; nothing is chained across
        a gap).
  m_d = ln(1 + mkt_d), mkt_d = ctx.market_daily(...) col "vw" (raw cap-weighted).
  Over the days where both are finite (n of them):
      r~ = r - mean(r);  m~ = m - mean(m)        (means over the SAME days)
      CoskewACX = mean(r~ * m~^2) / ( sqrt(mean(r~^2)) * mean(m~^2) )
  population (1/n) moments, no df correction.
  Observation rule = OSAP's predictor.py: n >= N - 5, where N is the number of
  market days in the window. No absolute minimum.
  Non-finite result (mean(r~^2) == 0 or mean(m~^2) == 0) -> NaN, never inf.
  Price-only: no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A never-trading price has
  mean(r~^2) = 0, so 0/0: undefined, not a value. Everything else is a
  continuous ratio of sample moments.
  What share of the universe does nothing? Expected < 1% (price >= $1 and the
  dollar-volume screen remove stale names, and n >= N - 5 also demands
  near-daily data); preflight decides.
  Tie handling: null. Zero-variance windows are NaN and blend_ranks
  renormalises. No noise or secondary key.

DEVIATIONS FROM OSAP:
  - rf omitted (the snapshot holds no risk-free rate). OSAP de-means both
    series over the window, so a constant rf cancels exactly; only rf's
    day-to-day variation (~1e-4 against 1-2% daily stock vol) is lost.
  - mkt: ctx.market_daily raw value-weighted all-stock series (common stock on
    NYSE/NASDAQ/NYSEMKT per current TICKERS, prior-day cap weights, causal
    bad-print guards, no delisting returns, gap returns and >+100% / <-80%
    daily prints excluded) replaces Ken French's mktrf + rf.
  - ret: SEP closeadj ratio (total return, no delisting return; closeadj is on
    a 3-decimal grid) replaces CRSP daily ret.
  - early window: the market series starts 1998-12-02, so the N - 5 rule
    (as OSAP writes it, no absolute floor) is applied against a SHORT
    market window for signals 1999-01 .. 1999-11 (N from ~41 to ~230 days
    instead of ~252). Coordinator decision: those truncated windows are NOT
    OSAP's construct (its window is always a full 12 months), so a signal whose
    window opens before the market series starts is NaN; the first scored
    signal is 1999-12 (11 of 276 decision months null): the 1999-11 window
    opens after BME 1998-11-30 and misses 1998-12-01, so it is nulled too
    (the check allows at most one business day of slack after BME(t-12)). A >= 230-day floor
    proposed in the spec was NOT adopted because OSAP has no such rule.
  - NYSE-only breakpoints / quintiles of the SignalDoc portfolio step are
    superseded by the harness universe and decile sort.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import to_bme

_DAYS_BACK = 400            # 12 months + the prior close before the first window day
_SLACK = 5                  # OSAP: max_nobs - nobs <= 5


def _compute(ctx):
    lo = to_bme([(ctx.signal_asof - pd.DateOffset(months=12)).normalize()]).iloc[0]

    mkt = ctx.market_daily(_DAYS_BACK, col="vw")
    if mkt is None or len(mkt) == 0:
        return pd.Series(np.nan, index=ctx.ids)
    mkt = mkt.astype(float)
    mkt.index = pd.DatetimeIndex(mkt.index)
    # OSAP's window is always a full 12 months of market days. Our market series
    # starts 1998-12-02, so a window that opens before the series does is a
    # truncated window, not OSAP's construct: null it (signals 1999-01..1999-11).
    if mkt.index.min() > lo + pd.offsets.BDay(1):
        return pd.Series(np.nan, index=ctx.ids)
    cal = mkt.index                                  # full market calendar, pre-cut
    mkt = mkt[(mkt.index > lo) & (mkt.index <= ctx.signal_asof)]
    mkt = mkt[np.isfinite(mkt.to_numpy()) & (mkt.to_numpy() > -1.0)]
    n_market = len(mkt)
    if n_market < 3:
        return pd.Series(np.nan, index=ctx.ids)

    d = ctx.daily("SEP", ["closeadj"], _DAYS_BACK)
    if d.empty:
        return pd.Series(np.nan, index=ctx.ids)
    px = d.pivot_table(index="date", columns="ID", values="closeadj", aggfunc="last").sort_index()
    px = px.where(px > 0)
    px.index = pd.DatetimeIndex(px.index)
    px = px.reindex(cal)                            # market calendar: stray SEP rows dropped
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.log(px / px.shift(1))               # previous market day
    lr = lr.replace([np.inf, -np.inf], np.nan)
    lr = lr.reindex(mkt.index)                      # window days that are market days

    r = lr.to_numpy()
    m = np.log1p(mkt.to_numpy())
    ok = np.isfinite(r)                             # m is finite on every retained day
    n = ok.sum(axis=0).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rbar = np.where(ok, r, 0.0).sum(axis=0) / n
        mbar = (ok * m[:, None]).sum(axis=0) / n
        rt = np.where(ok, r - rbar[None, :], 0.0)
        mt = np.where(ok, m[:, None] - mbar[None, :], 0.0)
        cos = (rt * mt ** 2).sum(axis=0) / n
        var_r = (rt ** 2).sum(axis=0) / n
        var_m = (mt ** 2).sum(axis=0) / n
        val = cos / (np.sqrt(var_r) * var_m)
    valid = (n >= n_market - _SLACK) & (n >= 3) & (var_r > 0) & (var_m > 0) & np.isfinite(val)
    val = np.where(valid, val, np.nan)
    return pd.Series(val, index=lr.columns).reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CoskewACX",
    col="f_coskewacx",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW coskewness is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="CoskewACX",
    source="Ang, Chen and Xing 2006 (Review of Financial Studies)",
    lookback_months=12,             # 12-calendar-month daily window
    history_months=12,              # return-window signal: a price at t-12 months
    notes="E[r~ m~^2]/(SD[r~] SD[m~]^2) on daily log returns vs raw VW market, 12m window, n >= N-5 market days; no rf",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous trading-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ff.mktrf + ff.rf", "MonthContext.market_daily('vw') from SEP + DAILY.marketcap",
         "harness raw VW all-stock series, not Ken French's; starts 1998-12-02 so 1999-01..1999-11 windows would be short and are nulled"),
        ("ff.rf", "omitted (not in the snapshot)",
         "cancels exactly under the de-meaning when constant; only its daily variation is lost"),
        ("max_nobs - nobs <= 5", "n >= N_market_days_in_window - 5",
         "OSAP's rule with N = market days; no absolute floor; a window opening before the market series (signals 1999-01..1999-11) is NaN"),
    ),
)
