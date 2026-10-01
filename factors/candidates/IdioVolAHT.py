"""
IdioVolAHT — idiosyncratic volatility: the root-mean-squared residual of a
stock's daily CAPM regression over its last 252 valid paired observations; a
stock with HIGH idiosyncratic risk is predicted to earn LOWER returns.

OSAP: IdioVolAHT, Ali, Hwang and Trombley 2003, Journal of Financial
Economics (Table 4). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/IdioVolAHT/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  m_d = ctx.market_daily(420, col="vw") (raw cap-weighted market of the
        harness); the market days d are its index.
  r_d = SEP.closeadj_d / SEP.closeadj_{d-1} - 1, d-1 being the market day
        before d. Prices are reindexed onto the market calendar before the
        lag, so a stray SEP weekend/holiday row of one name never breaks the
        lag for the others; a name with no row on either day has no return
        for d (nothing is chained across a gap).
  Per name, the pairs (r_d, m_d) with both finite are sorted in time and the
  LAST 252 are kept (the window is 252 valid ROWS of the stock's own history,
  not 252 trading days, as OSAP's rolling window over null-dropped rows).
  n = pairs kept; required n >= 100 (OSAP min_samples), else NaN.
  OLS of r on [1, m] over those pairs; IdioVolAHT = sqrt(SSE / (n - 2)), the
  regression standard error (asreg rmse, dof = n - k with k = 2).
  The value is the estimate on the signal date, the month's last trading day
  (OSAP keeps the last non-missing rmse of the month).
  Price-only: no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 only for a name
  whose returns are all exactly zero over 100+ valid rows (SSE = 0).
  Otherwise the rmse is continuous.
  What share of the universe does nothing? ~0%: a flat year of closeadj does
  not occur under the price >= $1 and dollar-volume screens; the spec
  measured a modal value share of about 0.06-0.12% on this snapshot.
  Preflight decides.
  Tie handling: null. A zero residual spread is an artefact of a stale price,
  not a measured risk, so it is set NaN and blend_ranks renormalises.

DEVIATIONS FROM OSAP:
  - rf omitted (the snapshot holds no risk-free rate). Over a 252-row window
    rf's slow drift adds a negligible trend to the residual; the intercept
    absorbs its level. The stock return and the market are both RAW.
  - mktrf: ctx.market_daily raw value-weighted all-stock series (common
    stock on the universe's exchanges, prior-day cap weights, causal
    bad-print guards, no delisting returns, gap returns and >+100% / <-80%
    daily prints excluded), not CRSP VW minus rf.
  - ret: SEP closeadj ratio (total return, no delisting return; 3-decimal
    closeadj grid) replaces CRSP daily ret; a return is never chained across
    a missing row (CRSP's ret on the first day after a gap is kept by OSAP).
  - reach: the read is 420 calendar days (~290 trading days), so a name with
    many missing days holds fewer than 252 valid rows where OSAP would reach
    further back; the 100-row minimum still applies.
  - early window: the market series starts 1998-12-02, so signals 1998-12 ..
    1999-03 hold fewer than 100 pairs and are NaN for every name; from
    1999-04 to 1999-11 the estimate rests on 100-250 rows (inside OSAP's own
    100-row rule, not its full window). No absolute floor beyond OSAP's 100.
  - exactly-zero SSE set NaN (OSAP would emit 0.0).
  - the 1997-12 SEP stub month is excluded from the pairs through
    ctx.partial_months("SEP") (never reached: the market series starts
    1998-12-02).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_DAYS_BACK = 420            # enough calendar days for 252 valid rows of an ordinary name
_WINDOW = 252               # OSAP window_size (valid rows)
_MIN_OBS = 100              # OSAP min_samples


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    mkt = ctx.market_daily(_DAYS_BACK, col="vw")
    if mkt is None or len(mkt) == 0:
        return nan
    mkt = mkt.astype(float)
    mkt.index = pd.DatetimeIndex(mkt.index)
    cal = mkt.index

    d = ctx.daily("SEP", ["closeadj"], _DAYS_BACK)
    if d.empty:
        return nan
    px = d.pivot_table(index="date", columns="ID", values="closeadj", aggfunc="last").sort_index()
    px = px.where(px > 0)
    px.index = pd.DatetimeIndex(px.index)
    px = px.reindex(cal)                            # market calendar: stray SEP rows dropped
    with np.errstate(divide="ignore", invalid="ignore"):
        ret = px / px.shift(1) - 1.0                # previous market day
    ret = ret.replace([np.inf, -np.inf], np.nan)

    # Days in a partial snapshot-start month never enter a window.
    partial = ctx.partial_months("SEP")
    if partial:
        ret = ret[~ret.index.to_period("M").isin(list(partial))]
    m = mkt.reindex(ret.index).to_numpy()
    good_m = np.isfinite(m) & (m > -1.0)

    R = ret.to_numpy()
    valid = np.isfinite(R) & good_m[:, None]
    # keep the LAST 252 valid rows of each name
    rank_from_end = np.cumsum(valid[::-1], axis=0)[::-1]
    keep = valid & (rank_from_end <= _WINDOW)
    n = keep.sum(axis=0).astype(float)

    mm = np.where(good_m, m, 0.0)[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        ybar = np.where(keep, R, 0.0).sum(axis=0) / n
        xbar = (keep * mm).sum(axis=0) / n
        dy = np.where(keep, R - ybar[None, :], 0.0)
        dx = np.where(keep, mm - xbar[None, :], 0.0)
        sxx = (dx * dx).sum(axis=0)
        sxy = (dx * dy).sum(axis=0)
        syy = (dy * dy).sum(axis=0)
        sse = np.maximum(syy - sxy * sxy / sxx, 0.0)
        val = np.sqrt(sse / (n - 2.0))
    ok = (n >= _MIN_OBS) & (sxx > 0) & np.isfinite(val) & (val > 0)
    val = np.where(ok, val, np.nan)
    return pd.Series(val, index=ret.columns).reindex(ctx.ids)


FACTOR = FactorDef(
    family="volatility",                # Phase C, 2026-10-01: Cat.Economic "volatility" (decision phase_c_family_partition)
    name="IdioVolAHT",
    col="f_ivolaht",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW idiosyncratic volatility is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="IdioVolAHT",
    source="Ali, Hwang and Trombley 2003 (Journal of Financial Economics)",
    lookback_months=14,             # 420 calendar days read for 252 valid rows
    history_months=5,               # return-window signal: ~100 trading days (OSAP's 100-row minimum)
    notes="sqrt(SSE/(n-2)) of daily CAPM regression over the last 252 valid (ret, mkt) rows, n >= 100; no rf",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous market-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ff.mktrf", "MonthContext.market_daily('vw') from SEP + DAILY.marketcap",
         "harness raw VW all-stock series, not Ken French's; starts 1998-12-02; not in the field_map index (harness accessor)"),
        ("ff.rf", "omitted (not in the snapshot)",
         "level absorbed by the intercept; its slow drift over 252 rows is negligible for a residual std"),
        ("rolling_ols window 252 rows, min 100; rmse", "last 252 valid pairs within 420 calendar days, n >= 100; sqrt(SSE/(n-2))",
         "OSAP's rule and dof; a gappy name reaches less far back than OSAP's row window; exactly-zero SSE set NaN"),
    ),
)
