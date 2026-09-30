"""
ReturnSkew — skewness of a stock's daily returns over one calendar month;
stocks with LOW return skewness are predicted to earn HIGHER returns.

OSAP: ReturnSkew, Bali, Engle and Murray 2015 (book, Table 14.10). Predicted
sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/ReturnSkew/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window: the market trading days of the signal's calendar month (the days
  of month t up to the signal date, which is the month's last trading day).
  No rolling window; the value is that month's own days only.
  r_d   = SEP.closeadj_d / SEP.closeadj_{d-1} - 1, d-1 being the market day
          before d. Prices are reindexed onto the market_daily calendar before
          the lag, so a stray SEP weekend/holiday row of one name never breaks
          the lag for the others; a name with no row on either day has no
          return for d (nothing is chained across a gap).
  ReturnSkew = population (biased) skewness of r_d over the month's days
  where the return is finite (n of them): m3 / m2^1.5 with
  m2 = mean((r - mean)^2), m3 = mean((r - mean)^3), exactly as polars
  `.skew()` (bias = True), NOT the sample-adjusted G1. Raw value, no log.
  Observation rule: at least 15 valid daily returns in the month, else NaN.
  Price-only: no filing date, no ART/ARQ choice. Shares the daily-return panel
  construction (market-calendar reindex, the signal month's days, the
  15-observation rule) with RealizedVol; this file needs no factor series.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? NaN: a month in which every
  daily return is exactly 0 (a flat, stale closeadj) has m2 = 0, so the
  skewness is 0/0; it is set NaN, not a value. No other exact value: the
  skewness of 15-23 returns is continuous.
  What share of the universe does nothing? ~0%: the spec measured the largest
  modal-value share at 0.115% (mean 0.065%) over the 276 decision months,
  distinct values >= 99.94% of scored names, and 10 qcut bins in every month.
  Preflight decides.
  Tie handling: null. Any non-finite skewness, and any return spread
  (sqrt m2) <= 1e-12, is set NaN and blend_ranks renormalises.

DEVIATIONS FROM OSAP:
  - SEP no-trade days are rows with the price carried forward (field_map trap
    sep_no_trade_days_are_rows): they give zero returns that count toward the 15
    observations and damp the measure for thin names; not filtered (the ADV screen
    bounds it), declared.
  - ret: SEP closeadj ratio (total return, no delisting return; closeadj is
    on a 3-decimal grid, which quantises back-adjusted prices below $0.50)
    replaces CRSP daily ret; a return is never chained across a missing row.
  - observation rule counts valid (finite) returns; OSAP's `pl.len()` counts
    all rows including null returns, so a name with null CRSP returns on
    listing days can differ by a day or two. Immaterial at coverage ~99.9%.
  - zero / noise-level variance set NaN (0/0 in OSAP).
  - the 1997-12 SEP stub month is dropped through ctx.partial_months("SEP")
    (never reached: the first signal month is 1998-12). market_daily starts
    1998-12-02, so the 1998-12 signal loses the 12-01 return but keeps about
    20 valid days.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_MIN_OBS = 15               # OSAP: ndays >= 15 per permno-month (Bali-Hovakimian 2009)
_CAL_DAYS = 45              # market calendar read: the month plus the prior close
_SPREAD_FLOOR = 1e-12       # return spread below this is a flat price, not a measured skew


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    sig = ctx.signal_asof
    month = sig.to_period("M")
    if month in ctx.partial_months("SEP"):
        return nan

    mkt = ctx.market_daily(_CAL_DAYS, col="vw")
    if mkt is None or len(mkt) == 0:
        return nan
    cal = pd.DatetimeIndex(mkt.index)                 # full market calendar

    d = ctx.daily("SEP", ["closeadj"], _CAL_DAYS)
    if d.empty:
        return nan
    px = d.pivot_table(index="date", columns="ID", values="closeadj", aggfunc="last").sort_index()
    px = px.where(px > 0)
    px.index = pd.DatetimeIndex(px.index)
    px = px.reindex(cal)                              # market calendar: stray SEP rows dropped
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = px / px.shift(1) - 1.0                  # previous market day
    ret = ret.replace([np.inf, -np.inf], np.nan)
    ret = ret[ret.index.to_period("M") == month]      # the signal month's days only
    if len(ret) < _MIN_OBS:
        return nan

    R = ret.to_numpy(dtype=float)
    ok = np.isfinite(R)
    n = ok.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        mu = np.where(ok, R, 0.0).sum(axis=0) / n
        e = np.where(ok, R - mu, 0.0)
        m2 = (e ** 2).sum(axis=0) / n
        m3 = (e ** 3).sum(axis=0) / n
        skew = m3 / m2 ** 1.5                         # population g1 (polars .skew(), bias=True)
    good = (n >= _MIN_OBS) & np.isfinite(skew) & (np.sqrt(m2) > _SPREAD_FLOOR)
    out = pd.Series(np.where(good, skew, np.nan), index=ret.columns)
    return out.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ReturnSkew",
    col="f_retskew",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW return skewness is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="ReturnSkew",
    source="Bali, Engle and Murray 2015 (Empirical Asset Pricing: The Cross Section of Stock Returns)",
    lookback_months=2,              # the calendar month read plus the prior close
    history_months=1,               # return-window signal: a price at t-1 month
    notes="population skewness (bias=True) of daily total returns over the signal's calendar month, >= 15 obs; no regression",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous market-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ret.skew() (polars, bias=True)", "population m3 / m2^1.5 of the month's valid daily returns",
         "OSAP's estimator, not the sample-adjusted G1; zero / <= 1e-12 spread set NaN"),
        ("ndays >= 15 (pl.len())", ">= 15 valid (finite) daily returns in the signal month",
         "OSAP counts all rows incl. null returns; can differ by a day or two for a few names"),
    ),
)
