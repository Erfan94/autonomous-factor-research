"""
MomSeason - seasonal momentum, years 2-5: the arithmetic average of the monthly
returns in the same calendar month as the predicted month t+1, at lags
23, 35, 47, 59. A high average same-month return in the past is predicted to be
followed by a high return in that month.

OSAP: MomSeason, Heston and Sadka 2008, Journal of Financial Economics
(Table 2 "2 Years 2-5 Annual"). Predicted sign: + (SignalDoc Sign = 1: HIGH average
same-month past return is the long leg), so ascending=True.
Spec: osap_source/cache/b4e911e6/MomSeason/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ret_k = closeadj at the business month-end k months before the signal
          / closeadj at the business month-end k+1 months before the signal - 1,
  for the 4 lags k in (23, 35, 47, 59). All are the same calendar month as the predicted
  month t+1. The 4 returns use closes at business month-ends
  t-23 .. t-60 of the total-return price SEP.closeadj (deepest close
  t-60). MomSeason = the ARITHMETIC MEAN of the 4 ret_k. Closes via
  ctx.at_month_ends("SEP", ["closeadj"], [23, 24, 35, 36, 47, 48, 59, 60]): last trade on or before each
  business month-end, 7-day tolerance. A return is built only between
  consecutive month-ends and is NaN if either close is missing or not > 0.
  The score is NaN unless all 4 returns exist.
  history_months=60, lookback_months=60.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1); the windows
  are disjoint (lags 23..59 versus 1..11). The spec's measured cross-sectional
  Spearman with the 12-1 value over the 228 scorable months: median -0.008,
  mean -0.005, p10/p90 -0.113/0.108, min/max -0.265/0.299. Lags 23, 35 and 47 are exactly the lags the MomOffSeason window excludes, and lag 59 lies outside its 44 lags; the two windows are disjoint.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (4 zero
  returns). It is a continuous mean with no default and no signal zero-fill.
  The mean is over only 4 returns, so the distribution is heavy-tailed (one
  extreme month moves a name a lot; the harness winsorises before ranking) and
  ties arise only from coincidences between a couple of names.
  What share of the universe does nothing? Spec measured a modal share of the scored cross-section of at most 0.132% (median 0.065%, at most 2-3 names); distinct values equal the number scored in 191 of 228 months and fall short by a two-name tie in the other 37; exact zeros occurred once in 228 months (one name-month); qcut gives 10 bins in every month.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end of every return (null otherwise, so blend_ranks
  renormalises). Preflight to confirm.

DEVIATIONS FROM OSAP:
  - DATA-START TRUNCATION. The deepest close is BME(t-60); SEP starts
    1997-12-31, so the first full-window signal is 2002-12-31, decision month
    2003-01. The 48 leading decision months (from 1999-01) are null by
    construction; 2003-01 .. 2021-12 (228 months) are scorable.
    Preflight's data-start warning at the first probe month (1998-12) is
    this block, not a construction error.
  - PARTIAL WINDOWS ARE NOT SCORED. OSAP's rowtotal / rownonmiss mean skips
    missing lags, so a firm with one lag available is scored from that lag
    alone. Here history_months equals the full window (60) and the score
    needs all 4 returns; names with part of the window are NaN (spec: a mean
    10.9% of the any-lag scored set). Coverage is 74.7%-88.3% of the universe
    (spec-measured) against near-complete in OSAP. A declared coordinator
    decision (events.jsonl id momentum_partial_windows).
  - A missing close makes that month's return NaN, and so the score NaN; OSAP
    fills a NaN ret with 0 on an existing row (ret.fillna(0)) and so would
    count it as a zero return.
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    month-end ratios; no delisting return in the window.
  - Calendar business month-ends with a 7-day tolerance, not row-based lags.
  - OSAP's paper sort is on NYSE/AMEX; the harness universe is its own.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_LAGS = [23, 35, 47, 59]


def _compute(ctx):
    months = sorted({m for k in _LAGS for m in (k, k + 1)})
    d = ctx.at_month_ends("SEP", ["closeadj"], months)
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(index=ctx.ids, columns=months)
    px = px.where(px > 0)
    # ret_k = close(t-k) / close(t-k-1) - 1, only between consecutive month-ends
    rets = pd.concat(
        {k: px[k] / px[k + 1] - 1.0 for k in _LAGS}, axis=1
    ).replace([np.inf, -np.inf], np.nan)
    return rets.mean(axis=1, skipna=False)      # NaN unless all 4 returns exist


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MomSeason",
    col="f_momseason",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH average same-month past return is the long leg
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MomSeason",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=60,
    history_months=60,              # 4 returns need closes back to the month-end 60 months ago
    notes="mean of 4 same-calendar-month returns at lags 23, 35, 47, 59; full window required; sign +1; first scorable 2003-01",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), mean of lags 23, 35, 47, 59",
         "mean of SEP.closeadj[t-k]/SEP.closeadj[t-k-1] - 1 over those 4 lags",
         "total-return month-end ratios; no delisting return; NaN close -> NaN (OSAP fills a NaN ret with 0 on an existing row)"),
        ("rowtotal / rownonmiss (partial windows scored)", "all 4 returns required",
         "history_months=60 and skipna=False: names without the full window are NaN (OSAP would score them)"),
        ("calendar-month lag merge", "ctx.at_month_ends(... 23, 24, 35, 36, 47, 48, 59, 60), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("coverage start", "first valid signal 2002-12-31 (decision month 2003-01)",
         "SEP starts 1997-12-31; the 48 leading decision months are null by construction"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
