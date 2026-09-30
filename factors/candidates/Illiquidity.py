"""
Illiquidity — Amihud's illiquidity: the twelve-month average of the daily
absolute return per dollar of trading volume; illiquid stocks are predicted
to earn HIGHER returns (a liquidity premium).

OSAP: Illiquidity, Amihud 2002, Journal of Financial Markets (Table 2).
Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/Illiquidity/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ill_d  = |r_d| / (close_d * volume_d) on each trading day d, with
           r_d = SEP.closeadj_d / SEP.closeadj_{d-1} - 1 (d-1 the previous
           trading day of the calendar built below) and close, volume both
           from SEP (split-restated, the SAME share basis: the product is a
           split-invariant dollar volume; closeunadj is never paired with
           volume). A day with volume <= 0, close <= 0 or no return is NaN
           (OSAP's +-inf -> NaN), skipped by the monthly mean.
  ill_m  = mean of ill_d over the calendar month's valid days (NaN if none).
  Signal = mean of ill_m over the 12 CALENDAR months t-11 .. t (the signal
           month included), only if ALL 12 are finite, else NaN (OSAP's
           count == 12 rule). Raw value; Amihud's x10^6 scaling is absent
           (rank-invariant).
  Calendar: trading days are the dates on which at least half the trailing
  21-date median number of universe names printed (harness
  market_trading_calendar applied to the universe's own SEP dates), so a
  stray weekend/holiday row of a few names is not a trading day and never
  becomes another name's "prior day". market_daily is not used because its
  series starts 1998-12-02 and the first windows open in 1998-01.
  Price/volume only: no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 only for a name
  whose every traded day in 12 months has a zero return; a name that never
  trades has no valid day and is NaN. Otherwise a continuous ratio.
  What share of the universe does nothing? ~0%: a year of zero returns on
  days with volume does not occur under the price >= $1 and dollar-volume
  screens; the spec measured a modal share of 0.06% on this snapshot.
  Preflight decides.
  Tie handling: null. Zero-volume days are NaN (dropped from the mean); a
  signal of exactly 0 (an all-zero-return year) is set NaN, since it is an
  artefact of a stale price, not a measured liquidity, and blend_ranks
  renormalises.

DEVIATIONS FROM OSAP:
  - ret: SEP closeadj ratio (total return, no delisting return; 3-decimal
    closeadj grid, which adds noise to |ret| for back-adjusted prices below
    $0.50) replaces CRSP daily ret; no return across a missing row.
  - prc: SEP.close (split-restated, same basis as SEP.volume), not CRSP
    |prc| (which carries the bid/ask midpoint on no-trade days).
  - vol: SEP.volume is consolidated; CRSP NASDAQ volume before 2004 double
    counts dealer-to-dealer trades, so the LEVEL differs by exchange mix
    (rank formed within sector, then across the pre-/post-2004 mix).
  - lags: calendar months t-11..t, where OSAP's shift(k) runs over the
    permno's own monthly panel rows (a name with a gap borrows an older
    month there; here the gap is NaN and sinks the all-12 rule).
  - SignalDoc's price > $5 / NYSE-only portfolio filter is not in OSAP's
    predictor.py and is not applied; the harness universe decides.
  - exactly-zero signal set NaN (OSAP would emit 0.0).
  - the 1997-12 SEP stub month: a window containing a partial snapshot-start
    month (ctx.partial_months("SEP")) is NaN; never reached (the first
    window is 1998-01..1998-12).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_DAYS_BACK = 400            # 12 calendar months (<= ~366 days) plus the prior close
_MONTHS = 12


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    month = ctx.signal_asof.to_period("M")
    window = pd.period_range(month - (_MONTHS - 1), month, freq="M")
    if any(p in ctx.partial_months("SEP") for p in window):
        return nan

    d = ctx.daily("SEP", ["closeadj", "close", "volume"], _DAYS_BACK)
    if d.empty:
        return nan
    cal = market_trading_calendar(d["date"])          # trading days, stray rows excluded
    d = d[d["date"].isin(cal)]

    def wide(col):
        w = d.pivot_table(index="date", columns="ID", values=col, aggfunc="last").sort_index()
        w.index = pd.DatetimeIndex(w.index)
        return w.reindex(cal)

    adj = wide("closeadj").astype(float)
    adj = adj.where(adj > 0)
    cl = wide("close").astype(float)
    vol = wide("volume").astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = adj / adj.shift(1) - 1.0                # previous trading day of the calendar
        dv = (cl * vol).where((cl > 0) & (vol > 0))   # zero-volume day -> NaN (OSAP's inf)
        ill = ret.abs() / dv
    ill = ill.replace([np.inf, -np.inf], np.nan)

    per = ill.index.to_period("M")
    ill = ill[(per >= window[0]) & (per <= window[-1])]
    monthly = ill.groupby(ill.index.to_period("M")).mean()     # skipna; NaN if no valid day
    monthly = monthly.reindex(window)                          # all 12 calendar months
    val = monthly.mean(axis=0, skipna=False)                   # any missing month -> NaN
    val = val.where(np.isfinite(val) & (val > 0))
    return val.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Illiquidity",
    col="f_illiq",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH illiquidity is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "SEP.close", "SEP.volume"),
    osap_acronym="Illiquidity",
    source="Amihud 2002 (Journal of Financial Markets)",
    lookback_months=12,             # 12 calendar months t-11..t
    history_months=11,              # return-window signal: a price at the end of month t-11
    notes="12-month mean of monthly mean of |ret|/(close x volume), calendar months t-11..t, all 12 required; zero-volume days NaN",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous trading-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("crsp.prc", "SEP.close",
         "split-restated, same basis as SEP.volume (never closeunadj); no bid/ask-midpoint fallback"),
        ("crsp.vol", "SEP.volume",
         "split-restated consolidated shares; CRSP NASDAQ volume pre-2004 double counts dealer trades, so the level differs by exchange mix"),
        ("ill_d = |ret|/(|prc|*vol); inf -> NaN", "|ret| / (close x volume), volume <= 0 -> NaN",
         "zero-volume days dropped from the monthly mean; exactly-zero signal set NaN"),
        ("ill_lag1..ill_lag11 (panel-row shifts), count == 12", "calendar months t-11..t, all 12 finite",
         "calendar months not panel rows; a month gap is NaN"),
        ("SignalDoc price > 5, NYSE only", "harness universe",
         "not in OSAP's predictor.py; not applied"),
    ),
)
