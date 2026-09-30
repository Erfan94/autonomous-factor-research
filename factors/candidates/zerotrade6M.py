"""
zerotrade6M — Liu (2006) turnover-adjusted zero-trading-day measure over the
previous 6 calendar months (OSAP ZeroTrade): zero-volume days plus a reciprocal-turnover
tie-breaker, scaled to a 21 x 6 day window; illiquid stocks (many no-trade
days, low turnover) are predicted to earn HIGHER returns.

OSAP: zerotrade6M (Acronym2 ZeroTrade), Liu 2006, Journal of Financial Economics.
Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/zerotrade6M/spec.md
(One OSAP script, ZZ1_zerotrade_zerotradeAlt1_zerotradeAlt12.py, emits zerotrade1M,
zerotrade6M and zerotrade12M; the three files here share one code path and differ
only in the window N and the deflator.)

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window: the 6 CALENDAR months t-6 .. t-1; the signal month t itself is
  EXCLUDED (OSAP's shift(1)). All 6 months must hold at least one trading-day
  row and a share count, else NaN (no panel-row borrowing).
  Days: SEP daily rows restricted to the market trading calendar (harness
  market_trading_calendar applied to the universe's own SEP dates), so a stray
  weekend/holiday row of a few names is never a day. SEP prints a no-trade day as
  an explicit volume-0 row, and those rows are what countzero counts.
  countzero = number of window days with SEP.volume == 0.
  Turn      = sum over window days of SEP.volume / SF1.sharesbas, where
              sharesbas is the ART value known at that day's month-end
              (harness fundamentals_at_month_ends, lags 1..6; every filing is
              dated on or before the signal). SEP.volume and SF1.sharesbas are
              both restated to today's split basis, so the ratio is split-free
              (SEP.close is not read). The sum runs over window days that carry a
              volume value (OSAP's pandas sum skips missing days).
  ndays     = number of window days with a volume value.
  Signal    = (countzero + (1 / Turn) / 11000) * (21 * 6 / ndays); raw value.
  The code is 1/Turn (Liu's formula), NOT the SignalDoc's "sum of monthly
  turnover" wording; the code governs. Deflator 11000 as in OSAP.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A name with no volume at all in
  the window has Turn = 0, so 1/Turn = +inf (OSAP emits +inf); a name with volume
  but no zero-volume day has countzero = 0 and a value equal to the small
  tie-breaker, a continuous function of turnover, so it is not an exact tie.
  What share of the universe does nothing? The spec measured, on the harness
  universe over every decision month: modal exact-value share 0.039-0.058 percent of
  scored names (distinct values equal the scored count), all ten qcut bins
  populated, no exact mass point. The Turn = 0 case is 2 name-months in 276 at
  the 1M window and none at 6M/12M.
  PLAIN STATEMENT: 99.68 percent of scored names (mean over months) have
  countzero = 0, so in this universe the signal is in effect a LOW-TURNOVER sort
  (Spearman with 1/Turn 0.992 mean), with the OSAP zero-day count acting on only
  6.7 names per month (those sit above every other name). The three
  zerotrade variants (1M, 6M, 12M) use overlapping windows of the same turnover
  series and should be expected to overlap heavily with each other and with any
  other turnover or illiquidity signal.
  Tie handling: null. Turn == 0 (inf) -> NaN, blend_ranks renormalises; no exact
  ties otherwise (average rank on the exact value).

DEVIATIONS FROM OSAP:
  - shrout: SF1.sharesbas (ART), company-level (all classes), at filing cadence
    carried to each month-end, not CRSP's per-PERMNO daily series. A window month
    without a share count makes the signal NaN (shares required in EVERY window
    month; within a month the sum covers the days that have volume).
  - vol: SEP.volume is consolidated; CRSP NASDAQ volume before 2004 double counts
    dealer-to-dealer trades, so the turnover LEVEL differs by exchange mix.
  - calendar months t-6..t-1, where OSAP's shift runs over the permno's own monthly
    panel rows (a name with a gap borrows an older month there; here the gap is NaN).
  - Turn == 0 -> NaN (OSAP emits +inf).
  - the 1997-12 SEP stub month: a window containing a partial snapshot-start month
    (ctx.partial_months("SEP")) is NaN; the first signal window
    (1998-06..1998-11) is complete.
  - SignalDoc NYSE-only portfolio filter (exchcd == 1) is not in OSAP's predictor
    code and is not applied; the harness universe decides.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_N = 6                     # window months t-N .. t-1
_DEFLATOR = 11000
_DAYS_BACK = 31 * (_N + 1) + 4  # from the start of month t-N to a signal at month t's end


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    month = ctx.signal_asof.to_period("M")
    window = pd.period_range(month - _N, month - 1, freq="M")     # month t excluded
    stub = set(ctx.partial_months("SEP"))
    if any(p in stub for p in window):
        return nan

    d = ctx.daily("SEP", ["volume"], _DAYS_BACK)
    if d.empty:
        return nan
    cal = market_trading_calendar(d["date"])             # trading days, stray rows excluded
    d = d[d["date"].isin(cal)]
    per_all = d["date"].dt.to_period("M")
    d = d[(per_all >= window[0]) & (per_all <= window[-1])]
    if d.empty:
        return nan

    vol = d.pivot_table(index="date", columns="ID", values="volume", aggfunc="last").sort_index()
    vol.index = pd.DatetimeIndex(vol.index)
    vol = vol.astype(float).where(lambda x: x >= 0)
    per = vol.index.to_period("M")

    # shares: SF1.sharesbas (ART) as known at each window month-end, lag m <-> month t-m
    sh_long = ctx.fundamentals_at_month_ends(["sharesbas"], range(1, _N + 1))
    if sh_long.empty:
        return nan
    sh_long = sh_long.assign(period=[month - int(m) for m in sh_long["months_back"]])
    sh_long["sharesbas"] = pd.to_numeric(sh_long["sharesbas"], errors="coerce")
    sh_long = sh_long.loc[sh_long["sharesbas"] > 0]       # a non-positive count is no count
    sh = sh_long.pivot_table(index="period", columns="ID", values="sharesbas", aggfunc="last")
    sh = sh.reindex(index=window, columns=vol.columns)
    has_shares = sh.notna().all(axis=0)                   # a share count in EVERY window month

    sh_days = sh.reindex(per)
    sh_days.index = vol.index
    with np.errstate(divide="ignore", invalid="ignore"):
        turn_d = vol / sh_days

    rows = vol.notna()
    n_by_month = rows.groupby(per).sum().reindex(window)           # volume rows per month
    all_months = (n_by_month > 0).all(axis=0)                      # a row in EVERY window month
    ndays = rows.sum(axis=0).astype(float)
    countzero = (vol == 0).sum(axis=0).astype(float)
    turn = turn_d.sum(axis=0, skipna=True)

    ok = has_shares & all_months & (ndays > 0) & (turn > 0)        # Turn == 0 (inf) -> NaN
    with np.errstate(divide="ignore", invalid="ignore"):
        val = (countzero + (1.0 / turn.where(turn > 0)) / _DEFLATOR) * (21.0 * _N / ndays.where(ndays > 0))
    val = val.where(ok & np.isfinite(val))
    return val.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="zerotrade6M",
    col="f_zt6m",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH value (illiquid) is attractive
    weight=1.0,
    inputs=("SEP.volume", "SF1.sharesbas"),
    osap_acronym="zerotrade6M",
    source="Liu 2006 (Journal of Financial Economics)",
    lookback_months=6 + 1,       # window t-N..t-1 plus the month-t skip
    history_months=6,            # volume-window signal: data from the start of month t-N
    notes="(zero-volume days + (1/turnover)/11000) x (21*6/ndays), calendar months t-6..t-1; turnover = SEP.volume/SF1.sharesbas",
    field_mappings=(
        ("crsp.vol (daily)", "SEP.volume",
         "split-restated consolidated shares; explicit 0 on a no-trade day (countzero); CRSP NASDAQ volume pre-2004 double counts dealer trades"),
        ("crsp.shrout (daily)", "SF1.sharesbas (ART, latest filing at each month-end)",
         "company-level count at filing cadence, split-restated (same basis as SEP.volume); a window month without a count makes the signal NaN"),
        ("time_d (CRSP trading days)", "SEP.date on the market trading calendar",
         "stray weekend/holiday rows excluded (market_trading_calendar)"),
        ("temp_zerotrade.shift(1) over panel rows", "calendar months t-6..t-1, month t excluded",
         "calendar months not panel rows; a month gap is NaN; Turn == 0 (inf) -> NaN"),
        ("SignalDoc exchcd == 1 (NYSE only)", "harness universe",
         "not in OSAP's predictor.py; not applied"),
    ),
)
