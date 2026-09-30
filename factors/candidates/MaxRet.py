"""
MaxRet — the maximum single-day return of the signal month; a lottery-like
(high-maximum) stock is predicted to earn LOWER returns.

OSAP: MaxRet, Bali, Cakici and Whitelaw 2011, Journal of Financial Economics
(Table 1). Predicted sign: - (SignalDoc Sign = -1: long LOW, short HIGH).
Spec: osap_source/cache/b4e911e6/MaxRet/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  r_d    = SEP.closeadj_d / SEP.closeadj_{d-1} - 1 on each trading day d, d-1 the
           previous day of a TRADING CALENDAR built from the universe's own SEP
           print dates (harness market_trading_calendar: a date counts only if
           its print count is at least half the trailing 21-date median), so a
           stray weekend/holiday row of a few names is not a trading day and
           never becomes another name's "prior day". closeadj must be > 0 at
           both days, else that day's return is NaN. Nothing is chained across a
           missing row: a name without a print on the calendar day before d has
           no return on d.
  Signal = max of r_d over the trading days of the CALENDAR MONTH of the signal
           date (skipna; NaN if the name has no valid return that month). The
           first trading day's return uses the previous month's last close (a
           full month has ~21 returns from ~22 closes), as CRSP dsf ret does.
  No minimum-days rule (OSAP has none), no winsorising, no skew or volume
  adjustment. Raw value; ascending=False: a LOW maximum is the long leg.
  Price only: no filing date, no ART/ARQ choice.
  The 1997-12 SEP stub month (ctx.partial_months("SEP")) is never a signal month;
  if the signal month is in partial_months the factor returns NaN.
  history_months=1 (the name needs a close one month back, so its first return of
  the month exists), lookback_months=1.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (every day of the
  month flat: the maximum of zeros), a real value, not a default.
  What share of the universe does nothing? The spec measured the exactly-0.0
  share at a mean of 0.0003% (max 0.04%), a modal share of any value at most
  0.30% (2000-05-31: 1/7 = +14.3% on the pre-decimalisation fractional-price
  grid, 9 of 2,670 names, a real tick value), at least 1,732 distinct values, and
  no qcut(10) collapse. Preflight to confirm.
  Tie handling: none needed and nothing removed, nulled or floored; the harness
  average rank covers the few exact ties.

DEVIATIONS FROM OSAP:
  - crsp.ret (daily CRSP) -> SEP closeadj ratio (total return incl. dividends, no
    delisting return). closeadj is on a 3-decimal grid, so a back-adjusted price
    below $0.50 prints coarse returns; the price floor is on the unadjusted price,
    so a heavily back-adjusted low closeadj is possible and would add |ret| noise
    in exactly the high-MaxRet tail (not measured).
  - No return is formed across a missing row (OSAP's dsf ret is the vendor's own).
  - No minimum number of days, as OSAP: a name with a single return that month is
    scored (the spec measured 0.1% of universe names below 15 returns).
  - The trading calendar is the universe's own print dates (not the market-wide
    calendar the spec measurement used); the half-of-median rule reproduces it.
  - OSAP's test is value-weighted 10-1; the harness ranks, equal-weighted deciles.
  - Harness universe, not all CRSP.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_DAYS_BACK = 45             # the signal month (<= 31 days) plus the prior month's last close


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    month = ctx.signal_asof.to_period("M")
    if month in ctx.partial_months("SEP"):
        return nan

    d = ctx.daily("SEP", ["closeadj"], _DAYS_BACK)
    if d.empty:
        return nan
    cal = market_trading_calendar(d["date"])          # trading days, stray rows excluded
    d = d[d["date"].isin(cal)]
    adj = d.pivot_table(index="date", columns="ID", values="closeadj", aggfunc="last").sort_index()
    adj.index = pd.DatetimeIndex(adj.index)
    adj = adj.reindex(cal).astype(float)
    adj = adj.where(adj > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = adj / adj.shift(1) - 1.0                # previous trading day of the calendar
    ret = ret.replace([np.inf, -np.inf], np.nan)

    ret = ret[ret.index.to_period("M") == month]      # the signal's calendar month
    if ret.empty:
        return nan
    val = ret.max(axis=0, skipna=True)                # NaN where the month has no valid return
    return val.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MaxRet",
    col="f_maxret",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a high maximum day predicts LOW returns; long LOW
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MaxRet",
    source="Bali, Cakici and Whitelaw 2011 (Journal of Financial Economics)",
    lookback_months=1,
    history_months=1,               # return-window signal: a close one month back so the first return of the month exists
    notes="max daily closeadj return over the signal's calendar month, trading-calendar lag, no minimum days; sign -1",
    field_mappings=(
        ("crsp.ret (daily, dsf)", "SEP.closeadj (ratio to the previous trading-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid noise below $0.50 adjusted price"),
        ("groupby(permno, month)['ret'].max()", "max over the signal's calendar month, skipna",
         "same; no minimum-days rule (as OSAP); 1997-12 stub month NaN via ctx.partial_months"),
        ("CRSP daily calendar", "harness market_trading_calendar on the universe's SEP dates",
         "a stray weekend/holiday row is not a trading day and never becomes another name's prior day"),
        ("Stock Weight VW, LS quantile 0.1 (paper)", "harness equal-weighted deciles",
         "harness owns weighting; SignalDoc notes the signal is weaker equal-weighted"),
    ),
)
