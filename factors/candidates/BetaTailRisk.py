"""
BetaTailRisk — tail-risk beta: the slope of a stock's monthly return on the
market-wide monthly tail-risk series (tailex) over a trailing 120-month
window; stocks that load positively on tail events are predicted to earn a
risk premium.

OSAP: BetaTailRisk, Kelly and Jiang 2014, Review of Financial Studies (Table
4A EW). Predicted sign: + (SignalDoc Sign = 1: high BetaTailRisk is the long
side).
Spec: osap_source/cache/b4e911e6/BetaTailRisk/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  r_k    = SEP.closeadj at business month-end k / closeadj at k-1, minus 1,
           over the 120 months ending at the signal month
           (ctx.monthly_closeadj(120): 121 month-ends -> 120 returns; a
           missing close nulls both adjacent months, nothing is chained
           across a gap).
  tx_k   = ctx.monthly_tailex(120): the harness-built monthly Kelly-Jiang
           tailex (mean log(r / p5) over the pooled daily returns at or below
           the month's 5th percentile), same month labels as r_k. The signal
           month is included (month-t return and month-t tailex are both
           known at the signal date, as in OSAP).
  Signal = OLS slope of r on tx WITH intercept (cov(r, tx) / var(tx)) over the
           months where both are finite, required n >= 72 pairs. The slope is
           NaN below 72 pairs, and when var(tx) or var(r) over the pairs is
           not > 0. Never floored.
  Sample start: tailex exists from 1998-01 (72 valid months at 2003-12), so
  the first scorable signal month is 2003-12 and decision months 1999-01 ..
  2003-11 are data-null by construction; about 79% of universe members hold
  >= 72 valid monthly returns at 2003-12. The regression window is 72-119
  months until 2007-12. A data fact, not a factor fault.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 only for a name
  whose monthly returns are all exactly zero over its paired window (a stale,
  never-moving close). Otherwise the OLS slope is continuous.
  What share of the universe does nothing? ~0%: a 72+ month run of zero
  returns does not occur in a universe screened on price >= $1, market cap
  and dollar volume; not measured here, preflight decides.
  Tie handling: null. A zero-return-variance window is set NaN (its slope is
  an artefact of a flat price, not a measured sensitivity) and blend_ranks
  renormalises. Names with < 72 valid pairs are NaN for the same reason.

HISTORY: history_months = 72, the OSAP min_periods (a name needs 72 valid
  monthly returns, not a full 120-month window). The harness gate
  has_price_at(72) requires a trade at BME(t-72), consistent with >= 72
  returns in the window. A gate at 120 would push the first signal to 2008
  and is deliberately not used; the n >= 72 pair count inside _compute is the
  binding requirement. lookback_months = 120 (the window).

DEVIATIONS FROM OSAP:
  - tailex: the harness series (pool = common stock on NYSE/NASDAQ/NYSEMKT,
    not all of CRSP; daily r < -80% bad-print guard; zero-volume days dropped
    with the next traded day's two-day return kept; no delisting returns)
    replaces OSAP's tailex from all CRSP daily returns. The 120-month /
    72-pair regression on monthly returns is rank-robust to these.
  - ret: SEP closeadj month-end ratio (total return, splits and dividends,
    no delisting return) replaces CRSP ret with dlret.
  - window: 120 calendar months with n >= 72 finite pairs, where OSAP uses
    the last 120 rows of the stock's own history (a listing gap reaches
    further back in OSAP).
  - shrcd <= 11 and the SignalDoc price > 5 screen: not in the factor; the
    harness universe decides (price >= $1, US common). The price > 5 screen
    is not reproduced.
  - var(r) == 0 names are set NaN (OSAP would emit 0.0).
  - tailex has no field_map key (harness-built series, read through the
    MonthContext accessor).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 120
_MIN_OBS = 72


def _compute(ctx):
    px = ctx.monthly_closeadj(_WINDOW).astype(float)      # IDs x (<=121) month-ends
    tx = ctx.monthly_tailex(_WINDOW).astype(float)        # month-end indexed Series

    cols = list(px.columns)
    if len(cols) < 2:
        return pd.Series(np.nan, index=px.index)
    prev = px.iloc[:, :-1].to_numpy()
    cur = px.iloc[:, 1:].to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where((prev > 0) & (cur > 0), cur / prev - 1.0, np.nan)  # NaN on either close missing or <= 0
    t = tx.reindex(pd.DatetimeIndex(cols[1:])).to_numpy()  # label-aligned month spans

    ok = np.isfinite(r) & np.isfinite(t)[None, :]
    n = ok.sum(axis=1).astype(float)
    r0 = np.where(ok, r, 0.0)
    t0 = np.where(ok, t[None, :], 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        rbar = r0.sum(axis=1) / n
        tbar = t0.sum(axis=1) / n
        dr = np.where(ok, r - rbar[:, None], 0.0)
        dt = np.where(ok, t[None, :] - tbar[:, None], 0.0)
        var_t = (dt * dt).sum(axis=1)
        var_r = (dr * dr).sum(axis=1)
        cov = (dr * dt).sum(axis=1)
        slope = cov / var_t
    valid = (n >= _MIN_OBS) & (var_t > 0) & (var_r > 0)
    slope = np.where(valid, slope, np.nan)
    return pd.Series(slope, index=px.index)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BetaTailRisk",
    col="f_btr",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high tail-risk beta predicts high returns
    weight=1.0,
    inputs=("SEP.closeadj", "SEP.volume"),
    osap_acronym="BetaTailRisk",
    source="Kelly and Jiang 2014 (Review of Financial Studies)",
    lookback_months=120,            # 120-month regression window (121 month-end closes)
    history_months=72,              # OSAP min_periods: 72 valid monthly returns
    notes="OLS slope of monthly return on harness tailex, 120m window, >= 72 pairs; first signal 2003-12",
    field_mappings=(
        ("crsp.ret (monthly)", "SEP.closeadj (month-end ratio via monthly_closeadj)",
         "total return from adjacent business month-ends; no delisting return"),
        ("TailRisk.tailex", "MonthContext.monthly_tailex(120) from SEP.closeadj, SEP.volume",
         "listed-exchange common-stock pool, r < -80% guard, zero-volume days dropped, no dlret; "
         "no field_map key (harness-built series); valid from 1998-01, so first scorable signal 2003-12"),
        ("rolling_ols window 120 rows, min 72", "120 calendar months, n >= 72 finite pairs, intercept fitted",
         "OSAP windows by the stock's own rows; var(r)==0 names set NaN"),
        ("crsp.shrcd <= 11; SignalDoc price > 5", "harness universe",
         "price > 5 screen not reproduced"),
    ),
)
