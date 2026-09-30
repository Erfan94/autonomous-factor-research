"""
STreversal — short-term reversal: last month's return, on the idea that one-month
winners give back part of the move (liquidity provision / overreaction).

OSAP: STreversal, Jegadeesh 1990, Journal of Finance (Table 2, S1, Jan-Dec;
Acronym2 Mom1m). Predicted sign: - (last month's winners underperform; long the
lowest-return decile D1, short the highest).
Spec: osap_source/cache/b4e911e6/STreversal/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  p0 = SEP.closeadj at the signal business month-end (ctx.at_month_ends lag 0)
  p1 = SEP.closeadj at the previous business month-end (lag 1)
  score = p0 / p1.where(p1 > 0) - 1
  closeadj is split- and dividend-adjusted, so the ratio is a total return over the
  month ending at the signal date (known at the signal date). Raw, no winsorising.
  ascending=False: a HIGH last-month return is unattractive (the low-return end is the long leg, harness D10),
  matching SignalDoc Sign = -1.
  Relation to the v0 Momentum leg (factual): Momentum is closeadj(signal - 1m) /
  closeadj(signal - 12m) - 1 and skips the most recent month; this signal is exactly
  that skipped month. The windows are adjacent and non-overlapping and share one
  price point (closeadj at signal - 1m). Spec-measured Spearman of raw STreversal
  with raw Momentum: mean 0.05 (range -0.38 to 0.46, 92 months).

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - p1 > 0 (closeadj is positive for a live price; guard kept for the ratio).
  - Non-finite results -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A stock whose price did not change
  between the two month-ends: exactly 0.0 (closeadj sits on a 3-dp grid, so equal
  month-end prices tie).
  What share of the universe does nothing? Spec measurement on 92 of 276 decision
  months: exact 0.0 is 0.26% of scored names mean (max 1.12% at 1999-06-30); modal
  value 0.0 in 70 of 92 months; distinct values ~ n; 10 qcut bins; coverage 99.8%
  mean (min 98.9%). Preflight measures it again.
  Tie handling: null for a missing return (see below); no rule for the true zeros,
  which are a real observation and far below the 10% cliff (average rank).

DEVIATIONS FROM OSAP:
  - ret.fill_null(0) is NOT reproduced: OSAP turns every MISSING return into 0.0,
    which would pile an artificial mass at zero above the true zero-return share. Here
    a missing return stays NaN and blend_ranks renormalises.
  - ret -> closeadj ratio - 1 between business month-ends (CRSP: calendar-month
    holding-period return). The two coincide when the last trading day of the month is
    the business month-end. Reads use ctx.at_month_ends with its 7-day tolerance.
  - dlret (delisting return, inside OSAP's ret) has no Sharadar field; a name
    delisted in month t has no month-end t row and is not in the t universe, so it
    cannot reach the signal.
  - history_months=1: the harness nulls a name with no trade near the window start,
    so a name listed this month is not scored.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    px = ctx.at_month_ends("SEP", ["closeadj"], [0, 1])
    w = px.pivot_table(index="ID", columns="months_back", values="closeadj", aggfunc="last")
    nan = pd.Series(np.nan, index=ctx.ids)
    p0 = w[0].astype(float).reindex(ctx.ids) if 0 in w.columns else nan
    p1 = w[1].astype(float).reindex(ctx.ids) if 1 in w.columns else nan

    out = p0.where(p0 > 0) / p1.where(p1 > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="STreversal",
    col="f_streversal",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW last-month return is attractive (the long leg)
    weight=1.0,
    inputs=("SEP.closeadj",),
    osap_acronym="STreversal",
    source="Jegadeesh 1990 (Journal of Finance)",
    lookback_months=1,              # one month-end of price history
    history_months=1,               # return-window signal: a trade near the t-1 month-end is required
    notes="closeadj(t)/closeadj(t-1 month-end) - 1; missing return stays NaN (no fill_null(0)); sign -1",
    field_mappings=(
        ("crsp.ret", "SEP.closeadj_t / SEP.closeadj_t-1 - 1 (ctx.at_month_ends)",
         "month-end to month-end total return via adjusted close; 7-day tolerance on each end"),
        ("crsp.dlret", "none", "delisting return unavailable; irrelevant to a name alive at the signal month-end"),
        ("fill_null(0)", "not reproduced", "missing return stays NaN instead of 0.0; removes OSAP's artificial zero mass"),
    ),
)
