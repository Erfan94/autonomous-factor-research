"""
MomOffSeason — off-season long-term reversal: the arithmetic average of the
monthly returns at lags 12..58 excluding the same calendar month as the
predicted month. A high average return over years 2-5 (off-season months) is
predicted to be followed by low returns.

OSAP: MomOffSeason, Heston and Sadka 2008, Journal of Financial Economics
(Table 2 Years 2-5 Nonannual). Predicted sign: - (SignalDoc Sign = -1: LOW
off-season average return is the long leg).
Spec: osap_source/cache/b4e911e6/MomOffSeason/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ret_k = closeadj at the business month-end k months before the signal
          / closeadj at the business month-end k+1 months before the signal - 1,
  for the 44 lags k in 12..58 excluding 23, 35 and 47 (the same calendar month
  as the predicted month t+1; lag 11 lies in year 1 and is outside the range,
  lag 59 is also dropped as in the OSAP code). The 44 returns use closes at
  the business month-ends t-12 .. t-59 of the total-return price SEP.closeadj.
  MomOffSeason = the ARITHMETIC MEAN of the 44 ret_k. Closes via
  ctx.at_month_ends("SEP", ["closeadj"], range(12, 60)): last trade on or
  before each business month-end, 7-day tolerance. A return is built only
  between consecutive month-ends and is NaN if either close is missing or not
  > 0. The score is NaN unless all 44 returns exist.
  history_months=59, lookback_months=59.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1); the two
  windows are disjoint (lags 12..58 versus 1..11). The spec's measured
  cross-sectional Spearman with the 12-1 value over the 229 scorable months:
  median 0.03, mean 0.01, p10/p90 -0.21/0.17, min -0.47.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (44 zero
  returns). It is a continuous mean with no default and no signal zero-fill.
  What share of the universe does nothing? Spec measured a modal share of the
  scored cross-section of at most 0.13% (median 0.06%); distinct values equal
  the number scored. Preflight to confirm.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end of every return (null otherwise, so blend_ranks
  renormalises).

DEVIATIONS FROM OSAP:
  - DATA-START TRUNCATION. The deepest close is BME(t-59); SEP starts
    1997-12-31, so the first full-window signal is 2002-11-29, decision month
    2002-12. The 47 decision months 1999-01 .. 2002-11 are null by
    construction; 2002-12 .. 2021-12 (229 months) are scorable. Preflight's
    data-start warning at the first probe month (1998-12) is this block, not
    a construction error.
  - PARTIAL WINDOWS ARE NOT SCORED. OSAP's pandas mean(axis=1) skips NaN, so a
    firm listed 14 months ago is scored from lags 12-13 alone. Here
    history_months equals the full window (59) and the score needs all 44
    returns; names with part of the window are NaN (spec: a mean 28% of the
    any-lag scored set). Coverage is therefore 75-88% of the universe
    (spec-measured) against near-complete in OSAP: names with under five
    years of history are dropped. A declared coordinator decision
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

# lags 12..58 excluding the same calendar month as the predicted month (23, 35, 47)
_LAGS = [k for k in range(12, 59) if (k + 1) % 12 != 0]


def _compute(ctx):
    d = ctx.at_month_ends("SEP", ["closeadj"], range(12, 60))
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(index=ctx.ids, columns=list(range(12, 60)))
    px = px.where(px > 0)
    # ret_k = close(t-k) / close(t-k-1) - 1, only between consecutive month-ends
    rets = pd.concat(
        {k: px[k] / px[k + 1] - 1.0 for k in _LAGS}, axis=1
    ).replace([np.inf, -np.inf], np.nan)
    return rets.mean(axis=1, skipna=False)      # NaN unless all 44 returns exist


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MomOffSeason",
    col="f_momoffseason",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW off-season average return is the long leg
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MomOffSeason",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=59,
    history_months=59,              # 44 returns need closes back to the month-end 59 months ago
    notes="mean of 44 monthly returns at lags 12..58 excl. 23/35/47; full window required; sign -1; first scorable 2002-12",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), mean of lags 12..58 excl. 23, 35, 47",
         "mean of SEP.closeadj[t-k]/SEP.closeadj[t-k-1] - 1 over those 44 lags",
         "total-return month-end ratios; no delisting return; NaN interior close -> NaN (OSAP zero-fills inside a firm's life)"),
        ("pandas mean(axis=1), skipna (partial windows scored)", "all 44 returns required",
         "history_months=59 and skipna=False: names with under five years of history are NaN (OSAP would score them)"),
        ("calendar-month lag merge", "ctx.at_month_ends(..., 12..59), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("coverage start", "first valid signal 2002-11-29 (decision month 2002-12)",
         "SEP starts 1997-12-31; the 47 leading decision months are null by construction"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
