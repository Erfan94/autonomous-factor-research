"""
CompositeDebtIssuance — five-year log growth in total debt (long-term debt
plus debt in current liabilities). Heavy debt issuers are predicted to earn
LOWER returns, so the long leg is LOW debt growth (repayers).

OSAP: CompositeDebtIssuance (Acronym2 DebtFinC), Lyandres, Sun and Zhang
2008, Review of Financial Studies. Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/CompositeDebtIssuance/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["debt"], years=5)   (ART default; latest filing
      known at the signal and the filing for the SAME fiscal period five
      years earlier, aligned by reportperiod within 45 days)
  CompositeDebtIssuance = log(SF1.debt / SF1.debt_lag), both > 0, else NaN.
  SF1.debt is the level dltt + dlc (NOT rebuilt from debtc + debtnc, which
  are null on ~20% of rows, the unclassified balance-sheet block). A
  balance-sheet LEVEL: ART equals ARQ on the same period, no flow, no TTM
  smear, no dimension override, no price window (no history_months).
  Non-finite -> NaN. Stale or missing five-year-ago period -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (unchanged
  dollar debt), but unrounded SF1 USD levels make that very rare. The real
  mass point is ZERO DEBT, where the log is undefined.
  What share of the universe does nothing? Checker measured a residual modal
  share of the scored log change of 0.07-0.43% per month. Zero debt at either
  end: 0.3% (1999-12), 13.7% (2008-12), 10.1% (2020-12) of the universe.
  Tie handling: remove by nulling: debt == 0 at either end -> NaN (log
  undefined; OSAP gets +/-inf, handling unverified). Blend_ranks renormalises.
  No floor and no zero-fill (a floor would manufacture a +/-large spike).

DEVIATIONS FROM OSAP:
  - debt includes operating-lease liabilities from ASC 842 (FY2018 early
    adopters, FY2019 calendar filers); Compustat dltt + dlc does not. A
    five-year change whose current end is a FY2019+ filing and whose base is
    earlier carries a lessee-wide positive step, for signals from 2019 on
    (the base stays pre-ASC 842 for five years). Sector ranking removes a
    sector-wide step, not a lessee/non-lessee step inside a sector.
  - ONE-SIDED zero exclusion from 2019: lease liabilities take current-end
    zeros from ~10-11% to ~1.6-1.9% of the universe while base-end zeros stay
    10-12%, so firms going from no debt to lease-only debt are dropped while
    the symmetric case no longer exists. The truncated tails differ before
    and after 2019.
  - bank debt in Sharadar includes repo and short-term borrowings; OSAP does
    not exclude financials and Compustat dltt + dlc for banks is narrower.
  - timing: latest ART filing (datekey known) against the same fiscal period
    five years earlier, refreshed quarterly; not OSAP's annual value at
    datadate + 6 months held 12 months. The 6-month lag is not reproduced.
  - five-year-ago level by reportperiod (45-day tolerance), not OSAP's
    shift(60) monthly rows.
  - upstream Compustat row filter (non-null at, prcc_c, ni) not reproduced.
  - coverage: SF1 is thin before FY1997, so the five-year pair is 9% of the
    universe at 1999-12, 50% at 2002-12 and ~81% from 2003-12; decision
    months before ~2002-06 fall under the coverage bar.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["debt"], years=5)
    d = y["debt"].astype(float)
    d_lag = y["debt_lag"].astype(float)
    ok = (d > 0) & (d_lag > 0)
    out = np.log(d.where(d > 0) / d_lag.where(d_lag > 0)).where(ok)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CompositeDebtIssuance",
    col="f_compdebtiss",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW debt growth is attractive
    weight=1.0,
    inputs=("SF1.debt",),
    osap_acronym="CompositeDebtIssuance",
    source="Lyandres, Sun and Zhang 2008 (Review of Financial Studies)",
    lookback_months=80,             # 60-month base + latest filing up to 15 months old + ~4m report-period-to-filing lag
    notes="log(debt / debt five years earlier), both > 0, report-period aligned; sign -1",
    field_mappings=(
        ("compustat.dltt + dlc", "SF1.debt (ART)",
         "verified-with-deviation: lease-inclusive from FY2019 (ASC 842), so the 5-year change is confounded for signals from 2019; bank repo/short-term borrowings included"),
        ("compustat.dltt/dlc shift(60)", "SF1.debt_lag via ctx.fundamentals_yoy(years=5)",
         "five-year-ago level by reportperiod (45-day tolerance), not 60 monthly rows; missing/stale -> NaN"),
        ("zero debt (log -> +/-inf)", "debt == 0 at either end -> NaN",
         "0.3-13.7% of universe dropped; from 2019 one-sided (current-end zeros fall to ~1.8%, base-end zeros stay 10-12%)"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
