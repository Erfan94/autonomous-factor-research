"""
DelEqu — change in book equity scaled by average total assets; firms that
grow book equity (retained earnings, issuance) are predicted to earn LOWER
returns.

OSAP: DelEqu, Richardson, Sloan, Soliman and Tuna 2005, Journal of Accounting
and Economics (Table 9A). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/DelEqu/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["equity", "assets"])
      (ART default; the latest filing known at the signal and the same fiscal
      period one year earlier, aligned by reportperiod within 45 days)
  DelEqu = (equity - equity_lag) / ((assets + assets_lag) / 2)
  Guards: average assets <= 0 or null -> NaN; equity null at either date ->
  NaN; missing year-ago period -> NaN; non-finite -> NaN. Negative book
  equity is kept (OSAP keeps it). Both fields are balance-sheet levels (ART
  equals ARQ on the same reportperiod): no flow, no TTM smear, no dimension
  override, same reporting currency so the ratio needs no fxusd gate.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (equity unchanged
  to the dollar over twelve months).
  What share of the universe does nothing? Essentially none (spec measured
  0.00-0.11% exact-zero on raw SF1 ART); preflight decides.
  Tie handling: null where an input is missing; no tie treatment needed
  beyond that, the change is continuous.

DEVIATIONS FROM OSAP:
  - ceq -> SF1.equity: SF1 equity is parent equity INCLUDING preferred stock
    (Compustat ceq excludes it). Preferred issues/redemptions therefore enter
    the signal here and do not in OSAP. Approximation (ruling
    book_equity_preferred_terms); preferred is not separable and is not
    removed.
  - timing: latest ART filing (0-3 months old, at most
    max_fundamental_age_months = 15) against the same fiscal period one year
    earlier (rolling four-quarter change, refreshed quarterly), not OSAP's
    fiscal-year values with datadate + 6 months held 12 months. The 6-month
    lag is not reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not OSAP's calendar
    merge on time_avail_m; a stale or missing year-ago filing is NaN.
  - avg assets > 0 guard (OSAP has none).
  - early window: SF1 starts 1997Q4, so the 1999-01 signal has a year-ago
    period for only part of the universe (~38-48%), ~71-89% from 1999-03.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["equity", "assets"])
    d_eq = y["equity"].astype(float) - y["equity_lag"].astype(float)
    avg_assets = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    out = d_eq / avg_assets.where(avg_assets > 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelEqu",
    col="f_delequ",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW growth in book equity is attractive
    weight=1.0,
    inputs=("SF1.equity", "SF1.assets"),
    osap_acronym="DelEqu",
    source="Richardson, Sloan, Soliman and Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="(equity - year-ago equity) / average assets; equity includes preferred (approx); sign -1",
    field_mappings=(
        ("compustat.ceq", "SF1.equity (ART)",
         "parent equity INCLUDING preferred (ceq excludes it): preferred changes enter the signal; approx per book_equity_preferred_terms"),
        ("compustat.at", "SF1.assets (ART)",
         "average of latest and year-ago assets, guard > 0; null -> NaN; no fxusd gate (same-currency ratio)"),
        ("ceq/at calendar-month merge", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance); missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
