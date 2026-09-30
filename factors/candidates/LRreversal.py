"""
LRreversal — long-run reversal: the stock's compounded return over months
t-36..t-13, skipping the most recent twelve months. Past three-year losers are
predicted to outperform.

OSAP: LRreversal (Acronym2 Mom36m), De Bondt and Thaler 1985, Journal of Finance
(Table 1 three-year). Predicted sign: - (SignalDoc Sign = -1: long LOW past
return, short HIGH).
Spec: osap_source/cache/b4e911e6/LRreversal/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  LRreversal = closeadj at the business month-end 13 months back
               / closeadj at the business month-end 37 months back - 1.
  That is the compound of the 24 monthly returns of months t-36..t-13 (OSAP
  calendar lags 13..36), read as ONE endpoint ratio of the total-return price
  SEP.closeadj (splits and dividends): 24 returns, 25 closes. Both endpoints via
  ctx.at_month_end("SEP", ["closeadj"], m): the last trade on or before the
  business month-end, 7-day tolerance (the harness history-gate rule).
  closeadj must be > 0 at both ends, else NaN. The window is disjoint from a
  12-1 momentum window (t-12..t-1); no return month is shared.
  history_months=37, lookback_months=37.
  Raw return, no winsorising. ascending=False: a LOW past return is the long leg.

DATA-START TRUNCATION: SEP closeadj starts 1997-12-31, so a close 37 months
before the signal exists from the 2001-01-31 signal. The first 25 decision months
(1998-12 .. 2000-12) are null for every name by construction; the first scorable
signal is 2001-01. Preflight's data-start warning on the first probe month is
this block, not a construction error.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no price change
  over the 24-month window); a continuous return with no default value and no
  zero-fill of the signal.
  What share of the universe does nothing? The spec measured a modal share of the
  scored cross-section of at most 0.21% (distinct values at least 1,581 of up to
  1,898 scored) and no qcut(10) collapse. Preflight to confirm.
  Tie handling: none needed and nothing removed or floored; the harness average
  rank covers the few exact ties. The only guard is a positive closeadj at both
  ends (null otherwise, so blend_ranks renormalises).

DEVIATIONS FROM OSAP:
  - crsp.ret (monthly total return incl. delisting return, dlret or -0.35/-0.55
    for performance delistings) -> SEP closeadj endpoint ratio; no delisting
    return in the past-return window (SEP ends at the last trade).
  - A missing close is NaN here; OSAP zero-fills a NaN ret inside an existing row
    and gives NaN for a missing row (spec: no scored name is affected).
  - Business month-end with a 7-day tolerance, not OSAP's row-based shift(i).
  - OSAP's test is equal-weighted; the harness ranks, equal-weighted deciles.
  - First 25 decision months null (see DATA-START TRUNCATION).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    p13 = ctx.at_month_end("SEP", ["closeadj"], 13)["closeadj"].astype(float).reindex(ctx.ids)
    p37 = ctx.at_month_end("SEP", ["closeadj"], 37)["closeadj"].astype(float).reindex(ctx.ids)
    out = p13.where(p13 > 0) / p37.where(p37 > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="LRreversal",
    col="f_lrreversal",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: past three-year losers earn more; long LOW
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="LRreversal",
    source="De Bondt and Thaler 1985 (Journal of Finance)",
    lookback_months=37,
    history_months=37,              # return window t-36..t-13 reaches 37 month-ends back
    notes="closeadj[t-13]/closeadj[t-37]-1: return over months t-36..t-13; sign -1; first scorable signal 2001-01",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), compounded lags 13..36",
         "SEP.closeadj[t-13] / SEP.closeadj[t-37] - 1",
         "month-end endpoint ratio, total return; no delisting return; NaN where an endpoint is missing (OSAP zero-fills a NaN ret inside an existing row)"),
        ("row-based shift(i) lags", "ctx.at_month_end(..., m), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("Stock Weight EW (paper)", "harness equal-weighted deciles", "harness owns weighting"),
        ("coverage start", "first valid signal 2001-01-31",
         "t-37 = 1997-12-31 is the first SEP row; 25 leading decision months (1998-12 .. 2000-12) are empty"),
    ),
)
