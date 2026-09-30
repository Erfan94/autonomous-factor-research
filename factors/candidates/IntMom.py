"""
IntMom — intermediate momentum: the stock's return over months t-12..t-7,
skipping the most recent six months. Past winners of the intermediate window
are predicted to keep outperforming.

OSAP: IntMom (Acronym2 Mom12to7), Novy-Marx 2012, Journal of Financial
Economics. Predicted sign: + (SignalDoc Sign = +1: high past intermediate
return, high future return; long HIGH).
Spec: osap_source/cache/b4e911e6/IntMom/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  IntMom = closeadj at the business month-end 7 months back
           / closeadj at the business month-end 13 months back - 1.
  That is the compound of the six monthly returns of months t-12..t-7 (the
  code's calendar lags 7..12), read as ONE endpoint ratio of the
  total-return price SEP.closeadj (splits and dividends). The seven most
  recent monthly returns (months t-6..t) are excluded, so month t's return is not used. Both
  endpoints via ctx.at_month_end("SEP", ["closeadj"], m): the last trade on
  or before the business month-end, 7-day tolerance (the harness history-gate
  rule). closeadj must be > 0 at both ends, else NaN. The SignalDoc wording
  "between t-12 and t-6" is read as the code's lags 7..12, not t-6.
  history_months=13: the harness nulls names with no price near the month-end
  13 months back. lookback_months=13.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0: a stale,
  never-trading price over the 13-month span gives a ratio of 1.
  What share of the universe does nothing? Spec measured an exact-0.0 share
  mean 0.07%, max 0.70%, modal share at most 0.70% (0 months at or above 5%).
  Preflight to confirm.
  Tie handling: none needed and nothing removed or floored; the harness
  average rank covers the few exact ties. The only guard is a positive
  closeadj at both ends (null otherwise, so blend_ranks renormalises).

DEVIATIONS FROM OSAP:
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    endpoint ratio; no delisting return (SEP ends at the last trade).
  - A missing monthly return inside the window is NaN here (endpoint ratio
    exists or not); OSAP zero-fills a NaN ret inside an existing row and gives
    NaN for a missing row. The endpoint ratio is identical to the compounded
    six-return product where both exist (spec measured max diff 1e-15).
  - Business month-end with a 7-day tolerance, not OSAP's calendar-month merge.
  - OSAP's paper sort is value-weighted; the harness ranks, equal-weighted
    deciles.
  - First scorable signal 1999-01-29 (t-13 = 1997-12-31, the first SEP row);
    the 1998-12 decision month is empty by construction.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    p7 = ctx.at_month_end("SEP", ["closeadj"], 7)["closeadj"].astype(float).reindex(ctx.ids)
    p13 = ctx.at_month_end("SEP", ["closeadj"], 13)["closeadj"].astype(float).reindex(ctx.ids)
    out = p7.where(p7 > 0) / p13.where(p13 > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="IntMom",
    col="f_intmom",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high intermediate past return is attractive
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="IntMom",
    source="Novy-Marx 2012 (Journal of Financial Economics)",
    lookback_months=13,
    history_months=13,              # return window t-13..t-7 reaches 13 month-ends back
    notes="closeadj[t-7]/closeadj[t-13]-1: return over months t-12..t-7; sign +1",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), compounded lags 7..12",
         "SEP.closeadj[t-7] / SEP.closeadj[t-13] - 1",
         "month-end endpoint ratio, total return; no delisting return; NaN where an endpoint is missing (OSAP zero-fills a NaN ret inside an existing row)"),
        ("calendar-month lag merge", "ctx.at_month_end(..., m), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("SignalDoc 'months t-12 to t-6'", "lags 7..12 as in the code",
         "the seven most recent monthly returns (t-6..t) are skipped"),
        ("Stock Weight VW (paper)", "harness equal-weighted deciles", "harness owns weighting"),
        ("coverage start", "first valid signal 1999-01-29", "t-13 = 1997-12-31 is the first SEP row; 1998-12 empty"),
    ),
)
