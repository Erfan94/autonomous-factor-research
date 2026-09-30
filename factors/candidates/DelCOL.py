"""
DelCOL — change in current operating liabilities (current liabilities net of
short-term debt) scaled by average total assets; firms whose operating
liabilities grow are predicted to earn LOWER returns.

OSAP: DelCOL, Richardson, Sloan, Soliman and Tuna 2005, Journal of Accounting
and Economics (Table 8C). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/DelCOL/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["liabilitiesc", "debtc", "assets"])
      (ART default; the latest filing known at the signal and the same fiscal
      period one year earlier, aligned by reportperiod within 45 days)
  col     = liabilitiesc - debtc;  col_lag likewise on the year-ago period
  DelCOL  = (col - col_lag) / ((assets + assets_lag) / 2)
  Guards: average assets <= 0 or null -> NaN; liabilitiesc or debtc null at
  either date -> NaN; missing year-ago period -> NaN; non-finite -> NaN.
  All three fields are balance-sheet levels (ART equals ARQ on the same
  reportperiod): no flow, no TTM smear, no dimension override, all in the
  filer's reporting currency so the ratio needs no fxusd gate.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no change in
  liabilitiesc - debtc between the two dates). A difference of two USD-level
  differences is essentially never an exact tie.
  What share of the universe does nothing? Expected well below 1% (the spec
  measured 0.02-0.06% on raw SF1 ART); preflight decides. The 27% exact-zero
  share of debtc is a level-side point mass that cancels inside the change.
  Tie handling: null (restrict the sample). Names with no classified current
  liabilities (unclassified balance sheets, ~20%: liabilitiesc and debtc both
  null, 71% financials, 20% real estate) are NaN, NOT zero-filled;
  blend_ranks renormalises. Ties otherwise negligible.

DEVIATIONS FROM OSAP:
  - OSAP zero-fills lct. For an unclassified filer that makes the signal
    -(dlc - dlc_lag)/avgAT where Compustat reports dlc, or NaN where it does
    not: an artefact of the fill. Here a null liabilitiesc or debtc at either
    date -> NaN, so coverage is ~80% of the universe, not the full sample.
  - ASC 842 lessee step: from FY2019 filings the current operating-lease
    liability sits in total current liabilities (liabilitiesc, as in
    Compustat lct) and SF1 debtc absorbs it too (Compustat dlc does not).
    liabilitiesc - debtc therefore nets the line out, so this construction
    should carry no lease step, whereas OSAP's lct - dlc carries a one-off
    positive lessee step in 2019-2020. The paired shift is not measured.
  - timing: latest ART filing (0-3 months old, at most
    max_fundamental_age_months = 15) against the same fiscal period one year
    earlier (rolling four-quarter change, refreshed quarterly), not OSAP's
    fiscal-year values with datadate + 6 months held 12 months. The 6-month
    lag is not reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not OSAP's shift(12)
    monthly rows; a stale or missing year-ago filing is NaN, not a false zero.
  - avg assets > 0 guard (OSAP has none).
  - early window: SF1 starts 1997Q4, so the 1999-01 signal has a year-ago
    period for only part of the universe (~38-48%), ~71-89% from 1999-03.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["liabilitiesc", "debtc", "assets"])
    col = y["liabilitiesc"].astype(float) - y["debtc"].astype(float)
    col_lag = y["liabilitiesc_lag"].astype(float) - y["debtc_lag"].astype(float)
    avg_assets = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    out = (col - col_lag) / avg_assets.where(avg_assets > 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelCOL",
    col="f_delcol",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW growth in operating liabilities is attractive
    weight=1.0,
    inputs=("SF1.liabilitiesc", "SF1.debtc", "SF1.assets"),
    osap_acronym="DelCOL",
    source="Richardson, Sloan, Soliman and Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="((liabilitiesc - debtc) - year-ago) / average assets; NaN where liabilitiesc/debtc null (unclassified, ~20%); ASC 842 line netted out (OSAP lct-dlc steps 2019-20); sign -1",
    field_mappings=(
        ("compustat.lct", "SF1.liabilitiesc (ART)",
         "null (unclassified balance sheets, ~20%, financials/REITs) stays NaN; OSAP zero-fills lct, which manufactures a -delta-dlc artefact, not reproduced"),
        ("compustat.dlc", "SF1.debtc (ART)",
         "null stays NaN (no zero-fill); from FY2019 debtc can absorb current operating-lease liabilities as does liabilitiesc, so the line nets out here; OSAP lct - dlc steps up in 2019-2020, declared"),
        ("compustat.at", "SF1.assets (ART)",
         "average of latest and year-ago assets, guard > 0; null -> NaN; no fxusd gate (same-currency ratio)"),
        ("lct/dlc/at shift(12)", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance), not 12 monthly rows; missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
