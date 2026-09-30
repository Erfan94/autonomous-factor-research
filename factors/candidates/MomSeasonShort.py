"""
MomSeasonShort — seasonal momentum, year 1: the return in the same calendar
month one year ago (the single monthly return of month t-11). A high return in
the same calendar month last year is predicted to be followed by a high return.

OSAP: MomSeasonShort, Heston and Sadka 2008, Journal of Financial Economics
(Table 2 Year 1 Annual). Predicted sign: + (SignalDoc Sign = +1: HIGH same-month
return last year is the long leg).
Spec: osap_source/cache/b4e911e6/MomSeasonShort/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  score = closeadj at the business month-end t-11 / closeadj at the business
  month-end t-12 - 1, with closes from ctx.at_month_ends("SEP", ["closeadj"],
  [11, 12]) (last trade on or before each business month-end, 7-day
  tolerance). Each close must be > 0; otherwise the score is NaN (null, so
  blend_ranks renormalises). Non-finite -> NaN.
  history_months=12, lookback_months=12.

OVERLAP WITH THE v0 MOMENTUM LEG (stated from the spec, no verdict): the v0
  leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11..t-1). This signal
  is exactly the OLDEST month of that window (nested, not disjoint). The spec's
  measured cross-sectional Spearman with the 12-1 value over 276 months:
  median 0.285, mean 0.276, min -0.080, max 0.641.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (close at t-11
  equals close at t-12: a no-trade carried price, or the 3-dp closeadj grid
  below $0.50). No default and no signal zero-fill.
  What share of the universe does nothing? Spec measured a modal share of the
  scored cross-section of median 0.22%, mean 0.32%, max 1.63% over 276 months
  (2021-11 0.09%); distinct/n >= 0.967 every month; 10 qcut bins every month.
  Preflight to confirm.
  Tie handling: none needed, nothing removed or floored; the only guard is a
  positive close at each end (null otherwise).

DEVIATIONS FROM OSAP:
  - crsp.ret (monthly total return incl. delisting return) -> SEP closeadj
    month-end ratio; no delisting return (none is reproduced in a past-return
    window).
  - A missing close is NaN; OSAP fills ret 0 on an existing row
    (ret.fillna(0)) and leaves a calendar-gap lag NaN.
  - Calendar business month-ends with a 7-day tolerance, not row-based lags.
  - Coverage 85.6%-99.4% of the universe (spec-measured): names without a
    close near BME(t-11) or BME(t-12) are NaN.
  - OSAP's paper sort is on NYSE/AMEX (SignalDoc Filter exchcd in 1,2); the
    harness universe is its own.
  - One return only, so a single extreme month moves a name far; the harness
    winsorises before ranking.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    d = ctx.at_month_ends("SEP", ["closeadj"], [11, 12])
    px = d.pivot(index="ID", columns="months_back", values="closeadj").astype(float)
    px = px.reindex(index=ctx.ids, columns=[11, 12])
    px = px.where(px > 0)
    return (px[11] / px[12] - 1.0).replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MomSeasonShort",
    col="f_momseasonshort",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH same-month return last year is the long leg
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="MomSeasonShort",
    source="Heston and Sadka 2008 (Journal of Financial Economics)",
    lookback_months=12,
    history_months=12,              # closes at the month-ends t-11 and t-12
    notes="single monthly return of month t-11 (closeadj BME(t-11)/BME(t-12)-1); oldest month of the 12-1 window; sign +1",
    field_mappings=(
        ("crsp.ret (monthly, dlret-adjusted), lag 11", "SEP.closeadj[t-11]/SEP.closeadj[t-12] - 1",
         "total-return month-end ratio; no delisting return; missing close -> NaN (OSAP fills 0 on an existing row)"),
        ("calendar-month lag merge (stata_multi_lag)", "ctx.at_month_ends(..., [11, 12]), 7-day tolerance",
         "business month-end; same rule as the history gate"),
        ("crsp.dlret", "none", "no delisting return in the past-return window"),
    ),
)
