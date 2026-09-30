"""
MomOffSeason06YrPlus — off-season long-term reversal, years 6-10: the
arithmetic average of the monthly returns at lags 60..118 excluding the same
calendar month as the predicted month. A high average return over years 6-10
(off-season months) is predicted to be followed by low returns.

OSAP: MomOffSeason06YrPlus, Heston and Sadka 2008, Journal of Financial
Economics (Table 2 Years 6-10 Nonannual). Predicted sign: - (SignalDoc
Sign = -1: LOW off-season average return is the long leg), so ascending=False.
Spec: osap_source/cache/b4e911e6/MomOffSeason06YrPlus/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ret_k = closeadj at the business month-end k months before the signal
          / closeadj at the business month-end k+1 months before the signal - 1,
  for the 55 lags k in 60..118 excluding 71, 83, 95 and 107 (the same calendar
  month as the predicted month t+1; lag 119 would also be one, and lies outside
  the range; lag 59 is in the previous year block and is outside the range).
  The 55 returns use closes at the business month-ends t-60 .. t-119 of the
  total-return price SEP.closeadj.
  MomOffSeason06YrPlus = the ARITHMETIC MEAN of the 55 ret_k. Closes via
  ctx.at_month_ends("SEP", ["closeadj"], range(60, 120)): last trade on or
  before each business month-end, 7-day tolerance. A return is built only
  between consecutive month-ends and is NaN if either close is missing or not
  > 0. The score is NaN unless all 55 returns exist.
  history_months=119, lookback_months=119.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1); the two
  windows are disjoint (lags 60..118 versus 1..11). The spec's measured
  cross-sectional Spearman with the 12-1 value over the 169 scorable months:
  median -0.03, mean -0.03, p10/p90 -0.14/0.08, min -0.19, max 0.18.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (55 zero
  returns). It is a continuous mean with no default and no signal zero-fill.
  What share of the universe does nothing? Spec measured a modal share of the
  scored cross-section of at most 0.081% (median 0.076%); distinct values equal
  the number scored. Preflight to confirm.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end of every return (null otherwise, so blend_ranks
  renormalises).

DEVIATIONS FROM OSAP:
  - DATA-START TRUNCATION. The deepest close is BME(t-119); SEP starts
    1997-12-31, so the first full-window signal is 2007-11-30, decision month
    2007-12. The 107 decision months 1999-01 .. 2007-11 are null by
    construction; 2007-12 .. 2021-12 (169 of 276 months) are scorable. Because
    coverage is pooled over all 276 months, the spec's recomputed pooled
    coverage is about 40.6% (59.0%-74.7% of the universe within the scorable
    months), against the Stage 1 coverage bar of 40%. Preflight's data-start
    warning at the first probe month is this block, not a construction error.
  - PARTIAL WINDOWS ARE NOT SCORED. OSAP's pandas mean(axis=1) skips NaN, so a
    firm with any one lag is scored. Here history_months equals the full window
    (119) and the score needs all 55 returns; names with under ten years of
    history are NaN (OSAP would score them). A declared coordinator decision
    (events.jsonl id momentum_partial_windows).
  - A missing interior close makes that month's return NaN, and so the score
    NaN; OSAP zero-fills a missing month inside a firm's life.
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    month-end ratios; no delisting return in the window.
  - Calendar business month-ends with a 7-day tolerance, not row-based lags.
  - OSAP's paper sort is on NYSE/AMEX; the harness universe is its own.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

# lags 60..118 excluding the same calendar month as the predicted month (71, 83, 95, 107)
_LAGS = [k for k in range(60, 119) if (k + 1) % 12 != 0]


def _compute(ctx):
    d = ctx.at_month_ends("SEP", ["closeadj"], range(60, 120))
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(index=ctx.ids, columns=list(range(60, 120)))
    px = px.where(px > 0)
    # ret_k = close(t-k) / close(t-k-1) - 1, only between consecutive month-ends
    rets = pd.concat(
        {k: px[k] / px[k + 1] - 1.0 for k in _LAGS}, axis=1
    ).replace([np.inf, -np.inf], np.nan)
    return rets.mean(axis=1, skipna=False)      # NaN unless all 55 returns exist


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MomOffSeason06YrPlus",
    col="f_momoffseason06yrplus",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW off-season average return is the long leg
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MomOffSeason06YrPlus",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=119,
    history_months=119,             # 55 returns need closes back to the month-end 119 months ago
    notes="mean of 55 monthly returns at lags 60..118 excl. 71/83/95/107; full window required; sign -1; first scorable 2007-12 (169 of 276 months)",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), mean of lags 60..118 excl. 71, 83, 95, 107",
         "mean of SEP.closeadj[t-k]/SEP.closeadj[t-k-1] - 1 over those 55 lags",
         "total-return month-end ratios; no delisting return; NaN interior close -> NaN (OSAP zero-fills inside a firm's life)"),
        ("pandas mean(axis=1), skipna (partial windows scored)", "all 55 returns required",
         "history_months=119 and skipna=False: names with under ten years of history are NaN (OSAP would score them)"),
        ("calendar-month lag merge", "ctx.at_month_ends(..., 60..119), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("coverage start", "first valid signal 2007-11-30 (decision month 2007-12)",
         "SEP starts 1997-12-31; the 107 leading decision months are null by construction; pooled coverage over all 276 months about 40.6%"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
