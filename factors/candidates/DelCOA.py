"""
DelCOA — change in non-cash current operating assets, (current assets minus
cash and short-term investments), scaled by average total assets; firms that
grow operating current assets (receivables, inventory) are predicted to earn
LOWER returns.

OSAP: DelCOA, Richardson, Sloan, Soliman and Tuna 2005, Journal of Accounting
and Economics (Table 8C). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/DelCOA/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["assetsc", "cashneq", "investmentsc", "assets"])
      (ART default; the latest filing known at the signal and the same fiscal
      period one year earlier, aligned by reportperiod within 45 days)
  che  = cashneq + investmentsc.fillna(0)   (NaN only where cashneq is NaN);
         the same on the year-ago period
  coa  = assetsc - che;  coa_lag likewise
  DelCOA = (coa - coa_lag) / ((assets + assets_lag) / 2)
  Guards: average assets <= 0 or null -> NaN; assetsc null at either date ->
  NaN; missing year-ago period -> NaN; non-finite -> NaN.
  All four fields are balance-sheet levels (ART equals ARQ on the same
  reportperiod): no flow, no TTM smear, no dimension override, all in the
  filer's reporting currency so the ratio needs no fxusd gate.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no change in
  assetsc - che between the two dates). Across two USD-level differences this
  is essentially never an exact tie; the one structural source is the
  zero-fill below, which this file does not apply.
  What share of the universe does nothing? Expected well below 1%; preflight
  decides. assetsc is exactly 0 on 0.02% of non-null rows.
  Tie handling: null (restrict the sample). The ~20% of names with no
  classified current assets (unclassified balance sheets: 71.5% financials,
  19.8% REITs; assetsc null) are NaN, not zero-filled; blend_ranks
  renormalises. Ties otherwise negligible.

DEVIATIONS FROM OSAP:
  - OSAP zero-fills act and che. For a firm with no classified current assets
    that turns the signal into -(che - che_lag)/avgAT, an artefact of the
    fill. Here assetsc null (either date) -> NaN, so coverage is ~80% of the
    universe. che itself is never null for those names, but the signal is.
  - che = cashneq + investmentsc.fillna(0): investmentsc also holds current
    financing / loan receivables for captive-finance filers (overstates che
    for CSCO, F, GM, IBM, HPE, HOG); for financials/REITs it understates che
    (not reachable: those names are NaN anyway).
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
    y = ctx.fundamentals_yoy(["assetsc", "cashneq", "investmentsc", "assets"])

    def che(sfx):
        return y[f"cashneq{sfx}"].astype(float) + y[f"investmentsc{sfx}"].astype(float).fillna(0.0)

    coa = y["assetsc"].astype(float) - che("")
    coa_lag = y["assetsc_lag"].astype(float) - che("_lag")
    avg_assets = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    out = (coa - coa_lag) / avg_assets.where(avg_assets > 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelCOA",
    col="f_delcoa",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW growth in operating current assets is attractive
    weight=1.0,
    inputs=("SF1.assetsc", "SF1.cashneq", "SF1.investmentsc", "SF1.assets"),
    osap_acronym="DelCOA",
    source="Richardson, Sloan, Soliman and Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="((assetsc - che) - year-ago) / average assets; NaN where assetsc is null (unclassified balance sheets); sign -1",
    field_mappings=(
        ("compustat.act", "SF1.assetsc (ART)",
         "null (unclassified balance sheets, ~20%, financials/REITs) stays NaN; OSAP zero-fills, which manufactures a -delta-che artefact, not reproduced"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc.fillna(0) (ART)",
         "investmentsc includes financing/loan receivables for captive-finance filers (overstates che); null investmentsc -> 0"),
        ("compustat.at", "SF1.assets (ART)",
         "average of latest and year-ago assets, guard > 0; null -> NaN; no fxusd gate (same-currency ratio)"),
        ("act/che/at shift(12)", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance), not 12 monthly rows; missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
