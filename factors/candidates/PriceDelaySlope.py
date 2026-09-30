"""
PriceDelaySlope — Hou-Moskowitz price delay D2: the lag-weighted share of a stock's
total market loading, (1*b1 + 2*b2 + 3*b3 + 4*b4) / (b0 + b1 + b2 + b3 + b4) from a
daily regression on the contemporaneous and four lagged market returns over a
one-year June-to-June window; slow-to-incorporate-news stocks are predicted to
earn higher returns.

OSAP: PriceDelaySlope, Hou and Moskowitz 2005, Review of Financial Studies
(Table 2A "D2 adjusted"). Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/PriceDelaySlope/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window for the signal at month-end t: the market trading days d with
  Jun 30 (y-1) < d <= Jun 30 y, where y = year(t) if month(t) >= 7 else
  year(t) - 1, i.e. the latest COMPLETED June window strictly before the signal
  month (a June signal still uses the previous window). The value is one number
  per name per window, held for 12 signals; no look-ahead (the window is
  complete a full business month before its first use).
  Daily return r_d = closeadj_d / closeadj_{d-1} - 1 from ctx.daily("SEP",
  ["closeadj"]), with prices reindexed onto the ctx.market_daily calendar
  BEFORE the shift (a stray SEP weekend/holiday row never breaks the lag; a name
  with no row on a market day has no return that day and the next).
  m_d = ctx.market_daily(..., col="vw") raw VW market return; its lags m_{d-1}
  .. m_{d-4} are taken on the market calendar BEFORE the window is cut.
  Per name, over the window days where r, m and all four lags are finite, one
  unrestricted OLS (intercept):  r ~ 1 + m + m_1 + m_2 + m_3 + m_4.
  With b0 the coefficient on m and bk on m_k (k = 1..4):
      score = (1*b1 + 2*b2 + 3*b3 + 4*b4) / (b0 + b1 + b2 + b3 + b4)
  Normalisation is by the sum of the market betas, not by the number of lags.
  OSAP's filters: n >= 26 finite days, var(r) > 0, var(m) > 0 over those days,
  and "a finite return in June y" (OSAP: last observation in June). Score NaN
  when the denominator is exactly 0 or the ratio is not finite. NO trim, clip or
  winsorisation is applied (the OSAP code has none; the SignalDoc text that
  describes one is not in the code). Score NaN when the window opens before the
  market series starts (see below).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A zero-return window has zero
  variance, so it is dropped by the var(r) > 0 rule (NaN), not assigned a mode.
  Otherwise a continuous ratio with no natural mode.
  What share of the universe does nothing? Spec measurement on the 257
  full-window months: modal value share 0.04-0.12% of scored names (every scored
  value distinct; 1,688-2,588 scored names), ten qcut bins every month; coverage
  91.7-99.9% (median 98.3%).
  Tie handling: null. Zero-variance windows are NaN and blend_ranks renormalises;
  average rank for the rest; no noise or secondary key.
  Tail shape (not a mass point): the denominator (sum of betas) can be near zero
  or negative, so the ratio is unbounded and a negative denominator flips the
  sign of the ratio. Spec figures: |value| > 10 for 0.11-5.3% of scored names
  (median 1.0%); denominator negative for 0.06-9.0% of scored names (median
  0.9%). Faithful to the OSAP code, which has no trim; not clipped here (ranks
  ignore magnitude; winsorisation is a harness duty). The "guard every
  denominator" rule is applied as exactly-zero -> NaN only, because a negative
  denominator is the OSAP value, not an error.

HISTORY: history_months=13 (the hard rule for return-window factors). For a July
  signal t-13 is the window start, so a name must have traded when its window
  opened; for a June signal t-13 falls one month before the window end. The gate
  only removes names on top of OSAP's in-compute rule (n >= 26 finite-return days
  with a June return), so names without a trade 13 months back are NaN where OSAP
  would score them (declared). lookback_months=24 (a June signal reads the window
  ending the June before).

DEVIATIONS FROM OSAP:
  - rf omitted (the snapshot holds no risk-free rate): OSAP regresses excess
    returns; a near-constant rf is absorbed by the intercept and only its
    day-to-day variation (~1e-4 against 1-2% daily stock vol) is lost.
  - mkt: ctx.market_daily raw value-weighted all-stock series (prior-day cap
    weights, causal bad-print guards, no delisting returns, gap returns and
    genuine > +100% days excluded) replaces Ken French's mktrf.
  - ret: SEP closeadj ratio on the market calendar (total return, no delisting
    return, no return across a missing row, 3-decimal closeadj grid) replaces
    CRSP daily ret.
  - Truncated early window (coordinator decision pricedelay_truncated_windows):
    the market series starts 1998-12-02, so the windows ending June 1998 and
    June 1999 would be absent / short (145 market days). A window opening before
    the market series is NaN: signals up to and including 2000-06 are NaN, the
    first scored signal is 2000-07 (257 scorable months).
  - No forward-fill across a failed window: OSAP carries the last value across
    a year whose window fails its rules (inside a firm's first..last valid
    window); here the score is NaN when the current window fails.
  - "last observation in June" becomes "a finite return dated in June y".
  - Harness universe, within-sector rank and winsorisation replace the all-stock
    daily CRSP sample and OSAP's NYSE-breakpoint decile sort.
  - No trim / winsorisation: the OSAP code has none (see CONSTRUCTION).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_MIN_OBS = 26            # OSAP: n >= 26
_NLAGS = 4
_PAD_DAYS = 20           # calendar days before the window start: prior close + 4 market lags


def _score(r, X):
    """(1*b1+2*b2+3*b3+4*b4)/(b0+b1+..+b4) from OLS of r on [1, X]; X = [m, L1..L4]."""
    yc = r - r.mean()
    Xc = X - X.mean(axis=0)
    b = np.linalg.lstsq(Xc, yc, rcond=None)[0]           # slopes; intercept absorbed by centring
    den = float(b.sum())
    if den == 0.0 or not np.isfinite(den):
        return np.nan
    val = float(np.arange(0, _NLAGS + 1) @ b) / den       # weights 0 (m), 1..4 (lags)
    return val if np.isfinite(val) else np.nan


def _compute(ctx):
    t = ctx.signal_asof
    y = t.year if t.month >= 7 else t.year - 1
    lo = pd.Timestamp(year=y - 1, month=6, day=30)       # exclusive
    hi = pd.Timestamp(year=y, month=6, day=30)           # inclusive
    days_back = (t - lo).days + _PAD_DAYS
    nan = pd.Series(np.nan, index=ctx.ids)

    mkt = ctx.market_daily(days_back, col="vw")
    if mkt is None or len(mkt) == 0:
        return nan
    mkt = mkt.astype(float)
    mkt.index = pd.DatetimeIndex(mkt.index)
    # Window opens before the market series starts: not OSAP's (always full) window.
    if mkt.index.min() > lo + pd.offsets.BDay(1):
        return nan
    mkt = mkt[mkt.index <= hi]
    cal = mkt.index                                      # market calendar, pre-cut
    m = mkt.to_numpy()
    mlag = np.column_stack([pd.Series(m).shift(k).to_numpy() for k in range(1, _NLAGS + 1)])
    win = (cal > lo) & (cal <= hi)
    june = (cal.month == 6) & (cal.year == y)
    if win.sum() < _MIN_OBS:
        return nan

    d = ctx.daily("SEP", ["closeadj"], days_back)
    if d.empty:
        return nan
    px = d.pivot_table(index="date", columns="ID", values="closeadj", aggfunc="last").sort_index()
    px = px.where(px > 0)
    px.index = pd.DatetimeIndex(px.index)
    px = px.reindex(cal)                                 # market calendar: stray SEP rows dropped
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = px / px.shift(1) - 1.0                     # previous MARKET day
    ret = ret.replace([np.inf, -np.inf], np.nan)

    R = ret.to_numpy()[win]
    M = m[win]
    L = mlag[win]
    jn = june[win]
    base_ok = np.isfinite(M) & np.isfinite(L).all(axis=1)
    out = np.full(R.shape[1], np.nan)
    for j in range(R.shape[1]):
        ok = base_ok & np.isfinite(R[:, j])
        n = int(ok.sum())
        if n < _MIN_OBS or not (ok & jn).any():
            continue
        r, mm = R[ok, j], M[ok]
        if not (np.var(r) > 0 and np.var(mm) > 0):
            continue
        out[j] = _score(r, np.column_stack([mm, L[ok]]))
    return pd.Series(out, index=ret.columns).reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="PriceDelaySlope",
    col="f_pricedelayslope",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH price delay earns HIGHER returns
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="PriceDelaySlope",
    source="Hou and Moskowitz 2005 (Review of Financial Studies)",
    lookback_months=24,             # a June signal reads the window ending the June before
    history_months=13,              # a trade 13 months back (window start for July signals)
    notes="(1b1+2b2+3b3+4b4)/(b0+..+b4) of daily r on m and 4 market lags, Jun-Jun window, n>=26; no trim; rf omitted; signals to 2000-06 NaN",
    field_mappings=(
        ("history gate", "history_months=13",
         "names without a trade 13 months back are NaN (OSAP would score them on >= 26 days)"),
        ("crsp.ret (daily)", "SEP.closeadj ratio to the previous MARKET-calendar day",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ff.mktrf", "MonthContext.market_daily('vw') from SEP + DAILY.marketcap",
         "harness raw VW all-stock series, not Ken French's; starts 1998-12-02"),
        ("ff.rf (ret - rf)", "omitted (not in the snapshot)",
         "absorbed by the intercept when near-constant; only its daily variation is lost"),
        ("June-bucket window, forward-filled between valid windows", "latest completed Jun(y-1)..Jun(y) window strictly before the signal month",
         "no forward-fill across a failed window; score NaN then"),
        ("last observation in June", "a finite return dated in June y", "same intent, calendar-based"),
        ("window of the FF daily sample", "window opening before 1998-12-02 is NaN",
         "coordinator decision: signals 1998-12..2000-06 NaN; 257 scorable months"),
    ),
)
