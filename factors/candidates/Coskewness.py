"""
Coskewness — coskewness of a stock's monthly return with the market over the
past 60 months, E[r~ m~^2] / (SD[r~] * SD[m~]^2); a stock that adds negative
skewness to the market is a risk the market pays for, so HIGH coskewness is
predicted to earn LOWER returns.

OSAP: Coskewness, Harvey and Siddique 2000, Journal of Finance (in text
p 1276). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/Coskewness/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  r_k = closeadj at business month-end k / closeadj at k-1, minus 1, for the
        60 months ending at the signal month (ctx.monthly_closeadj(60): 61
        month-ends -> 60 simple returns; a missing close nulls both adjacent
        months, nothing is chained across a gap).
  m_k = ctx.monthly_market(60, col="vw"): the cap-weighted market's monthly
        return compounded from the guarded daily series, same month spans as
        r_k, aligned by month-end label. Raw, not excess.
  Over the months where both are finite (n of them), n >= 12:
      r~ = r - mean(r);  m~ = m - mean(m)        (means over the SAME months)
      Coskewness = mean(r~ * m~^2) / ( sqrt(mean(r~^2)) * mean(m~^2) )
  population (1/n) moments. Non-finite result (mean(r~^2) == 0 or
  mean(m~^2) == 0) -> NaN. The window includes the signal month. Price-only:
  no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A window with zero return
  variance gives 0/0: undefined, not a value. Everything else is a continuous
  ratio of sample moments.
  What share of the universe does nothing? ~0%: the monthly zero-return share
  of universe stock-months is 0.24-0.68% and no name has an all-zero window
  at the probes; preflight decides.
  Tie handling: null. Zero-variance windows are NaN and blend_ranks
  renormalises. No noise or secondary key.

DEVIATIONS FROM OSAP:
  - rf omitted (the snapshot holds no risk-free rate). OSAP uses r - rf and
    de-means; rf is NOT constant over a 60-month window (about 5%/yr in
    1999-2000 to ~0 in 2009-2015), so de-meaning does not cancel it. The
    resulting difference is small against ~10% stock and ~4.5% market monthly
    vol but is not zero, and is not measured here.
  - mktrf: ctx.monthly_market raw value-weighted series (common stock on
    NYSE/NASDAQ/NYSEMKT per current TICKERS, no size screen, no delisting
    returns, gap returns and >+100% / <-80% daily prints excluded) replaces
    Ken French's Mkt-RF.
  - ret: SEP closeadj month-end ratio (total return, no delisting return)
    replaces CRSP ret.
  - window: 60 calendar months with n >= 12 valid pairs, where OSAP uses the
    stock's own last 60 rows.
  - early window: monthly_market is blank for 1998-12 (series stub), so the
    first 12 paired months exist at the 1999-12 signal: signals 1999-01 ..
    1999-11 are NaN for every name (about 4% of months); windows hold 12-59
    months until 2003-12.
  - the SignalDoc's VW tercile portfolio is superseded by the harness
    universe and decile sort.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 60
_MIN_OBS = 12


def _compute(ctx):
    px = ctx.monthly_closeadj(_WINDOW).astype(float)           # IDs x (<=61) month-ends
    mkt = ctx.monthly_market(_WINDOW, col="vw").astype(float)  # 60 month-ends, RAW VW

    cols = list(px.columns)
    if len(cols) < 2:
        return pd.Series(np.nan, index=px.index)
    prev = px.iloc[:, :-1].to_numpy()
    cur = px.iloc[:, 1:].to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(prev > 0, cur / prev - 1.0, np.nan)       # NaN on either close missing
    m = mkt.reindex(pd.DatetimeIndex(cols[1:])).to_numpy()     # label-aligned month spans

    ok = np.isfinite(r) & np.isfinite(m)[None, :]
    n = ok.sum(axis=1).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rbar = np.where(ok, r, 0.0).sum(axis=1) / n
        mbar = np.where(ok, m[None, :], 0.0).sum(axis=1) / n
        rt = np.where(ok, r - rbar[:, None], 0.0)
        mt = np.where(ok, m[None, :] - mbar[:, None], 0.0)
        cos = (rt * mt ** 2).sum(axis=1) / n
        var_r = (rt ** 2).sum(axis=1) / n
        var_m = (mt ** 2).sum(axis=1) / n
        val = cos / (np.sqrt(var_r) * var_m)
    valid = (n >= _MIN_OBS) & (var_r > 0) & (var_m > 0) & np.isfinite(val)
    val = np.where(valid, val, np.nan)
    return pd.Series(val, index=px.index)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Coskewness",
    col="f_coskewness",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW coskewness is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="Coskewness",
    source="Harvey and Siddique 2000 (Journal of Finance)",
    lookback_months=60,             # 60-month window (61 month-end closes)
    history_months=12,              # OSAP minimum: 12 monthly returns (not 60)
    notes="E[r~ m~^2]/(SD[r~] SD[m~]^2) on monthly returns vs raw VW market, 60m window, >= 12 pairs; no rf",
    field_mappings=(
        ("crsp.ret (monthly)", "SEP.closeadj (month-end ratio via monthly_closeadj)",
         "total return from adjacent business month-ends; no delisting return"),
        ("ff.mktrf", "MonthContext.monthly_market(col='vw') from SEP + DAILY.marketcap",
         "harness raw VW market, not Mkt-RF; blank 1998-12 so first scorable signal 1999-12"),
        ("ff.rf", "omitted (not in the snapshot)",
         "NOT constant over 60 months, so it does not cancel under de-meaning; small unmeasured deviation"),
        ("window", "60 calendar months, n >= 12 finite pairs",
         "OSAP uses the stock's last 60 rows; zero-variance windows -> NaN"),
    ),
)
