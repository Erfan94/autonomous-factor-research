"""
MRreversal — medium-run reversal: the stock's compounded return over months
t-18..t-13, skipping the most recent twelve months. Past medium-run losers are
predicted to outperform.

OSAP: MRreversal (Acronym2 Mom1813), De Bondt and Thaler 1985, Journal of Finance
(Figure 2, two-year line). Predicted sign: - (SignalDoc Sign = -1: long LOW past
return, short HIGH).
Spec: osap_source/cache/b4e911e6/MRreversal/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  MRreversal = closeadj at the business month-end 13 months back
               / closeadj at the business month-end 19 months back - 1.
  That is the compound of the six monthly returns of months t-18..t-13 (OSAP
  calendar lags 13..18), read as ONE endpoint ratio of the total-return price
  SEP.closeadj (splits and dividends): six returns, seven closes. Both endpoints
  via ctx.at_month_end("SEP", ["closeadj"], m): the last trade on or before the
  business month-end, 7-day tolerance (the harness history-gate rule).
  closeadj must be > 0 at both ends, else NaN. The window is disjoint from a
  12-1 momentum window (t-12..t-1); no return month is shared.
  history_months=19, lookback_months=19.
  Raw return, no winsorising. ascending=False: a LOW past return is the long leg.

PARTIAL WINDOWS (declared, coordinator decision momentum_partial_windows): BOTH
  endpoints are required. OSAP zero-fills a missing monthly return and scores any
  name with at least one of the six returns present (a window that starts after
  t-19 is scored on the months that exist); that partial-window scoring is NOT
  reproduced. A name with a close at t-13 but none at t-19 is NaN here.

DATA-START TRUNCATION: SEP closeadj starts 1997-12-31, so a close 19 months
before the signal exists from the 1999-07-30 signal. The first 7 decision months
(1998-12 .. 1999-06) are null for every name by construction. Preflight's
data-start warning on the first probe month is this block, not a construction
error.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no price change
  over the six-month window); a continuous return with no default value and no
  zero-fill of the signal.
  What share of the universe does nothing? The spec measured the exactly-0.0
  share at a mean of 0.07% (max 0.67%), modal share of any value at most 0.67%,
  at least 1,658 distinct values, and no qcut(10) collapse. Preflight to confirm.
  Tie handling: none needed and nothing removed or floored; the harness average
  rank covers the few exact ties. The only guard is a positive closeadj at both
  ends (null otherwise, so blend_ranks renormalises).

DEVIATIONS FROM OSAP:
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    endpoint ratio; no delisting return in the window (SEP ends at the last
    trade).
  - Partial windows not scored: both endpoints required (see PARTIAL WINDOWS).
    The spec measured names with a t-13 close but no t-19 close at 1.9% of the
    universe on average (max 5.6%).
  - A missing close is NaN here; OSAP zero-fills a NaN ret inside an existing row.
  - Business month-end with a 7-day tolerance, not OSAP's row-based merge lags.
  - OSAP's test is equal-weighted with a 0.2-quantile long-short; the harness
    ranks, equal-weighted deciles.
  - First 7 decision months null (see DATA-START TRUNCATION).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    p13 = ctx.at_month_end("SEP", ["closeadj"], 13)["closeadj"].astype(float).reindex(ctx.ids)
    p19 = ctx.at_month_end("SEP", ["closeadj"], 19)["closeadj"].astype(float).reindex(ctx.ids)
    out = p13.where(p13 > 0) / p19.where(p19 > 0) - 1.0      # both endpoints required
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MRreversal",
    col="f_mrreversal",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: past medium-run losers earn more; long LOW
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MRreversal",
    source="De Bondt and Thaler 1985 (Journal of Finance)",
    lookback_months=19,
    history_months=19,              # return window t-18..t-13 reaches 19 month-ends back
    notes="closeadj[t-13]/closeadj[t-19]-1: return over months t-18..t-13; both endpoints required; sign -1; first scorable signal 1999-07",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), compounded lags 13..18",
         "SEP.closeadj[t-13] / SEP.closeadj[t-19] - 1",
         "month-end endpoint ratio, total return; no delisting return; NaN where an endpoint is missing"),
        ("ret.fillna(0); score if >= 1 of 6 lags present", "both endpoints required",
         "OSAP partial-window scoring not reproduced (coordinator decision momentum_partial_windows); names with t-13 but no t-19 close are NaN"),
        ("calendar merge lags", "ctx.at_month_end(..., m), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("Stock Weight EW, LS quantile 0.2 (paper)", "harness equal-weighted deciles", "harness owns weighting"),
        ("coverage start", "first valid signal 1999-07-30",
         "t-19 = 1997-12-31 is the first SEP row; 7 leading decision months (1998-12 .. 1999-06) are empty"),
    ),
)
