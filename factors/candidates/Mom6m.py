"""
Mom6m — six-month momentum: the return over the five monthly returns of
months t-5..t-1, skipping the current month. Past winners are predicted to
keep outperforming.

OSAP: Mom6m, Jegadeesh and Titman 1993, Journal of Finance (Table 1A K=3 row 6).
Predicted sign: + (SignalDoc Sign = +1: high past return, high future return;
long HIGH).
Spec: osap_source/cache/b4e911e6/Mom6m/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Mom6m = closeadj at the business month-end 1 month before the signal
          / closeadj at the business month-end 6 months before the signal - 1.
  Five monthly returns (months t-5..t-1), six closes; the product of the
  month-end-to-month-end returns equals the endpoint ratio of the total-return
  price SEP.closeadj (splits and dividends). Despite the name it is five
  months, as in OSAP's code (lags 1..5). Month t is not used. Both endpoints
  via ctx.at_month_ends("SEP", ["closeadj"], [1, 6]): the last trade on or
  before the business month-end, 7-day tolerance (the harness history-gate
  rule). closeadj must be > 0 at both ends, else NaN.
  history_months=6, lookback_months=6 (the gate nulls names with no price
  near the month-end 6 months back). No winsorising here (harness owns it).

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1). Mom6m's
  window t-5..t-1 lies entirely inside it (five of its eleven months). The
  spec's measured cross-sectional Spearman between the two on the harness
  universe over 276 months: median 0.64, mean 0.63, p10/p90 0.50/0.76,
  min 0.02.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no price change
  over five months gives a ratio of 1). There is no default value and no
  signal zero-fill.
  What share of the universe does nothing? Spec measured a modal share of the
  scored cross-section of at most 0.35% (median 0.11%), at least 1,712
  distinct values. Preflight to confirm.
  Tie handling: none needed, nothing removed or floored; the harness average
  rank covers the few exact ties. The only guard is a positive closeadj at
  both ends (null otherwise, so blend_ranks renormalises).

DEVIATIONS FROM OSAP:
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    endpoint ratio. No delisting return in the window (SEP ends at the last
    trade).
  - A missing close at either endpoint is NaN; OSAP zero-fills a NaN ret
    inside an existing row and NaNs a missing calendar row. Interior months
    are not read, so a missing interior close does not matter here, whereas
    OSAP's compounded lags give NaN when an interior calendar month is missing.
  - Calendar business month-ends with a 7-day tolerance, not OSAP's row-based
    lags.
  - OSAP's paper portfolio period is 3 months; the harness holds one month.
  - No data-start loss: SEP starts 1997-12-31, the first decision month
    (1999-01, signal 1998-12-31) reaches 1998-06-30.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    d = ctx.at_month_ends("SEP", ["closeadj"], [1, 6])
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(ctx.ids)
    if 1 not in px.columns or 6 not in px.columns:
        return pd.Series(np.nan, index=ctx.ids)
    p_end, p_start = px[1], px[6]
    out = p_end.where(p_end > 0) / p_start.where(p_start > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Mom6m",
    col="f_mom6m",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: past winners are attractive
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="Mom6m",
    source="Jegadeesh and Titman 1993 (Journal of Finance)",
    lookback_months=6,
    history_months=6,               # return window t-5..t-1 reaches 6 month-ends back
    notes="closeadj[t-1]/closeadj[t-6]-1: five monthly returns t-5..t-1; sign +1",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), compounded lags 1..5",
         "SEP.closeadj[t-1] / SEP.closeadj[t-6] - 1",
         "month-end endpoint ratio, total return; no delisting return; NaN where an endpoint is missing (OSAP zero-fills a NaN ret inside an existing row)"),
        ("calendar-month lag merge", "ctx.at_month_ends(..., [1, 6]), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("Portfolio Period 3 (paper)", "harness one-month hold", "harness owns the holding period"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
