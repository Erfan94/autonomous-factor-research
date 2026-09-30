"""
ChEQ — year-over-year growth of book equity (ratio of this year's book equity
to last year's); firms that grow book equity quickly (issuance, retention) are
predicted to earn LOWER returns, so the long leg is LOW equity growth.

OSAP: ChEQ, Lockwood and Prombutr 2010, Journal of Financial Research
(SUSG, sustainable growth). Predicted sign: - (SignalDoc Sign = -1: high
value, low return).
Spec: osap_source/cache/b4e911e6/ChEQ/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["equity"])   (ART default; latest filing known at
      the signal and the filing for the SAME fiscal period one year earlier,
      aligned by reportperiod within 45 days)
  ChEQ = SF1.equity / SF1.equity_lag where BOTH are > 0, else NaN.
  Raw ratio (1.0 = no change), no log (monotone). Equity is a balance-sheet
  LEVEL, so ART equals ARQ on the same reportperiod: no flow, no TTM smear,
  no dimension override. Both levels are in the same reporting currency, so
  the ratio needs no fxusd gate.
  Guards: equity <= 0 now or a year ago -> NaN (OSAP's own filter; negative
  equity is real and is NOT filled with 0 or 1, which would create a mass
  point). Missing or stale year-ago period -> NaN (never a false 1.0).
  Non-finite -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 1.0 (equity
  unchanged year on year).
  What share of the universe does nothing? Essentially none: equity moves
  with every quarter of earnings, dividends, buybacks and option issuance;
  only dormant shells or rounded reported equity tie at 1.0, expected well
  under 1%. Preflight to confirm the modal share.
  Tie handling: null. Filing-staleness ties (same filing at both dates) are
  removed by fundamentals_yoy, which returns NaN instead of 1.0. No
  zero-fill, no floor. Remaining exact 1.0 values get the harness average
  rank.

DEVIATIONS FROM OSAP:
  - ceq: SF1.equity is parent equity INCLUDING preferred; Compustat ceq
    EXCLUDES preferred (pstk/pstkl/pstkrv/pstkq are not in SF1). Per ruling
    book_equity_preferred_terms this is approx: growth of total parent equity
    proxies growth of common equity and differs only for preferred issuers.
  - timing: latest ART filing (0-3 months old, at most
    max_fundamental_age_months = 15) against the same fiscal period one year
    earlier (rolling four-quarter growth, refreshed quarterly), not OSAP's
    fiscal-year ceq with datadate + 6 months held 12 months. The 6-month lag
    is not reproduced.
  - year-ago level by reportperiod (fundamentals_yoy), not OSAP's shift(12)
    monthly rows, which misalign after a skipped fiscal year.
  - upstream Compustat row filter (non-null at, prcc_c, ni) not reproduced:
    a difference in sample, not in value.
  - early window: SF1 calendardate starts 1997Q4, so early-1999 signal months
    whose latest filing is 1998Q1-Q3 have no year-ago period and are NaN;
    coverage broadens by about March-May 1999. Not back-filled.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["equity"])
    eq = y["equity"].astype(float)
    eq_lag = y["equity_lag"].astype(float)
    ok = (eq > 0) & (eq_lag > 0)
    out = (eq / eq_lag.where(eq_lag > 0)).where(ok)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChEQ",
    col="f_cheq",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW equity growth is attractive
    weight=1.0,
    inputs=("SF1.equity",),
    osap_acronym="ChEQ",
    source="Lockwood and Prombutr 2010 (Journal of Financial Research)",
    lookback_months=27,             # latest filing up to 15 months old + year-ago period 12 months earlier
    notes="equity / year-ago equity (both > 0), report-period aligned; sign -1",
    field_mappings=(
        ("compustat.ceq", "SF1.equity (ART)",
         "approx (ruling book_equity_preferred_terms): SF1.equity includes preferred, Compustat ceq excludes it; growth of total parent equity proxies common-equity growth"),
        ("compustat.ceq shift(12)", "SF1.equity_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance), not 12 monthly rows; missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span, 0-3 months old; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
