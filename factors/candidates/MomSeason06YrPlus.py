"""
MomSeason06YrPlus - seasonal momentum, years 6-10: the arithmetic average of the monthly
returns in the same calendar month as the predicted month t+1, at lags
71, 83, 95, 107, 119. A high average same-month return in the past is predicted to be
followed by a high return in that month.

OSAP: MomSeason06YrPlus, Heston and Sadka 2008, Journal of Financial Economics
(Table 2 "2 Years 6-10 Annual"). Predicted sign: + (SignalDoc Sign = 1: HIGH average
same-month past return is the long leg), so ascending=True.
Spec: osap_source/cache/b4e911e6/MomSeason06YrPlus/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ret_k = closeadj at the business month-end k months before the signal
          / closeadj at the business month-end k+1 months before the signal - 1,
  for the 5 lags k in (71, 83, 95, 107, 119). All are the same calendar month as the predicted
  month t+1. The 5 returns use closes at business month-ends
  t-71 .. t-120 of the total-return price SEP.closeadj (deepest close
  t-120). MomSeason06YrPlus = the ARITHMETIC MEAN of the 5 ret_k. Closes via
  ctx.at_month_ends("SEP", ["closeadj"], [71, 72, 83, 84, 95, 96, 107, 108, 119, 120]): last trade on or before each
  business month-end, 7-day tolerance. A return is built only between
  consecutive month-ends and is NaN if either close is missing or not > 0.
  The score is NaN unless all 5 returns exist.
  history_months=120, lookback_months=120.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1); the windows
  are disjoint (lags 71..119 versus 1..11). The spec's measured cross-sectional
  Spearman with the 12-1 value over the 168 scorable months: median -0.015,
  mean -0.015, p10/p90 -0.106/0.089, min/max -0.227/0.205.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (5 zero
  returns). It is a continuous mean with no default and no signal zero-fill.
  The mean is over only 5 returns, so the distribution is heavy-tailed (one
  extreme month moves a name a lot; the harness winsorises before ranking) and
  ties arise only from coincidences between a couple of names.
  What share of the universe does nothing? Spec measured a modal share of at most 0.081% (median 0.077%, i.e. one name); distinct values equal the number scored in all 168 months; no exact zero in any month; qcut gives 10 bins in every month.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end of every return (null otherwise, so blend_ranks
  renormalises). Preflight to confirm.

DEVIATIONS FROM OSAP:
  - DATA-START TRUNCATION. The deepest close is BME(t-120); SEP starts
    1997-12-31, so the first full-window signal is 2007-12-31, decision month
    2008-01. The 108 leading decision months (from 1999-01) are null by
    construction; 2008-01 .. 2021-12 (168 months) are scorable.
    Preflight's data-start warning at the first probe month (1998-12) is
    this block, not a construction error.
  - PARTIAL WINDOWS ARE NOT SCORED. OSAP's rowtotal / rownonmiss mean skips
    missing lags, so a firm with one lag available is scored from that lag
    alone. Here history_months equals the full window (120) and the score
    needs all 5 returns; names with part of the window are NaN (spec: a mean
    12.9% of the any-lag scored set). Coverage is 58.8%-74.4% of the universe
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

_LAGS = [71, 83, 95, 107, 119]


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
    return rets.mean(axis=1, skipna=False)      # NaN unless all 5 returns exist


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MomSeason06YrPlus",
    col="f_momseason06yrplus",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH average same-month past return is the long leg
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MomSeason06YrPlus",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=120,
    history_months=120,              # 5 returns need closes back to the month-end 120 months ago
    notes="mean of 5 same-calendar-month returns at lags 71, 83, 95, 107, 119; full window required; sign +1; first scorable 2008-01",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), mean of lags 71, 83, 95, 107, 119",
         "mean of SEP.closeadj[t-k]/SEP.closeadj[t-k-1] - 1 over those 5 lags",
         "total-return month-end ratios; no delisting return; NaN close -> NaN (OSAP fills a NaN ret with 0 on an existing row)"),
        ("rowtotal / rownonmiss (partial windows scored)", "all 5 returns required",
         "history_months=120 and skipna=False: names without the full window are NaN (OSAP would score them)"),
        ("calendar-month lag merge", "ctx.at_month_ends(... 71, 72, 83, 84, 95, 96, 107, 108, 119, 120), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("coverage start", "first valid signal 2007-12-31 (decision month 2008-01)",
         "SEP starts 1997-12-31; the 108 leading decision months are null by construction"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
