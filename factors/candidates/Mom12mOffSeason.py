"""
Mom12mOffSeason — momentum without the seasonal part: the arithmetic average
of the ten monthly returns of months t-10..t-1. Past winners over the
non-annual months are predicted to keep outperforming.

OSAP: Mom12mOffSeason, Heston and Sadka 2008, Journal of Financial Economics
(Table 2 Year 1 Nonannual). Predicted sign: + (SignalDoc Sign = +1; long HIGH).
Spec: osap_source/cache/b4e911e6/Mom12mOffSeason/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ret_k = closeadj at the business month-end k months before the signal
          / closeadj at the business month-end k+1 months before the signal - 1,
  for k = 1..10 (eleven month-end closes, lags 1..11 of the total-return price
  SEP.closeadj). Mom12mOffSeason = the ARITHMETIC MEAN of the ten ret_k (not a
  compounded return, not an endpoint ratio). The "exclude the same calendar
  month" clause of the OSAP code is vacuous here (lag 11 is outside
  range(1, 11)), so every lag 1..10 is kept; month t (lag 0) is skipped.
  All closes via ctx.at_month_ends("SEP", ["closeadj"], range(1, 12)): last
  trade on or before each business month-end, 7-day tolerance. A return is
  built only between consecutive month-ends and is NaN if either close is
  missing or not > 0. The score is NaN unless all ten returns exist.
  history_months=11, lookback_months=11.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1). This window
  (t-10..t-1) is the same window minus month t-11, as an arithmetic mean
  instead of a compound. The spec's measured cross-sectional Spearman with
  the 12-1 value on the harness universe over 276 months: median 0.92, mean
  0.91, p10/p90 0.84/0.95, min 0.55.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (ten zero
  returns). It is a continuous mean with no default and no signal zero-fill.
  What share of the universe does nothing? Spec measured a modal share of the
  scored cross-section of at most 0.12% (median 0.05%); distinct values equal
  the number scored. Preflight to confirm.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end of every return (null otherwise, so blend_ranks
  renormalises).

DEVIATIONS FROM OSAP:
  - PARTIAL WINDOWS ARE NOT SCORED. OSAP's pandas mean(axis=1) skips NaN, so a
    firm with only a few prior rows is scored from the returns it has. Here
    history_months equals the full window (11) and the score needs all ten
    returns; names with part of the window are NaN (spec: about 59 names a
    month, 2.8% of scored names, on the harness universe). A declared
    coordinator decision (events.jsonl id momentum_partial_windows).
  - A missing interior close makes that month's return NaN, and so the score
    NaN; OSAP zero-fills a missing month inside a firm's life.
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    month-end ratios; no delisting return in the window.
  - Calendar business month-ends with a 7-day tolerance, not row-based lags.
  - OSAP's paper sort is on NYSE/AMEX; the harness universe is its own.
  - No data-start loss: the first decision month (1999-01, signal
    1998-12-31) reaches 1998-01-30.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    d = ctx.at_month_ends("SEP", ["closeadj"], range(1, 12))
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(index=ctx.ids, columns=list(range(1, 12)))
    px = px.where(px > 0)
    # ret_k = close(t-k) / close(t-k-1) - 1, only between consecutive month-ends
    rets = pd.concat(
        {k: px[k] / px[k + 1] - 1.0 for k in range(1, 11)}, axis=1
    ).replace([np.inf, -np.inf], np.nan)
    return rets.mean(axis=1, skipna=False)      # NaN unless all ten returns exist


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Mom12mOffSeason",
    col="f_mom12moffseason",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="Mom12mOffSeason",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=11,
    history_months=11,              # ten returns need closes 11 month-ends back
    notes="mean of ten monthly returns t-10..t-1 (arithmetic, not compounded); full window required; sign +1",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), mean of lags 1..10",
         "mean of SEP.closeadj[t-k]/SEP.closeadj[t-k-1] - 1, k = 1..10",
         "total-return month-end ratios; no delisting return; NaN interior close -> NaN (OSAP zero-fills inside a firm's life)"),
        ("pandas mean(axis=1), skipna (partial windows scored)", "all ten returns required",
         "history_months=11 and skipna=False: names with part of the window are NaN (OSAP would score them)"),
        ("calendar-month lag merge", "ctx.at_month_ends(..., 1..11), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
