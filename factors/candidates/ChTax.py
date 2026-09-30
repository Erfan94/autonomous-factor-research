"""
ChTax — 4-quarter change in quarterly total tax expense scaled by lagged total
assets (Thomas and Zhang 2011, Table 2 col 1); firms whose tax expense rises
are predicted to earn HIGHER returns (earnings-growth information in taxes).

OSAP: ChTax (Acronym2 TaxGr), Thomas and Zhang 2011, Journal of Accounting
Research. Predicted sign: + (SignalDoc Sign = +1: high value, high return).
Spec: osap_source/cache/b4e911e6/ChTax/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["taxexp","assets"], dimension="ARQ")
      (latest filed quarter and the same fiscal quarter one year earlier,
      aligned by reportperiod within 45 days)
  ChTax = (taxexp - taxexp_lag) / assets_lag
  Denominator: year-ago QUARTER total assets from the same ARQ frame
  (assets_lag > 0, else NaN).
  taxexp null on either side -> NaN (no fill); missing year-ago quarter ->
  NaN; non-finite -> NaN. Negative taxexp (tax benefits, ~15% of ARQ rows) is
  legitimate and is not clipped.
  dimension="ARQ" is MANDATORY: taxexp is a flow. ARQ is the single-quarter
  value; ART is a trailing-four-quarter sum (ART equals ARQ on only ~17% of
  rows), whose 12-month difference would smear four quarters and is thinly
  populated in 1998. The assets legs are balance-sheet levels (ART == ARQ).
  Both sides in the filer's reporting currency; no fxusd gate.
  Score = +ChTax (ascending=True).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0: taxexp equal in
  both quarters. Sharadar zero-fills taxexp when the statement does not carry
  it (ARQ exact-zero ~20% of rows), so loss-makers, NOL and tax-free
  structures and vendor-imputed zeros all give (0 - 0)/assets_lag = 0.
  What share of the universe does nothing? Measured by the field-checker on
  the harness universe: taxexp exactly 0 in BOTH quarters is 4.5-11.2% of the
  universe by month (an unfiltered US-common pair sample gave ~17%). An
  unchanged NONZERO taxexp is ~0.45%, the residual modal share.
  Tie handling: null (restrict the sample). ChTax is set to NaN wherever
  taxexp is exactly 0 in BOTH quarters; blend_ranks renormalises. One-end-zero
  pairs (0 against a nonzero) are KEPT: they are a real change from or to a
  zero tax bill. Coordinator decision: a both-zero pair is either an
  unreported quarter or a loss-maker with no tax in either year, for which the
  change is undefined rather than a flat middle; OSAP's zero-tax firms are
  therefore removed here, not ranked. No noise or secondary key is used to
  break ties.

DEVIATIONS FROM OSAP:
  - both-zero pairs are NaN; OSAP keeps them at 0 (its txtq is NaN for an
    unreported quarter, so the vendor zero-fill inflates the tie here).
  - denominator: year-ago quarter assets (12 months old, from the ARQ yoy
    frame) instead of OSAP's annual `at` forward-filled, which is the latest
    fiscal year-end known 12 months earlier (18-30 months before the signal,
    stale by design). A level difference of a few to ~10% inside a ratio
    that is ranked.
  - timing: latest ARQ filing with datekey <= signal against the same fiscal
    quarter a year earlier, refreshed once per quarterly filing (as OSAP);
    OSAP's rdq / datadate + 3 month rule and 3-month hold are not reproduced
    (the hold is harness-side).
  - year-ago quarter by reportperiod (fundamentals_yoy), not a calendar
    lookup on time_avail_m; a stale filing yields NaN, not a false zero.
  - early window: SF1 starts 1997Q4, so the 1999-01..02 signal months hold only
    early filers whose year-ago quarter is >= 1998Q4 (thin, not back-filled).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["taxexp", "assets"], dimension="ARQ")
    tax = y["taxexp"].astype(float)
    tax_lag = y["taxexp_lag"].astype(float)
    den = y["assets_lag"].astype(float)

    chg = (tax - tax_lag) / den.where(den > 0)

    # Tie rule: Sharadar zero-fills taxexp; 0 in BOTH quarters -> undefined.
    both_zero = (tax == 0) & (tax_lag == 0)
    out = chg.where(tax.notna() & tax_lag.notna() & ~both_zero)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChTax",
    col="f_chtax",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH tax-expense change is attractive
    weight=1.0,
    inputs=("SF1.taxexp", "SF1.assets"),
    osap_acronym="ChTax",
    source="Thomas and Zhang 2011 (Journal of Accounting Research)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago quarter 12 months earlier + ~4m report-period-to-filing lag
    dimension="ARQ",                # taxexp is a flow: ART is a TTM sum whose 12m difference smears four quarters
    notes="(taxexp - year-ago quarter taxexp) / year-ago quarter assets, ARQ; NaN where taxexp is 0 in both quarters; sign +1",
    field_mappings=(
        ("compustat.txtq", "SF1.taxexp (ARQ)",
         "single-quarter flow; Sharadar zero-fills taxexp, so exactly 0 in both quarters -> NaN (OSAP keeps 0); one-end-zero kept; negatives not clipped"),
        ("compustat.at (annual, l12)", "SF1.assets_lag via fundamentals_yoy (ARQ)",
         "year-ago QUARTER assets (12 months old) instead of OSAP's stale annual at (18-30 months old); guard > 0"),
        ("txtq l12 (calendar-matched)", "taxexp_lag via ctx.fundamentals_yoy",
         "same fiscal quarter a year earlier by reportperiod (45-day tolerance); missing/stale -> NaN"),
        ("rdq / datadate + 3 months availability", "latest ARQ filing with datekey <= signal",
         "refreshed per quarterly filing; OSAP's 3-month hold is harness-side"),
    ),
)
