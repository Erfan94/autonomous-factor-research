"""
RealizedVol — realized (total) volatility: the standard deviation of a stock's
daily returns over one calendar month; stocks with HIGH total volatility are
predicted to earn LOWER returns.

OSAP: RealizedVol, Ang, Hodrick, Xing and Zhang 2006, Journal of Finance
(Table 6A). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/RealizedVol/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window: the market trading days of the signal's calendar month (the days
  of month t up to the signal date, which is the month's last trading day).
  No rolling window; the value is that month's own days only.
  r_d   = SEP.closeadj_d / SEP.closeadj_{d-1} - 1, d-1 being the market day
          before d. Prices are reindexed onto the market_daily calendar before
          the lag, so a stray SEP weekend/holiday row of one name never breaks
          the lag for the others; a name with no row on either day has no
          return for d (nothing is chained across a gap).
  RealizedVol = sample standard deviation (ddof = 1, OSAP's polars `.std()`)
  of r_d over the month's days where the return is finite (n of them). Raw:
  no log, no annualisation, no factor regression.
  Observation rule = OSAP's: at least 15 valid daily observations in the
  month (ZZ0 script: `ret.count().over(permno, time_avail_m) >= 15`), else
  NaN. Price-only: no filing date, no ART/ARQ choice.
  Shares the daily-return panel construction (market-calendar reindex, the
  signal month's days, the 15-observation rule) with IdioVol3F; the two
  differ only in what is measured, the raw return here versus the FF3
  regression residual there. This file needs no factor series.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0: a month in which
  every daily return is exactly 0 (a flat, stale closeadj) has standard
  deviation 0. Anything else is a continuous standard deviation.
  What share of the universe does nothing? ~0%: the spec measured 0 exact
  zeros in each of the 276 decision months, distinct values >= 99.9% of
  scored names, largest modal share 0.115% (mean 0.065%), and 10 qcut bins
  in every month. Preflight decides.
  Tie handling: null. A zero spread is an artefact of a stale price, not a
  measured risk, so it is set NaN and blend_ranks renormalises (a dead
  branch on the measured snapshot).

DEVIATIONS FROM OSAP:
  - SEP no-trade days are rows with the price carried forward (field_map trap
    sep_no_trade_days_are_rows): they give zero returns that count toward the 15
    observations and damp the measure for thin names; not filtered (the ADV screen
    bounds it), declared.
  - The trading calendar is ctx.market_daily's (built from SEP + DAILY.marketcap), which
    starts 1998-12-02, so the 1998-12 signal loses the 12-01 and 12-02 returns.
  - history_months=1 drops a name whose first month is t, which OSAP would score on
    >= 15 days.
  - SignalDoc's Detailed Definition says "residuals from CAPM regressions";
    the OSAP code (the authority) emits RealizedVol as the plain std of the
    daily excess return, the regression residuals feeding IdioVol3F instead.
    This file follows the code: TOTAL volatility, no regression.
  - rf omitted (the snapshot holds no risk-free rate). rf is near-constant
    within a calendar month and its day-to-day variation is orders of
    magnitude below daily stock volatility, so std(ret) equals std(ret - rf)
    to rounding.
  - ret: SEP closeadj ratio (total return, no delisting return; closeadj is
    on a 3-decimal grid, which quantises back-adjusted prices below $0.50)
    replaces CRSP daily ret; a return is never chained across a missing row.
  - exactly-zero volatility set NaN (OSAP would emit 0.0).
  - the 1997-12 SEP stub month is dropped through ctx.partial_months("SEP")
    (never reached: the first signal month is 1998-12).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_MIN_OBS = 15               # OSAP: ret.count() >= 15 per permno-month (Bali-Hovakimian 2009)
_CAL_DAYS = 45              # market calendar read: the month plus the prior close


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

    n = ret.notna().sum(axis=0)
    vol = ret.std(axis=0, ddof=1)                     # OSAP: polars .std()
    vol = vol.where((n >= _MIN_OBS) & np.isfinite(vol) & (vol > 0))
    return vol.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="RealizedVol",
    col="f_realvol",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW total volatility is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="RealizedVol",
    source="Ang, Hodrick, Xing and Zhang 2006 (Journal of Finance)",
    lookback_months=2,              # the calendar month read plus the prior close
    history_months=1,               # return-window signal: a price at t-1 month
    notes="std (ddof=1) of daily total returns over the signal's calendar month, >= 15 obs; no rf, no regression",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous market-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ff.rf", "omitted (not in the snapshot)",
         "near-constant within the month; std of the excess return equals std of the raw return to rounding"),
        ("ret.std() (RealizedVol)", "ddof=1 std of the raw daily return, total volatility",
         "follows the OSAP code, not SignalDoc's CAPM-residual wording; exactly-zero spread set NaN"),
        ("ret.count() >= 15", ">= 15 valid daily returns in the signal month", "OSAP's rule"),
    ),
)
