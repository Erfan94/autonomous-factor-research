"""
IdioVol3F — idiosyncratic volatility: the standard deviation of a stock's
daily residuals from a Fama-French three-factor regression over one calendar
month; stocks with HIGH idiosyncratic risk are predicted to earn LOWER
returns.

OSAP: IdioVol3F, Ang, Hodrick, Xing and Zhang 2006, Journal of Finance
(Table 7B). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/IdioVol3F/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Window: the market trading days of the signal's calendar month (the days
  of month t up to the signal date, which is the month's last trading day).
  No rolling window; the value is that month's own days only.
  r_d   = SEP.closeadj_d / SEP.closeadj_{d-1} - 1, d-1 being the market day
          before d. Prices are reindexed onto the market_daily calendar before
          the lag, so a stray SEP weekend/holiday row of one name never breaks
          the lag for the others; a name with no row on either day has no
          return for d (nothing is chained across a gap).
  X_d   = [1, mkt_d, smb_d, hml_d] from ctx.ff3_daily (the harness's
          Sharadar-native Fama-French rebuild; only days where all three
          factors exist are served).
  Per name, over the days where the return is finite (n of them), OLS of r on
  X (intercept and three slopes); IdioVol3F = sample standard deviation
  (ddof = 1, the residual mean is 0 by the intercept) of the residuals. OSAP's
  polars `.std()`, NOT sqrt(SSE / (n - 4)).
  Observation rule = OSAP's: at least 15 valid daily observations in the
  month, else NaN. Price-only: no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0: a month in which
  every daily return is exactly 0 has all residuals 0 (OLS of zeros on the
  factors). Anything else is a continuous standard deviation.
  What share of the universe does nothing? ~0%: a whole calendar month of
  exactly flat closeadj does not occur under the price >= $1 and
  dollar-volume screens; the spec measured a modal value share <= 0.12% on
  this snapshot, inside which this block sits. Preflight decides.
  Tie handling: null. A zero residual spread is an artefact of a stale price,
  not a measured risk, so it is set NaN and blend_ranks renormalises.

DEVIATIONS FROM OSAP:
  - SEP no-trade days are rows with the price carried forward (field_map trap
    sep_no_trade_days_are_rows): they give zero returns that count toward the 15
    observations and damp the measure for thin names; not filtered (the ADV screen
    bounds it), declared.
  - rf omitted (the snapshot holds no risk-free rate). Within one calendar
    month rf is effectively constant, so the regression intercept absorbs it
    and the residual standard deviation is unchanged; the stock return and
    the regressors are both RAW.
  - mktrf / smb / hml: ctx.ff3_daily, the harness rebuild (NYSE-breakpoint
    2x3 sorts on SF1 book equity and DAILY.marketcap; CURRENT TICKERS
    exchange for the breakpoints; BE = equity + taxliabilities with no
    preferred stock; no delisting returns; mkt RAW), not Ken French's series.
  - ret: SEP closeadj ratio (total return, no delisting return; closeadj is
    on a 3-decimal grid, which quantises back-adjusted prices below $0.50)
    replaces CRSP daily ret; a return is never chained across a missing row.
  - data start TRUNCATION: smb / hml exist only from the first trading day
    after the June-1999 formation, so every signal before 1999-07-30 (the
    first complete-factor month) is NaN for every name: a data-start fact of
    the harness's factor build, not a defect. About 7 of the 276 decision
    months.
  - exactly-zero residual spread set NaN (OSAP would emit 0.0).
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

    ff = ctx.ff3_daily(int((sig - month.start_time).days) + 1)
    if ff is None or len(ff) == 0:
        return nan
    ff = ff.astype(float)
    ff.index = pd.DatetimeIndex(ff.index)
    ff = ff[(ff.index.to_period("M") == month) & np.isfinite(ff.to_numpy()).all(axis=1)]
    if len(ff) < _MIN_OBS:
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
    ret = ret.replace([np.inf, -np.inf], np.nan).reindex(ff.index)

    Y = ret.to_numpy()
    X = np.column_stack([np.ones(len(ff)), ff[["mkt", "smb", "hml"]].to_numpy()])
    ok = np.isfinite(Y)
    n = ok.sum(axis=0)
    out = np.full(Y.shape[1], np.nan)

    # Names sharing one missing-day pattern share one design matrix: one lstsq each.
    pats, inv = np.unique(ok.T, axis=0, return_inverse=True)
    inv = np.asarray(inv).reshape(-1)
    for k in range(len(pats)):
        p = pats[k]
        if p.sum() < _MIN_OBS:
            continue
        cols = np.where(inv == k)[0]
        Xp = X[p]
        Yp = Y[np.ix_(p, cols)]
        beta, *_ = np.linalg.lstsq(Xp, Yp, rcond=None)
        res = Yp - Xp @ beta
        out[cols] = res.std(axis=0, ddof=1)           # OSAP: polars .std() of the residuals

    out = np.where((n >= _MIN_OBS) & np.isfinite(out) & (out > 0), out, np.nan)
    return pd.Series(out, index=ret.columns).reindex(ctx.ids)


FACTOR = FactorDef(
    family="volatility",                # Phase C, 2026-10-01: Cat.Economic "volatility" (decision phase_c_family_partition)
    name="IdioVol3F",
    col="f_ivol3f",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW idiosyncratic volatility is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap", "SF1.equity", "SF1.assets",
            "SF1.liabilities", "SF1.taxliabilities"),
    osap_acronym="IdioVol3F",
    source="Ang, Hodrick, Xing and Zhang 2006 (Journal of Finance)",
    lookback_months=2,              # the calendar month read plus the prior close
    history_months=1,               # return-window signal: a price at t-1 month
    notes="std (ddof=1) of daily FF3 residuals over the signal's calendar month, >= 15 obs; no rf; NaN before 1999-07",
    field_mappings=(
        ("crsp.ret (daily)", "SEP.closeadj (ratio to the previous market-calendar row)",
         "total return, no delisting return; no return across a missing row; 3-decimal closeadj grid"),
        ("ff.mktrf, ff.smb, ff.hml", "MonthContext.ff3_daily: mkt, smb, hml (harness rebuild)",
         "Sharadar-native 2x3 sort (SF1 equity + taxliabilities, DAILY.marketcap, current-TICKERS exchange), "
         "no delisting returns, mkt RAW; not in the field_map index (harness accessor)"),
        ("ff.rf", "omitted (not in the snapshot)",
         "constant within the month, absorbed by the intercept; residual std unchanged"),
        ("ff.smb / ff.hml start", "first complete-factor month is 1999-07",
         "signals before 1999-07-30 are NaN for every name (data-start truncation, ~7 of 276 months)"),
        ("ret.count() >= 15; resid.std()", ">= 15 valid (return, mkt, smb, hml) days; ddof=1 of the residuals",
         "OSAP's rule and estimator; exactly-zero spread set NaN"),
    ),
)
