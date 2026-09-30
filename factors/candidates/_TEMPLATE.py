"""
<FactorName> — <one line: what it measures and why it might predict returns>

OSAP: <Acronym>, <Authors Year, Journal>. Predicted sign: <+/->.
Spec: osap_source/cache/<ref-prefix>/<Acronym>/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  <formula in words, with the exact SF1 / SEP / DAILY fields>

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? <e.g. exactly 0.0>
  What share of the universe does nothing? <estimate, and what preflight measured>
  Tie handling: <remove (restrict sample) | null | floor the denominator> and why.

DEVIATIONS FROM OSAP:
  - <field>: <what Sharadar has instead, and what it changes>

Copy this file to factors/candidates/<FactorName>.py. Delete this docstring's
angle-bracket prompts; keep the headings.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    """ctx is a harness.data_layer.MonthContext. Available:

      ctx.universe                      frame indexed by ID: mkt_cap_usd, adv_usd,
                                        px_usd, closeadj, sector, liq_tier, ...
      ctx.fundamentals(fields, lag_months=0, dimension=None)
                                        latest SF1 filing per ID with datekey <=
                                        signal - lag, within the age limit. NaN
                                        where none. Frame indexed by ID.
      ctx.fundamentals_history(fields, n_periods, dimension="ARQ")
                                        last N filings KNOWN at the signal, long
                                        frame with q_back (0 = latest); align
                                        quarters by reportperiod, not by as-of
      ctx.fundamentals_yoy(fields, years=1)
                                        latest filing AND the same fiscal period
                                        `years` earlier, aligned by reportperiod
                                        (<field> and <field>_lag). USE THIS for
                                        every year-over-year change, never
                                        fundamentals(lag_months=12)
      ctx.monthly_closeadj(months_back) wide closeadj at business month-ends
      ctx.has_price_at(months_back)     the history gate (applied by the harness
                                        when history_months is set)
      ctx.daily(table, fields, days_back)  SEP or DAILY rows in (signal - d, signal]
      ctx.ticker_meta(fields)           TICKERS columns (siccode, ...) — CURRENT
                                        classifications; sample restrictions only
      ctx.signal_asof, ctx.ids

    Return a Series indexed by ID (any subset; missing IDs become NaN).
    Guard every denominator: `den.where(den > 0)`. A negative denominator is a
    SIGN FLIP, not an outlier, and winsorisation will not save it.
    Never filter by date, universe or anything the harness owns.
    """
    f = ctx.fundamentals(["<field_a>", "<field_b>"])
    num = f["<field_a>"].astype(float)
    den = f["<field_b>"].astype(float)
    return num / den.where(den > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET. A family is assigned in Phase C, after this factor's
    # Stage 1 row exists and before any Stage 2 number; the loop writes it here.
    name="<FactorName>",
    col="f_<short>",
    compute=_compute,
    ascending=True,                 # from the spec's PREDICTED SIGN, never intuition
    weight=1.0,
    inputs=("SF1.<field_a>", "SF1.<field_b>"),
    osap_acronym="<Acronym>",
    source="<Authors Year (Journal)>",
    lookback_months=15,             # how far back the signal reaches
    # history_months=12,            # REQUIRED for any return-window signal
    # dimension="ARQ",              # only if the ART default makes it WRONG
    notes="<one line>",
    field_mappings=(
        ("<Compustat/CRSP input>", "<SF1/SEP field>", "<deviation, concretely>"),
    ),
)
